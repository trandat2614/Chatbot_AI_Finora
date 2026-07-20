"""
Break-even analysis tool for FINORA AI Business Advisor.

All calculations are performed by Python, NOT by the LLM, to ensure accuracy.
"""
from dataclasses import dataclass, field
from typing import Optional

from core.exceptions import InvalidInputError, DivisionByZeroError
from utils.validators import (
    validate_non_negative,
    validate_positive,
    validate_selling_price_above_variable_cost,
)


@dataclass
class BreakEvenInput:
    """Validated input for break-even analysis."""

    fixed_cost: float
    selling_price: float
    variable_cost_per_unit: float
    actual_revenue: Optional[float] = None
    actual_units_sold: Optional[float] = None


@dataclass
class BreakEvenResult:
    """Result of break-even analysis."""

    # Core metrics
    contribution_margin_per_unit: float = 0.0
    contribution_margin_ratio: float = 0.0
    break_even_quantity: float = 0.0
    break_even_revenue: float = 0.0

    # Optional — only when actual revenue provided
    margin_of_safety: Optional[float] = None
    margin_of_safety_percentage: Optional[float] = None

    # Status
    break_even_status: str = "unknown"
    interpretation: str = ""
    warnings: list[str] = field(default_factory=list)


class BreakEvenTool:
    """Calculates break-even metrics from business input data.

    Design principle: no division by zero, no LLM in the math path.
    """

    def calculate(self, inp: BreakEvenInput) -> BreakEvenResult:
        """Run the break-even calculation.

        Args:
            inp: Validated break-even input.

        Returns:
            BreakEvenResult with all computable metrics populated.

        Raises:
            InvalidInputError: On invalid numeric inputs.
            DivisionByZeroError: When contribution margin is zero.
        """
        # ---- Validate inputs ------------------------------------------------
        validate_non_negative(inp.fixed_cost, "Chi phí cố định")
        validate_positive(inp.selling_price, "Giá bán")
        validate_non_negative(inp.variable_cost_per_unit, "Chi phí biến đổi/đơn vị")
        validate_selling_price_above_variable_cost(
            inp.selling_price, inp.variable_cost_per_unit
        )

        result = BreakEvenResult()

        # ---- Core formulas --------------------------------------------------
        result.contribution_margin_per_unit = (
            inp.selling_price - inp.variable_cost_per_unit
        )

        if result.contribution_margin_per_unit == 0:
            raise DivisionByZeroError("Contribution Margin per Unit")

        result.contribution_margin_ratio = (
            result.contribution_margin_per_unit / inp.selling_price
        )

        result.break_even_quantity = (
            inp.fixed_cost / result.contribution_margin_per_unit
        )

        if result.contribution_margin_ratio == 0:
            raise DivisionByZeroError("Contribution Margin Ratio")

        result.break_even_revenue = (
            inp.fixed_cost / result.contribution_margin_ratio
        )

        # ---- Margin of Safety (optional) ------------------------------------
        if inp.actual_revenue is not None:
            validate_non_negative(inp.actual_revenue, "Doanh thu thực tế")
            result.margin_of_safety = inp.actual_revenue - result.break_even_revenue
            if inp.actual_revenue > 0:
                result.margin_of_safety_percentage = (
                    result.margin_of_safety / inp.actual_revenue * 100
                )
            else:
                result.margin_of_safety_percentage = 0.0
                result.warnings.append(
                    "Doanh thu thực tế bằng 0 — không thể tính % Margin of Safety."
                )

        # ---- Status and interpretation --------------------------------------
        result.break_even_status = self._determine_status(
            inp.actual_revenue, result.break_even_revenue
        )
        result.interpretation = self._build_interpretation(inp, result)

        return result

    # ------------------------------------------------------------------ #
    # Private helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _determine_status(
        actual_revenue: Optional[float],
        break_even_revenue: float,
    ) -> str:
        if actual_revenue is None:
            return "Chưa có doanh thu thực tế để đánh giá"
        if actual_revenue >= break_even_revenue:
            return "✅ Đã vượt điểm hòa vốn"
        return "⚠️ Chưa đạt điểm hòa vốn"

    @staticmethod
    def _build_interpretation(
        inp: BreakEvenInput,
        result: BreakEvenResult,
    ) -> str:
        lines = [
            f"• Mỗi đơn vị bán ra đóng góp {result.contribution_margin_per_unit:,.0f} ₫ "
            f"({result.contribution_margin_ratio*100:.1f}%) vào lợi nhuận sau chi phí biến đổi.",
            f"• Cần bán ít nhất {result.break_even_quantity:,.1f} đơn vị hoặc đạt "
            f"doanh thu {result.break_even_revenue:,.0f} ₫ để hoà vốn.",
        ]
        if result.margin_of_safety is not None:
            if result.margin_of_safety >= 0:
                lines.append(
                    f"• Biên an toàn hiện tại là {result.margin_of_safety:,.0f} ₫ "
                    f"({result.margin_of_safety_percentage:.1f}%) — "
                    "doanh thu có thể giảm thêm mức này trước khi thua lỗ."
                )
            else:
                lines.append(
                    f"• Doanh thu hiện tại thiếu {abs(result.margin_of_safety):,.0f} ₫ "
                    "để đạt điểm hòa vốn."
                )
        return "\n".join(lines)


def calculate_break_even(
    fixed_cost: float,
    selling_price: float,
    variable_cost_per_unit: float,
    actual_revenue: Optional[float] = None,
    actual_units_sold: Optional[float] = None,
) -> BreakEvenResult:
    """Convenience function wrapping BreakEvenTool.

    Args:
        fixed_cost: Total fixed costs per period.
        selling_price: Selling price per unit.
        variable_cost_per_unit: Variable cost per unit.
        actual_revenue: Actual revenue achieved (optional).
        actual_units_sold: Actual units sold (optional).

    Returns:
        BreakEvenResult.
    """
    tool = BreakEvenTool()
    inp = BreakEvenInput(
        fixed_cost=fixed_cost,
        selling_price=selling_price,
        variable_cost_per_unit=variable_cost_per_unit,
        actual_revenue=actual_revenue,
        actual_units_sold=actual_units_sold,
    )
    return tool.calculate(inp)
