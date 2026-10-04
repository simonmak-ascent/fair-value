"""Alias registry: synonyms and legacy names resolve to one canonical engine.

Different names for the same capability must not create extra MCP tools (that
would inflate Tool Count and duplicate parameter enums). Instead, every synonym
resolves here to a canonical tool and method. Aliases are consulted when
normalizing inputs; they never register a tool of their own.

The deliberate ``calculate_ecL`` spelling lives here so the public name is
preserved without leaking the quirk into the canonical surface.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

# alias tool name -> canonical tool name
TOOL_ALIASES: Dict[str, str] = {
    # discounted cash flow
    "valuation_dcf": "calculate_dcf",
    "run_dcf": "calculate_dcf",
    "dcf": "calculate_dcf",
    "discounted_cash_flow": "calculate_dcf",
    # options
    "black_scholes_price": "calculate_option",
    "price_option": "calculate_option",
    "bs_price": "calculate_option",
    "option_value": "calculate_option",
    # cost of capital
    "calculate_wacc": "calculate_discount_rate",
    "wacc": "calculate_discount_rate",
    "cost_of_capital": "calculate_discount_rate",
    "discount_rate": "calculate_discount_rate",
    # credit loss
    "calculate_ecl": "calculate_credit_loss",
    "calculate_ecL": "calculate_credit_loss",
    "ecl": "calculate_credit_loss",
    "expected_credit_loss": "calculate_credit_loss",
    # market multiples
    "valuation_cca": "calculate_market_multiple",
    "comps": "calculate_market_multiple",
    "comparable_company_analysis": "calculate_market_multiple",
    "market_approach": "calculate_market_multiple",
}

# canonical tool -> {alias method name -> canonical method name}
METHOD_ALIASES: Dict[str, Dict[str, str]] = {
    "calculate_dcf": {
        "net_present_value": "npv",
        "gordon": "terminal_gordon",
        "exit_multiple": "terminal_multiple",
        "value_in_use": "viu_pre_tax",
        "risk_adjusted_npv": "rnpv",
    },
    "calculate_option": {
        "bs": "black_scholes",
        "binomial": "binomial_american",
        "american": "binomial_american",
        "fx": "garman_kohlhagen",
        "barrier": "barrier_first_passage",
        "asian": "asian_average",
        "cash_or_nothing": "digital",
        "inline": "range",
    },
    "calculate_discount_rate": {
        "cost_of_capital": "wacc",
        "cost_of_equity": "capm",
        "build_up_rate": "build_up",
    },
    "calculate_credit_loss": {
        "ecl": "ecl_12m",
        "expected_credit_loss": "ecl_12m",
        "lifetime": "ecl_lifetime",
    },
}


def resolve_tool(name: str) -> str:
    """Return the canonical tool name for ``name`` (unchanged when canonical)."""
    return TOOL_ALIASES.get(name, name)


def resolve_method(tool: str, method: str) -> str:
    """Return the canonical method for ``tool``/``method`` (unchanged when canonical)."""
    canonical = resolve_tool(tool)
    return METHOD_ALIASES.get(canonical, {}).get(method, method)


def resolve(name: str, method: Optional[str] = None) -> Tuple[str, Optional[str]]:
    """Resolve an alias tool (and optional method) to canonical form."""
    tool = resolve_tool(name)
    return tool, (resolve_method(tool, method) if method is not None else None)
