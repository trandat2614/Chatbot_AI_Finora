"""
Input validators for FINORA AI Business Advisor.

Business-domain validators that operate on primitive Python types.
DataFrame-level validation is handled in the analysis tools themselves.
"""
from typing import Optional

from core.exceptions import InvalidInputError


def validate_positive(value: float, field_name: str) -> float:
    """Ensure a numeric value is strictly positive (> 0).

    Args:
        value: The value to check.
        field_name: Human-readable field name for error messages.

    Returns:
        The validated value.

    Raises:
        InvalidInputError: If the value is not positive.
    """
    if value <= 0:
        raise InvalidInputError(
            f"'{field_name}' phải lớn hơn 0. Giá trị nhận được: {value}"
        )
    return value


def validate_non_negative(value: float, field_name: str) -> float:
    """Ensure a numeric value is non-negative (≥ 0).

    Args:
        value: The value to check.
        field_name: Human-readable field name for error messages.

    Returns:
        The validated value.

    Raises:
        InvalidInputError: If the value is negative.
    """
    if value < 0:
        raise InvalidInputError(
            f"'{field_name}' không được âm. Giá trị nhận được: {value}"
        )
    return value


def validate_selling_price_above_variable_cost(
    selling_price: float,
    variable_cost: float,
) -> None:
    """Ensure the selling price exceeds the variable cost per unit.

    Args:
        selling_price: Unit selling price.
        variable_cost: Variable cost per unit.

    Raises:
        InvalidInputError: If selling_price ≤ variable_cost.
    """
    if selling_price <= variable_cost:
        raise InvalidInputError(
            f"Giá bán ({selling_price:,.0f}) phải lớn hơn chi phí biến đổi "
            f"({variable_cost:,.0f}). "
            "Kiểm tra lại: nếu giá bán thấp hơn chi phí biến đổi, "
            "mỗi đơn vị bán ra sẽ lỗ."
        )


def validate_periods(periods: int, min_periods: int = 1, max_periods: int = 12) -> int:
    """Validate that a forecast period count is within allowed bounds.

    Args:
        periods: Number of forecast periods requested.
        min_periods: Minimum allowed value (default 1).
        max_periods: Maximum allowed value (default 12).

    Returns:
        The validated periods value.

    Raises:
        InvalidInputError: If out of range.
    """
    if not (min_periods <= periods <= max_periods):
        raise InvalidInputError(
            f"Số kỳ dự báo phải từ {min_periods} đến {max_periods}. "
            f"Giá trị nhận được: {periods}"
        )
    return periods


def validate_csv_columns(
    df_columns: list[str],
    required: list[str],
) -> list[str]:
    """Check that all required columns are present in the DataFrame.

    Args:
        df_columns: List of column names from the uploaded CSV.
        required: Column names that must be present.

    Returns:
        List of missing column names (empty list = all present).
    """
    df_col_lower = [c.strip().lower() for c in df_columns]
    return [col for col in required if col.lower() not in df_col_lower]


def safe_float(value: object, default: Optional[float] = None) -> Optional[float]:
    """Safely convert a value to float.

    Args:
        value: The value to convert.
        default: Value to return on failure (default None).

    Returns:
        Converted float or the default value.
    """
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
