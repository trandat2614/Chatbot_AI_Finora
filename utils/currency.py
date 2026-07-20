"""
Currency formatting utilities for FINORA AI Business Advisor.

Provides consistent VND and generic number formatting across the application.
"""


def format_vnd(amount: float, *, symbol: bool = True) -> str:
    """Format a number as Vietnamese Dong (VND).

    Args:
        amount: The monetary amount.
        symbol: If True (default), append the ₫ symbol.

    Returns:
        Formatted string, e.g. ``"1.234.567 ₫"``.
    """
    try:
        formatted = f"{amount:,.0f}".replace(",", ".")
        return f"{formatted} ₫" if symbol else formatted
    except (TypeError, ValueError):
        return "N/A"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format a number as a percentage string.

    Args:
        value: The percentage value (e.g. 12.5 → ``"12.50%"``).
        decimals: Number of decimal places.

    Returns:
        Formatted string.
    """
    try:
        return f"{value:.{decimals}f}%"
    except (TypeError, ValueError):
        return "N/A"


def format_number(value: float, decimals: int = 0) -> str:
    """Format a generic number with thousands separators.

    Args:
        value: The number to format.
        decimals: Number of decimal places.

    Returns:
        Formatted string.
    """
    try:
        return f"{value:,.{decimals}f}"
    except (TypeError, ValueError):
        return "N/A"


def parse_vnd(text: str) -> float:
    """Parse a VND-formatted string back to a float.

    Args:
        text: String such as ``"1.234.567 ₫"`` or ``"1234567"``.

    Returns:
        Numeric value.

    Raises:
        ValueError: If the string cannot be parsed.
    """
    cleaned = text.replace("₫", "").replace(".", "").replace(",", "").strip()
    return float(cleaned)
