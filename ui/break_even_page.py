"""
Break-even analysis page for FINORA AI Business Advisor.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from tools.break_even_tool import calculate_break_even, BreakEvenResult
from core.exceptions import InvalidInputError, DivisionByZeroError
from utils.currency import format_vnd, format_percentage


def render_break_even_page(
    llm_client=None,
    vector_store=None,
) -> None:
    """Render the break-even analysis page."""
    st.header("\U0001f4b0 Ph\u00e2n t\u00edch Đi\u1ec3m H\u00f2a V\u1ed1n")
    st.caption(
        "T\u00ednh to\u00e1n ch\u00ednh x\u00e1c b\u1eb1ng Python. AI ch\u1ec9 gi\u1ea3i th\u00edch k\u1ebft qu\u1ea3."
    )

    with st.form("break_even_form"):
        st.subheader("Nh\u1eadp d\u1eef li\u1ec7u")
        col1, col2 = st.columns(2)

        with col1:
            fixed_cost = st.number_input(
                "Chi ph\u00ed c\u1ed1 đ\u1ecbnh (\u20ab/th\u00e1ng)",
                min_value=0.0,
                value=50_000_000.0,
                step=1_000_000.0,
                format="%.0f",
                help="L\u01b0\u01a1ng, thu\u00ea m\u1eb7t b\u1eb1ng, kh\u1ea5u hao...",
                key="be_fixed_cost",
            )
            selling_price = st.number_input(
                "Gi\u00e1 b\u00e1n/\u0111\u01a1n v\u1ecb (\u20ab)",
                min_value=0.0,
                value=500_000.0,
                step=10_000.0,
                format="%.0f",
                key="be_selling_price",
            )
            variable_cost = st.number_input(
                "Chi ph\u00ed bi\u1ebfn đ\u1ed5i/\u0111\u01a1n v\u1ecb (\u20ab)",
                min_value=0.0,
                value=200_000.0,
                step=10_000.0,
                format="%.0f",
                help="Gi\u00e1 v\u1ed1n, phong b\u00ec, ph\u00ed ship...",
                key="be_variable_cost",
            )

        with col2:
            actual_revenue = st.number_input(
                "Doanh thu th\u1ef1c t\u1ebf (\u20ab, n\u1ebfu c\u00f3)",
                min_value=0.0,
                value=0.0,
                step=1_000_000.0,
                format="%.0f",
                help="\u0110\u1ec3 tr\u1ed1ng n\u1ebfu ch\u01b0a c\u00f3 d\u1eef li\u1ec7u",
                key="be_actual_revenue",
            )
            actual_units = st.number_input(
                "S\u1ed1 đ\u01a1n v\u1ecb đ\u00e3 b\u00e1n (n\u1ebfu c\u00f3)",
                min_value=0.0,
                value=0.0,
                step=1.0,
                format="%.0f",
                key="be_actual_units",
            )

        submitted = st.form_submit_button(
            "\U0001f4ca T\u00ednh to\u00e1n",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        _run_break_even(
            fixed_cost=fixed_cost,
            selling_price=selling_price,
            variable_cost=variable_cost,
            actual_revenue=actual_revenue if actual_revenue > 0 else None,
            actual_units=actual_units if actual_units > 0 else None,
            llm_client=llm_client,
            vector_store=vector_store,
        )


def _run_break_even(
    fixed_cost, selling_price, variable_cost,
    actual_revenue, actual_units, llm_client, vector_store
) -> None:
    """Run break-even calculation and display results."""
    try:
        result = calculate_break_even(
            fixed_cost=fixed_cost,
            selling_price=selling_price,
            variable_cost_per_unit=variable_cost,
            actual_revenue=actual_revenue,
            actual_units_sold=actual_units,
        )
    except (InvalidInputError, DivisionByZeroError) as exc:
        st.error(f"\U0001f6ab L\u1ed7i đ\u1ea7u v\u00e0o: {exc}")
        return
    except Exception as exc:
        st.error(f"\U0001f6ab L\u1ed7i kh\u00f4ng x\u00e1c đ\u1ecbnh: {exc}")
        return

    # Display results
    st.subheader("\U0001f4ca K\u1ebft qu\u1ea3 T\u00ednh to\u00e1n")
    st.markdown(f"**Tr\u1ea1ng th\u00e1i: {result.break_even_status}**")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "S\u1ed1 \u0111\u01a1n v\u1ecb h\u00f2a v\u1ed1n",
            f"{result.break_even_quantity:,.1f} đv",
        )
        st.metric(
            "Contribution Margin/\u0111v",
            format_vnd(result.contribution_margin_per_unit),
        )
    with col2:
        st.metric(
            "Doanh thu h\u00f2a v\u1ed1n",
            format_vnd(result.break_even_revenue),
        )
        st.metric(
            "Contribution Margin Ratio",
            format_percentage(result.contribution_margin_ratio * 100),
        )
    with col3:
        if result.margin_of_safety is not None:
            st.metric(
                "Bi\u00ean an to\u00e0n",
                format_vnd(result.margin_of_safety),
                delta=format_percentage(result.margin_of_safety_percentage or 0),
            )

    st.markdown("#### Di\u1ec5n gi\u1ea3i")
    st.markdown(result.interpretation)

    if result.warnings:
        for w in result.warnings:
            st.warning(w)

    # Chart
    _render_break_even_chart(result, fixed_cost, selling_price, variable_cost, actual_revenue)

    # AI analysis
    if llm_client:
        _render_ai_analysis(result, fixed_cost, selling_price, variable_cost, actual_revenue, llm_client, vector_store)


def _render_break_even_chart(result, fixed_cost, selling_price, variable_cost, actual_revenue):
    """Render break-even chart."""
    import numpy as np
    max_units = max(int(result.break_even_quantity * 2), 100)
    units = list(range(0, max_units + 1, max(1, max_units // 50)))

    data = {
        "S\u1ed1 đ\u01a1n v\u1ecb": units,
        "T\u1ed5ng doanh thu": [u * selling_price for u in units],
        "T\u1ed5ng chi ph\u00ed": [fixed_cost + u * variable_cost for u in units],
    }
    df_chart = pd.DataFrame(data).set_index("S\u1ed1 đ\u01a1n v\u1ecb")
    st.subheader("\U0001f4c8 Bi\u1ec3u đ\u1ed3 H\u00f2a V\u1ed1n")
    st.line_chart(df_chart)


def _render_ai_analysis(result, fixed_cost, selling_price, variable_cost, actual_revenue, llm_client, vector_store):
    """Request AI analysis of break-even results."""
    from rag.rag_service import answer_with_rag
    from core.prompts import BREAK_EVEN_ANALYSIS_PROMPT

    with st.expander("\U0001f916 Ph\u00e2n t\u00edch t\u1eeb AI", expanded=True):
        with st.spinner("AI đang ph\u00e2n t\u00edch..."):
            calc_text = f"""
