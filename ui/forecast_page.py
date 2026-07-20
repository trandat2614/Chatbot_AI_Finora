"""
Forecast and Marketing Strategy page for FINORA AI Business Advisor.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from services.forecast_service import ForecastService
from services.financial_service import FinancialService
from services.advisor_service import AdvisorService
from ui.components import display_signals
from utils.currency import format_vnd
from core.exceptions import InsufficientDataError

_forecast_service = ForecastService()
_financial_service = FinancialService()


def render_forecast_page(
    llm_client=None,
    vector_store=None,
) -> None:
    """Render the forecast and marketing strategy page."""
    st.header("📈 Dự Báo Doanh Thu & Chiến Lược Marketing")
    st.caption(
        "Mô hình Machine Learning (Linear Regression) dự báo doanh thu. "
        "AI đề xuất chiến lược marketing dựa trên xu hướng dữ liệu."
    )

    # Check for uploaded data
    df = st.session_state.get("revenue_df")
    if df is None:
        # Allow upload directly on this page
        uploaded_file = st.file_uploader(
            "Tải lên file CSV (hoặc vào trang Phân Tích Doanh Thu trước)",
            type=["csv"],
            key="forecast_csv_upload",
        )
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state["revenue_df"] = df
            except Exception as exc:
                st.error(f"🚫 Không đọc được file CSV: {exc}")
                return
        else:
            st.info(
                "📂 Vui lòng tải lên file CSV hoặc đến trang "
                "**Phân Tích Doanh Thu** để tải dữ liệu trước."
            )
            return

    # Forecast settings
    st.subheader("⚙️ Cấu hình dự báo")
    periods = st.slider(
        "Số kỳ dự báo (tháng)",
        min_value=1,
        max_value=12,
        value=3,
        key="forecast_periods",
    )

    if st.button("🔮 Chạy Dự Báo", type="primary", key="run_forecast"):
        _run_forecast(df, periods, llm_client, vector_store)


def _run_forecast(df, periods, llm_client, vector_store) -> None:
    """Execute forecast and display results."""
    with st.spinner("Đang chạy mô hình dự báo..."):
        forecast_result, eval_result, warnings = _forecast_service.run_forecast(df, periods)

    # Warnings
    if warnings:
        for w in warnings:
            st.warning(w)

    if forecast_result is None:
        st.error("🚫 Không thể thực hiện dự báo. Kiểm tra dữ liệu và cảnh báo phía trên.")
        return

    # Display forecast results
    st.subheader("📊 Kết Quả Dự Báo")

    # Combined chart: historical + forecast
    _render_forecast_chart(forecast_result)

    # Forecast table
    st.subheader("📋 Chi Tiết Dự Báo")
    forecast_df = pd.DataFrame({
        "Kỳ Dự Báo": forecast_result.forecast_dates,
        "Doanh Thu Dự Kiến (₫)": [f"{v:,.0f}" for v in forecast_result.predicted_revenue],
    })
    st.dataframe(forecast_df, use_container_width=True)

    # Trend info
    trend_direction = "📈 tăng" if forecast_result.trend_per_period > 0 else "📉 giảm"
    st.info(
        f"**Xu hướng:** {trend_direction} ~{abs(forecast_result.trend_per_period):,.0f} ₫/kỳ "
        f"| Mô hình: {forecast_result.model_name} "
        f"| Dữ liệu huấn luyện: {forecast_result.training_rows} kỳ"
    )

    # Model performance
    if eval_result:
        st.subheader("📐 Hiệu Suất Mô Hình")
        if eval_result.can_evaluate:
            ecol1, ecol2, ecol3 = st.columns(3)
            with ecol1:
                st.metric("MAE", format_vnd(eval_result.mae or 0))
            with ecol2:
                st.metric("RMSE", format_vnd(eval_result.rmse or 0))
            with ecol3:
                if eval_result.mape is not None:
                    st.metric("MAPE", f"{eval_result.mape:.1f}%")
                else:
                    st.metric("MAPE", "N/A")
        else:
            st.caption(eval_result.warning or "Chưa đủ dữ liệu để đánh giá mô hình.")

    # Confidence warnings
    st.warning(forecast_result.confidence_warning)
    st.caption(f"⚠️ Giới hạn mô hình: {forecast_result.model_limitations}")

    # Business signals
    try:
        revenue_m, profit_m, marketing_m, signals, _ = _financial_service.analyse(df)
        st.subheader("🚨 Business Signals")
        display_signals(signals)
    except Exception:
        signals = None

    # AI marketing strategy
    if llm_client:
        st.subheader("💡 Chiến Lược Marketing AI")
        _render_ai_marketing_strategy(
            forecast_result, eval_result, signals,
            llm_client, vector_store
        )


def _render_forecast_chart(forecast_result) -> None:
    """Render combined historical + forecast chart."""
    import pandas as pd

    historical_df = pd.DataFrame({
        "date": pd.to_datetime(forecast_result.historical_dates),
        "revenue": forecast_result.historical_revenue,
        "type": "Lịch sử",
    })

    forecast_df = pd.DataFrame({
        "date": pd.to_datetime(forecast_result.forecast_dates),
        "revenue": forecast_result.predicted_revenue,
        "type": "Dự báo",
    })

    # Combine for chart
    combined = pd.concat([
        historical_df.set_index("date")[["revenue"]].rename(columns={"revenue": "Doanh thu lịch sử"}),
        forecast_df.set_index("date")[["revenue"]].rename(columns={"revenue": "Dự báo"}),
    ])

    st.subheader("📈 Biểu Đồ Doanh Thu & Dự Báo")
    st.line_chart(combined)


def _render_ai_marketing_strategy(
    forecast_result, eval_result, signals,
    llm_client, vector_store
) -> None:
    """Generate AI marketing strategy based on forecast and signals."""
    from rag.rag_service import answer_with_rag
    from core.prompts import FORECAST_ANALYSIS_PROMPT

    forecast_text, perf_text = _forecast_service.format_forecast_for_llm(
        forecast_result, eval_result
    )
    signals_text = signals.as_text() if signals else "Chưa có business signals."

    with st.spinner("AI đang phân tích và đề xuất chiến lược..."):
        try:
            chunks, rag_ctx = answer_with_rag(
                "chiến lược marketing doanh thu dự báo",
                vector_store
            )

            prompt = FORECAST_ANALYSIS_PROMPT.format(
                forecast_results=forecast_text,
                model_performance=perf_text or "Chưa có dữ liệu đánh giá mô hình.",
                business_signals=signals_text,
                rag_context=rag_ctx,
            )

            answer = llm_client.generate_response(prompt)
            st.markdown(answer)

            if chunks:
                with st.expander("📚 Nguồn tài liệu"):
                    for c in chunks:
                        st.caption(f"📄 {c.filename}")
        except Exception as exc:
            st.warning(f"Không thể lấy phân tích AI: {exc}")
