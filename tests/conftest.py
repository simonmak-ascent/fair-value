"""Shared fixtures for the engine wiring tests (A-001).

Every fixture keeps the suite offline: network-backed provider functions in
``valuation_engine`` are replaced, and market-derived DCF is stubbed per-test.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


FAKE_METRICS = {
    "revenue": 1000.0,
    "revenue_growth": 0.05,
    "ebitda_margin": 0.20,
    "shares_outstanding": 100.0,
    "eps": 5.0,
    "book_value_per_share": 50.0,
    "sales_per_share": 10.0,
    "ebitda": 200.0,
    "net_debt": 50.0,
    "sector": "Technology",
}


@pytest.fixture
def fake_provider(monkeypatch):
    """Replace the network-backed provider seam functions."""
    import valuation_engine as ve

    monkeypatch.setattr(ve, "_get_market_metrics", lambda t: dict(FAKE_METRICS))
    monkeypatch.setattr(ve, "_get_company_info", lambda t: {"name": "Test Co"})
    monkeypatch.setattr(ve, "_get_stock_price", lambda t: 42.0)
    monkeypatch.setattr(ve, "_get_volatility", lambda t: 0.25)
    return ve


@pytest.fixture
def dcf_inputs():
    return {
        "revenue": 1000.0,
        "growth_rate": 0.05,
        "ebitda_margin": 0.20,
        "capex_pct": 0.05,
        "depreciation_pct": 0.03,
        "nwc_pct": 0.02,
        "tax_rate": 0.25,
        "wacc": 0.10,
        "terminal_growth": 0.025,
        "shares_outstanding": 100.0,
        "net_debt": 50.0,
        "years": 5,
    }


@pytest.fixture
def peer_metrics():
    return [
        {"pe_ratio": 20.0, "pb_ratio": 3.0, "ps_ratio": 4.0, "ev_ebitda": 14.0},
        {"pe_ratio": 24.0, "pb_ratio": 3.4, "ps_ratio": 4.4, "ev_ebitda": 16.0},
    ]


@pytest.fixture
def unlisted_holding():
    return {
        "ticker": "PRIV",
        "shares": 1,
        "type": "unlisted",
        "annual_cash_flow": 100.0,
        "discount_rate": 0.10,
        "growth_rate": 0.02,
        "projection_years": 5,
    }
