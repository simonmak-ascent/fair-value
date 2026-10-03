"""AC-7: summary aggregation is null-aware and never fabricates."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import valuation_engine as ve


def test_summary_with_provider(fake_provider):
    res = fake_provider.get_valuation_summary("AAPL")
    assert res["ticker"] == "AAPL"
    assert res["company"]["name"] == "Test Co"
    assert res["price"] == 42.0
    assert res["volatility"] == 0.25


def test_summary_missing_fields_are_none(monkeypatch):
    def _boom(ticker):
        raise RuntimeError("provider down")

    monkeypatch.setattr(ve, "_get_company_info", _boom)
    monkeypatch.setattr(ve, "_get_market_metrics", _boom)
    monkeypatch.setattr(ve, "_get_stock_price", _boom)
    monkeypatch.setattr(ve, "_get_volatility", _boom)

    res = ve.get_valuation_summary("AAPL")
    assert res["company"] is None
    assert res["metrics"] is None
    assert res["price"] is None
    assert res["volatility"] is None
