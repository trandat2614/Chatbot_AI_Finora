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
from dataclasses import dataclass, field
from typing import Optional

from langchain_chroma import Chroma

from core.llm_client import LLMClient
from core.prompts import GENERAL_QA_PROMPT
from rag.rag_service import retrieve_context, format_retrieved_context, get_source_citations
from tools.business_rule_engine import BusinessSignals
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class AdvisorResponse:
    """Structured response from the advisor service."""

    answer: str = ""
    sources: list[dict] = field(default_factory=list)
    rag_context_used: bool = False
    business_signals_count: int = 0
    warnings: list[str] = field(default_factory=list)


class AdvisorService:
    """Main advisor service that orchestrates RAG + LLM."""

    def __init__(
        self,
        llm_client: LLMClient,
        vector_store: Optional[Chroma] = None,
    ) -> None:
        self._llm = llm_client
        self._vector_store = vector_store

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

        # ---- RAG retrieval -----------------------------------------------
        chunks = []
        if self._vector_store is not None:
            try:
                chunks = retrieve_context(
                    question, self._vector_store, settings.RETRIEVAL_TOP_K
                )
                response.sources = get_source_citations(chunks)
                response.rag_context_used = len(chunks) > 0
            except Exception as exc:
                logger.warning("RAG retrieval failed: %s", exc)
                warnings.append("Không thể trích xuất kiến thức nội bộ.")

        rag_context = format_retrieved_context(chunks, question)

        # ---- Signal context ----------------------------------------------
        signals_text = signals.as_text() if signals else "Chưa có dữ liệu để phân tích signals."
        if signals:
            response.business_signals_count = len(signals.signals)

        # ---- Build LLM message -------------------------------------------
        if order_summary is not None:
            summary_text = json.dumps(order_summary, ensure_ascii=False, indent=2)
            business_context = (
                f"{business_context}\n\n## Dữ liệu tổng hợp đơn hàng do client cung cấp\n"
                f"```json\n{summary_text}\n```\n"
                "Chỉ được dùng đúng các số liệu trên; không tự suy diễn số còn thiếu."
            )

        user_message = GENERAL_QA_PROMPT.format(
            user_question=question,
            business_context=business_context or "Chưa có dữ liệu kinh doanh được tải lên.",
            business_signals=signals_text,
            rag_context=rag_context,
        )

        # ---- LLM call ----------------------------------------------------
        try:
            response.answer = self._llm.generate_response(user_message, history=history)
        except Exception as exc:
            logger.error("LLM call failed: %s", exc)
            response.answer = "⚠️ Không thể kết nối với AI lúc này. Vui lòng thử lại sau."
            warnings.append("Dịch vụ Gemini tạm thời không khả dụng.")

        response.warnings = warnings
        return response
