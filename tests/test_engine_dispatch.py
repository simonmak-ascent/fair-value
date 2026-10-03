"""Engine dispatch: validation, aliases, envelope, error handling."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.engine import dispatch, is_implemented


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


def test_margin_ramp_reports_steps():
    res = dispatch(
        "calculate_dcf",
        {
            "method": "margin_ramp",
            "revenue": 100.0,
            "growth_rate": 0.2,
            "start_margin": -0.1,
            "target_margin": 0.2,
            "ramp_years": 3,
            "discount_rate": 0.1,
            "years": 5,
        },
    )
    assert res["status"] == "ok"
    assert len(res["steps"]) == 5


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
