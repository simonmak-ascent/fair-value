"""Structured-product pricing invariants and dispatch."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.engine import dispatch
from src.derivatives.options import black_scholes_price
from src.derivatives import structured_products as sp


def test_cbbc_below_vanilla_call():
    vanilla = black_scholes_price(100.0, 100.0, 1.0, 0.03, 0.30, "call")
    cbbc = sp.barrier_mc(100.0, 100.0, 100.0, 80.0, "knock_out", 1.0, 0.03, 0.30, "call")["value"]
    assert 0 < cbbc < vanilla


def test_derivative_warrant_below_european_call():
    vanilla = black_scholes_price(100.0, 100.0, 1.0, 0.03, 0.30, "call")
    warrant = sp.geometric_asian(100.0, 100.0, 100.0, 1.0, 0.03, 0.30, "call", "geometric")["value"]
    assert 0 < warrant < vanilla


def test_inline_warrant_probability_bounds():
    res = sp.range_digital(100.0, 100.0, 90.0, 110.0, 1.0, 0.03, 0.30, 1.0)
    assert 0 <= res["probability"] <= 1
    assert 0 < res["value"] <= 100.0


def test_credit_linked_note_between_recovery_and_straight():
    import math

    straight = 100.0 * math.exp(-0.03 * 2) + 100.0 * 0.05 * (1 - math.exp(-0.06)) / 0.03
    cldn = sp.credit_linked_note(100.0, 0.05, 0.40, 2.0, 0.03, 0.05)["value"]
    assert 0.40 * 100.0 * math.exp(-0.06) - 1e-6 <= cldn <= straight


def test_eln_value_reduced_by_short_put():
    res = sp.equity_linked_note(100.0, 100.0, 90.0, 1.0, 0.03, 0.30, 0.05)
    assert res["short_put"] > 0
    assert res["value"] > 0


def test_accumulator_positive_when_deep_in_the_money():
    res = sp.accumulator_mc(100.0, 100.0, 50.0, 500.0, [0.25, 0.5, 0.75, 1.0], 0.03, 0.20, 1, 1.0)
    assert res["value"] > 0


def test_monte_carlo_deterministic():
    a = sp.barrier_mc(100.0, 100.0, 100.0, 80.0, "knock_out", 1.0, 0.03, 0.30, "call")["value"]
    b = sp.barrier_mc(100.0, 100.0, 100.0, 80.0, "knock_out", 1.0, 0.03, 0.30, "call")["value"]
    assert a == b


def test_dispatch_option_asian_and_barrier_ok():
    for method, extra in (
        ("asian_average", {"average_type": "geometric"}),
        ("barrier_first_passage", {"barrier": 80.0, "barrier_type": "knock_out"}),
    ):
        res = dispatch(
            "calculate_option",
            {
                "method": method,
                "spot": 100.0,
                "strike": 100.0,
                "maturity": 1.0,
                "risk_free": 0.03,
                "volatility": 0.30,
                "option_type": "call",
                **extra,
            },
        )
        assert res["status"] == "ok", res


def test_dispatch_structured_requires_notional():
    res = dispatch(
        "calculate_structured_product",
        {
            "method": "cbbc",
            "spot": 100.0,
            "strike": 100.0,
            "barrier": 80.0,
            "barrier_type": "knock_out",
            "maturity": 1.0,
            "risk_free": 0.03,
            "volatility": 0.30,
            "option_type": "call",
        },
    )
    assert res["status"] == "error"
    assert "notional" in res["error"]["message"]


def test_dispatch_structured_cbbc_ok():
    res = dispatch(
        "calculate_structured_product",
        {
            "method": "cbbc",
            "notional": 100.0,
            "spot": 100.0,
            "strike": 100.0,
            "barrier": 80.0,
            "barrier_type": "knock_out",
            "maturity": 1.0,
            "risk_free": 0.03,
            "volatility": 0.30,
            "option_type": "call",
        },
    )
    assert res["status"] == "ok", res
    assert res["value"] > 0


def test_cbbc_residual_knock_out_value():
    res = sp.cbbc_residual(
        notional=100.0, spot=100.0, call_price=70.0, entitlement=1.0, barrier=80.0,
        barrier_type="knock_out", maturity=1.0, risk_free=0.03, volatility=0.30,
        option_type="call",
    )
    assert res["value"] > 0
    assert res["knock_out_residual"] == 10.0  # (80 - 70) / 1


def test_inline_warrant_avg_close_to_single_fixing():
    single = sp.range_digital(100.0, 100.0, 90.0, 110.0, 1.0, 0.03, 0.30, 1.0)["value"]
    avg = sp.range_digital_average(100.0, 100.0, 90.0, 110.0, 1.0, 0.03, 0.30, 1.0, 1)["value"]
    assert avg > 0
    assert abs(avg - single) / single < 0.05


def test_dispatch_hkex_methods_ok():
    for method, extra in (
        ("cbbc_residual", {"call_price": 70.0, "entitlement": 1.0, "barrier": 80.0,
                            "barrier_type": "knock_out", "option_type": "call"}),
        ("inline_warrant_avg", {"lower_strike": 90.0, "upper_strike": 110.0, "payout": 1.0,
                                 "fixing_days": 3}),
    ):
        args = {"method": method, "notional": 100.0, "spot": 100.0, "maturity": 1.0,
                "risk_free": 0.03, "volatility": 0.30, **extra}
        res = dispatch("calculate_structured_product", args)
        assert res["status"] == "ok", res
        assert res["value"] > 0
