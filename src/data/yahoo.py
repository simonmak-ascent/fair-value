"""Map Yahoo Finance `quoteSummary` payloads onto valuation method inputs. No I/O, no credentials.

`apdb-etl` is the estate's Yahoo ingester (`yahoo-finance2`), and it requests
exactly these modules: `assetProfile`, `summaryDetail`, `price`, `quoteType`, `financialData`,
`defaultKeyStatistics`, `calendarEvents`, `majorHoldersBreakdown`. This module reads the subset that
feeds a valuation and refuses anything absent.

**What Yahoo can and cannot supply.** `financialData.freeCashflow` is a trailing-twelve-month scalar,
not a series, and the statement modules are not requested because `yahoo-finance2`'s own guidance is
that quote-summary statement modules "provide little data" since late 2024. So Yahoo contributes:

* identity — ticker, name, currency, sector, industry;
* a trailing free cash flow and a beta, when present.

It does **not** contribute a projected cash-flow series, an EBITDA, a peer multiple, a risk-free rate
or an equity risk premium. Those are the caller's, and inventing them here is how a plausible number
acquires a citation it did not earn.

A missing field raises `MissingProviderData`; nothing is defaulted.

Only the modules named in `YAHOO_MODULES` are read. A field this module wants from a module nobody
requested would silently be absent at runtime, so the list is part of the contract with the caller.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

#: The `quoteSummary` modules this module reads. `apdb-etl` requests these plus `summaryDetail`,
#: `calendarEvents` and `majorHoldersBreakdown`; a caller fetching its own payload must request at
#: least these five, or the accessor that reads a missing module raises `MissingProviderData`
#: (`company_identity` is the exception — an absent label comes back as `None`).
YAHOO_MODULES: tuple[str, ...] = (
    "price",
    "quoteType",
    "assetProfile",
    "financialData",
    "defaultKeyStatistics",
)


class MissingProviderData(ValueError):
    """A field the method needs is absent from the provider payload."""

    def __init__(self, field: str, source: str = "yahoo", ticker: str = "") -> None:
        where = f" for {ticker}" if ticker else ""
        super().__init__(f"{source} payload{where} has no {field}")
        self.field = field
        self.source = source
        self.ticker = ticker


def _section(summary: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    value = summary.get(name)
    return value if isinstance(value, Mapping) else {}


def _num(section: Mapping[str, Any], field: str, where: str, ticker: str = "") -> float:
    value = section.get(field)
    if value is None or isinstance(value, bool):
        raise MissingProviderData(f"{where}.{field}", "yahoo", ticker)
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise MissingProviderData(f"{where}.{field}", "yahoo", ticker) from exc


def _symbol(summary: Mapping[str, Any]) -> str:
    price = _section(summary, "price")
    return str(price.get("symbol") or summary.get("symbol") or "")


def company_identity(summary: Mapping[str, Any], *, symbol: str = "") -> dict[str, Any]:
    """Who the company is and what currency it reports in — to label a result, never to compute."""
    price = _section(summary, "price")
    profile = _section(summary, "assetProfile")
    quote_type = _section(summary, "quoteType")
    return {
        "ticker": symbol or _symbol(summary) or None,
        "name": price.get("longName") or price.get("shortName") or quote_type.get("longName"),
        "currency": price.get("currency"),
        "sector": profile.get("sector"),
        "industry": profile.get("industry"),
        "source": "yahoo",
    }


def trailing_free_cash_flow(summary: Mapping[str, Any], *, symbol: str = "") -> float:
    """`financialData.freeCashflow` — a trailing-twelve-month figure, not a forecast.

    Named `trailing_` because putting it straight into a DCF values a company by its last twelve
    months. A forward valuation needs the caller's projection.
    """
    return _num(
        _section(summary, "financialData"),
        "freeCashflow",
        "financialData",
        symbol or _symbol(summary),
    )


def beta(summary: Mapping[str, Any], *, symbol: str = "") -> float:
    """`defaultKeyStatistics.beta`, when Yahoo reports one.

    Frequently absent for Hong Kong and small-cap listings, so `capm_inputs(..., beta_value=...)` is
    the ordinary path rather than a fallback. Nothing in this estate maps this field today: `apdb-etl`
    requests the module but stores EODHD's `Technicals.Beta` as `beta`.
    """
    return _num(
        _section(summary, "defaultKeyStatistics"),
        "beta",
        "defaultKeyStatistics",
        symbol or _symbol(summary),
    )


def capm_inputs(
    summary: Mapping[str, Any] | None = None,
    *,
    risk_free: float,
    market_return: float,
    beta_value: float | None = None,
    symbol: str = "",
) -> dict[str, Any]:
    """`calculate_discount_rate(method="capm")` inputs.

    Beta comes from the payload when it is there and may be supplied explicitly otherwise. The two
    rates are always the caller's: Yahoo carries no risk-free curve and no equity risk premium, and a
    plausible default would be invented data inside a published number.
    """
    found = beta_value
    if found is None:
        if summary is None:
            raise MissingProviderData("defaultKeyStatistics.beta (or beta_value=)", "yahoo", symbol)
        found = beta(summary, symbol=symbol)
    return {
        "method": "capm",
        "risk_free": float(risk_free),
        "beta": float(found),
        "market_return": float(market_return),
    }


def dcf_inputs(
    cash_flows: Sequence[float],
    *,
    discount_rate: float,
    symbol: str = "",
) -> dict[str, Any]:
    """`calculate_dcf(method="dcf")` inputs from the caller's projected cash flows.

    Not fed from the payload: `financialData.freeCashflow` is one trailing scalar, and a DCF over
    history returns the present value of the past while the envelope cites "PV of projected FCFF".
    """
    # A caller argument is not provider data: raising MissingProviderData here would tell a caller
    # that Yahoo omitted something the caller itself supplied.
    if not cash_flows:
        raise ValueError(f"cash_flows is empty{' for ' + symbol if symbol else ''}")
    if not discount_rate > 0.0:
        raise ValueError(f"discount_rate must be positive, got {discount_rate!r}")
    return {
        "method": "dcf",
        "cash_flows": [float(c) for c in cash_flows],
        "discount_rate": float(discount_rate),
    }


def multiples_inputs(*, ebitda: float, ev_ebitda_multiple: float) -> dict[str, Any]:
    """`calculate_market_multiple(method="ev_ebitda")` inputs.

    Both are the caller's: Yahoo's requested modules carry no EBITDA, and the registry's `ev_ebitda`
    takes exactly `ebitda` and `ev_ebitda_multiple`, rejecting anything else.
    """
    # Same guard as `dcf_inputs`: a negative EBITDA through a bare multiply returns `status: ok` with
    # a negative enterprise value and an attached citation.
    if float(ebitda) <= 0.0:
        raise ValueError(f"ebitda must be positive, got {ebitda!r}")
    if float(ev_ebitda_multiple) <= 0.0:
        raise ValueError(f"ev_ebitda_multiple must be positive, got {ev_ebitda_multiple!r}")
    return {
        "method": "ev_ebitda",
        "ebitda": float(ebitda),
        "ev_ebitda_multiple": float(ev_ebitda_multiple),
    }
