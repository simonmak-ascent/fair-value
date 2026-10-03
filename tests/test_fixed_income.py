"""Fixed-income analytics invariants and dispatch."""

import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.engine import dispatch
from src.derivatives import fixed_income as fi

PAR: Dict[str, Any] = dict(face=100.0, coupon_rate=0.05, years=5.0, frequency=2)


def test_par_bond_prices_at_face():
    assert abs(fi.bond_price(ytm=0.05, **PAR)["value"] - 100.0) < 1e-6


def test_yield_recovers_coupon_for_par_bond():
    res = fi.bond_yield(price=100.0, **PAR)
    assert abs(res["value"] - 0.05) < 1e-6


def test_duration_positive_and_modified_below_macaulay():
    res = fi.duration(ytm=0.05, **PAR)
    assert res["macaulay_duration"] > 0
    assert res["modified_duration"] < res["macaulay_duration"]


def test_convexity_positive():
    assert fi.convexity(ytm=0.05, **PAR)["value"] > 0


def test_dispatch_fixed_income_ok_and_requires_ytm():
    ok = dispatch(
        "calculate_fixed_income",
        {
            "method": "bond_price",
            "face": 100.0,
            "coupon_rate": 0.05,
            "years": 5.0,
            "frequency": 2,
            "ytm": 0.05,
        },
    )
    assert ok["status"] == "ok", ok
    bad = dispatch(
        "calculate_fixed_income",
        {"method": "bond_price", "face": 100.0, "coupon_rate": 0.05, "years": 5.0, "frequency": 2},
    )
    assert bad["status"] == "error"
    assert "ytm" in bad["error"]["message"]
