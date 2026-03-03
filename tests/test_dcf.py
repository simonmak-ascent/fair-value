"""
Test DCF valuation
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.valuation.dcf import (
    project_free_cash_flows,
    calculate_terminal_value_gordon,
    calculate_terminal_value_exit,
    discount_cash_flows,
    discount_single_value,
    dcf_valuation
)


def test_project_free_cash_flows():
    """Test FCF projection"""
    result = project_free_cash_flows(
        revenue=100,
        growth_rate=0.05,
        ebitda_margin=0.20,
        capex_pct=0.05,
        depreciation_pct=0.03,
        nwc_pct=0.02,
        tax_rate=0.25,
        years=5
    )
    
    assert len(result) == 5
    assert result['year'].iloc[0] == 1
    assert result['revenue'].iloc[0] == 105  # 100 * 1.05


def test_terminal_value_gordon():
    """Test Gordon growth terminal value"""
    tv = calculate_terminal_value_gordon(100, 0.10, 0.025)
    expected = 100 * 1.025 / (0.10 - 0.025)
    assert abs(tv - expected) < 0.01


def test_terminal_value_gordon_invalid():
    """Test Gordon growth with WACC <= growth"""
    tv = calculate_terminal_value_gordon(100, 0.02, 0.025)
    assert tv == 0.0


def test_terminal_value_exit():
    """Test exit multiple terminal value"""
    tv = calculate_terminal_value_exit(100, 10)
    assert tv == 1000


def test_discount_cash_flows():
    """Test discounting cash flows"""
    cash_flows = [100, 110, 121]
    pv = discount_cash_flows(cash_flows, 0.10)
    expected = 100/1.1 + 110/1.1**2 + 121/1.1**3
    assert abs(pv - expected) < 0.01


def test_discount_single_value():
    """Test discounting single future value"""
    pv = discount_single_value(100, 0.10, 1)
    assert abs(pv - 90.91) < 0.01


def test_dcf_valuation():
    """Test full DCF valuation"""
    result = dcf_valuation(
        ticker="TEST",
        revenue=1000,
        growth_rate=0.05,
        ebitda_margin=0.20,
        capex_pct=0.05,
        depreciation_pct=0.03,
        nwc_pct=0.02,
        tax_rate=0.25,
        wacc=0.10,
        terminal_growth=0.025,
        shares_outstanding=100,
        net_debt=50,
        years=5
    )
    
    assert result['ticker'] == 'TEST'
    assert result['method'] == 'DCF'
    assert 'enterprise_value' in result
    assert 'equity_value' in result
    assert 'value_per_share' in result
    assert result['value_per_share'] > 0


def test_dcf_valuation_atm():
    """Test DCF with ATM option (spot = strike)"""
    # This is essentially testing with no debt
    result = dcf_valuation(
        ticker="TEST",
        revenue=100,
        growth_rate=0.02,
        ebitda_margin=0.15,
        capex_pct=0.03,
        depreciation_pct=0.02,
        nwc_pct=0.01,
        tax_rate=0.25,
        wacc=0.08,
        terminal_growth=0.02,
        shares_outstanding=10,
        net_debt=0,
        years=3
    )
    
    assert result['enterprise_value'] > 0
