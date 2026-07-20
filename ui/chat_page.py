"""
AI Business Advisor chat page for FINORA AI Business Advisor.
"""
from __future__ import annotations

import streamlit as st

from services.advisor_service import AdvisorService
from services.financial_service import FinancialService
from tools.business_rule_engine import evaluate_business_rules
from ui.components import display_sources

_financial_service = FinancialService()

EXAMPLE_QUESTIONS = [
    "Doanh thu t\u0103ng nh\u01b0ng l\u1ee3i nhu\u1eadn gi\u1ea3m c\u00f3 th\u1ec3 do đ\u00e2u?",
    "T\u00f4i n\u00ean theo d\u00f5i ch\u1ec9 s\u1ed1 n\u00e0o đ\u1ec3 đ\u00e1nh gi\u00e1 hi\u1ec7u qu\u1ea3 marketing?",
    "D\u1ef1a tr\u00ean d\u1eef li\u1ec7u hi\u1ec7n t\u1ea1i, chi\u1ebfn l\u01b0\u1ee3c marketing 3 th\u00e1ng t\u1edbi n\u00ean l\u00e0 g\u00ec?",
    "ROAS b\u1eb1ng bao nhi\u00eau l\u00e0 t\u1ed1t cho ng\u01b0\u1eddi b\u00e1n h\u00e0ng TMDT?",
    "L\u00e0m th\u1ebf n\u00e0o đ\u1ec3 t\u0103ng t\u1ef7 l\u1ec7 kh\u00e1ch h\u00e0ng quay l\u1ea1i?",
]


def render_chat_page(
    llm_client=None,
    vector_store=None,
) -> None:
    """Render the AI Business Advisor chat page."""
    st.header("\U0001f916 AI Business Advisor")
    st.caption(
        "H\u1ecfi b\u1ea5t k\u1ef3 c\u00e2u h\u1ecfi n\u00e0o v\u1ec1 kinh doanh, t\u00e0i ch\u00ednh, marketing. "
        "AI s\u1eed d\u1ee5ng d\u1eef li\u1ec7u c\u1ee7a b\u1ea1n (n\u1ebfu c\u00f3) v\u00e0 ki\u1ebfn th\u1ee9c n\u1ed9i b\u1ed9."
    )

    if llm_client is None:
        st.warning(
            "\u26a0\ufe0f Ch\u01b0a c\u1ea5u h\u00ecnh OpenAI API. "
            "Vui l\u00f2ng t\u1ea1o file `.env` v\u00e0 đi\u1ec1n `OPENAI_API_KEY`."
        )
        return

    # Init session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Example questions
    with st.expander("\U0001f4a1 C\u00e2u h\u1ecfi m\u1eabu", expanded=False):
        for q in EXAMPLE_QUESTIONS:
            if st.button(q, key=f"example_{q[:20]}"):
                st.session_state["prefill_question"] = q

    # Chat history display
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("\U0001f4da Ngu\u1ed3n t\u00e0i li\u1ec7u"):
                    display_sources(msg["sources"])
            if msg["role"] == "assistant" and msg.get("metrics_used"):
                with st.expander("\U0001f4ca D\u1eef li\u1ec7u đ\u01b0\u1ee3c s\u1eed d\u1ee5ng"):
                    st.text(msg["metrics_used"])

    # Clear history button
    if st.session_state.chat_history:
        if st.button("\U0001f5d1\ufe0f X\u00f3a l\u1ecbch s\u1eed chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

    # Chat input
    prefill = st.session_state.pop("prefill_question", "")
    user_input = st.chat_input(
        "Nh\u1eadp c\u00e2u h\u1ecfi c\u1ee7a b\u1ea1n...",
        key="chat_input",
    ) or prefill

    if user_input:
        _handle_chat(user_input, llm_client, vector_store)


def _handle_chat(question: str, llm_client, vector_store) -> None:
    """Process a chat message and display the response."""
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Get business context from session state
    business_context = ""
    signals = None
    df = st.session_state.get("revenue_df")
    if df is not None:
        try:
            revenue_m, profit_m, marketing_m, signals, _ = _financial_service.analyse(df)
            business_context = _financial_service.format_metrics_for_llm(
                revenue_m, profit_m, marketing_m
            )
        except Exception:
            pass

    # AI response
    with st.chat_message("assistant"):
        with st.spinner("AI đang suy ngh\u0129..."):
            advisor = AdvisorService(llm_client=llm_client, vector_store=vector_store)
            try:
                response = advisor.answer(
                    question=question,
                    business_context=business_context,
                    signals=signals,
                )
                st.markdown(response.answer)

                if response.sources:
                    with st.expander("\U0001f4da Ngu\u1ed3n t\u00e0i li\u1ec7u"):
                        display_sources(response.sources)

                if business_context:
                    with st.expander("\U0001f4ca D\u1eef li\u1ec7u đ\u01b0\u1ee3c s\u1eed d\u1ee5ng"):
                        st.text(business_context[:2000])

                # Store in history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response.answer,
                    "sources": response.sources,
                    "metrics_used": business_context[:500] if business_context else "",
                })

                if response.warnings:
                    for w in response.warnings:
                        st.warning(w)

            except Exception as exc:
                st.error(f"\U0001f6ab L\u1ed7i: {exc}")
