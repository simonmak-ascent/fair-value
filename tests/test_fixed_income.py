"""Fixed-income analytics invariants and dispatch."""

import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from mcp_server.engine import dispatch
from src.derivatives import fixed_income as fi
from src.derivatives.term_structure import discount_factor as fi_discount_factor

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


def test_discount_factor_single_period():
    assert abs(fi_discount_factor(0.05, 1.0, 1)["value"] - 1.0 / 1.05) < 1e-12


def test_flat_par_bootstraps_to_flat_zero():
    from src.derivatives import term_structure as ts

    res = ts.zero_curve([0.05, 0.05, 0.05], [1.0, 2.0, 3.0], 1)
    assert all(abs(z - 0.05) < 1e-9 for z in res["zero_rates"])


def test_forward_rate_flat_curve_is_flat():
    from src.derivatives import term_structure as ts

    res = ts.forward_rate([0.05, 0.05, 0.05], [1.0, 2.0, 3.0], 1.0, 2.0)
    assert abs(res["value"] - 0.05) < 1e-9


def test_pv_curve_discounts_a_cashflow():
    from src.derivatives import term_structure as ts

    res = ts.pv_curve([105.0], [1.0], [0.05], [1.0])
    assert abs(res["value"] - 100.0) < 1e-9


def test_dispatch_zero_curve_ok():
    res = dispatch(
        "calculate_fixed_income",
        {
            "method": "zero_curve",
            "par_rates": [0.05, 0.05],
            "tenors": [1.0, 2.0],
            "frequency": 1,
        },
    )
    assert res["status"] == "ok", res
    assert len(res["zero_rates"]) == 2


def test_matrix_pricing_interpolates_between_benchmarks():
    res = fi.matrix_pricing(3.0, [1.0, 5.0], [0.02, 0.06])
    assert res["value"] == 0.04


def test_matrix_pricing_exact_and_bounds():
    assert fi.matrix_pricing(1.0, [1.0, 5.0], [0.02, 0.06])["value"] == 0.02
    assert fi.matrix_pricing(5.0, [1.0, 5.0], [0.02, 0.06])["value"] == 0.06
    with pytest.raises(ValueError):
        fi.matrix_pricing(9.0, [1.0, 5.0], [0.02, 0.06])
    with pytest.raises(ValueError):
        fi.matrix_pricing(3.0, [5.0, 1.0], [0.02, 0.06])


def test_dispatch_matrix_pricing_carries_ivs_citation():
    res = dispatch(
        "calculate_fixed_income",
        {
            "method": "matrix_pricing",
            "target_tenor": 3.0,
            "benchmark_tenors": [1.0, 5.0],
            "benchmark_yields": [0.02, 0.06],
        },
    )
    assert res["status"] == "ok", res
    assert res["value"] == 0.04
    assert "IVS.103.A05" in res["citations"]["ivs"]
