"""
Discounted Cash Flow (DCF) Valuation Module
"""

import pandas as pd
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


def project_free_cash_flows(
    revenue: float,
    growth_rate: float,
    ebitda_margin: float,
    capex_pct: float,
    depreciation_pct: float,
    nwc_pct: float,
    tax_rate: float,
    years: int = 5,
) -> pd.DataFrame:
    """
    Project free cash flows for n years

    Args:
        revenue: Base revenue
        growth_rate: Annual revenue growth rate
        ebitda_margin: EBITDA margin
        capex_pct: CapEx as % of revenue
        depreciation_pct: Depreciation as % of revenue
        nwc_pct: Net working capital as % of revenue
        tax_rate: Corporate tax rate
        years: Number of projection years

    Returns:
        DataFrame with yearly projections
    """
    projections = []

    for year in range(1, years + 1):
        rev = revenue * (1 + growth_rate) ** year
        ebitda = rev * ebitda_margin
        depreciation = rev * depreciation_pct
        ebit = ebitda - depreciation
        tax = max(ebit * tax_rate, 0)  # No negative tax
        nopat = ebit - tax
        capex = rev * capex_pct
        nwc_change = rev * nwc_pct * growth_rate
        fcf = nopat + depreciation - capex - nwc_change

        projections.append(
            {
                "year": year,
                "revenue": rev,
                "ebitda": ebitda,
                "ebit": ebit,
                "tax": tax,
                "nopat": nopat,
                "depreciation": depreciation,
                "capex": capex,
                "nwc_change": nwc_change,
                "free_cash_flow": fcf,
            }
        )

    return pd.DataFrame(projections)


def calculate_terminal_value_gordon(
    final_fcf: float, wacc: float, perpetual_growth: float
) -> float:
    """
    Calculate terminal value using Gordon growth model

    TV = FCF(n) × (1+g) / (WACC - g)

    Args:
        final_fcf: Final year FCF
        wacc: Weighted average cost of capital
        perpetual_growth: Perpetual growth rate

    Returns:
        Terminal value
    """
    if wacc <= perpetual_growth:
        logger.warning("WACC must be greater than perpetual growth rate")
        return 0.0

    return final_fcf * (1 + perpetual_growth) / (wacc - perpetual_growth)


def calculate_terminal_value_exit(final_fcf: float, exit_multiple: float) -> float:
    """
    Calculate terminal value using exit multiple method

    TV = FCF(n) × Exit Multiple

    Args:
        final_fcf: Final year FCF
        exit_multiple: EV/EBITDA exit multiple

    Returns:
        Terminal value
    """
    return final_fcf * exit_multiple


def discount_cash_flows(
    cash_flows: List[float], wacc: float, discounting_start_year: int = 1
) -> float:
    """
    Calculate present value of projected cash flows

    Args:
        cash_flows: List of cash flows
        wacc: Discount rate
        discounting_start_year: Year to start discounting from

    Returns:
        Present value of cash flows
    """
    pv = 0.0
    for i, cf in enumerate(cash_flows):
        discount_factor = 1 / (1 + wacc) ** (i + discounting_start_year)
        pv += cf * discount_factor
    return pv


def discount_single_value(future_value: float, wacc: float, years: int) -> float:
    """
    Discount a single future value to present

    Args:
        future_value: Future value to discount
        wacc: Discount rate
        years: Number of years

    Returns:
        Present value
    """
    return future_value / (1 + wacc) ** years


