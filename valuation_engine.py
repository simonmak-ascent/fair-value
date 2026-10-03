"""
Main valuation engine - public entry point for all valuation operations.

A-001: this module is a thin facade over the computation modules in ``src/``.
It validates the requested operation, lazily imports the concrete
implementation, delegates, and normalizes the outcome into a shared
result/error envelope. Network access happens only when a valuation is
actually requested, never at import time.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

logger = logging.getLogger(__name__)

_SUPPORTED_SPREADSHEETS = {".xlsx", ".xls"}
_SUPPORTED_PDFS = {".pdf"}
_SUPPORTED_WORDS = {".docx", ".doc"}
_SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}

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
# Data provider seam (monkeypatched in tests so the suite stays offline)
# ---------------------------------------------------------------------------


def _get_market_metrics(ticker: str) -> Dict:
    from src.fetch_data import get_key_metrics

    return get_key_metrics(ticker)


def _get_company_info(ticker: str) -> Dict:
    from src.fetch_data import get_company_info

    return get_company_info(ticker)


def _get_stock_price(ticker: str) -> float:
    from src.fetch_data import get_stock_price

    return get_stock_price(ticker)


def _get_volatility(ticker: str) -> float:
    from src.fetch_data import get_volatility

    return get_volatility(ticker)


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
    """Run a DCF valuation from explicit inputs or current market data."""
    from src.valuation.dcf import dcf_valuation, dcf_from_market_data

    try:
        if params.get("revenue") is not None:
            kwargs = {k: v for k, v in params.items() if k in _DCF_KWARGS}
            result = dcf_valuation(ticker=ticker, **kwargs)
        else:
            metrics = _get_market_metrics(ticker)
            result = dcf_from_market_data(
                ticker,
                metrics,
                wacc=params.get("wacc", 0.10),
                terminal_growth=params.get("terminal_growth", 0.025),
                years=params.get("years", 5),
            )
    except TypeError as exc:
        return _error("MISSING_INPUT", f"Invalid DCF inputs: {exc}", method="DCF", ticker=ticker)
    except Exception as exc:  # data/provider failure
        return _error("DATA_UNAVAILABLE", f"DCF failed: {exc}", method="DCF", ticker=ticker)

    if not result or result.get("error"):
        reason = (result or {}).get("error", "no data available")
        return _error("DATA_UNAVAILABLE", reason, method="DCF", ticker=ticker)

    data_timestamp = None
    if params.get("revenue") is None:
        from src.output.result import utc_now_iso

        data_timestamp = utc_now_iso()

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
        data_timestamp=data_timestamp,
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
        try:
            target_metrics = _get_market_metrics(ticker)
        except Exception as exc:
            return _error("DATA_UNAVAILABLE", f"CCA failed: {exc}", method="CCA", ticker=ticker)

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
# Report review
# ---------------------------------------------------------------------------


def review_report(file_path: str) -> Dict:
    """Dispatch a report file to the analyzer matching its type."""
    if not file_path or not str(file_path).strip():
        return _error("INVALID_ARGUMENT", "file_path is required", method="review")

    path = Path(file_path)
    from src.report_review import guards

    try:
        guards.validate_path(str(path))
    except guards.InputValidationError as exc:
        return _error(exc.code, exc.message, method="review")

    suffix = path.suffix.lower()
    if suffix in _SUPPORTED_SPREADSHEETS or suffix in _SUPPORTED_WORDS:
        macro = guards.detect_macros(str(path))
        if macro.get("has_macros") or macro.get("is_macro_capable"):
            return _error(
                "MACROS_DETECTED",
                "macro-enabled documents are rejected by the report-review guard",
                method="review",
            )
    if suffix in _SUPPORTED_SPREADSHEETS:
        return review_excel(str(path))
    if suffix in _SUPPORTED_PDFS:
        return review_pdf(str(path))
    if suffix in _SUPPORTED_WORDS:
        return review_word(str(path))
    if suffix in _SUPPORTED_IMAGES:
        return review_image(str(path))
    return _error("UNSUPPORTED_FILE_TYPE", f"Unsupported file type: {suffix}", method="review")


def review_excel(file_path: str) -> Dict:
    try:
        from src.report_review import excel_analyzer

        return _with_disclaimer(excel_analyzer.analyze_excel_model(file_path))
    except Exception as exc:
        return _error("DATA_UNAVAILABLE", f"Excel review failed: {exc}", method="review")


def review_pdf(file_path: str) -> Dict:
    try:
        from src.report_review import pdf_analyzer

        return _with_disclaimer(pdf_analyzer.analyze_pdf_report(file_path))
    except Exception as exc:
        return _error("DATA_UNAVAILABLE", f"PDF review failed: {exc}", method="review")


def review_word(file_path: str) -> Dict:
    try:
        from src.report_review import word_analyzer

        return _with_disclaimer(word_analyzer.analyze_word_report(file_path))
    except Exception as exc:
        return _error("DATA_UNAVAILABLE", f"Word review failed: {exc}", method="review")


def review_image(file_path: str) -> Dict:
    try:
        from src.report_review import image_analyzer

        return _with_disclaimer(image_analyzer.extract_valuation_data(file_path))
    except Exception as exc:
        return _error("DATA_UNAVAILABLE", f"Image review failed: {exc}", method="review")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def scan_directory(directory: str = ".") -> List[Dict]:
    """Scan a directory for valuation files.

    Returns a list of ``{path, type, size}`` records. If the directory does
    not exist, returns a single-element list carrying an ``INVALID_ARGUMENT``
    error object (never raises).
    """
    path = Path(directory)
    if not path.exists() or not path.is_dir():
        return [
            {
                "error": {
                    "code": "INVALID_ARGUMENT",
                    "message": f"not a directory: {directory}",
                }
            }
        ]

    from src.constants import SUPPORTED_FILE_TYPES

    patterns: List[str] = []
    for extensions in SUPPORTED_FILE_TYPES.values():
        patterns.extend(extensions)

    found_files: List[Path] = []
    for pattern in patterns:
        found_files.extend(path.glob(f"**/*{pattern}"))

    return [
        {"path": str(f), "type": f.suffix.lower(), "size": f.stat().st_size} for f in found_files
    ]


def get_valuation_summary(ticker: str) -> Dict:
    """Return a company/metrics/price/volatility summary (absent -> None)."""

    def _safe(fn):
        try:
            return fn(ticker)
        except Exception as exc:
            logger.warning("summary fetch failed for %s: %s", ticker, exc)
            return None

    from src.output.result import DISCLAIMER, utc_now_iso

    return {
        "ticker": ticker,
        "status": "ok",
        "company": _safe(_get_company_info),
        "metrics": _safe(_get_market_metrics),
        "price": _safe(_get_stock_price),
        "volatility": _safe(_get_volatility),
        "data_timestamp": utc_now_iso(),
        "data_sources": "Yahoo Finance (yfinance)",
        "disclaimer": DISCLAIMER,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Financial Valuation Engine")
    parser.add_argument("--ticker", help="Stock ticker")
    parser.add_argument("--method", default="dcf", help="Valuation method")
    parser.add_argument("--review", help="Review file path")
    parser.add_argument("--scan", help="Scan directory")

    args = parser.parse_args(argv)

    if not (args.ticker or args.review or args.scan):
        parser.print_help(sys.stderr)
        return 2

    if args.review:
        print(review_report(args.review))
    elif args.scan:
        for f in scan_directory(args.scan):
            print(f)
    else:
        print(run_valuation(args.ticker, args.method))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
