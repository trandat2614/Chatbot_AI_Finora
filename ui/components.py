"""
Reusable Streamlit UI components for FINORA AI Business Advisor.
"""
import streamlit as st
from utils.currency import format_vnd, format_percentage


def metric_card(
    label: str,
    value: str,
    delta: str | None = None,
    help_text: str | None = None,
) -> None:
    """Render a styled metric card."""
    st.metric(label=label, value=value, delta=delta, help=help_text)


def section_header(title: str, description: str = "") -> None:
    """Render a section header with optional description."""
    st.markdown(f"### {title}")
    if description:
        st.caption(description)


def warning_box(message: str) -> None:
    """Render a warning message."""
    st.warning(f"\u26a0\ufe0f {message}")


def error_box(message: str) -> None:
    """Render an error message."""
    st.error(f"\U0001f6ab {message}")


def success_box(message: str) -> None:
    """Render a success message."""
    st.success(f"\u2705 {message}")


def info_box(message: str) -> None:
    """Render an info message."""
    st.info(f"\u2139\ufe0f {message}")


def display_signals(signals) -> None:
    """Display business signals as Streamlit alerts."""
    if not signals or not signals.signals:
        st.info("\u2705 Kh\u00f4ng c\u00f3 t\u00edn hi\u1ec7u b\u1ea5t th\u01b0\u1eddng n\u00e0o đ\u01b0\u1ee3c ph\u00e1t hi\u1ec7n.")
        return

    critical = signals.by_severity("critical")
    warnings = signals.by_severity("warning")
    infos = signals.by_severity("info")

    for sig in critical:
        st.error(
            f"\U0001f6a8 **{sig.title}**\n\n"
            f"{sig.description}\n\n"
            f"*B\u1eb1ng ch\u1ee9ng:* {sig.evidence}\n\n"
            f"*H\u00e0nh \u0111\u1ed9ng:* {sig.recommended_action}"
        )

    for sig in warnings:
        st.warning(
            f"\u26a0\ufe0f **{sig.title}**\n\n"
            f"{sig.description}\n\n"
            f"*B\u1eb1ng ch\u1ee9ng:* {sig.evidence}\n\n"
            f"*H\u00e0nh \u0111\u1ed9ng:* {sig.recommended_action}"
        )

    for sig in infos:
        st.info(
            f"\u2139\ufe0f **{sig.title}**\n\n"
            f"{sig.description}\n\n"
            f"*H\u00e0nh \u0111\u1ed9ng:* {sig.recommended_action}"
        )


def display_sources(sources: list[dict]) -> None:
    """Display RAG source citations."""
    if not sources:
        return
    st.markdown("**Ngu\u1ed3n t\u00e0i li\u1ec7u s\u1eed d\u1ee5ng:**")
    for s in sources:
        score_str = f" (score: {s['score']:.3f})" if s.get("score") else ""
        st.markdown(f"- \U0001f4c4 `{s['filename']}`{score_str}")
