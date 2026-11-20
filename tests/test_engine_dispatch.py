"""Engine dispatch: validation, aliases, envelope, error handling."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from src.mcp.engine import _non_finite, dispatch, is_implemented


def test_valid_call_returns_ok_envelope():
    res = dispatch(
        "calculate_dcf", {"method": "dcf", "cash_flows": [100.0, 110.0], "discount_rate": 0.1}
    )
    assert res["status"] == "ok"
    assert res["method"] == "calculate_dcf.dcf"
    assert res["value"] > 0
    assert res["disclaimer"]


def test_missing_method_is_error():
    res = dispatch("calculate_dcf", {"cash_flows": [1.0], "discount_rate": 0.1})
    assert res["status"] == "error"
    assert res["error"]["code"] == "INVALID_ARGUMENT"


def test_missing_required_input_is_error():
    res = dispatch("calculate_dcf", {"method": "dcf", "cash_flows": [1.0]})
    assert res["status"] == "error"
    assert "discount_rate" in res["error"]["message"]


def test_extraneous_input_is_error():
    res = dispatch(
        "calculate_dcf", {"method": "dcf", "cash_flows": [1.0], "discount_rate": 0.1, "x": 1}
    )
    assert res["status"] == "error"
    assert "unexpected" in res["error"]["message"]


def test_unknown_method_is_error():
    res = dispatch("calculate_dcf", {"method": "bogus"})
    assert res["status"] == "error"
    assert "unknown method" in res["error"]["message"]


def test_alias_tool_and_method_resolve():
    res = dispatch("calculate_ecL", {"method": "ecl", "ead": 100.0, "pd": 0.02, "lgd": 0.45})
    assert res["status"] == "ok"
    assert abs(res["value"] - 0.9) < 1e-9


def test_computation_error_becomes_envelope():
    res = dispatch(
        "calculate_discount_rate",
        {
            "method": "wacc",
            "equity_weight": 0.6,
            "debt_weight": 0.6,
            "cost_equity": 0.1,
            "cost_debt": 0.05,
            "tax_rate": 0.25,
        },
    )
    assert res["status"] == "error"
    assert res["error"]["code"] == "COMPUTATION_ERROR"


@pytest.mark.parametrize(
    "result, expected",
    [
        (1.0, None),
        (float("nan"), "value = nan"),
        ({"value": float("inf")}, "value.value = inf"),
        ({"value": [1.0, float("-inf")]}, "value.value[1] = -inf"),
        ({"statistics": {"centre": float("nan")}}, "value.statistics.centre = nan"),
        ({"ok": True, "n": 3}, None),  # a bool field must not trip the walk
        ({"nested": {"deep": [{"x": 1}, {"x": float("inf")}]}}, "value.nested.deep[1].x = inf"),
    ],
)
def test_non_finite_scan_covers_every_shape(result, expected):
    """The walk must reach lists and nested dicts, not just a top-level scalar.

    Without this the guard is only proven on the one shape a handler happened to return, and a
    regression that dropped list recursion would leave the suite green.
    """
    assert _non_finite(result) == expected


def test_non_finite_result_becomes_envelope_not_nan():
    """A result of inf/nan must not reach the caller as a success envelope.

    Found on the live deployment 2026-11-20: `binomial_american` with a large `volatility`
    overflows the lattice's `exp`, the value comes back `nan`, and the REST layer's strict JSON
    encoder turns that into an HTTP 500 with no envelope at all — a client cannot tell it from a
    gateway failure. The overflows are numpy warnings, not exceptions, so nothing upstream caught it.
    """
    res = dispatch(
        "calculate_option",
        {
            "method": "binomial_american",
            "spot": 100.0,
            "strike": 100.0,
            "maturity": 1.0,
            "risk_free": 0.05,
            "volatility": 1000.0,
            "option_type": "call",
            "steps": 100,
        },
    )
    assert res["status"] == "error"
    assert res["error"]["code"] == "COMPUTATION_ERROR"
    assert "finite" in res["error"]["message"]


def test_unimplemented_method_is_typed_error():
    assert not is_implemented("calculate_convertible_bond", "quantlib")
    args = {
        "method": "quantlib",
        "spot": 100.0,
        "face": 100.0,
        "coupon_rate": 0.03,
        "maturity": 3.0,
        "conversion_ratio": 1.0,
        "volatility": 0.25,
        "risk_free": 0.03,
        "credit_spread": 0.02,
        "call_schedule": [],
        "put_schedule": [],
        "rights_priority": "debt",
    }
    res = dispatch("calculate_convertible_bond", args)
    assert res["status"] == "error"
    assert res["error"]["code"] == "NOT_IMPLEMENTED"


def test_margin_ramp_dcf_reports_dispersion():
    res = dispatch(
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
            "net_debt": 0.0,
            "range_method": "central",
        },
    )
    assert res["status"] == "ok"
    assert "dispersion" in res


def test_option_call_and_put():
    call = dispatch(
        "calculate_option",
        {
            "method": "black_scholes",
            "spot": 100.0,
            "strike": 100.0,
            "maturity": 1.0,
            "risk_free": 0.05,
            "volatility": 0.2,
            "option_type": "call",
        },
    )
    put = dispatch(
        "calculate_option",
        {
            "method": "black_scholes",
            "spot": 100.0,
            "strike": 100.0,
            "maturity": 1.0,
            "risk_free": 0.05,
            "volatility": 0.2,
            "option_type": "put",
        },
    )
    assert call["status"] == "ok" and put["status"] == "ok"
    # put-call parity: C - P = S - K e^{-rT}
    import math

    assert abs((call["value"] - put["value"]) - (100.0 - 100.0 * math.exp(-0.05))) < 1e-6


def test_non_financial_asset_fair_value_methods():
    cases = [
        ("investment_property", {"noi": 100.0, "cap_rate": 0.05}, 2000.0),
        ("ppe_revaluation", {"replacement_cost": 1000.0, "accumulated_depreciation": 300.0}, 700.0),
        ("biological_asset", {"expected_price": 10.0, "quantity": 5.0, "costs_to_sell": 8.0}, 42.0),
    ]
    for method, params, expected in cases:
        res = dispatch("calculate_residual", {"method": method, **params})
        assert res["status"] == "ok", res
        assert abs(res["value"] - expected) < 1e-9
