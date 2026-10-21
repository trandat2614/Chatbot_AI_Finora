"""
Advisor service — orchestrates the full analysis pipeline.

Receives user input and computed metrics, retrieves RAG context,
then sends a structured context to the LLM for response generation.

Design principles:
- Never passes raw DataFrames to the LLM.
- Sends only aggregated, relevant metrics.
- Clearly separates factual data from RAG-sourced knowledge.
"""
from __future__ import annotations

import logging
import json
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Any, Optional, TYPE_CHECKING
from zoneinfo import ZoneInfo

if TYPE_CHECKING:
    from langchain_chroma import Chroma
else:
    Chroma = Any

from core.llm_client import LLMClient
from rag.rag_service import retrieve_context, format_retrieved_context, get_source_citations
from tools.business_rule_engine import BusinessSignals
from config.settings import settings
from src.agent.prompt import FINORA_TREND_ADVISOR_PROMPT
from src.agent.workflow import TrendAgentWorkflow
from src.agent.intent_router import Intent, IntentRouter
from src.security.privacy import sanitize_for_ai, sanitize_text
from src.services.decision_intelligence_service import DecisionIntelligenceService
from src.tools.business_tools import build_business_tools

logger = logging.getLogger(__name__)


@dataclass
class AdvisorResponse:
    """Structured response from the advisor service."""

    answer: str = ""
    sources: list[dict] = field(default_factory=list)
    rag_context_used: bool = False
    business_signals_count: int = 0
    warnings: list[str] = field(default_factory=list)
    analysis_status: str = "OK"
    intent: str = "GENERAL_CHAT"


