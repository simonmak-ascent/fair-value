"""Canonical MCP tool surface for fair-value (A-003).

Single source of truth for this repo's MCP tool definitions: name, title,
description, input schema, output schema, MCP annotations, and a handler
reference resolvable to a Python callable.

Consumed by the FastMCP server (A-004) and reconciled against the sibling
MCPs (A-005). Deliberately declarative and import-light: no ``fastmcp``
import, no network, and no handler execution at import time.
"""

from __future__ import annotations

import importlib
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

SERVER_NAME = "fair-value"
SURFACE_VERSION = "1.1"

_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True)
class ToolSpec:
    """Immutable definition of one MCP tool."""

    name: str
    title: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    handler: str
    annotations: Dict[str, bool] = field(default_factory=dict)


def _annotations(*, open_world: bool = False) -> Dict[str, bool]:
    return {
        "readOnlyHint": True,
        "idempotentHint": True,
        "destructiveHint": False,
        "openWorldHint": open_world,
    }


def _obj(properties: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


# Shared result envelope (A-006), documented so the description need not
# restate return values (TDQS: Contextual Completeness).
_ENVELOPE_OUTPUT: Dict[str, Any] = {
    "type": "object",
    "description": "Shared result envelope returned by every tool.",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["ok", "error"],
            "description": "'ok' on success, 'error' on failure.",
        },
        "method": {
            "type": ["string", "null"],
            "description": "Method or tool name that produced the result.",
        },
        "ticker": {
            "type": ["string", "null"],
            "description": "Ticker the result pertains to, when applicable.",
        },
        "value": {
            "description": "Primary result: a number for scalar tools, an object for valuation tools.",
        },
        "assumptions": {
            "type": ["object", "null"],
            "description": "Inputs and assumptions used, echoed for traceability.",
        },
        "formula_ref": {
            "type": ["string", "null"],
            "description": "Formula or standards reference for the method.",
        },
        "data_timestamp": {
            "type": ["string", "null"],
            "description": "ISO-8601 UTC timestamp of the underlying data, when fetched.",
        },
        "steps": {
            "type": ["array", "null"],
            "description": "Ordered computation steps, when the method reports them.",
        },
        "error": {
            "type": ["object", "null"],
            "description": "Error detail, present only when status='error'.",
            "properties": {
                "code": {"type": "string", "description": "Stable machine-readable error code."},
                "message": {"type": "string", "description": "Human-readable error message."},
            },
        },
    },
    "required": ["status"],
}

_STR = {"type": "string"}
_NUM = {"type": "number"}
_OBJ = {"type": "object"}

# Public alias for reuse by the server when registering delegated tools.
ENVELOPE_OUTPUT = _ENVELOPE_OUTPUT


def _num(desc: str) -> Dict[str, Any]:
    return {"type": "number", "description": desc}


def _int(desc: str) -> Dict[str, Any]:
    return {"type": "integer", "description": desc}


def _str(desc: str) -> Dict[str, Any]:
    return {"type": "string", "description": desc}


