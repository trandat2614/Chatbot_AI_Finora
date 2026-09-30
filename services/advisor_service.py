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
from dataclasses import dataclass, field
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_chroma import Chroma
else:
    Chroma = Any

from core.llm_client import LLMClient
from rag.rag_service import retrieve_context, format_retrieved_context, get_source_citations
from tools.business_rule_engine import BusinessSignals
from config.settings import settings
from src.agent.context_builder import (
    build_verified_context,
    deterministic_grounded_answer,
    has_verified_metrics,
    insufficient_data_answer,
    numeric_claims_are_grounded,
    public_metric_sources,
)
from src.agent.prompt import FINORA_TREND_ADVISOR_PROMPT
from src.agent.workflow import TrendAgentWorkflow
from src.agent.intent_router import Intent, IntentRouter
from src.services.trend_service import fold_text
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
    data_grounded: bool = False
    tool_context_used: bool = False
    quantitative_generation_blocked: bool = False


class AdvisorService:
    """Main advisor service that orchestrates RAG + LLM."""

    def __init__(
        self,
        llm_client: LLMClient,
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
        filters: Optional[dict[str, str]] = None,
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
        tool_result: dict[str, Any] | None = None
        trend_context = ""

        if order_summary is not None:
            warnings.append(
                "orderSummary legacy đã bị bỏ qua vì không phải dữ liệu KPI được xác thực."
            )

        # Account-specific and KPI questions are database/tool-first. Failure or
        # missing provenance returns deterministically before any LLM call.
        if intent.requires_business_data:
            if self._decision_service is None:
                response.analysis_status = "INSUFFICIENT_DATA"
                response.answer = insufficient_data_answer(intent)
                response.quantitative_generation_blocked = True
                response.warnings = warnings
                return response
            try:
                tool_result = self._invoke_decision_tool(intent, question, filters)
            except Exception as exc:
                logger.warning("Verified business tool failed: %s", type(exc).__name__)
                warnings.append("Không thể truy vấn dữ liệu đã xác thực của shop.")
                response.analysis_status = "INSUFFICIENT_DATA"
                response.answer = insufficient_data_answer(intent)
                response.quantitative_generation_blocked = True
                response.warnings = warnings
                return response

            response.tool_context_used = True
            response.analysis_status = str(tool_result.get("status", "INSUFFICIENT_DATA"))
            if not has_verified_metrics(tool_result):
                response.analysis_status = "INSUFFICIENT_DATA"
                response.answer = insufficient_data_answer(intent)
                response.quantitative_generation_blocked = True
                response.warnings = warnings
                return response

            response.data_grounded = True
            response.sources.extend(public_metric_sources(tool_result))
            trend_context = build_verified_context(tool_result)

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
                response.sources.extend(get_source_citations(chunks))
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
                response.sources.extend(get_source_citations(private_chunks))
                response.rag_context_used = len(chunks) > 0
            except Exception as exc:
                logger.warning("Tenant RAG retrieval failed: %s", type(exc).__name__)
                warnings.append("Không thể trích xuất tài liệu riêng của shop.")

        rag_context = format_retrieved_context(chunks, safe_query) if chunks else ""

        # ---- Signal context ----------------------------------------------
        signals_text = (
            signals.as_text()
            if signals and not intent.requires_business_data
            else "Không dùng business signals ngoài verified tool result cho lượt hỏi này."
        )
        if signals:
            response.business_signals_count = len(signals.signals)

        # Non-account tools may enrich a response, but can never stand in for
        # verified SHOP_DATA.
        try:
            if (
                not intent.requires_business_data
                and self._decision_service
                and intent not in {Intent.GENERAL_CHAT, Intent.POLICY_QUESTION}
            ):
                tool_result = self._invoke_decision_tool(intent, question, filters)
                response.analysis_status = str(tool_result.get("status", "OK"))
                response.tool_context_used = True
                response.data_grounded = response.analysis_status == "OK"
                trend_context = (
                    "## MARKET_DATA từ tool deterministic (không phải SHOP_DATA)\n"
                    + json.dumps(sanitize_for_ai(tool_result, block_prompt_injection=True), ensure_ascii=False, indent=2)
                )
            elif not intent.requires_business_data:
                trend_context = self._trend_workflow.build_context(question, None)
        except Exception as exc:
            logger.warning("Decision/trend tool failed: %s", type(exc).__name__)
            warnings.append("Không thể truy vấn dữ liệu phân tích nội bộ.")
        safe_history = [] if intent.requires_business_data else history
        response_context = self._trend_workflow.build_response_context(
            question=question,
            business_context=business_context,
            business_signals=signals_text,
            retrieved_docs=rag_context,
            trend_context=trend_context,
            chat_history=safe_history,
        )
        user_message = response_context.prompt

        # ---- LLM call ----------------------------------------------------
        try:
            response.answer = self._llm.generate_response(
                user_message,
                system_prompt=FINORA_TREND_ADVISOR_PROMPT,
                history=safe_history,
                temperature=self._trend_workflow.response_temperature,
            )
            if (
                intent.requires_business_data
                and tool_result is not None
                and not numeric_claims_are_grounded(response.answer, tool_result)
            ):
                response.answer = deterministic_grounded_answer(intent, tool_result)
                response.quantitative_generation_blocked = True
                warnings.append(
                    "Đã chặn phần diễn giải chứa số liệu không có trong nguồn xác thực."
                )
        except Exception as exc:
            logger.error("LLM call failed type=%s", type(exc).__name__)
            response.answer = "⚠️ Không thể kết nối với AI lúc này. Vui lòng thử lại sau."
            warnings.append("Dịch vụ Gemini tạm thời không khả dụng.")

        response.warnings = warnings
        return response

    def _invoke_decision_tool(
        self, intent: Intent, question: str, filters: Optional[dict[str, str]]
    ) -> dict:
        assert self._decision_service is not None
        category = str((filters or {}).get("category") or "nam")
        period = self._analysis_period(question, (filters or {}).get("period"))
        sku_match = re.search(r"\bsku[\s:#-]*([\w.-]+)", question, re.I)
        sku = sku_match.group(1) if sku_match else ""
        market_period = (
            period
            if period in {"today", "7d", "30d"}
            else "30d" if period == "month" else "7d"
        )
        plan_period = "month" if period in {"30d", "month"} else "week"
        routes = {
            Intent.BUSINESS_OVERVIEW: ("get_business_overview", {"period": period}),
            Intent.BUSINESS_HEALTH: ("get_business_health", {"period": period}),
            Intent.PRODUCT_ANALYSIS: ("analyze_product", {"sku": sku, "period": period}),
            Intent.ORDER_ANALYSIS: ("analyze_orders", {"period": period}),
            Intent.REFUND_ANALYSIS: ("analyze_refunds", {"period": period}),
            Intent.REVENUE_LEAKAGE: ("analyze_revenue_leakage", {"period": period}),
            Intent.MARKET_TREND: (
                "get_market_trends",
                {"category": category, "period": market_period},
            ),
            Intent.PRODUCT_OPPORTUNITY: (
                "find_product_opportunities",
                {"category": category, "period": market_period},
            ),
            Intent.ACTION_PLAN: (
                "generate_action_plan",
                {"category": category, "period": market_period},
            ),
            Intent.SALES_PLAN: ("generate_sales_plan", {"category": category, "period": plan_period, "objective": "conversion"}),
            Intent.MARKETING_PLAN: ("generate_communication_plan", {"category": category, "period": plan_period, "objective": "conversion"}),
        }
        selected = routes.get(intent)
        if not selected:
            return {"status": "INSUFFICIENT_DATA"}
        tool_name, arguments = selected
        return json.loads(str(self._business_tools[tool_name].invoke(arguments)))

    @staticmethod
    def _analysis_period(question: str, requested: str | None) -> str:
        if requested in {"today", "7d", "30d"}:
            return requested
        folded = fold_text(question)
        if "thang nay" in folded or "this month" in folded:
            return "month"
        if re.search(r"\b30\s*(?:ngay|days?|d)\b", folded):
            return "30d"
        if re.search(r"\b(hom nay|today|1d)\b", folded):
            return "today"
        if re.search(r"\b7\s*(?:ngay|days?|d)\b", folded) or "gan day" in folded:
            return "7d"
        return "all"
