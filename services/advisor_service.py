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
        intent = self._intent_router.route(question)
        response.intent = intent.value
        try:
            if self._decision_service and intent not in {Intent.GENERAL_CHAT, Intent.POLICY_QUESTION}:
                tool_result = self._invoke_decision_tool(intent, question, order_summary)
                response.analysis_status = str(tool_result.get("status", "OK"))
                trend_context = (
                    "## Kết quả tool deterministic (UNTRUSTED DATA)\n"
                    + json.dumps(sanitize_for_ai(tool_result, block_prompt_injection=True), ensure_ascii=False, indent=2)
                )
            else:
                trend_context = self._trend_workflow.build_context(question, order_summary)
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