TOOL_SURFACE: Tuple[ToolSpec, ...] = (
    ToolSpec(
        name="valuation_dcf",
        title="Discounted cash flow valuation",
        description=(
            "Value a company by discounting projected free cash flows to present "
            "value. Supply explicit assumptions, or omit them to derive from current "
            "market data. Use this for going-concern cash-flow businesses; for asset-"
            "heavy holding companies use valuation_nav, and for peer-based pricing use "
            "valuation_cca. Returns fair value per share plus the WACC and terminal value."
        ),
        input_schema=_obj(
            {
                "ticker": _str("Equity ticker, e.g. 'AAPL' or '9988.HK'."),
                "revenue": _num("Base-year revenue in the reporting currency."),
                "growth_rate": _num("Annual revenue growth rate as a decimal (e.g. 0.05)."),
                "ebitda_margin": _num("EBITDA as a fraction of revenue (decimal)."),
                "capex_pct": _num("Capital expenditure as a fraction of revenue (decimal)."),
                "depreciation_pct": _num("Depreciation as a fraction of revenue (decimal)."),
                "nwc_pct": _num(
                    "Change in net working capital as a fraction of revenue (decimal)."
                ),
                "tax_rate": _num("Effective corporate tax rate as a decimal."),
                "wacc": _num("Weighted average cost of capital as a decimal."),
                "terminal_growth": _num(
                    "Perpetuity growth rate applied to terminal value (decimal)."
                ),
                "shares_outstanding": _num("Diluted shares outstanding."),
                "net_debt": _num("Total debt minus cash and equivalents."),
                "years": _int("Projection horizon in years (default 5)."),
            },
            ["ticker"],
        ),
        output_schema=_ENVELOPE_OUTPUT,
        handler="valuation_engine.run_dcf",
        annotations=_annotations(open_world=True),
    ),
    ToolSpec(
        name="valuation_nav",
        title="Net asset value valuation",
        description=(
            "Value an asset-heavy or holding company as the sum of its listed and "
            "unlisted holdings less liabilities. Use this when value is asset-based "
            "rather than cash-flow-based; for cash-flow businesses use valuation_dcf. "
            "Returns net asset value and NAV per share."
        ),
        input_schema=_obj(
            {
                "ticker": _str("Holding-company equity ticker."),
                "holdings": {
                    "type": "array",
                    "items": _OBJ,
                    "description": "Holdings to value; each item {ticker, shares, type} where type is 'listed' or 'unlisted'.",
                },
                "liabilities": _num("Total liabilities to deduct from gross asset value."),
                "shares_outstanding": _num("Shares outstanding, used to compute NAV per share."),
            },
            ["ticker"],
        ),
        output_schema=_ENVELOPE_OUTPUT,
        handler="valuation_engine.run_nav",
        annotations=_annotations(open_world=True),
    ),
    ToolSpec(
        name="valuation_cca",
        title="Comparable company analysis",
        description=(
            "Value a company by applying median peer multiples (P/E, P/B, P/S, "
            "EV/EBITDA) to the target's metrics. Use this for market-based pricing when "
            "comparable peers are available; for intrinsic value use valuation_dcf. "
            "Returns an implied value per multiple and an average."
        ),
        input_schema=_obj(
            {
                "ticker": _str("Target equity ticker."),
                "target_metrics": {
                    "type": "object",
                    "description": "Target metrics: eps, book_value_per_share, sales_per_share, ebitda, net_debt.",
                },
                "peer_metrics": {
                    "type": "array",
                    "items": _OBJ,
                    "description": "Peer metrics list; each item {pe_ratio, pb_ratio, ps_ratio, ev_ebitda}.",
                },
            },
            ["ticker"],
        ),
        output_schema=_ENVELOPE_OUTPUT,
        handler="valuation_engine.run_cca",
        annotations=_annotations(open_world=True),
    ),
    ToolSpec(
        name="review_report",
        title="Review a valuation report",
        description=(
            "Analyze an existing valuation report (spreadsheet, PDF, Word document, or "
            "image) and check methodology, formulas, WACC and terminal value, key "
            "assumptions, and data sources. Use this to audit a document rather than to "
            "produce a valuation. Macro-enabled and unsafe files are rejected, and "
            "external-data formulas are flagged. Returns findings plus a review report."
        ),
        input_schema=_obj(
            {
                "file_path": _str(
                    "Path to the report: .xlsx/.xls, .pdf, .docx/.doc, or an image (.png/.jpg/.tif)."
                )
            },
            ["file_path"],
        ),
        output_schema={
            "type": "object",
            "description": "Report analysis; includes status and, on success, the detected file type, findings, and a review report.",
            "properties": {
                "status": _str("'ok' on success, 'error' on failure."),
                "analyzer": _str("Analyzer used: 'excel', 'pdf', 'word', or 'image'."),
                "review_report": _str("Human-readable review summary."),
                "error": _STR,
            },
            "required": ["status"],
        },
        handler="valuation_engine.review_report",
        annotations=_annotations(),
    ),
    ToolSpec(
        name="get_valuation_summary",
        title="Get a company valuation summary",
        description=(
            "Return a company profile with key market metrics (price, market cap, beta, "
            "P/E), price, and historical volatility. Use this to gather inputs for a "
            "valuation or to sanity-check a fair value against the market. Read-only and "
            "fetches live market data."
        ),
        input_schema=_obj({"ticker": _str("Equity ticker to profile.")}, ["ticker"]),
        output_schema=_ENVELOPE_OUTPUT,
        handler="valuation_engine.get_valuation_summary",
        annotations=_annotations(open_world=True),
    ),
    ToolSpec(
        name="calculate_wacc",
        title="Weighted average cost of capital",
        description=(
            "Compute WACC = we*ke + wd*kd*(1 - tax) from capital weights and costs. "
            "Use this when you already have the weights and component costs; to derive "
            "them from market data use get_valuation_summary first. Returns the WACC and "
            "its equity/debt contributions."
        ),
        input_schema=_obj(
            {
                "equity_weight": _num(
                    "Market-value weight of equity (decimals summing to 1 with debt_weight)."
                ),
                "debt_weight": _num(
                    "Market-value weight of debt (decimals summing to 1 with equity_weight)."
                ),
                "cost_equity": _num("Cost of equity as a decimal (e.g. 0.10 for 10%)."),
                "cost_debt": _num("Pre-tax cost of debt as a decimal."),
                "tax_rate": _num("Marginal corporate tax rate as a decimal."),
            },
            ["equity_weight", "debt_weight", "cost_equity", "cost_debt"],
        ),
        output_schema=_ENVELOPE_OUTPUT,
        handler="src.cost_of_capital.wacc.calculate_wacc",
        annotations=_annotations(),
    ),
    ToolSpec(
        name="calculate_ecl",
        title="Expected credit loss",
        description=(
            "Compute IFRS 9 / HKFRS 9 expected credit loss as EAD x PD x LGD. Use this "
            "for a single exposure; for portfolio or staging PD models use the delegated "
            "credit-risk tools. Returns the ECL amount in the exposure's currency."
        ),
        input_schema=_obj(
            {
                "exposure_at_default": _num("Exposure at default (EAD) in currency units."),
                "probability_of_default": _num(
                    "Probability of default over the horizon, as a decimal 0-1."
                ),
                "loss_given_default": _num(
                    "Loss given default as a decimal 0-1 (1 - recovery rate)."
                ),
            },
            ["exposure_at_default", "probability_of_default", "loss_given_default"],
        ),
        output_schema=_ENVELOPE_OUTPUT,
        handler="src.credit_risk.ecl.calculate_ecL",
        annotations=_annotations(),
    ),
    ToolSpec(
        name="black_scholes_price",
        title="Black-Scholes option price",
        description=(
            "Price a European call or put with the Black-Scholes-Merton model. Use this "
            "for a single European option; for swaps, convertible bonds, futures, or "
            "greeks use the delegated derivatives tools. Returns the option price and "
            "the inputs used."
        ),
        input_schema=_obj(
            {
                "spot": _num("Current underlying spot price."),
                "strike": _num("Option strike price."),
                "maturity": _num("Time to expiry in years (e.g. 0.5 for six months)."),
                "risk_free": _num("Continuously-compounded risk-free rate as a decimal."),
                "volatility": _num("Annualized volatility of the underlying as a decimal."),
                "option_type": {
                    "type": "string",
                    "enum": ["call", "put"],
                    "description": "Option type; defaults to 'call' when omitted.",
                },
            },
            ["spot", "strike", "maturity", "risk_free", "volatility"],
        ),
        output_schema=_ENVELOPE_OUTPUT,
        handler="src.derivatives.options.black_scholes_price",
        annotations=_annotations(),
    ),
)


