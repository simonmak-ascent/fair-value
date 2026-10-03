"""A-013: machine-readable valuation method catalog (MCP resource).

Served as the MCP resource ``valuation://methods`` so agents can discover the
methods, formula references, and standards each tool implements without
guessing from prose.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from .tool_surface import SERVER_NAME, SURFACE_VERSION, TOOL_SURFACE

# Per-tool method metadata: method name, formula reference, governing standards.
_METHOD_META: Dict[str, Dict[str, Any]] = {
    "valuation_dcf": {
        "method": "DCF",
        "formula_ref": "IVS 105 income approach; PV of projected FCFF",
        "standards": ["IVS 2025", "IFRS 13"],
    },
    "valuation_nav": {
        "method": "NAV",
        "formula_ref": "IVS 105 asset-based approach; assets - liabilities",
        "standards": ["IVS 2025"],
    },
    "valuation_cca": {
        "method": "CCA",
        "formula_ref": "IVS 105 market approach; median peer multiples",
        "standards": ["IVS 2025", "IFRS 13"],
    },
    "review_report": {
        "method": "Review",
        "formula_ref": "IVS 2025 review; methodology + assumption checks",
        "standards": ["IVS 2025", "IFRS 13"],
    },
    "get_valuation_summary": {
        "method": "Profile",
        "formula_ref": "n/a (market data)",
        "standards": [],
    },
    "calculate_wacc": {
        "method": "WACC",
        "formula_ref": "WACC = we*ke + wd*kd*(1 - tax)",
        "standards": ["IVS 2025"],
    },
    "calculate_ecl": {
        "method": "ECL",
        "formula_ref": "ECL = EAD x PD x LGD",
        "standards": ["IFRS 9", "HKFRS 9"],
    },
    "black_scholes_price": {
        "method": "Black-Scholes",
        "formula_ref": "Black-Scholes-Merton European option price",
        "standards": ["IFRS 13"],
    },
}


def build_catalog() -> Dict[str, Any]:
    """Return the machine-readable method catalog for the whole tool surface."""
    tools: List[Dict[str, Any]] = []
    for spec in TOOL_SURFACE:
        meta = _METHOD_META.get(spec.name, {})
        tools.append(
            {
                "name": spec.name,
                "title": spec.title,
                "description": spec.description,
                "method": meta.get("method"),
                "formula_ref": meta.get("formula_ref"),
                "standards": meta.get("standards", []),
                "handler": spec.handler,
                "read_only": spec.annotations.get("readOnlyHint", True),
                "open_world": spec.annotations.get("openWorldHint", False),
                "input_schema": spec.input_schema,
            }
        )
    return {
        "server": SERVER_NAME,
        "surface_version": SURFACE_VERSION,
        "tool_count": len(TOOL_SURFACE),
        "tools": tools,
    }


def catalog_json() -> str:
    """Return :func:`build_catalog` serialized as deterministic JSON."""
    return json.dumps(build_catalog(), indent=2, sort_keys=True)
