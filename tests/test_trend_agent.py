"""Offline tests for the Shopee trend loader, tools, and chatbot integration."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

from services.advisor_service import AdvisorService
from src.agent.intent_router import Intent, IntentRouter
from src.agent.prompt import ADAPTIVE_RESPONSE_INSTRUCTION
from src.agent.workflow import RESPONSE_TEMPERATURE, TREND_TOOL_REGISTRY, TrendAgentWorkflow
from src.services.trend_service import TrendDataLoader
from src.tools.trend_tools import compare_shop_product_with_trends


DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "trends"


def test_loader_parses_all_sample_csvs_and_builds_database(tmp_path: Path) -> None:
    database_path = tmp_path / "trends.sqlite3"
    loader = TrendDataLoader(DATA_DIR, database_path)

    assert len(loader.loaded_files) >= 5
    assert len(loader.data) >= 500
    assert set(loader.data["gender"]) == {"nam", "nu"}
    assert set(loader.data["timeframe"]) == {"today", "7d", "30d"}
    assert pd.api.types.is_integer_dtype(loader.data["Giá"])
    assert pd.api.types.is_integer_dtype(loader.data["Lượt bán tăng"])
    assert pd.api.types.is_integer_dtype(loader.data["Đã bán 30 ngày"])
    assert pd.api.types.is_float_dtype(loader.data["Hoa hồng %"])
    assert pd.api.types.is_bool_dtype(loader.data["Shop Mall"])

    with sqlite3.connect(database_path) as connection:
        database_count = connection.execute("SELECT COUNT(*) FROM trends").fetchone()[0]
    assert database_count == len(loader.data)


def test_loader_replaces_same_capture_after_source_file_is_renamed(tmp_path: Path) -> None:
    old_path = tmp_path / "shopee-xu-huong 29-09 ttnu.csv"
    new_path = tmp_path / "shopee-xu-huong 29-09 thoi trang nu.csv"
    database_path = tmp_path / "trends.sqlite3"
    pd.DataFrame([{"Sản phẩm": "Áo nữ"}]).to_csv(
        old_path, index=False, encoding="utf-8-sig"
    )

    loader = TrendDataLoader(tmp_path, database_path)
    old_path.rename(new_path)
    loader.load()

    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            "SELECT source_file FROM trends ORDER BY source_row"
        ).fetchall()
    assert rows == [(new_path.name,)]


def test_short_fashion_category_routes_to_matching_market_data() -> None:
    class _TrendDecisionService:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str]] = []

        def get_market_trends(self, category: str, period: str) -> dict:
            self.calls.append((category, period))
            return {
                "status": "OK",
                "source": "public_marketplace_snapshot",
                "category": category,
                "period": period,
                "items": [{"rank": 1, "product_name": "Áo nữ", "price": 100_000}],
            }

    service = _TrendDecisionService()
    advisor = AdvisorService(llm_client=_EchoLLM(), decision_service=service)
    response = advisor.answer("Thời trang nữ")

    assert IntentRouter().route("Thời trang nữ") == Intent.MARKET_TRENDS
    assert response.intent == Intent.MARKET_TRENDS.value
    assert response.analysis_status == "OK"
    assert response.tool_context_used
    assert service.calls == [("nu", "7d")]


def test_compare_product_tool_returns_financial_gap_analysis() -> None:
    payload = json.loads(
        compare_shop_product_with_trends.invoke(
            {
                "product_name": "Áo thun form rộng 100% cotton",
                "current_price": 120_000,
                "cogs": 60_000,
                "affiliate_rate": 5,
                "category": "nam",
            }
        )
    )

    assert payload["market_benchmark"]["median_price"] > 0
    assert payload["gap_analysis"]["price_gap"] is not None
    assert len(payload["profit_margin_check"]["current_price_scenarios"]) == 2
    assert payload["similar_products"]


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


def test_agent_response_contains_metrics_extracted_from_csv() -> None:
    workflow = TrendAgentWorkflow()
    context = workflow.build_context("Xu hướng áo nam Shopee 7 ngày là gì?")
    trend_payload = json.loads(context.split("\n", 1)[1])
    expected_median = trend_payload["metrics"]["median_price"]

    llm = _EchoLLM()
    advisor = AdvisorService(llm_client=llm)
    response = advisor.answer("Xu hướng áo nam Shopee 7 ngày là gì?")

    assert str(expected_median) in response.answer
    assert "average_affiliate_rate" in response.answer
    assert "Cố vấn Tài chính & Kinh doanh E-commerce" in llm.last_system_prompt
    assert llm.last_temperature == RESPONSE_TEMPERATURE
    assert set(TREND_TOOL_REGISTRY) == {
        "get_shopee_fashion_trends",
        "compare_shop_product_with_trends",
    }


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