def list_tools() -> List[ToolSpec]:
    """Return all tool specs in the surface."""
    return list(TOOL_SURFACE)


def tool_names() -> List[str]:
    """Return the tool names in defined order."""
    return [t.name for t in TOOL_SURFACE]


def get_tool(name: str) -> ToolSpec:
    """Return the tool spec with ``name``; raise ``KeyError`` if absent."""
    for tool in TOOL_SURFACE:
        if tool.name == name:
            return tool
    raise KeyError(f"unknown tool: {name}")


def validate_surface(specs: Optional[Tuple[ToolSpec, ...]] = None) -> List[str]:
    """Return a list of problems with the surface (empty when valid)."""
    specs = TOOL_SURFACE if specs is None else specs
    problems: List[str] = []
    seen: Dict[str, int] = {}
    for spec in specs:
        if not _NAME_RE.match(spec.name):
            problems.append(f"invalid tool name (not snake_case): {spec.name}")
        seen[spec.name] = seen.get(spec.name, 0) + 1
        for prop_name, prop in (spec.input_schema.get("properties", {}) or {}).items():
            if not prop.get("description"):
                problems.append(f"{spec.name}.{prop_name}: missing parameter description")
    for name, count in seen.items():
        if count > 1:
            problems.append(f"duplicate tool name: {name}")
    return problems


def resolve_handler(spec: ToolSpec) -> Callable[..., Any]:
    """Import and return the callable referenced by ``spec.handler``."""
    module_name, _, attr = spec.handler.rpartition(".")
    if not module_name or not attr:
        raise ImportError(f"invalid handler reference: {spec.handler}")
    module = importlib.import_module(module_name)
    handler = getattr(module, attr)
    if not callable(handler):
        raise ImportError(f"handler is not callable: {spec.handler}")
    return handler
