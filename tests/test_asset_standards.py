"""A-004: asset-standard coverage (IVS 210 intangibles; IAS 36 recoverable amount)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from src.valuation.asset_standards import (
    mpeem,
    recoverable_amount,
    relief_from_royalty,
    with_without,
)


def test_relief_from_royalty():
    # revenue 1000 x 5% = 50 per year, discounted at 10% for 2 years.
    value = relief_from_royalty(1000.0, 0.05, 0.10, 2)
    assert value == pytest.approx(50 * (1 / 1.1 + 1 / 1.21), rel=1e-9)


def test_mpeem():
    value = mpeem([100.0, 100.0], [10.0, 10.0], 0.10)
    assert value == pytest.approx(90 / 1.1 + 90 / 1.21, rel=1e-9)


def test_mpeem_length_mismatch_raises():
    with pytest.raises(ValueError):
        mpeem([100.0, 100.0], [10.0], 0.10)
    with pytest.raises(ValueError):
        mpeem([], [], 0.10)


def test_with_without():
    value = with_without([120.0, 120.0], [100.0, 100.0], 0.10)
    assert value == pytest.approx(20 / 1.1 + 20 / 1.21, rel=1e-9)


def test_with_without_alignment_raises():
    with pytest.raises(ValueError):
        with_without([120.0], [100.0, 100.0], 0.10)


def test_recoverable_amount_is_the_higher():
    assert recoverable_amount(80.0, 100.0) == 100.0
    assert recoverable_amount(120.0, 90.0) == 120.0


def test_registered_and_dispatched_with_citations():
    from mcp_server import method_spec

    assert method_spec.get("calculate_residual", "relief_from_royalty") is not None
    assert method_spec.get("calculate_residual", "mpeem") is not None
    assert method_spec.get("calculate_residual", "with_without") is not None
    assert method_spec.get("calculate_residual", "recoverable_amount") is not None

    from mcp_server.engine import dispatch

    res = dispatch(
        "calculate_residual",
        {
            "method": "recoverable_amount",
            "fair_value_less_costs_to_dispose": 80.0,
            "value_in_use": 100.0,
        },
    )
    assert res["status"] == "ok"
    assert res["value"] == 100.0
    assert res["solution_type"] == "closed_form"
    assert "IVS.103.A10" in res["citations"]["ivs"]
    assert "IAS.36.18" in res["citations"]["ifrs"]

    rr = dispatch(
        "calculate_residual",
        {
            "method": "relief_from_royalty",
            "revenue": 1000.0,
            "royalty_rate": 0.05,
            "discount_rate": 0.10,
            "periods": 2,
        },
    )
    assert rr["status"] == "ok"
    assert "IVS.210.A10" in rr["citations"]["ivs"]
