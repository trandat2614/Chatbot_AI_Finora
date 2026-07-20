"""
LLM client for FINORA AI Business Advisor.

Wraps the OpenAI Responses API with:
- Timeout handling
- API error handling
- No logging of sensitive data
- Dependency injection via constructor
"""
import logging
from typing import Optional

from openai import OpenAI, APIError, AuthenticationError, APITimeoutError

from config.settings import settings
from core.exceptions import (
    LLMClientError,
    LLMAuthenticationError,
    LLMTimeoutError,
    ConfigurationError,
)
from core.prompts import FINORA_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class LLMClient:
    """Thin wrapper around the OpenAI client.

    Uses the Responses API (``client.responses.create``).  Falls back to
    ``client.chat.completions.create`` when the Responses API endpoint is
    unavailable (older SDK versions).

    Args:
        api_key: OpenAI API key.  Defaults to ``settings.OPENAI_API_KEY``.
        model: Model identifier.  Defaults to ``settings.OPENAI_MODEL``.
        timeout: Request timeout in seconds.  Defaults to ``settings.LLM_TIMEOUT``.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self._api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.timeout = timeout or settings.LLM_TIMEOUT
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS

        if not self._api_key or self._api_key == "your_gemini_api_key":
            raise ConfigurationError(
                "GEMINI_API_KEY chưa được cấu hình. "
                "Vui lòng tạo file .env và điền API key."
            )

        # Never log the key — only log a masked version
        masked = f"{self._api_key[:6]}...{self._api_key[-4:]}" if len(self._api_key) > 10 else "***"
        logger.info("LLMClient initialised. model=%s key=%s", self.model, masked)

        self._client = OpenAI(
            api_key=self._api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            timeout=self.timeout
        )

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _call_api(self, system_prompt: str, user_message: str) -> str:
        """Send a single request to the OpenAI API and return the text.

        Tries the Responses API first; falls back to Chat Completions.

        Args:
            system_prompt: System role instruction.
            user_message: User turn message.

        Returns:
            Model response text.

        Raises:
            LLMAuthenticationError: On 401 / invalid key.
            LLMTimeoutError: On request timeout.
            LLMClientError: On any other API error.
        """
        try:
            # Google Generative AI's OpenAI compatibility endpoint only supports Chat Completions
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content or ""

        except AuthenticationError as exc:
            logger.error("OpenAI authentication failed.")
            raise LLMAuthenticationError(
                "API key không hợp lệ hoặc đã hết hạn. "
                "Vui lòng kiểm tra lại OPENAI_API_KEY."
            ) from exc
        except APITimeoutError as exc:
            logger.error("OpenAI API timeout after %ss.", self.timeout)
            raise LLMTimeoutError(
                f"Yêu cầu tới OpenAI API đã timeout sau {self.timeout} giây. "
                "Vui lòng thử lại."
            ) from exc
        except APIError as exc:
            logger.error("OpenAI API error: %s", exc)
            raise LLMClientError(
                f"Lỗi từ OpenAI API: {exc}"
            ) from exc

    # ------------------------------------------------------------------ #
    # Public interface
    # ------------------------------------------------------------------ #

    def generate_response(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate a free-form response.

        Args:
            user_message: The user's question or instruction.
            system_prompt: Override the default system prompt.

        Returns:
            Model response as a string.
        """
        prompt = system_prompt or FINORA_SYSTEM_PROMPT
        logger.debug("generate_response called. model=%s", self.model)
        return self._call_api(prompt, user_message)

    def generate_business_analysis(
        self,
        analysis_prompt: str,
        context: str,
    ) -> str:
        """Generate a structured business analysis.

        Args:
            analysis_prompt: Specialised prompt template (from core.prompts).
            context: Pre-formatted context string (metrics + signals + RAG).

        Returns:
            Model response as a string.
        """
        logger.debug("generate_business_analysis called.")
        full_message = f"{analysis_prompt}\n\n---\n\n{context}"
        return self._call_api(FINORA_SYSTEM_PROMPT, full_message)

    def generate_marketing_recommendations(
        self,
        marketing_context: str,
        user_question: str = "",
    ) -> str:
        """Generate marketing strategy recommendations.

        Args:
            marketing_context: Pre-formatted context (metrics + signals + RAG).
            user_question: Optional specific question from the user.

        Returns:
            Model response as a string.
        """
        logger.debug("generate_marketing_recommendations called.")
        message = marketing_context
        if user_question:
            message += f"\n\n## Câu hỏi cụ thể\n{user_question}"
        return self._call_api(FINORA_SYSTEM_PROMPT, message)
