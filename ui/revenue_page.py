"""
Revenue analysis page for FINORA AI Business Advisor.
"""
from __future__ import annotations

import io
import streamlit as st
import pandas as pd

from services.financial_service import FinancialService
from ui.components import display_signals
from utils.currency import format_vnd, format_percentage
from core.exceptions import DataValidationError

_service = FinancialService()


def render_revenue_page(
    llm_client=None,
    vector_store=None,
) -> None:
    """Render the revenue analysis page."""
    st.header("\U0001f4c8 Ph\u00e2n T\u00edch Doanh Thu")
    st.caption(
        "T\u1ea3i l\u00ean file CSV ch\u1ee9a d\u1eef li\u1ec7u kinh doanh đ\u1ec3 b\u1eaft đ\u1ea7u ph\u00e2n t\u00edch."
    )

    uploaded_file = st.file_uploader(
        "T\u1ea3i l\u00ean file CSV",
        type=["csv"],
        help="Xem README đ\u1ec3 bi\u1ebft format CSV c\u1ea7n thi\u1ebft.",
        key="revenue_csv_upload",
    )

    if uploaded_file is not None:
        _process_csv(uploaded_file, llm_client, vector_store)
    else:
        st.info(
            "\U0001f4c2 Vui l\u00f2ng t\u1ea3i l\u00ean file CSV. "
            "B\u1ea1n c\u00f3 th\u1ec3 d\u00f9ng file m\u1eabu t\u1ea1i `data/sample_revenue.csv`."
        )


def _process_csv(uploaded_file, llm_client, vector_store) -> None:
    """Process uploaded CSV and display analysis."""
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as exc:
        st.error(f"\U0001f6ab Kh\u00f4ng đ\u1ecdc đ\u01b0\u1ee3c file CSV: {exc}")
        return

    # Store in session state
    st.session_state["revenue_df"] = df

    # Preview
    with st.expander("\U0001f4cb Xem tr\u01b0\u1edbc d\u1eef li\u1ec7u", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"T\u1ed5ng: {len(df)} d\u00f2ng | {len(df.columns)} c\u1ed9t")

    # Run analysis
    try:
        revenue_m, profit_m, marketing_m, signals, warnings = _service.analyse(df)
    except DataValidationError as exc:
        st.error(f"\U0001f6ab L\u1ed7i d\u1eef li\u1ec7u: {exc}")
        return
    except Exception as exc:
        st.error(f"\U0001f6ab L\u1ed7i ph\u00e2n t\u00edch: {exc}")
        return

    # Warnings
    if warnings:
        with st.expander("\u26a0\ufe0f C\u1ea3nh b\u00e1o d\u1eef li\u1ec7u", expanded=False):
            for w in warnings:
                st.warning(w)

    # Revenue metrics
    if revenue_m:
        st.subheader("\U0001f4ca T\u1ed5ng Quan Doanh Thu")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("T\u1ed5ng Doanh Thu", format_vnd(revenue_m.total_revenue))
        with col2:
            st.metric(
                "Doanh Thu G\u1ea7n Nh\u1ea5t",
                format_vnd(revenue_m.latest_revenue),
                delta=f"{revenue_m.revenue_growth_rate:.1f}%" if revenue_m.revenue_growth_rate is not None else None,
            )
        with col3:
            if revenue_m.average_order_value:
                st.metric("AOV", format_vnd(revenue_m.average_order_value))
        with col4:
            if revenue_m.customer_acquisition_cost:
                st.metric("CAC", format_vnd(revenue_m.customer_acquisition_cost))

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("K\u1ef3 T\u1ed1t Nh\u1ea5t", revenue_m.best_period)
        with col_b:
            st.metric("K\u1ef3 X\u1ea5u Nh\u1ea5t", revenue_m.worst_period)

        if revenue_m.revenue_trend:
            st.info(revenue_m.revenue_trend)

        # Revenue chart
        _render_revenue_chart(df)

        # Channel analysis
        if revenue_m.revenue_by_channel:
            st.subheader("\U0001f4e6 Doanh Thu Theo K\u00eanh")
            ch_df = pd.DataFrame.from_dict(
                revenue_m.revenue_by_channel, orient="index", columns=["Revenue"]
            )
            st.bar_chart(ch_df)

        # Product analysis
        if revenue_m.revenue_by_product:
            st.subheader("\U0001f6cd\ufe0f Doanh Thu Theo S\u1ea3n Ph\u1ea9m")
            pr_df = pd.DataFrame.from_dict(
                revenue_m.revenue_by_product, orient="index", columns=["Revenue"]
            ).sort_values("Revenue", ascending=False).head(10)
            st.bar_chart(pr_df)

    # Profit metrics
    if profit_m:
        st.subheader("\U0001f4b0 L\u1ee3i Nhu\u1eadn")
        pcol1, pcol2 = st.columns(2)
        with pcol1:
            if profit_m.total_gross_profit is not None:
                st.metric(
                    "Gross Profit",
                    format_vnd(profit_m.total_gross_profit),
                    delta=f"Margin: {profit_m.gross_profit_margin:.1f}%" if profit_m.gross_profit_margin else None,
                )
        with pcol2:
            if profit_m.total_net_profit is not None:
                st.metric(
                    "Net Profit",
                    format_vnd(profit_m.total_net_profit),
                    delta=f"Margin: {profit_m.net_profit_margin:.1f}%" if profit_m.net_profit_margin else None,
                )
        if profit_m.not_computable:
            st.caption(f"Ch\u01b0a t\u00ednh đ\u01b0\u1ee3c: {'; '.join(profit_m.not_computable)}")

    # Business signals
    st.subheader("\U0001f6a8 Business Signals")
    display_signals(signals)


def _render_revenue_chart(df: pd.DataFrame) -> None:
    """Render revenue over time chart."""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    if "date" in df.columns and "revenue" in df.columns:
        try:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
            chart_df = df.set_index("date")[["revenue"]]
            st.subheader("\U0001f4c8 Bi\u1ec3u đ\u1ed3 Doanh Thu")
            st.line_chart(chart_df)
        except Exception:
            pass