- Chi ph\u00ed c\u1ed1 đ\u1ecbnh: {format_vnd(fixed_cost)}
- Gi\u00e1 b\u00e1n: {format_vnd(selling_price)}
- Chi ph\u00ed bi\u1ebfn đ\u1ed5i: {format_vnd(variable_cost)}
- Contribution Margin/\u0111v: {format_vnd(result.contribution_margin_per_unit)}
- Contribution Margin Ratio: {format_percentage(result.contribution_margin_ratio*100)}
- S\u1ed1 đ\u01a1n v\u1ecb h\u00f2a v\u1ed1n: {result.break_even_quantity:,.1f}
- Doanh thu h\u00f2a v\u1ed1n: {format_vnd(result.break_even_revenue)}
- Tr\u1ea1ng th\u00e1i: {result.break_even_status}
"""
            try:
                chunks, rag_ctx = answer_with_rag("ph\u00e2n t\u00edch đi\u1ec3m h\u00f2a v\u1ed1n contribution margin", vector_store)
                prompt = BREAK_EVEN_ANALYSIS_PROMPT.format(
                    calculation_results=calc_text,
                    business_signals="Kh\u00f4ng c\u00f3 business signals trong ph\u00e2n t\u00edch n\u00e0y.",
                    rag_context=rag_ctx,
                )
                answer = llm_client.generate_response(prompt)
                st.markdown(answer)
                if chunks:
                    with st.expander("\U0001f4da Ngu\u1ed3n t\u00e0i li\u1ec7u"):
                        for c in chunks:
                            st.caption(f"\U0001f4c4 {c.filename}")
            except Exception as exc:
                st.warning(f"Kh\u00f4ng th\u1ec3 l\u1ea5y ph\u00e2n t\u00edch AI: {exc}")
