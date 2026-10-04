"""
Main valuation engine - public entry point for all valuation operations.

A-001: this module is a thin facade over the computation modules in ``src/``.
It validates the requested operation, lazily imports the concrete
implementation, delegates, and normalizes the outcome into a shared
result/error envelope. It performs no network or database I/O: every input is
supplied explicitly by the caller (market-data acquisition belongs to apdb-etl).
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Method-specific kwargs accepted from ``params`` (keeps unknown keys out of
# the delegated calls).
_DCF_KWARGS = {
    "revenue",
    "growth_rate",
    "ebitda_margin",
    "capex_pct",
    "depreciation_pct",
    "nwc_pct",
    "tax_rate",
    "wacc",
    "terminal_growth",
    "shares_outstanding",
    "net_debt",
    "years",
    "terminal_method",
}


# ---------------------------------------------------------------------------
# Result envelope
# ---------------------------------------------------------------------------


def _ok(method: str, ticker: Optional[str] = None, **fields) -> Dict:
    """Build a success envelope via the shared envelope module (A-006)."""
    from src.output.result import ok as _envelope_ok

    fields.setdefault("value", fields.get("value_per_share"))
    return _envelope_ok(method, ticker, **fields)


def _error(
    code: str,
    message: object,
    method: Optional[str] = None,
    ticker: Optional[str] = None,
) -> Dict:
    """Build an error envelope via the shared envelope module (A-006)."""
    from src.output.result import error as _envelope_error

    return _envelope_error(code, message, method=method, ticker=ticker)


def _with_disclaimer(result: Dict) -> Dict:
    """Attach the not-advice disclaimer to an analyzer result (A-006)."""
    from src.output.result import DISCLAIMER

    if isinstance(result, dict):
        out = dict(result)
        out.setdefault("status", "ok")
        out["disclaimer"] = DISCLAIMER
        return out
    return result


# ---------------------------------------------------------------------------
# Valuation entry points
# ---------------------------------------------------------------------------


def run_valuation(ticker: str, method: str, params: Optional[Dict] = None) -> Dict:
    """Main entry point for running valuations ('dcf', 'nav', 'cca')."""
    params = params or {}

    if not ticker or not str(ticker).strip():
        return _error("INVALID_ARGUMENT", "ticker is required", method=method)

    normalized = (method or "").lower().strip()
    if normalized == "dcf":
        return run_dcf(ticker, params)
    if normalized == "nav":
        return run_nav(ticker, params)
    if normalized == "cca":
        return run_cca(ticker, params)
    return _error("UNKNOWN_METHOD", f"Unknown method: {method}", method=method, ticker=ticker)


def run_dcf(ticker: str, params: Dict) -> Dict:
    """Run a DCF valuation from explicit inputs (no market-data fetch)."""
    from src.valuation.dcf import dcf_valuation

    if params.get("revenue") is None:
        return _error(
            "MISSING_INPUT",
            "DCF requires explicit inputs (at least 'revenue')",
            method="DCF",
            ticker=ticker,
        )
    try:
        kwargs = {k: v for k, v in params.items() if k in _DCF_KWARGS}
        result = dcf_valuation(ticker=ticker, **kwargs)
    except TypeError as exc:
        return _error("MISSING_INPUT", f"Invalid DCF inputs: {exc}", method="DCF", ticker=ticker)
    except Exception as exc:
        return _error("COMPUTATION_ERROR", f"DCF failed: {exc}", method="DCF", ticker=ticker)

    if not result or result.get("error"):
        reason = (result or {}).get("error", "no data available")
        return _error("DATA_UNAVAILABLE", reason, method="DCF", ticker=ticker)

    return _ok(
        "DCF",
        ticker,
        value_per_share=result.get("value_per_share"),
        enterprise_value=result.get("enterprise_value"),
        equity_value=result.get("equity_value"),
        assumptions={
            "wacc": result.get("wacc"),
            "terminal_growth": result.get("terminal_growth"),
        },
        formula_ref="DCF (Gordon/exit-multiple terminal value)",
        steps=["project FCF", "discount", "terminal value", "bridge to equity"],
    )


def run_nav(ticker: str, params: Dict) -> Dict:
    """Run a NAV valuation from holdings or explicit asset inputs."""
    from src.valuation.nav import (
        calculate_nav,
        calculate_nav_per_share,
        nav_from_holdings,
    )

    holdings = params.get("holdings")
    if holdings is not None:
        if len(holdings) == 0:
            return _error(
                "MISSING_INPUT",
                "NAV requires at least one holding",
                method="NAV",
                ticker=ticker,
            )
        try:
            result = nav_from_holdings(
                ticker,
                holdings,
                liabilities=params.get("liabilities", 0),
                shares_outstanding=params.get("shares_outstanding", 1),
                listed_prices=params.get("listed_prices"),
            )
        except Exception as exc:
            return _error("DATA_UNAVAILABLE", f"NAV failed: {exc}", method="NAV", ticker=ticker)
        nav_per_share = result.get("nav_per_share")
        return _ok("NAV", ticker, nav_per_share=nav_per_share, value_per_share=nav_per_share)

    has_assets = (
        params.get("listed_securities") is not None or params.get("unlisted_assets") is not None
    )
    if has_assets:
        if not params.get("listed_securities") and not params.get("unlisted_assets"):
            return _error(
                "MISSING_INPUT",
                "NAV requires at least one asset",
                method="NAV",
                ticker=ticker,
            )
        try:
            nav = calculate_nav(
                listed_securities=params.get("listed_securities", {}),
                unlisted_assets=params.get("unlisted_assets", []),
                receivables=params.get("receivables", 0),
                aging=params.get("aging", {"current": 1.0}),
                pd_by_age=params.get("pd_by_age", {"current": 0.005}),
                total_liabilities=params.get("total_liabilities", 0),
                minority_interest=params.get("minority_interest", 0),
                minority_discount=params.get("minority_discount", 0.0),
                listed_prices=params.get("listed_prices"),
            )
            per_share = calculate_nav_per_share(nav, params.get("shares_outstanding", 1))
        except Exception as exc:
            return _error("DATA_UNAVAILABLE", f"NAV failed: {exc}", method="NAV", ticker=ticker)
        return _ok(
            "NAV",
            ticker,
            nav_per_share=per_share.get("nav_per_share"),
            value_per_share=per_share.get("nav_per_share"),
        )

    return _error(
        "MISSING_INPUT",
        "NAV requires 'holdings' or asset inputs",
        method="NAV",
        ticker=ticker,
    )


def run_cca(ticker: str, params: Dict) -> Dict:
    """Run a Comparable Company Analysis."""
    from src.valuation.multiples import cca_valuation

    target_metrics = params.get("target_metrics")
    peer_metrics = params.get("peer_metrics")

    if target_metrics is None:
        return _error(
            "MISSING_INPUT",
            "CCA requires explicit 'target_metrics' (no market-data fetch)",
            method="CCA",
            ticker=ticker,
        )

    if peer_metrics is not None and len(peer_metrics) == 0:
        return _error("DATA_UNAVAILABLE", "no peer data available", method="CCA", ticker=ticker)

    try:
        if peer_metrics is None:
            result = cca_valuation(ticker, target_metrics)
        else:
            result = cca_valuation(ticker, target_metrics, peer_metrics)
    except Exception as exc:
        return _error("DATA_UNAVAILABLE", f"CCA failed: {exc}", method="CCA", ticker=ticker)

    valuations = (result or {}).get("valuations") or {}
    implied = valuations.get("average_valuation")
    if not valuations or not implied:
        return _error(
            "DATA_UNAVAILABLE",
            "no peer multiples available",
            method="CCA",
            ticker=ticker,
        )

    from src.output.result import utc_now_iso

    return _ok(
        "CCA",
        ticker,
        implied_value=implied,
        value_per_share=implied,
        assumptions={"n_peers": result.get("n_peers")},
        formula_ref="CCA (median peer multiples)",
        data_timestamp=utc_now_iso(),
        steps=["collect peers", "median multiples", "apply to target"],
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Financial Valuation Engine")
    parser.add_argument("--ticker", help="Stock ticker")
    parser.add_argument("--method", default="dcf", help="Valuation method")

    args = parser.parse_args(argv)

    if not args.ticker:
        parser.print_help(sys.stderr)
        return 2

    print(run_valuation(args.ticker, args.method))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
