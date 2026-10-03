"""Convertible-bond lattice invariants and dispatch."""

import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.derivatives.convertible_lattice import convertible_bond_value

BASE: Dict[str, Any] = dict(
    spot=100.0,
    face=100.0,
    coupon_rate=0.03,
    maturity=3.0,
    conversion_ratio=1.0,
    volatility=0.30,
    risk_free=0.03,
    credit_spread=0.02,
    steps=200,
)


def test_value_positive_and_at_least_conversion():
    res = convertible_bond_value(**BASE)
    assert res["value"] > 0
    assert res["value"] >= res["conversion_value"] - 1e-6


def test_call_feature_lowers_value():
    params: Dict[str, Any] = {**BASE, "conversion_ratio": 0.01}
    without = convertible_bond_value(**params)["value"]
    with_call = convertible_bond_value(
        **params, call_schedule=[{"date_years": 2.0, "price": 95.0}]
    )["value"]
    assert with_call < without


def test_put_feature_raises_value():
    params: Dict[str, Any] = {**BASE, "conversion_ratio": 0.01}
    without = convertible_bond_value(**params)["value"]
    with_put = convertible_bond_value(**params, put_schedule=[{"date_years": 2.0, "price": 105.0}])[
        "value"
    ]
    assert with_put > without


def test_credit_spread_lowers_value():
    low = convertible_bond_value(**{**BASE, "credit_spread": 0.01})["value"]
    high = convertible_bond_value(**{**BASE, "credit_spread": 0.08})["value"]
    assert high < low


def test_value_increases_with_spot():
    low = convertible_bond_value(**{**BASE, "spot": 80.0})["value"]
    high = convertible_bond_value(**{**BASE, "spot": 120.0})["value"]
    assert high > low


def test_deep_itm_tracks_conversion():
    res = convertible_bond_value(**{**BASE, "spot": 200.0})
    assert res["value"] >= res["conversion_value"] - 1e-6
    assert res["value"] < res["conversion_value"] * 1.06


def test_low_conversion_tracks_bond_floor():
    res = convertible_bond_value(**{**BASE, "conversion_ratio": 0.001})
    assert abs(res["value"] - res["bond_floor"]) / res["bond_floor"] < 0.03


def test_higher_volatility_increases_value():
    low = convertible_bond_value(**{**BASE, "volatility": 0.05})["value"]
    high = convertible_bond_value(**{**BASE, "volatility": 0.60})["value"]
    assert high > low


def test_dispatch_returns_envelope():
    from mcp_server.engine import dispatch

    res = dispatch(
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
            "call_schedule": [],
            "put_schedule": [],
            "rights_priority": "holder",
        },
    )
    assert res["status"] == "ok"
    assert res["value"] > 0
    assert res["bond_floor"] > 0


def test_call_price_caps_near_bond_value():
    # Regression: on issuer call the value must be ~the call price, not ~0.
    res = convertible_bond_value(
        **{**BASE, "conversion_ratio": 0.01},
        call_schedule=[{"date_years": 2.0, "price": 95.0}],
    )
    assert 80.0 < res["value"] < 98.0


def test_lsmc_matches_lattice():
    from src.derivatives.convertible_alt import convertible_lsmc

    for params, call in (
        (BASE, []),
        ({**BASE, "conversion_ratio": 1.0}, [{"date_years": 2.0, "price": 95.0}]),
    ):
        lat = convertible_bond_value(**params, call_schedule=call)["value"]
        mc = convertible_lsmc(
            **{**params, "steps": 150}, call_schedule=call, put_schedule=[], paths=60000
        )["value"]
        assert abs(mc - lat) / lat < 0.06, (params, lat, mc)


def test_lsmc_dispatch_ok():
    from mcp_server.engine import dispatch

    res = dispatch(
        "calculate_convertible_bond",
        {
            "method": "lsmc",
            "spot": 100.0,
            "face": 100.0,
            "coupon_rate": 0.03,
            "maturity": 3.0,
            "conversion_ratio": 1.0,
            "volatility": 0.30,
            "risk_free": 0.03,
            "credit_spread": 0.02,
            "call_schedule": [],
            "put_schedule": [],
            "rights_priority": "holder",
        },
    )
    assert res["status"] == "ok", res
    assert res["value"] > 0