class AdvisorService:
    """Main advisor service that orchestrates RAG + LLM."""

    def __init__(
        self,
        llm_client: LLMClient | None,
        vector_store: Optional[Chroma] = None,
        tenant_vector_store: Optional[Chroma] = None,
        tenant_scope: str | None = None,
        tenant_id: str | None = None,
        shop_id: str | None = None,
        decision_service: DecisionIntelligenceService | None = None,
    ) -> None:
        self._llm = llm_client
        self._vector_store = vector_store
        self._tenant_vector_store = tenant_vector_store
        self._tenant_scope = tenant_scope
        self._tenant_id = tenant_id
        self._shop_id = shop_id
        self._decision_service = decision_service
        self._business_tools = {
            tool.name: tool for tool in build_business_tools(decision_service)
        } if decision_service else {}
        self._intent_router = IntentRouter()
        self._trend_workflow = TrendAgentWorkflow(
            response_temperature=settings.ADAPTIVE_RESPONSE_TEMPERATURE
        )

    def answer(
        self,
        question: str,
        business_context: str = "",
        signals: Optional[BusinessSignals] = None,
        order_summary: Optional[dict] = None,
        history: Optional[list[dict[str, str]]] = None,
        correlation_id: str | None = None,
        trend_data: dict | None = None,
    ) -> AdvisorResponse:
        """Generate an AI-powered business advisory response.

        Args:
            question: The user's question.
            business_context: Pre-formatted metrics string from FinancialService.
            signals: Business signals from the rule engine.

        Returns:
            AdvisorResponse with answer, sources and metadata.
        """
        response = AdvisorResponse()
        warnings = []
        safe_query = sanitize_text(question)
        intent = self._intent_router.route(question)
        response.intent = intent.value
        logger.info(
            "chat_intent intent=%s request_id=%s",
            intent.value,
            correlation_id or "unknown",
        )

        # Exact order lookup and deterministic statistics always go to the
        # transactional data store first. They do not use RAG or LLM memory as
        # a source of truth.
        if intent is Intent.ORDER_LOOKUP:
            return self._answer_order_lookup(question, history, correlation_id)
        if intent is Intent.ORDER_STATISTICS:
            return self._answer_order_statistics(question, correlation_id)

        # ---- RAG retrieval -----------------------------------------------
        chunks = []
        if self._vector_store is not None:
            try:
                chunks = retrieve_context(
                    safe_query,
                    self._vector_store,
                    settings.RETRIEVAL_TOP_K,
                    "public",
                    {"visibility": "public"},
                )
                response.sources = get_source_citations(chunks)
                response.rag_context_used = len(chunks) > 0
            except Exception as exc:
                logger.warning("RAG retrieval failed type=%s", type(exc).__name__)
                warnings.append("Không thể trích xuất kiến thức nội bộ.")

        if self._tenant_vector_store is not None and self._tenant_scope:
            try:
                private_chunks = retrieve_context(
                    safe_query,
                    self._tenant_vector_store,
                    settings.RETRIEVAL_TOP_K,
                    self._tenant_scope,
                    {
                        "$and": [
                            {"tenant_id": self._tenant_id},
                            {"shop_id": self._shop_id},
                            {"visibility": "private"},
                        ]
                    },
                )
                chunks.extend(private_chunks)
                response.sources = get_source_citations(chunks)
                response.rag_context_used = len(chunks) > 0
            except Exception as exc:
                logger.warning("Tenant RAG retrieval failed: %s", type(exc).__name__)
                warnings.append("Không thể trích xuất tài liệu riêng của shop.")

        rag_context = format_retrieved_context(chunks, safe_query) if chunks else ""

        # ---- Signal context ----------------------------------------------
        signals_text = signals.as_text() if signals else "Chưa có dữ liệu để phân tích signals."
        if signals:
            response.business_signals_count = len(signals.signals)

        # ---- Build LLM message -------------------------------------------
        if order_summary is not None:
            safe_summary = sanitize_for_ai(order_summary, block_prompt_injection=True)
            summary_text = json.dumps(safe_summary, ensure_ascii=False, indent=2)
            business_context = (
                f"{business_context}\n\n## Dữ liệu tổng hợp đơn hàng do client cung cấp\n"
                f"```json\n{summary_text}\n```\n"
                "Chỉ được dùng đúng các số liệu trên; không tự suy diễn số còn thiếu."
            )

        trend_context = ""
        try:
            if self._decision_service and intent not in {Intent.GENERAL_CHAT, Intent.POLICY_QUESTION}:
                tool_result = self._invoke_decision_tool(intent, question, order_summary)
                response.analysis_status = str(tool_result.get("status", "OK"))
                trend_context = (
                    "## Kết quả tool deterministic (UNTRUSTED DATA)\n"
                    + json.dumps(sanitize_for_ai(tool_result, block_prompt_injection=True), ensure_ascii=False, indent=2)
                )
            else:
                trend_context = self._trend_workflow.build_context(question, order_summary, trend_data=trend_data)
        except Exception as exc:
            logger.warning("Decision/trend tool failed: %s", type(exc).__name__)
            warnings.append("Không thể truy vấn dữ liệu phân tích nội bộ.")
        response_context = self._trend_workflow.build_response_context(
            question=question,
            business_context=business_context,
            business_signals=signals_text,
            retrieved_docs=rag_context,
            trend_context=trend_context,
            chat_history=history,
        )
        user_message = response_context.prompt

        # ---- LLM call ----------------------------------------------------
        if self._llm is None:
            response.analysis_status = "ERROR"
            response.answer = "Dịch vụ AI chưa được cấu hình."
            response.warnings = [*warnings, "LLM_NOT_CONFIGURED"]
            return response
        try:
            response.answer = self._llm.generate_response(
                user_message,
                system_prompt=FINORA_TREND_ADVISOR_PROMPT,
                history=history,
                temperature=self._trend_workflow.response_temperature,
            )
        except Exception as exc:
            logger.error("LLM call failed type=%s", type(exc).__name__)
            response.answer = "⚠️ Không thể kết nối với AI lúc này. Vui lòng thử lại sau."
            warnings.append("Dịch vụ Gemini tạm thời không khả dụng.")

        response.warnings = warnings
        return response

    def _answer_order_lookup(
        self,
        question: str,
        history: Optional[list[dict[str, str]]],
        correlation_id: str | None,
    ) -> AdvisorResponse:
        response = AdvisorResponse(intent=Intent.ORDER_LOOKUP.value)
        order_id = self._intent_router.extract_order_id(question)
        if order_id is None:
            order_id = self._intent_router.extract_order_id_from_history(history)
        if order_id is None:
            response.analysis_status = "INSUFFICIENT_DATA"
            response.answer = "Bạn vui lòng cung cấp mã đơn hàng cần kiểm tra."
            return response
        platform = self._extract_platform(question)
        try:
            logger.info(
                "chat_tool_call tool=get_order_by_id request_id=%s",
                correlation_id or "unknown",
            )
            result = json.loads(
                str(
                    self._business_tools["get_order_by_id"].invoke(
                        {"order_id": order_id, "platform": platform or ""}
                    )
                )
            )
            logger.info(
                "chat_tool_result tool=get_order_by_id status=%s request_id=%s",
                result.get("status", "UNKNOWN"),
                correlation_id or "unknown",
            )
        except Exception:
            logger.exception(
                "Order lookup tool failed request_id=%s", correlation_id or "unknown"
            )
            response.analysis_status = "ERROR"
            response.answer = "Hiện không thể kiểm tra đơn hàng. Vui lòng thử lại sau."
            response.warnings = ["ORDER_LOOKUP_UNAVAILABLE"]
            return response

        status = result.get("status")
        if status == "NOT_FOUND":
            response.analysis_status = "INSUFFICIENT_DATA"
            response.answer = (
                f"Không tìm thấy đơn {order_id} trong phạm vi dữ liệu của shop hiện tại."
            )
            return response
        if status == "AMBIGUOUS":
            response.analysis_status = "INSUFFICIENT_DATA"
            response.answer = (
                f"Mã đơn {order_id} tồn tại trên nhiều nền tảng "
                f"({', '.join(result.get('platforms', []))}). Bạn muốn kiểm tra nền tảng nào?"
            )
            return response

        order = result["order"]
        items = order.get("items", [])
        item_text = "; ".join(
            f"{item.get('product_name', 'Sản phẩm')} × {item.get('quantity', 0)}"
            for item in items[:5]
        ) or "chưa có chi tiết sản phẩm"
        response.answer = (
            f"Đơn {order['order_id']} ({str(order['platform']).upper()}): "
            f"trạng thái {order['status']}; tổng tiền "
            f"{self._format_vnd(order.get('total_amount', 0))}; {item_text}."
        )
        return response

    def _answer_order_statistics(
        self, question: str, correlation_id: str | None
    ) -> AdvisorResponse:
        response = AdvisorResponse(intent=Intent.ORDER_STATISTICS.value)
        start_at, end_at = self._statistics_range(question)
        platform = self._extract_platform(question)
        folded = self._fold(question)
        # Cancellation questions use the aggregate cancelled_orders field. Do
        # not pre-filter to an English status because marketplaces localize it.
        status = None
        try:
            logger.info(
                "chat_tool_call tool=get_order_statistics request_id=%s",
                correlation_id or "unknown",
            )
            result = json.loads(
                str(
                    self._business_tools["get_order_statistics"].invoke(
                        {
                            "start_at": start_at.isoformat() if start_at else "",
                            "end_at": end_at.isoformat() if end_at else "",
                            "platform": platform or "",
                            "status": status or "",
                        }
                    )
                )
            )
        except Exception:
            logger.exception(
                "Order statistics tool failed request_id=%s", correlation_id or "unknown"
            )
            response.analysis_status = "ERROR"
            response.answer = "Hiện không thể truy xuất thống kê đơn hàng. Vui lòng thử lại sau."
            response.warnings = ["ORDER_STATISTICS_UNAVAILABLE"]
            return response

        if "ban chay" in folded and result.get("top_products"):
            top = result["top_products"][0]
            response.answer = (
                f"Sản phẩm bán chạy nhất là {top['product_name']} với "
                f"{top['units_sold']} sản phẩm, doanh thu {self._format_vnd(top['revenue'])}."
            )
        elif "nen tang nao" in folded and result.get("revenue_by_platform"):
            name, amount = max(result["revenue_by_platform"].items(), key=lambda item: item[1])
            response.answer = (
                f"{name.upper()} có doanh thu cao nhất: {self._format_vnd(amount)}."
            )
        elif "huy" in folded:
            response.answer = f"Có {result['cancelled_orders']} đơn bị hủy trong kỳ đã chọn."
        elif "doanh thu" in folded:
            response.answer = (
                f"Doanh thu trong kỳ là {self._format_vnd(result['revenue'])} từ "
                f"{result['total_orders']} đơn."
            )
        else:
            response.answer = (
                f"Có {result['total_orders']} đơn trong kỳ đã chọn; doanh thu "
                f"{self._format_vnd(result['revenue'])}."
            )
        return response

    @staticmethod
    def _extract_platform(question: str) -> str | None:
        folded = AdvisorService._fold(question)
        if "shopee" in folded:
            return "shopee"
        if "tiktok" in folded:
            return "tiktok_shop"
        if "lazada" in folded:
            return "lazada"
        return None

    @staticmethod
    def _fold(value: str) -> str:
        from utils.text import fold_text

        return fold_text(value)

    @staticmethod
    def _format_vnd(value: object) -> str:
        return f"{float(value or 0):,.0f}".replace(",", ".") + " VND"

    def _statistics_range(self, question: str) -> tuple[datetime | None, datetime | None]:
        folded = self._fold(question)
        zone = ZoneInfo(settings.BUSINESS_TIMEZONE)
        now = datetime.now(zone)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if "hom nay" in folded or "today" in folded:
            return day_start, day_start + timedelta(days=1)
        if "tuan nay" in folded or "this week" in folded:
            start = day_start - timedelta(days=day_start.weekday())
            return start, start + timedelta(days=7)
        if "thang nay" in folded or "this month" in folded:
            start = day_start.replace(day=1)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
            return start, end
        match = re.search(r"\b(7|30)\s*(?:ngay|days?|d)\b", folded)
        if match:
            return now - timedelta(days=int(match.group(1))), now
        return None, None

    def _invoke_decision_tool(
        self, intent: Intent, question: str, order_summary: Optional[dict]
    ) -> dict:
        assert self._decision_service is not None
        category = str((order_summary or {}).get("category") or (order_summary or {}).get("gender") or "nam")
        period = "30d" if re.search(r"30\s*(?:ngay|days?|d)", question, re.I) else "7d"
        sku = str((order_summary or {}).get("seller_sku") or (order_summary or {}).get("sku") or "")
        plan_period = "month" if period == "30d" else "week"
        routes = {
            Intent.BUSINESS_HEALTH: ("get_business_health", {}),
            Intent.PRODUCT_ANALYSIS: ("analyze_product", {"sku": sku}),
            Intent.FINANCIAL_ANALYSIS: ("analyze_revenue_leakage", {}),
            Intent.MARKET_TREND: ("get_market_trends", {"category": category, "period": period}),
            Intent.PRODUCT_OPPORTUNITY: ("find_product_opportunities", {"category": category, "period": period}),
            Intent.ACTION_PLAN: ("generate_action_plan", {"category": category, "period": period}),
            Intent.SALES_PLAN: ("generate_sales_plan", {"category": category, "period": plan_period, "objective": "conversion"}),
            Intent.MARKETING_PLAN: ("generate_communication_plan", {"category": category, "period": plan_period, "objective": "conversion"}),
        }
        selected = routes.get(intent)
        if not selected:
            return {"status": "INSUFFICIENT_DATA"}
        tool_name, arguments = selected
        return json.loads(str(self._business_tools[tool_name].invoke(arguments)))
