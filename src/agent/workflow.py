"""Deterministic routing for the trend tools used by the existing chatbot."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from langchain_core.tools import BaseTool

from src.services.trend_service import fold_text
from src.tools.trend_tools import (
    compare_shop_product_with_trends,
    get_shopee_fashion_trends,
)

TREND_TOOLS: tuple[BaseTool, ...] = (
    get_shopee_fashion_trends,
    compare_shop_product_with_trends,
)
TREND_TOOL_REGISTRY: dict[str, BaseTool] = {tool.name: tool for tool in TREND_TOOLS}
RESPONSE_TEMPERATURE = 0.6


@dataclass(frozen=True)
class HybridResponseContext:
    """Grounded, conversational context passed to the response-generation node."""

    prompt: str
    response_mode: str
    has_grounding_data: bool


class TrendAgentWorkflow:
    """Route trend-related chat turns to typed LangChain tools before the LLM."""

    _TREND_TERMS = (
        "xu huong", "trend", "shopee", "thi truong", "form", "chat lieu",
        "boxy", "raglan", "affiliate", "hoa hong", "gia doi thu",
    )

    def __init__(self, response_temperature: float = RESPONSE_TEMPERATURE) -> None:
        if not 0.5 <= response_temperature <= 0.7:
            raise ValueError("response_temperature phải nằm trong khoảng 0.5-0.7.")
        self.response_temperature = float(response_temperature)

    def should_use_trends(self, question: str) -> bool:
        """Return whether the user turn needs Shopee trend context."""
        folded = fold_text(question)
        return any(term in folded for term in self._TREND_TERMS)

    def invoke_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Invoke a registered trend tool by name."""
        try:
            selected = TREND_TOOL_REGISTRY[tool_name]
        except KeyError as exc:
            raise ValueError(f"Tool không được đăng ký: {tool_name}") from exc
        result = selected.invoke(arguments)
        return str(result)

    def build_context(
        self,
        question: str,
        order_summary: dict[str, Any] | None = None,
    ) -> str:
        """Build verified trend context for the current chatbot turn."""
        if not self.should_use_trends(question):
            return ""

        category = self._infer_category(question, order_summary)
        timeframe = self._infer_timeframe(question)
        blocks = [
            self.invoke_tool(
                "get_shopee_fashion_trends",
                {"category": category, "timeframe": timeframe, "limit": 5},
            )
        ]

        comparison = self._comparison_arguments(order_summary)
        if comparison:
            comparison.setdefault("category", category)
            blocks.append(self.invoke_tool("compare_shop_product_with_trends", comparison))
        return (
            "## Dữ liệu xu hướng đã tính từ Shopee CSV\n"
            + "\n\n## So sánh sản phẩm của shop\n".join(blocks)
        )

    def build_response_context(
        self,
        *,
        question: str,
        business_context: str = "",
        business_signals: str = "",
        retrieved_docs: str = "",
        trend_context: str = "",
        chat_history: list[dict[str, str]] | None = None,
    ) -> HybridResponseContext:
        """Compose the hybrid context consumed by the final LLM response node.

        Grounding sources remain in separate labelled sections so the model can
        distinguish shop facts, RAG documents, and market benchmarks. Recent
        conversation turns are included both here for semantic continuity and as
        native chat messages by the LLM client.
        """
        response_mode = self._response_mode(question)
        mode_instruction = {
            "concise": (
                "Trả lời tự nhiên, trực diện trong 1-2 đoạn ngắn. Không tạo bảng hoặc "
                "heading nếu người dùng không yêu cầu."
            ),
            "deep": (
                "Phân tích có cấu trúc. Dùng bullet points hoặc bảng Markdown khi giúp "
                "so sánh dữ liệu và chốt hành động rõ hơn."
            ),
            "standard": (
                "Trả lời ở độ dài vừa phải, ưu tiên ý chính và hành động thực tế; chỉ "
                "thêm cấu trúc khi cần để dễ đọc."
            ),
        }[response_mode]

        grounded_sections: list[str] = []
        if business_context.strip():
            grounded_sections.append(f"### Dữ liệu shop/client\n{business_context.strip()}")
        if trend_context.strip():
            grounded_sections.append(f"### Benchmark Trends/Tools\n{trend_context.strip()}")
        if retrieved_docs.strip():
            grounded_sections.append(f"### Tài liệu truy xuất từ RAG\n{retrieved_docs.strip()}")

        grounding_text = (
            "\n\n".join(grounded_sections)
            if grounded_sections
            else (
                "Không có số liệu grounding phù hợp cho lượt hỏi này. Nếu đây là câu hỏi "
                "sáng tạo hoặc nghiệp vụ, hãy chủ động dùng kiến thức chuyên môn nền."
            )
        )
        history_text = self._format_history(chat_history)
        signals_text = business_signals.strip() or "Không có business signal định lượng."

        prompt = f"""## Câu hỏi hiện tại
{question}

## Chế độ phản hồi đã định tuyến: {response_mode}
{mode_instruction}

## Grounding Data
{grounding_text}

## Business Signals
{signals_text}

## Conversational Context
{history_text}

Hãy trả lời câu hỏi hiện tại. Chỉ trích dẫn số liệu xuất hiện trong Grounding Data.
Với ý tưởng sáng tạo hoặc kiến thức nghiệp vụ không cần số liệu riêng của shop, hãy
chủ động dùng kiến thức chuyên sâu và đưa ra hướng dẫn thực thi cụ thể.
"""
        return HybridResponseContext(
            prompt=prompt,
            response_mode=response_mode,
            has_grounding_data=bool(grounded_sections),
        )

    @staticmethod
    def _response_mode(question: str) -> str:
        folded = fold_text(question)
        deep_terms = (
            "phan tich", "so sanh", "chien luoc", "ke hoach", "danh gia",
            "gap", "loi nhuan", "doanh thu", "chi tiet", "roadmap",
        )
        if any(term in folded for term in deep_terms):
            return "deep"
        tokens = folded.split()
        greeting_or_quick = (
            len(tokens) <= 10
            or folded in {"xin chao", "chao", "hello", "hi", "cam on", "ok"}
        )
        return "concise" if greeting_or_quick else "standard"

    @staticmethod
    def _format_history(
        chat_history: list[dict[str, str]] | None,
        *,
        max_messages: int = 8,
        max_characters: int = 6_000,
    ) -> str:
        if not chat_history:
            return "Chưa có lịch sử hội thoại trước đó."
        lines: list[str] = []
        total = 0
        for item in chat_history[-max_messages:]:
            role = "Người dùng" if item.get("role") == "user" else "Finora"
            content = str(item.get("content", "")).strip()
            if not content:
                continue
            remaining = max_characters - total
            if remaining <= 0:
                break
            content = content[:remaining]
            line = f"- {role}: {content}"
            lines.append(line)
            total += len(line)
        return "\n".join(lines) if lines else "Chưa có lịch sử hội thoại trước đó."

    @staticmethod
    def _infer_category(question: str, order_summary: dict[str, Any] | None) -> str:
        if order_summary:
            explicit = order_summary.get("category") or order_summary.get("gender")
            if explicit:
                return str(explicit)
        folded = fold_text(question)
        if re.search(r"\b(nu|female|women)\b", folded):
            return "nu"
        return "nam"

    @staticmethod
    def _infer_timeframe(question: str) -> str:
        folded = fold_text(question)
        if re.search(r"\b30\s*(?:d|day|days|ngay)\b", folded):
            return "30d"
        if re.search(r"\b(hom nay|today|1d)\b", folded):
            return "today"
        return "7d"

    @staticmethod
    def _comparison_arguments(order_summary: dict[str, Any] | None) -> dict[str, Any] | None:
        if not order_summary:
            return None
        aliases = {
            "product_name": ("product_name", "productName", "name"),
            "current_price": ("current_price", "currentPrice", "price"),
            "cogs": ("cogs", "COGS", "cost"),
            "affiliate_rate": ("affiliate_rate", "affiliateRate", "commission_rate"),
            "category": ("category", "gender"),
        }
        result: dict[str, Any] = {}
        for target, candidates in aliases.items():
            for candidate in candidates:
                if candidate in order_summary and order_summary[candidate] is not None:
                    result[target] = order_summary[candidate]
                    break
        required = {"product_name", "current_price", "cogs", "affiliate_rate"}
        return result if required.issubset(result) else None


def serialise_tool_schemas() -> str:
    """Return JSON schemas for diagnostics or a future model-native executor."""
    schemas = [
        {"name": item.name, "description": item.description, "args": item.args}
        for item in TREND_TOOLS
    ]
    return json.dumps(schemas, ensure_ascii=False, indent=2)
