"""
Custom exceptions for FINORA AI Business Advisor.

Defines a hierarchy of application-specific exceptions so that callers
can handle different failure modes precisely without relying on built-in
or third-party exception types.
"""


class FinoraBaseError(Exception):
    """Base class for all FINORA application errors."""


# ------------------------------------------------------------------ #
# Configuration errors
# ------------------------------------------------------------------ #


class ConfigurationError(FinoraBaseError):
    """Raised when required configuration (e.g. API key) is missing or invalid."""


# ------------------------------------------------------------------ #
# Data validation errors
# ------------------------------------------------------------------ #


class DataValidationError(FinoraBaseError):
    """Raised when input data fails schema or business-rule validation."""


class MissingColumnsError(DataValidationError):
    """Raised when a required column is absent from the uploaded data."""

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(
            f"Dữ liệu thiếu các cột bắt buộc: {', '.join(missing)}"
        )


class InsufficientDataError(DataValidationError):
    """Raised when the dataset does not have enough rows for an operation."""

    def __init__(self, required: int, actual: int, operation: str = "") -> None:
        self.required = required
        self.actual = actual
        suffix = f" cho {operation}" if operation else ""
        super().__init__(
            f"Cần ít nhất {required} kỳ dữ liệu{suffix}, "
            f"hiện tại chỉ có {actual} kỳ."
        )


# ------------------------------------------------------------------ #
# Financial calculation errors
# ------------------------------------------------------------------ #


class FinancialCalculationError(FinoraBaseError):
    """Raised when a financial calculation cannot be completed."""


class DivisionByZeroError(FinancialCalculationError):
    """Raised when a calculation would result in division by zero."""

    def __init__(self, formula: str = "") -> None:
        msg = "Không thể thực hiện phép chia cho 0"
        if formula:
            msg += f" trong công thức: {formula}"
        super().__init__(msg)


class InvalidInputError(FinancialCalculationError):
    """Raised when a numeric input is outside allowed bounds."""


# ------------------------------------------------------------------ #
# RAG / LLM errors
# ------------------------------------------------------------------ #


class RAGError(FinoraBaseError):
    """Raised when the RAG retrieval pipeline fails."""


class VectorStoreNotFoundError(RAGError):
    """Raised when the vector store has not been initialised yet."""

    def __init__(self) -> None:
        super().__init__(
            "Vector store chưa được khởi tạo.\n"
            "Vui lòng chạy lệnh: python ingest.py"
        )


class LLMClientError(FinoraBaseError):
    """Raised when an OpenAI API call fails."""


class LLMTimeoutError(LLMClientError):
    """Raised when the OpenAI API call times out."""


class LLMAuthenticationError(LLMClientError):
    """Raised when the OpenAI API key is invalid or unauthorised."""


# ------------------------------------------------------------------ #
# Forecast errors
# ------------------------------------------------------------------ #


class ForecastError(FinoraBaseError):
    """Raised when the forecasting pipeline fails."""
