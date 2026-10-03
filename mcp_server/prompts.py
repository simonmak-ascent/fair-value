"""A-013: guided MCP prompts for common valuation workflows."""

from __future__ import annotations


def value_company_dcf(ticker: str) -> str:
    """Guide a discounted cash flow valuation for a listed company."""
    return (
        f"Value {ticker} using a discounted cash flow.\n"
        f"1. Call `calculate_company_summary` (method 'profile') with ticker='{ticker}' to collect market inputs.\n"
        f"2. Call `calculate_dcf` (method 'dcf') with the projected cash flows and discount rate.\n"
        f"3. Report fair value per share, WACC, terminal growth, the key assumptions, "
        f"and the implied margin of safety.\n"
        f"State clearly that this is not investment advice."
    )


def review_valuation_report(file_path: str) -> str:
    """Guide a structured review of an existing valuation report file."""
    return (
        f"Review the valuation report at '{file_path}'.\n"
        f"1. Call `calculate_report_review` (method 'audit') with file_path='{file_path}'.\n"
        f"2. Summarise the identified methodology, formula validation findings, the "
        f"discount-rate/terminal-value checks, and any data-source or injection flags.\n"
        f"3. List concrete issues and their severity; do not restate the whole report."
    )


def explain_cost_of_capital(ticker: str) -> str:
    """Guide a cost-of-capital explanation using profile data and WACC."""
    return (
        f"Explain the cost of capital for {ticker}.\n"
        f"1. Call `calculate_company_summary` (method 'profile') for '{ticker}' to obtain beta, "
        f"price, and market data.\n"
        f"2. Call `calculate_discount_rate` (method 'wacc') with sensible equity/debt weights "
        f"and costs, and state every input you assumed.\n"
        f"3. Interpret the result and note sensitivity to the risk-free rate and beta."
    )


# name -> prompt function (function __doc__ is the prompt description)
GUIDED_PROMPTS = {
    "value_company_dcf": value_company_dcf,
    "review_valuation_report": review_valuation_report,
    "explain_cost_of_capital": explain_cost_of_capital,
}
