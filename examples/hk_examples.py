"""Worked Hong Kong market examples for the fair-value MCP engine.

Run from the repo root:  python examples/hk_examples.py

All three examples are offline and deterministic (Monte-Carlo engines are
seeded), so they are safe to run in CI or locally.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.engine import dispatch  # noqa: E402


def hk_convertible_bond() -> Dict[str, Any]:
    """Value a 3-year HKD convertible with a 2-year issuer call at par."""
    return dispatch(
        "calculate_convertible_bond",
        {
            "method": "lattice_tsf",
            "spot": 100.0,
            "face": 100.0,
            "coupon_rate": 0.03,
            "maturity": 3.0,
            "conversion_ratio": 1.0,
            "volatility": 0.30,
            "risk_free": 0.03,
            "credit_spread": 0.02,
            "call_schedule": [{"date_years": 2.0, "price": 95.0}],
            "put_schedule": [],
            "rights_priority": "holder",
        },
    )


def hk_inline_warrant() -> Dict[str, Any]:
    """Price an HKEX inline range warrant paying 1 if 90 < S_T < 110."""
    return dispatch(
        "calculate_structured_product",
        {
            "method": "inline_warrant",
            "notional": 10000.0,
            "spot": 100.0,
            "lower_strike": 90.0,
            "upper_strike": 110.0,
            "maturity": 0.5,
            "risk_free": 0.03,
            "volatility": 0.25,
            "payout": 1.0,
        },
    )


def hk_loss_making_company() -> Dict[str, Any]:
    """Margin-ramp value of a loss-making listing, with dispersion."""
    return dispatch(
        "calculate_loss_making_company",
        {
            "method": "margin_ramp_dcf",
            "revenue": 1000.0,
            "growth_rate": 0.10,
            "start_margin": -0.05,
            "target_margin": 0.15,
            "ramp_years": 5,
            "discount_rate": 0.12,
            "years": 5,
            "shares_outstanding": 100.0,
            "net_debt": 200.0,
            "range_method": "central",
        },
    )


def main() -> None:
    for label, result in (
        ("HK convertible bond (lattice_tsf)", hk_convertible_bond()),
        ("HKEX inline warrant", hk_inline_warrant()),
        ("Loss-making listing (margin-ramp DCF)", hk_loss_making_company()),
    ):
        value = result.get("value")
        print(f"{label}: status={result.get('status')} value={value}")
        if result.get("status") == "error":
            print(json.dumps(result["error"], indent=2))


if __name__ == "__main__":
    main()
