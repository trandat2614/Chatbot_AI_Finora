"""
FINORA AI Business Advisor — Main Streamlit Application Entry Point.

Run with: streamlit run app.py

Architecture:
- st.cache_resource is used for LLM client and vector store (created once per session).
- Session state is used for chat history and uploaded DataFrames.
- Raw DataFrames are never sent to the LLM.
- All financial calculations are done in Python tools.
"""
import logging

import streamlit as st

from utils.logger import setup_logging

# Setup logging before any other imports
setup_logging(level=logging.INFO)

from config.settings import settings
from ui.sidebar import render_sidebar
from ui.chat_page import render_chat_page
from ui.break_even_page import render_break_even_page
from ui.revenue_page import render_revenue_page
from ui.forecast_page import render_forecast_page

# ------------------------------------------------------------------ #
# Page configuration
# ------------------------------------------------------------------ #
st.set_page_config(
    page_title="Finora AI Business Advisor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": "Finora AI Business Advisor v1.0 — Powered by Google Gemini + LangChain",
    },
)


# ------------------------------------------------------------------ #
# Cached resources (created once per Streamlit session)
# ------------------------------------------------------------------ #

@st.cache_resource(show_spinner="Đang khởi tạo AI client...")
def get_llm_client():
    """Load LLM client once per Streamlit session."""
    from core.llm_client import LLMClient
    from core.exceptions import ConfigurationError

    try:
        return LLMClient()
    except ConfigurationError:
        return None
    except Exception as e:
        logging.getLogger(__name__).error("Failed to init LLM client: %s", e)
        return None


@st.cache_resource(show_spinner="Đang tải cơ sở kiến thức...")
def get_vector_store():
    """Load vector store once per Streamlit session.

    Returns None if the vector store has not been initialised yet
    (i.e. ingest.py has not been run).
    """
    from rag.vector_store import load_vector_store, vector_store_exists
    from core.exceptions import VectorStoreNotFoundError, ConfigurationError

    if not settings.is_api_key_configured():
        return None

    if not vector_store_exists():
        return None

    try:
        return load_vector_store()
    except (VectorStoreNotFoundError, ConfigurationError):
        return None
    except Exception as e:
        logging.getLogger(__name__).warning("Failed to load vector store: %s", e)
        return None


# ------------------------------------------------------------------ #
# Main application
# ------------------------------------------------------------------ #

def main() -> None:
    """Application entry point."""
    render_sidebar()

    # Load shared resources
    llm_client = get_llm_client()
    vector_store = get_vector_store()

    # API key check banner
    if not settings.is_api_key_configured():
        st.error(
            "⚠️ **GEMINI_API_KEY chưa được cấu hình.**\n\n"
            "1. Sao chép `.env.example` thành `.env`\n"
            "2. Điền `GEMINI_API_KEY` vào file `.env`\n"
            "3. Restart Streamlit\n\n"
            "Hoặc khi deploy Streamlit Cloud: thêm key vào **Secrets**."
        )

    # Vector store status banner
    if settings.is_api_key_configured() and vector_store is None:
        st.warning(
            "ℹ️ **Cơ sở kiến thức chưa được tải.**\n\n"
            "Chạy lệnh sau để nạp tài liệu:\n```\npython ingest.py\n```\n"
            "Sau đó restart Streamlit. Tính năng RAG sẽ hoạt động đầy đủ."
        )

    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 AI Business Advisor",
        "💰 Điểm Hòa Vốn",
        "📈 Phân Tích Doanh Thu",
        "🔮 Dự Báo & Marketing",
    ])

    with tab1:
        render_chat_page(llm_client=llm_client, vector_store=vector_store)

    with tab2:
        render_break_even_page(llm_client=llm_client, vector_store=vector_store)

    with tab3:
        render_revenue_page(llm_client=llm_client, vector_store=vector_store)

    with tab4:
        render_forecast_page(llm_client=llm_client, vector_store=vector_store)


if __name__ == "__main__":
    main()
