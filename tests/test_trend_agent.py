"""Offline tests for request-scoped trend JSON and adaptive chat context."""
from __future__ import annotations

import json

from services.advisor_service import AdvisorService
from src.agent.prompt import ADAPTIVE_RESPONSE_INSTRUCTION
from src.agent.workflow import RESPONSE_TEMPERATURE, TREND_TOOL_REGISTRY, TrendAgentWorkflow
from tests.test_product_trends import export


class _EchoLLM:
    def __init__(self) -> None:
        self.last_message = ""
        self.last_system_prompt = ""
        self.last_temperature = None

    def generate_response(
        self,
        user_message: str,
        system_prompt: str | None = None,
        history=None,
        temperature: float | None = None,
    ) -> str:
        self.last_message = user_message
        self.last_system_prompt = system_prompt or ""
        self.last_temperature = temperature
        return user_message


def test_agent_uses_only_backend_json_given_for_current_turn() -> None:
    workflow = TrendAgentWorkflow()
    context = workflow.build_context("Xu hướng hôm nay", trend_data=export())
    assert "backend_reported_snapshot" in context
    assert '"medianPrice": 250000' in context
    assert TREND_TOOL_REGISTRY == {}
    llm = _EchoLLM()
    response = AdvisorService(llm_client=llm).answer("Xu hướng hôm nay", trend_data=export())
    assert "250000" in response.answer
    assert llm.last_temperature == RESPONSE_TEMPERATURE


def test_agent_missing_backend_json_reports_no_local_fallback() -> None:
    context = TrendAgentWorkflow().build_context("Xu hướng hôm nay")
    assert "INSUFFICIENT_DATA" in context
    assert "trend_data" in context


def test_adaptive_context_combines_rag_history_and_response_mode() -> None:
    workflow = TrendAgentWorkflow()
    context = workflow.build_response_context(
        question="Phân tích sâu cách tối ưu giá và nội dung bán áo boxy",
        business_context="Giá shop: 120000",
        business_signals="Biên lợi nhuận hiện tại: 18%",
        retrieved_docs="Tài liệu nội bộ: ưu tiên thử A/B title.",
        trend_context="Giá trung vị thị trường: 139430",
        chat_history=[{"role": "user", "content": "Shop của tôi bán áo nam."}],
    )

    assert context.response_mode == "deep"
    assert context.has_grounding_data
    assert "Tài liệu nội bộ: ưu tiên thử A/B title." in context.prompt
    assert "Giá trung vị thị trường: 139430" in context.prompt
    assert "Shop của tôi bán áo nam." in context.prompt


def test_short_non_trend_question_still_uses_adaptive_prompt() -> None:
    llm = _EchoLLM()
    advisor = AdvisorService(llm_client=llm)

    response = advisor.answer("Mẹo đóng gói áo chống nhăn?")

    assert "Chế độ phản hồi đã định tuyến: concise" in response.answer
    assert "không có số liệu grounding" in response.answer.lower()
    assert "không từ chối" in ADAPTIVE_RESPONSE_INSTRUCTION.lower()
    assert llm.last_temperature == 0.6
