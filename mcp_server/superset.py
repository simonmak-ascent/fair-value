"""Superset coverage and canonical mapping (A-005).

The strict-superset promise is enforced here: every tool the sibling MCPs
expose must resolve to either a native tool of this repo or a delegated
sibling tool. Chosen strategy: ``delegate`` — call each sibling's pure
``tool_surface.call_tool(name, arguments)`` dispatcher and wrap the result in
the shared A-006 envelope (rather than mounting their FastMCP servers, which
would couple us to their FastMCP major version).
"""

from __future__ import annotations

import importlib
import importlib.util
from typing import Any, Callable, Dict, List, Optional, Tuple, cast

from .superset_baseline import (
    INTANGIBLE_TOOLS,
    STARTUP_TOOLS,
    UNION_TOOLS,
)

STRATEGY = "delegate"

# Optional extras that provide the sibling surfaces.
SUPERSET_DEPENDENCIES = (
    "intangible-valuation-mcp>=2.1.2",
    "startup-valuation>=2.1.2",
)

# owner -> import path of the pure ``call_tool`` dispatcher.
SIBLING_CALL_TOOL_PATHS: Dict[str, Tuple[str, str]] = {
    "startup-valuation": ("startup_valuation.mcp.tool_surface", "call_tool"),
    # intangible-valuation-mcp ships top-level modules (server/tool_surface).
    "intangible-valuation": ("tool_surface", "call_tool"),
}

_INTANGIBLE_SET = set(INTANGIBLE_TOOLS)
_STARTUP_SET = set(STARTUP_TOOLS)

# Names provided by more than one sibling -> single canonical owner.
OVERLAPS: Dict[str, str] = {
    name: "intangible-valuation" for name in (_INTANGIBLE_SET & _STARTUP_SET)
}

_OWNERS = {
    "intangible-valuation": _INTANGIBLE_SET,
    "startup-valuation": _STARTUP_SET,
}

try:  # native tools defined by this repo
    from .tool_surface import tool_names as _tool_names

    _NATIVE = set(_tool_names())
except Exception:  # pragma: no cover
    _NATIVE = set()


def _resolution(name: str) -> str:
    if name in _NATIVE:
        return f"native:{name}"
    if name in OVERLAPS:
        return f"delegate:{OVERLAPS[name]}:{name}"
    for owner, tools in _OWNERS.items():
        if name in tools:
            return f"delegate:{owner}:{name}"
    return ""


CANONICAL_MAP: Dict[str, str] = {name: _resolution(name) for name in UNION_TOOLS}


def coverage_for(names, mapping: Dict[str, str]) -> Dict[str, Any]:
    """Return coverage of ``names`` against ``mapping`` (pure)."""
    resolved = {n: mapping.get(n, "") for n in names}
    native = [n for n, r in resolved.items() if r.startswith("native:")]
    delegated = [n for n, r in resolved.items() if r.startswith("delegate:")]
    missing = [n for n, r in resolved.items() if not r]
    return {
        "total": len(names),
        "native": native,
        "delegated": delegated,
        "missing": missing,
    }


def coverage() -> Dict[str, Any]:
    """Coverage of the sibling baseline by this repo's superset."""
    return coverage_for(UNION_TOOLS, CANONICAL_MAP)


def missing_tools() -> List[str]:
    """Baseline tools that are neither native nor delegated."""
    return coverage()["missing"]


def sibling_available(owner: str) -> bool:
    """Whether the sibling dispatcher for ``owner`` is importable."""
    path = SIBLING_CALL_TOOL_PATHS.get(owner)
    if not path:
        return False
    try:
        return importlib.util.find_spec(path[0]) is not None
    except (ImportError, ValueError):
        return False


def sibling_call_tool(owner: str) -> Callable[..., Dict[str, Any]]:
    """Import and return the sibling's pure ``call_tool`` dispatcher."""
    module_name, func_name = SIBLING_CALL_TOOL_PATHS[owner]
    module = importlib.import_module(module_name)
    return getattr(module, func_name)


def delegate_call(
    owner: str,
    name: str,
    arguments: Optional[Dict[str, Any]] = None,
    *,
    call_tool: Optional[Callable[..., Any]] = None,
) -> Dict[str, Any]:
    """Delegate a baseline tool to a sibling, wrapped in the A-006 envelope.

    ``call_tool`` may be injected for tests; otherwise the sibling dispatcher
    is imported (raising if the extra is not installed).
    """
    from src.output.result import error as _error

    try:
        dispatcher = call_tool if call_tool is not None else sibling_call_tool(owner)
        result = dispatcher(name, dict(arguments or {}))
    except Exception as exc:
        return _error("DATA_UNAVAILABLE", f"{owner}:{name} failed: {exc}", method=name)

    from src.output.result import ok as _ok

    return _ok(name, value=cast(Any, result), formula_ref=f"{owner}:{name}")
