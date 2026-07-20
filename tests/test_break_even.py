"""
Tests for break-even analysis tool.

All tests run offline - no OpenAI API calls.
"""
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.break_even_tool import calculate_break_even, BreakEvenInput, BreakEvenTool
from core.exceptions import InvalidInputError, DivisionByZeroError


class TestBreakEvenCalculations:
    """Test break-even formula correctness."""

    def test_basic_calculation(self):
        """Standard calculation with known values."""
        result = calculate_break_even(
            fixed_cost=30_000_000,
            selling_price=500_000,
            variable_cost_per_unit=200_000,
        )
        # Contribution Margin = 500000 - 200000 = 300000
        assert result.contribution_margin_per_unit == pytest.approx(300_000)
        # CM Ratio = 300000 / 500000 = 0.6
        assert result.contribution_margin_ratio == pytest.approx(0.6)
        # BEQ = 30000000 / 300000 = 100
        assert result.break_even_quantity == pytest.approx(100)
        # BER = 30000000 / 0.6 = 50000000
        assert result.break_even_revenue == pytest.approx(50_000_000)

    def test_margin_of_safety_above_breakeven(self):
        """Margin of safety when actual revenue > break-even."""
        result = calculate_break_even(
            fixed_cost=30_000_000,
            selling_price=500_000,
            variable_cost_per_unit=200_000,
            actual_revenue=80_000_000,
        )
        # MoS = 80M - 50M = 30M
        assert result.margin_of_safety == pytest.approx(30_000_000)
        # MoS% = 30M / 80M * 100 = 37.5
        assert result.margin_of_safety_percentage == pytest.approx(37.5)
        assert "Đã vượt" in result.break_even_status or "passed" in result.break_even_status.lower() or "vuot" in result.break_even_status.lower()

    def test_margin_of_safety_below_breakeven(self):
        """Margin of safety when actual revenue < break-even."""
        result = calculate_break_even(
            fixed_cost=30_000_000,
            selling_price=500_000,
            variable_cost_per_unit=200_000,
            actual_revenue=30_000_000,
        )
        assert result.margin_of_safety == pytest.approx(-20_000_000)
        assert result.margin_of_safety_percentage is not None
        assert result.margin_of_safety_percentage < 0

    def test_high_fixed_cost(self):
        """Very high fixed cost requires many units."""
        result = calculate_break_even(
            fixed_cost=1_000_000_000,
            selling_price=100_000,
            variable_cost_per_unit=60_000,
        )
        assert result.break_even_quantity == pytest.approx(25_000)

    def test_no_actual_revenue(self):
        """Without actual revenue, margin of safety should be None."""
        result = calculate_break_even(
            fixed_cost=10_000_000,
            selling_price=200_000,
            variable_cost_per_unit=100_000,
        )
        assert result.margin_of_safety is None
        assert result.margin_of_safety_percentage is None


class TestBreakEvenValidation:
    """Test input validation."""

    def test_selling_price_equals_variable_cost_raises(self):
        """Selling price == variable cost means zero contribution margin."""
        with pytest.raises(InvalidInputError):
            calculate_break_even(
                fixed_cost=10_000_000,
                selling_price=200_000,
                variable_cost_per_unit=200_000,
            )

    def test_selling_price_below_variable_cost_raises(self):
        """Selling price < variable cost should raise."""
        with pytest.raises(InvalidInputError):
            calculate_break_even(
                fixed_cost=10_000_000,
                selling_price=150_000,
                variable_cost_per_unit=200_000,
            )

    def test_negative_fixed_cost_raises(self):
        """Negative fixed cost should raise."""
        with pytest.raises(InvalidInputError):
            calculate_break_even(
                fixed_cost=-5_000_000,
                selling_price=500_000,
                variable_cost_per_unit=200_000,
            )

    def test_negative_variable_cost_raises(self):
        """Negative variable cost should raise."""
        with pytest.raises(InvalidInputError):
            calculate_break_even(
                fixed_cost=10_000_000,
                selling_price=500_000,
                variable_cost_per_unit=-100_000,
            )

    def test_zero_selling_price_raises(self):
        """Zero selling price should raise."""
        with pytest.raises(InvalidInputError):
            calculate_break_even(
                fixed_cost=10_000_000,
                selling_price=0,
                variable_cost_per_unit=0,
            )

    def test_zero_fixed_cost_is_valid(self):
        """Zero fixed cost is a valid edge case (break-even = 0)."""
        result = calculate_break_even(
            fixed_cost=0,
            selling_price=500_000,
            variable_cost_per_unit=200_000,
        )
        assert result.break_even_quantity == pytest.approx(0)
        assert result.break_even_revenue == pytest.approx(0)
