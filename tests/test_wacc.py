"""
Test WACC calculation
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cost_of_capital.wacc import (
    calculate_wacc,
    get_capital_structure_from_balance_sheet,
    calculate_wacc_sensitivity
)


def test_calculate_wacc_equal_weights():
    """Test WACC with equal equity/debt weights"""
    result = calculate_wacc(0.5, 0.5, 0.10, 0.05, 0.25)
    expected = 0.5 * 0.10 + 0.5 * 0.05 * 0.75
    assert abs(result - expected) < 0.0001


def test_calculate_wacc_zero_weights():
    """Test WACC with zero weights"""
    result = calculate_wacc(0, 0, 0.10, 0.05, 0.25)
    assert result == 0.0


def test_calculate_wacc_normalizes_weights():
    """Test that weights are normalized"""
    result = calculate_wacc(2, 1, 0.10, 0.05, 0.25)
    expected = (2/3) * 0.10 + (1/3) * 0.05 * 0.75
    assert abs(result - expected) < 0.0001


def test_calculate_wacc_100_percent_equity():
    """Test WACC with 100% equity"""
    result = calculate_wacc(1.0, 0, 0.10, 0.05, 0.25)
    assert result == 0.10


def test_calculate_wacc_100_percent_debt():
    """Test WACC with 100% debt"""
    result = calculate_wacc(0, 1.0, 0.10, 0.05, 0.25)
    expected = 0.05 * 0.75
    assert abs(result - expected) < 0.0001


def test_capital_structure_from_balance_sheet():
    """Test capital structure calculation"""
    result = get_capital_structure_from_balance_sheet(100, 50)
    assert result['equity_weight'] == pytest.approx(2/3, rel=0.01)
    assert result['debt_weight'] == pytest.approx(1/3, rel=0.01)
    assert result['debt_to_equity'] == 0.5


def test_capital_structure_zero():
    """Test capital structure with zero values"""
    result = get_capital_structure_from_balance_sheet(0, 0)
    assert result['equity_weight'] == 0
    assert result['debt_weight'] == 0


def test_wacc_sensitivity_generation():
    """Test sensitivity analysis generation"""
    result = calculate_wacc_sensitivity(
        0.10,
        {'cost_of_equity': (0.08, 0.12), 'debt_weight': (0.2, 0.4)},
        steps=5
    )
    assert 'cost_of_equity' in result
    assert 'debt_weight' in result
    assert len(result['cost_of_equity']) == 5
    assert len(result['debt_weight']) == 5
