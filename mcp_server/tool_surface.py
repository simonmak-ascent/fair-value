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
SURFACE_VERSION = "1.0"

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


_ENVELOPE_OUTPUT = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["ok", "error"]},
        "method": {"type": ["string", "null"]},
        "ticker": {"type": ["string", "null"]},
        "error": {
            "type": ["object", "null"],
            "properties": {"code": {"type": "string"}, "message": {"type": "string"}},
        },
    },
    "required": ["status"],
}

_STR = {"type": "string"}
_NUM = {"type": "number"}
_OBJ = {"type": "object"}


TOOL_SURFACE: Tuple[ToolSpec, ...] = (
    ToolSpec(
        name="valuation_dcf",
        title="Discounted cash flow valuation",
        description=(
            "Value a company by discounting projected free cash flows. Supply "
            "explicit inputs, or omit them to derive from current market data."
        ),
        input_schema=_obj(
            {
                "ticker": _STR,
                "revenue": _NUM,
                "growth_rate": _NUM,
                "ebitda_margin": _NUM,
                "capex_pct": _NUM,
                "depreciation_pct": _NUM,
                "nwc_pct": _NUM,
                "tax_rate": _NUM,
                "wacc": _NUM,
                "terminal_growth": _NUM,
                "shares_outstanding": _NUM,
                "net_debt": _NUM,
                "years": {"type": "integer"},
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
        description="Value a holding/asset-rich company by net asset value.",
        input_schema=_obj(
            {
                "ticker": _STR,
                "holdings": {"type": "array", "items": _OBJ},
                "liabilities": _NUM,
                "shares_outstanding": _NUM,
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
        description="Value a company using median peer multiples (P/E, P/B, P/S, EV/EBITDA).",
        input_schema=_obj(
            {
                "ticker": _STR,
                "target_metrics": _OBJ,
                "peer_metrics": {"type": "array", "items": _OBJ},
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
        description="Analyze a spreadsheet, PDF, Word document, or image valuation report.",
        input_schema=_obj({"file_path": _STR}, ["file_path"]),
        output_schema={
            "type": "object",
            "properties": {"status": _STR},
            "required": ["status"],
        },
        handler="valuation_engine.review_report",
        annotations=_annotations(),
    ),
    ToolSpec(
        name="get_valuation_summary",
        title="Valuation summary",
        description="Return company profile, key metrics, price, and volatility for a ticker.",
        input_schema=_obj({"ticker": _STR}, ["ticker"]),
        output_schema=_ENVELOPE_OUTPUT,
        handler="valuation_engine.get_valuation_summary",
        annotations=_annotations(open_world=True),
    ),
    ToolSpec(
        name="calculate_wacc",
        title="Weighted average cost of capital",
        description="Calculate WACC from equity/debt weights and costs.",
        input_schema=_obj(
            {
                "equity_weight": _NUM,
                "debt_weight": _NUM,
                "cost_equity": _NUM,
                "cost_debt": _NUM,
                "tax_rate": _NUM,
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
        description="Compute IFRS/HKFRS 9 expected credit loss = EAD x PD x LGD.",
        input_schema=_obj(
            {
                "exposure_at_default": _NUM,
                "probability_of_default": _NUM,
                "loss_given_default": _NUM,
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
        description="Price a European option with the Black-Scholes-Merton model.",
        input_schema=_obj(
            {
                "spot": _NUM,
                "strike": _NUM,
                "maturity": _NUM,
                "risk_free": _NUM,
                "volatility": _NUM,
                "option_type": {"type": "string", "enum": ["call", "put"]},
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