def dcf_valuation(
    ticker: str,
    revenue: float,
    growth_rate: float,
    ebitda_margin: float,
    capex_pct: float,
    depreciation_pct: float,
    nwc_pct: float,
    tax_rate: float,
    wacc: float,
    terminal_growth: float,
    shares_outstanding: float,
    net_debt: float = 0,
    years: int = 5,
    terminal_method: str = "gordon",
) -> Dict:
    """
    Complete DCF valuation

    Args:
        ticker: Stock ticker
        revenue: Base revenue
        growth_rate: Revenue growth rate
        ebitda_margin: EBITDA margin
        capex_pct: CapEx as % of revenue
        depreciation_pct: Depreciation as % of revenue
        nwc_pct: Net working capital as % of revenue
        tax_rate: Corporate tax rate
        wacc: Weighted average cost of capital
        terminal_growth: Terminal growth rate
        shares_outstanding: Shares outstanding
        net_debt: Net debt (debt - cash)
        years: Projection years
        terminal_method: 'gordon' or 'exit_multiple'

    Returns:
        DCF valuation results
    """
    # Project cash flows
    projections = project_free_cash_flows(
        revenue, growth_rate, ebitda_margin, capex_pct, depreciation_pct, nwc_pct, tax_rate, years
    )

    cash_flows = projections["free_cash_flow"].tolist()

    # Calculate terminal value
    if terminal_method == "gordon":
        terminal_value = calculate_terminal_value_gordon(cash_flows[-1], wacc, terminal_growth)
    else:
        # Use 10x EBITDA as default exit multiple
        final_ebitda = projections["ebitda"].iloc[-1]
        terminal_value = calculate_terminal_value_exit(final_ebitda, 10.0)

    # Discount terminal value
    terminal_value_pv = discount_single_value(terminal_value, wacc, years)

    # Discount projected cash flows
    pv_cash_flows = discount_cash_flows(cash_flows, wacc)

    # Enterprise value
    enterprise_value = pv_cash_flows + terminal_value_pv

    # Equity value
    equity_value = enterprise_value - net_debt

    # Value per share
    value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0

    return {
        "ticker": ticker,
        "method": "DCF",
        "projections": projections.to_dict("records"),
        "terminal_value": terminal_value,
        "terminal_value_pv": terminal_value_pv,
        "pv_cash_flows": pv_cash_flows,
        "enterprise_value": enterprise_value,
        "net_debt": net_debt,
        "equity_value": equity_value,
        "value_per_share": value_per_share,
        "wacc": wacc,
        "terminal_growth": terminal_growth,
        "terminal_method": terminal_method,
    }


def dcf_from_market_data(
    ticker: str, metrics: Dict, wacc: float, terminal_growth: float = 0.025, years: int = 5
) -> Dict:
    """
    DCF valuation using market data from yfinance

    Args:
        ticker: Stock ticker
        metrics: Market metrics from get_key_metrics
        wacc: Weighted average cost of capital
        terminal_growth: Terminal growth rate
        years: Projection years

    Returns:
        DCF valuation results
    """
    from ..fetch_data import get_balance_sheet

    # Get financial data
    balance = get_balance_sheet(ticker)

    # Extract base values
    revenue = metrics.get("revenue", 0)
    revenue_growth = metrics.get("revenue_growth", 0)

    if revenue == 0:
        return {"error": "No revenue data available"}

    # Estimate EBITDA margin (simplified)
    ebitda_margin = metrics.get("ebitda_margin", 0.20)

    # Estimate shares outstanding
    shares = metrics.get("shares_outstanding", 1)

    # Estimate net debt
    try:
        total_debt = balance.loc["Total Debt"].iloc[0] if "Total Debt" in balance.index else 0
        cash = (
            balance.loc["Cash And Cash Equivalents"].iloc[0]
            if "Cash And Cash Equivalents" in balance.index
            else 0
        )
        net_debt = max(total_debt - cash, 0)
    except Exception:
        net_debt = 0

    # Run DCF
    return dcf_valuation(
        ticker=ticker,
        revenue=revenue,
        growth_rate=revenue_growth,
        ebitda_margin=ebitda_margin,
        capex_pct=0.05,  # 5% of revenue
        depreciation_pct=0.03,  # 3% of revenue
        nwc_pct=0.02,  # 2% of revenue
        tax_rate=0.25,
        wacc=wacc,
        terminal_growth=terminal_growth,
        shares_outstanding=shares,
        net_debt=net_debt,
        years=years,
    )
