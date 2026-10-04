"""AC-1..AC-3: routing and error shaping for DCF / NAV / CCA."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

import valuation_engine as ve


def test_dcf_explicit_inputs(dcf_inputs):
    res = ve.run_valuation("TEST", "dcf", dcf_inputs)
    assert res["status"] == "ok"
    assert res["method"] == "DCF"
    assert res["value_per_share"] > 0


def test_dcf_invalid_inputs_is_missing_input():
    res = ve.run_valuation("TEST", "dcf", {"revenue": 100.0})  # missing required
    assert res["status"] == "error"
    assert res["error"]["code"] == "MISSING_INPUT"


def test_unknown_method():
    res = ve.run_valuation("TEST", "bogus")
    assert res["status"] == "error"
    assert res["error"]["code"] == "UNKNOWN_METHOD"


def test_blank_ticker():
    res = ve.run_valuation("", "dcf")
    assert res["status"] == "error"
    assert res["error"]["code"] == "INVALID_ARGUMENT"


def test_nav_holdings(unlisted_holding):
    res = ve.run_valuation(
        "HOLD",
        "nav",
        {"holdings": [unlisted_holding], "liabilities": 0, "shares_outstanding": 10},
    )
    assert res["status"] == "ok"
    assert res["method"] == "NAV"
    assert res["nav_per_share"] > 0


def test_nav_empty_holdings():
    res = ve.run_valuation("HOLD", "nav", {"holdings": []})
    assert res["status"] == "error"
    assert res["error"]["code"] == "MISSING_INPUT"


def test_nav_no_inputs():
    res = ve.run_valuation("HOLD", "nav", {})
    assert res["status"] == "error"
    assert res["error"]["code"] == "MISSING_INPUT"


def test_cca_with_peers(peer_metrics):
    target = {
        "eps": 5.0,
        "book_value_per_share": 50.0,
        "sales_per_share": 10.0,
        "ebitda": 200.0,
        "net_debt": 50.0,
    }
    res = ve.run_valuation(
        "TEST",
        "cca",
        {"target_metrics": target, "peer_metrics": peer_metrics},
    )
    assert res["status"] == "ok"
    assert res["method"] == "CCA"
    assert res["implied_value"] > 0


def test_cca_no_peers():
    res = ve.run_valuation(
        "TEST",
        "cca",
        {"target_metrics": {"eps": 5.0}, "peer_metrics": []},
    )
    assert res["status"] == "error"
    assert res["error"]["code"] == "DATA_UNAVAILABLE"
