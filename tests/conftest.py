"""Shared fixtures for the engine wiring tests (A-001).

Every fixture keeps the suite offline. The engine performs no network or
database I/O, so inputs are supplied explicitly.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


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
