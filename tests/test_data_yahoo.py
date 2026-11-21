"""Yahoo-only mapping: what `quoteSummary` supplies, what it does not, and the refusals.

The module list here is the one `apdb-etl` requests (`jobs.ts:224-233`), and the field names are the
ones its mappers already read (`yahoo.ts`): `financialData.freeCashflow`, `assetProfile.*`,
`price.*`, `quoteType.*`. `defaultKeyStatistics.beta` is read defensively — when Yahoo omits it the
caller supplies beta instead.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.yahoo import (  # noqa: E402
    YAHOO_MODULES,
    MissingProviderData,
    capm_inputs,
    company_identity,
    dcf_inputs,
    multiples_inputs,
    trailing_free_cash_flow,
)


def summary(**overrides):
    base = {
        "price": {"symbol": "0700.HK", "longName": "Tencent Holdings", "currency": "HKD"},
        "quoteType": {"quoteType": "EQUITY"},
        "assetProfile": {"sector": "Technology", "industry": "Internet Content & Information"},
        "financialData": {"freeCashflow": 190_171_000_000},
        "defaultKeyStatistics": {"beta": 0.747},
    }
    base.update(overrides)
    return base


def test_the_module_contract_is_declared():
    """Every module the accessors read is named, so a caller can request the right set."""
    assert YAHOO_MODULES == ("price", "quoteType", "assetProfile", "financialData",
                             "defaultKeyStatistics")
    for block in YAHOO_MODULES:
        assert isinstance(summary().get(block), dict)


def test_identity_comes_from_price_and_asset_profile():
    ident = company_identity(summary())
    assert ident == {
        "ticker": "0700.HK",
        "name": "Tencent Holdings",
        "currency": "HKD",
        "sector": "Technology",
        "industry": "Internet Content & Information",
        "source": "yahoo",
    }


def test_a_payload_without_a_price_block_still_identifies_by_passed_symbol():
    ident = company_identity({"assetProfile": {"sector": "Technology"}}, symbol="0700.HK")
    assert ident["ticker"] == "0700.HK" and ident["name"] is None


def test_trailing_free_cash_flow_is_read_and_is_named_as_trailing():
    assert trailing_free_cash_flow(summary()) == 190_171_000_000.0
    with pytest.raises(MissingProviderData) as exc:
        trailing_free_cash_flow({"financialData": {}})
    assert exc.value.field == "financialData.freeCashflow"


def test_capm_takes_beta_from_the_payload_and_both_rates_from_the_caller():
    payload = capm_inputs(summary(), risk_free=0.0425, market_return=0.09)
    assert payload == {"method": "capm", "risk_free": 0.0425, "beta": 0.747, "market_return": 0.09}


def test_capm_accepts_beta_when_yahoo_does_not_report_one():
    without = summary(defaultKeyStatistics={})
    payload = capm_inputs(without, risk_free=0.0425, market_return=0.09, beta_value=1.1)
    assert payload["beta"] == 1.1
    with pytest.raises(MissingProviderData):
        capm_inputs(without, risk_free=0.0425, market_return=0.09)
    with pytest.raises(MissingProviderData):
        capm_inputs(None, risk_free=0.0425, market_return=0.09)


def test_dcf_takes_the_callers_projection_not_the_trailing_scalar():
    payload = dcf_inputs([100.0, 110.0, 121.0], discount_rate=0.078)
    assert payload == {"method": "dcf", "cash_flows": [100.0, 110.0, 121.0], "discount_rate": 0.078}


def test_dcf_refuses_empty_flows_and_a_non_positive_rate_as_caller_errors():
    """A bad argument is not missing provider data — a caller catching the latter must not catch it."""
    with pytest.raises(ValueError) as exc:
        dcf_inputs([], discount_rate=0.1)
    assert not isinstance(exc.value, MissingProviderData)
    with pytest.raises(ValueError):
        dcf_inputs([1.0], discount_rate=0.0)


def test_a_non_numeric_or_boolean_amount_is_refused_like_a_missing_one():
    # Yahoo does return "N/A" for these fields; that is the branch that fires in production.
    for bad in ("N/A", True, {}):
        with pytest.raises(MissingProviderData):
            trailing_free_cash_flow({"financialData": {"freeCashflow": bad}})


def test_multiples_refuse_a_non_positive_ebitda_or_multiple():
    with pytest.raises(ValueError):
        multiples_inputs(ebitda=-1.0, ev_ebitda_multiple=12.5)
    with pytest.raises(ValueError):
        multiples_inputs(ebitda=100.0, ev_ebitda_multiple=0.0)


def test_the_capm_path_needs_no_positional_placeholder():
    payload = capm_inputs(risk_free=0.0425, market_return=0.09, beta_value=1.1)
    assert payload["beta"] == 1.1


def test_multiples_payload_matches_the_registry_parameters():
    payload = multiples_inputs(ebitda=297_499_000_832, ev_ebitda_multiple=12.5)
    assert payload == {"method": "ev_ebitda", "ebitda": 297_499_000_832, "ev_ebitda_multiple": 12.5}


def test_every_payload_dispatches_without_an_argument_error():
    """The registry rejects missing *and* extraneous arguments, so the shapes are proved by dispatch."""
    from src.mcp.engine import dispatch

    for payload in (
        capm_inputs(summary(), risk_free=0.0425, market_return=0.09),
        dcf_inputs([100.0, 110.0], discount_rate=0.078),
        multiples_inputs(ebitda=297_499_000_832, ev_ebitda_multiple=12.5),
    ):
        result = dispatch(
            {
                "capm": "calculate_discount_rate",
                "dcf": "calculate_dcf",
                "ev_ebitda": "calculate_market_multiple",
            }[payload["method"]],
            payload,
        )
        assert result["status"] == "ok", (payload, result)
