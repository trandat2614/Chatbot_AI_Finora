"""
Streamlit sidebar for FINORA AI Business Advisor.
"""
import streamlit as st
from config.settings import settings


def render_sidebar() -> None:
    """Render the application sidebar with description and status."""
    with st.sidebar:
        import os
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)

        st.markdown(
            """
            # 📊 Finora AI
            ### Business Advisor
            """
        )
        st.markdown(
            """
            **Tr\u1ee3 l\u00fd ph\u00e2n t\u00edch kinh doanh AI** cho ng\u01b0\u1eddi b\u00e1n h\u00e0ng \u0111a k\u00eanh.
            """
        )

        st.divider()

        st.markdown("### T\u00ednh n\u0103ng")
        features = [
            "\U0001f916 H\u1ecfi \u0111\u00e1p kinh doanh (RAG + AI)",
            "\U0001f4b0 Ph\u00e2n t\u00edch đi\u1ec3m h\u00f2a v\u1ed1n",
            "\U0001f4c8 Ph\u00e2n t\u00edch doanh thu",
            "\U0001f52e D\u1ef1 b\u00e1o & chi\u1ebfn l\u01b0\u1ee3c marketing",
        ]
        for f in features:
            st.markdown(f"- {f}")

        st.divider()

        # API Key status
        st.markdown("### Tr\u1ea1ng th\u00e1i h\u1ec7 th\u1ed1ng")
        if settings.is_api_key_configured():
            st.success("\u2705 Gemini API: K\u1ebft n\u1ed1i")
        else:
            st.error("\u274c Gemini API: Ch\u01b0a c\u00e0i đ\u1eb7t")
            st.caption("T\u1ea1o file .env v\u00e0 đi\u1ec1n GEMINI_API_KEY")

        st.divider()

        st.markdown("### Nguy\u00ean t\u1eafc AI")
        st.caption(
            "\u2022 Ch\u1ec9 ph\u00e2n t\u00edch d\u1eef li\u1ec7u đ\u01b0\u1ee3c cung c\u1ea5p\n"
            "\u2022 Kh\u00f4ng t\u1ef1 t\u1ea1o s\u1ed1 li\u1ec7u\n"
            "\u2022 C\u00e1c ph\u00e9p t\u00ednh do Python th\u1ef1c hi\u1ec7n\n"
            "\u2022 D\u1ef1 b\u00e1o kh\u00f4ng ch\u1eafc ch\u1eafn 100%\n"
            "\u2022 Kh\u00f4ng thay th\u1ebf chuy\u00ean gia t\u00e0i ch\u00ednh"
        )

        st.divider()
        st.caption("Finora AI v1.0 | Powered by Google Gemini + LangChain")
