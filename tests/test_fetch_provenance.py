"""A-010: fetch_data provenance, caching, idempotency, and no-fabrication."""

import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import fetch_data as fd  # noqa: E402


class _FakeTicker:
    """Offline stand-in for ``yfinance.Ticker``."""

    _info_by_ticker = {
        "ACME": {"longName": "Acme Corp", "marketCap": 1000, "beta": 1.2},
        "EMPTY": {},
    }

    def __init__(self, ticker):
        self.ticker = ticker

    @property
    def info(self):
        return dict(self._info_by_ticker.get(self.ticker, {}))


@pytest.fixture(autouse=True)
def _fake_yf(monkeypatch):
    fd.clear_cache()
    monkeypatch.setattr(fd, "yf", types.SimpleNamespace(Ticker=_FakeTicker))
    yield
    fd.clear_cache()


def test_cache_hit_is_idempotent():
    first = fd.get_key_metrics("ACME")
    second = fd.get_key_metrics("ACME")
    assert first == second

    prov = fd.get_provenance()["get_key_metrics"]
    assert prov["source"] == "yfinance"
    assert prov["ttl_seconds"] == fd.DEFAULT_CACHE_TTL
    assert prov["cached"] is True  # second call served from cache
    assert fd.cache_stats()["entries"] >= 1


def test_first_call_reports_not_cached():
    fd.get_key_metrics("ACME")
    assert fd.get_provenance()["get_key_metrics"]["cached"] is False


def test_fetched_at_is_iso8601():
    from datetime import datetime

    fd.get_company_info("ACME")
    ts = fd.get_provenance()["get_company_info"]["fetched_at"]
    datetime.fromisoformat(ts)  # raises if malformed


def test_idempotency_key_stable_for_same_args():
    fd.get_stock_price("ACME")
    k1 = fd.get_provenance()["get_stock_price"]["idempotency_key"]
    fd.get_stock_price("ACME")
    k2 = fd.get_provenance()["get_stock_price"]["idempotency_key"]
    assert k1 == k2


def test_idempotency_key_differs_for_different_args():
    fd.get_stock_price("ACME")
    k1 = fd.get_provenance()["get_stock_price"]["idempotency_key"]
    fd.get_stock_price("OTHER")
    k2 = fd.get_provenance()["get_stock_price"]["idempotency_key"]
    assert k1 != k2


def test_missing_keys_are_absent_not_fabricated():
    info = fd.get_company_info("ACME")
    assert info["name"] == "Acme Corp"
    assert "sector" not in info  # missing -> absent, not "" or 0
    assert "industry" not in info


def test_strict_price_returns_none_when_unavailable():
    assert fd.get_stock_price_optional("EMPTY") is None


def test_strict_price_returns_value_when_available():
    class T(_FakeTicker):
        @property
        def info(self):
            return {"currentPrice": 42.5}

    fd.yf.Ticker = T
    assert fd.get_stock_price_optional("ACME") == 42.5


def test_clear_cache_resets_entries():
    fd.get_key_metrics("ACME")
    assert fd.cache_stats()["entries"] >= 1
    fd.clear_cache()
    assert fd.cache_stats()["entries"] == 0


def test_provenance_reports_data_unavailable_for_empty():
    fd.get_company_info("EMPTY")
    assert fd.get_provenance()["get_company_info"]["data_available"] is False
