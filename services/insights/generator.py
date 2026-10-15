"""LLM-backed insight wording with strict validation and safe fallback."""
from __future__ import annotations

import json
import logging
import re
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from services.insights.prompts import INSIGHTS_SYSTEM_PROMPT, INSIGHTS_USER_TEMPLATE
from services.insights.rules import InsightCandidate, Severity

logger = logging.getLogger(__name__)


class InsightLLM(Protocol):
    def generate_response(
        self,
        user_message: str,
        system_prompt: str | None = None,
        history: list[dict[str, str]] | None = None,
        temperature: float | None = None,
    ) -> str: ...


class GeneratedText(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    title: str = Field(min_length=1, max_length=60)
    summary: str = Field(min_length=1, max_length=500)
    recommendation: str = Field(min_length=1, max_length=500)


class GeneratedPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[GeneratedText] = Field(max_length=5)


class GeneratedInsight(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    severity: Severity
    title: str = Field(min_length=1, max_length=60)
    summary: str = Field(min_length=1, max_length=500)
    recommendation: str = Field(min_length=1, max_length=500)
    evidence: dict[str, float | int | str | None]


def _json_payload(raw: str) -> GeneratedPayload:
    text = raw.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1)
    return GeneratedPayload.model_validate_json(text)


def _number(evidence: dict, key: str, suffix: str = "") -> str:
    value = evidence.get(key)
    if isinstance(value, float):
        return f"{value:,.2f}{suffix}"
    return f"{value}{suffix}"


def _fallback(candidate: InsightCandidate) -> GeneratedInsight:
    evidence = candidate.evidence
    kind = candidate.type
    templates: dict[str, tuple[str, str, str]] = {
        "low_data": (
            "Chưa đủ dữ liệu để kết luận",
            f"Kỳ này mới có {_number(evidence, 'order_count')} đơn, dưới ngưỡng {_number(evidence, 'minimum_order_count')} đơn.",
            "Tiếp tục ghi nhận đơn hàng trước khi điều chỉnh chiến lược kinh doanh.",
        ),
        "revenue_growth": (
            "Doanh thu đang tăng",
            f"Doanh thu tăng {_number(evidence, 'change_pct', '%')} so với kỳ trước.",
            "Xác định kênh và sản phẩm đóng góp chính để duy trì đà tăng.",
        ),
        "revenue_decline": (
            "Doanh thu đang giảm",
            f"Doanh thu giảm {abs(float(evidence.get('change_pct') or 0)):,.2f}% so với kỳ trước.",
            "Kiểm tra kênh và sản phẩm giảm mạnh nhất rồi ưu tiên một biện pháp phục hồi.",
        ),
        "order_growth": (
            "Số đơn đang tăng",
            f"Số đơn tăng {_number(evidence, 'change_pct', '%')} so với kỳ trước.",
            "Duy trì nguồn đơn hiện tại và theo dõi khả năng xử lý đơn của shop.",
        ),
        "order_decline": (
            "Số đơn đang giảm",
            f"Số đơn giảm {abs(float(evidence.get('change_pct') or 0)):,.2f}% so với kỳ trước.",
            "Rà soát phễu bán hàng ở kênh giảm mạnh nhất trong kỳ.",
        ),
        "channel_concentration": (
            "Doanh thu phụ thuộc một kênh",
            f"Kênh {evidence.get('channel')} đóng góp {_number(evidence, 'share_pct', '%')} doanh thu.",
            "Thử một chiến dịch nhỏ trên kênh khác để giảm rủi ro phụ thuộc.",
        ),
        "weak_channel": (
            "Một kênh bán đang suy yếu",
            f"Kênh {evidence.get('channel')} giảm {abs(float(evidence.get('change_pct') or 0)):,.2f}% so với kỳ trước.",
            "Kiểm tra sản phẩm, giá và nguồn truy cập của kênh này trước khi tăng ngân sách.",
        ),
        "low_profit_margin": (
            "Biên lợi nhuận cần chú ý",
            f"Biên lợi nhuận kỳ này là {_number(evidence, 'profit_margin_pct', '%')}.",
            "Rà soát khoản phí lớn nhất và chọn một khoản để tối ưu trong kỳ tới.",
        ),
        "high_profit_margin": (
            "Biên lợi nhuận tích cực",
            f"Biên lợi nhuận kỳ này đạt {_number(evidence, 'profit_margin_pct', '%')}.",
            "Ghi nhận tổ hợp sản phẩm và kênh đang tạo biên tốt để ưu tiên nguồn lực.",
        ),
        "costs_outpace_revenue": (
            "Chi phí tăng nhanh hơn doanh thu",
            f"Tốc độ tăng chi phí cao hơn doanh thu {_number(evidence, 'growth_gap_pct', '%')}.",
            "Phân loại các khoản phí tăng và cắt giảm khoản không tạo thêm doanh thu.",
        ),
        "product_concentration": (
            "Doanh thu phụ thuộc sản phẩm chủ lực",
            f"Sản phẩm {evidence.get('product')} chiếm {_number(evidence, 'share_pct', '%')} doanh thu.",
            "Chuẩn bị một sản phẩm thay thế hoặc bán kèm để phân tán rủi ro.",
        ),
        "low_selling_product": (
            "Sản phẩm có tỷ trọng thấp",
            f"Sản phẩm {evidence.get('product')} chỉ chiếm {_number(evidence, 'share_pct', '%')} doanh thu.",
            "Đánh giá lại nội dung bán, giá hoặc quyết định ngừng ưu tiên sản phẩm này.",
        ),
        "slow_break_even": (
            "Tiến độ hòa vốn còn chậm",
            f"Shop đạt {_number(evidence, 'progress_pct', '%')} mục tiêu hòa vốn và còn {_number(evidence, 'remaining_amount')}.",
            "Đặt mục tiêu lợi nhuận kỳ tới dựa trên số đơn cần thêm trong evidence.",
        ),
    }
    title, summary, recommendation = templates.get(
        kind,
        (
            "Tín hiệu kinh doanh cần xem xét",
            "Dữ liệu kỳ này cho thấy một thay đổi đáng chú ý.",
            "Đối chiếu evidence và chọn một hành động đo lường được cho kỳ tới.",
        ),
    )
    return GeneratedInsight(
        type=kind,
        severity=candidate.severity,
        title=title,
        summary=summary,
        recommendation=recommendation,
        evidence=evidence,
    )


class InsightGenerator:
    def __init__(self, llm_client: InsightLLM | None) -> None:
        self.llm_client = llm_client

    def generate(self, candidates: list[InsightCandidate]) -> list[GeneratedInsight]:
        selected = candidates[:5]
        if not selected:
            return []
        if self.llm_client is None:
            return [_fallback(item) for item in selected]

        user_prompt = INSIGHTS_USER_TEMPLATE.format(
            candidates_json=json.dumps(
                [item.model_dump(mode="json") for item in selected],
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )
        payload: GeneratedPayload | None = None
        for attempt in range(2):
            try:
                raw = self.llm_client.generate_response(
                    user_message=user_prompt,
                    system_prompt=INSIGHTS_SYSTEM_PROMPT,
                    temperature=0.2,
                )
                payload = _json_payload(raw)
                break
            except Exception as exc:
                # The broad catch is deliberate: provider timeouts/errors must
                # never make the deterministic insights API unavailable.
                logger.warning(
                    "insight_llm_generation_failed attempt=%s error=%s",
                    attempt + 1,
                    type(exc).__name__,
                )
        if payload is None:
            return [_fallback(item) for item in selected]

        by_type = {item.type: item for item in selected}
        generated: list[GeneratedInsight] = []
        seen: set[str] = set()
        for text in payload.items:
            candidate = by_type.get(text.type)
            if candidate is None or text.type in seen:
                continue
            seen.add(text.type)
            generated.append(
                GeneratedInsight(
                    type=text.type,
                    severity=candidate.severity,
                    title=text.title,
                    summary=text.summary,
                    recommendation=text.recommendation,
                    evidence=candidate.evidence,
                )
            )
        # A partial model response is completed deterministically.
        generated.extend(_fallback(item) for item in selected if item.type not in seen)
        return generated[:5]
