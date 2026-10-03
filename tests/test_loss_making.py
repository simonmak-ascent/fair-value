"""Loss-making-company models and the shared dispersion kernel."""

import sys
from pathlib import Path
from typing import Any, Dict

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.engine import dispatch
from src.valuation import loss_making as lm


def test_dispersion_ordering_and_tail():
    stats = lm.dispersion([10.0, 20.0, 30.0, 40.0, 50.0])
    p = stats["percentiles"]
    assert p["p5"] <= p["p25"] <= p["p50"] <= p["p75"] <= p["p95"]
    assert stats["long_tail"] == 10.0
    assert stats["mean"] == 30.0


def test_pick_rejects_unknown_range_method():
    stats = lm.dispersion([1.0, 2.0])
    with pytest.raises(ValueError):
        lm.pick(stats, "mode")


def test_margin_ramp_net_debt_reduces_per_share():
    base: Dict[str, Any] = dict(
        revenue=1000.0,
        growth_rate=0.10,
        start_margin=-0.05,
        target_margin=0.15,
        ramp_years=5,
        discount_rate=0.12,
        years=5,
        shares_outstanding=100.0,
        net_debt=0.0,
        range_method="central",
    )
    no_debt = lm.margin_ramp_dcf(**base)["value"]
    with_debt = lm.margin_ramp_dcf(**{**base, "net_debt": 200.0})["value"]
    assert with_debt < no_debt


def test_revenue_multiple_scales_with_multiple():
    low = lm.revenue_multiple(1000.0, 2.0, 500.0, 100.0, "central")["value"]
    high = lm.revenue_multiple(1000.0, 4.0, 500.0, 100.0, "central")["value"]
    assert high > low


def test_merton_equity_bounds_and_monotone():
    low = lm.merton_equity(1000.0, 0.30, 800.0, 0.03, 1.0, "central")["value"]
    high = lm.merton_equity(2000.0, 0.30, 800.0, 0.03, 1.0, "central")["value"]
    assert 0 < low < 1000.0
    assert high > low


def test_scenario_weighted_mean():
    res = lm.scenario_weighted(
        [{"value": 100.0, "probability": 0.5}, {"value": 200.0, "probability": 0.5}], "mean"
    )
    assert res["value"] == 150.0


def test_vc_method_decreases_with_target_return():
    low = lm.vc_method(1000.0, 0.50, 100.0, 100.0, "central")["value"]
    high = lm.vc_method(1000.0, 1.00, 100.0, 100.0, "central")["value"]
    assert high < low


def test_distressed_waterfall_senior_first():
    claims = [
        {"name": "senior", "amount": 900.0, "priority": 1},
        {"name": "junior", "amount": 200.0, "priority": 2},
    ]
    res = lm.distressed_waterfall(1000.0, claims, "central")
    assert res["recoveries"][0]["recovery"] == 900.0
    assert res["recoveries"][1]["recovery"] == 100.0
    assert res["residual_to_equity"] == 0.0


def test_bank_residual_income_premium_when_roe_above_cost():
    res = lm.bank_residual_income(1000.0, 150.0, 0.10, 0.03, "central")
    assert res["justified_pb"] > 1.0


def test_dispatch_loss_making_ok_and_requires_range_method():
    args = dict(
        method="margin_ramp_dcf",
        revenue=1000.0,
        growth_rate=0.10,
        start_margin=-0.05,
        target_margin=0.15,
        ramp_years=5,
        discount_rate=0.12,
        years=5,
        shares_outstanding=100.0,
        net_debt=200.0,
        range_method="central",
    )
    res = dispatch("calculate_loss_making_company", args)
    assert res["status"] == "ok", res
    assert "dispersion" in res
    missing = {k: v for k, v in args.items() if k != "range_method"}
    bad = dispatch("calculate_loss_making_company", missing)
    assert bad["status"] == "error"
    assert "range_method" in bad["error"]["message"]
