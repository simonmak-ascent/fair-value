"""Canonical MCP tool surface for fair-value.

The surface is **derived from the method-spec registry**
(:mod:`mcp_server.method_spec`): each registered ``calculate_*`` tool becomes
one MCP tool whose input schema, method enum, per-parameter descriptions, and
required sets come from the registry — never restated by hand. Import is
side-effect free: no ``fastmcp`` import, no network, no handler execution.
"""

from __future__ import annotations

import importlib
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Tuple

SERVER_NAME = "fair-value"
SURFACE_VERSION = "3.0"

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


# Shared result envelope, documented once so descriptions need not restate it.
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
            "description": "Primary result: a number for scalar methods, an object for valuation methods.",
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

# Public alias for reuse by the server when registering tools.
ENVELOPE_OUTPUT = _ENVELOPE_OUTPUT


_BEHAVIOR = (
    "Read-only and deterministic: it performs no network or database I/O, mutates no state, and "
    "returns the same result for the same inputs. Each method "
    "requires its exact inputs (no defaults), so a missing input, an unknown method, or an extra "
    "field returns an error envelope (code INVALID_ARGUMENT) instead of raising. The result "
    "envelope carries status, method, value, assumptions, formula_ref, data_timestamp, steps and error."
)


def _tidy(base: str) -> str:
    """Drop behaviour sentences that :data:`_BEHAVIOR` restates once, centrally."""
    kept = [
        sentence.strip()
        for sentence in base.split(". ")
        if "Read-only" not in sentence and "shared result envelope" not in sentence
    ]
    return ". ".join(s for s in kept if s).strip()


def _build_surface() -> Tuple[ToolSpec, ...]:
    from . import method_spec as ms
    from . import method_spec_seed  # noqa: F401  (registers the tables)

    specs: List[ToolSpec] = []
    for tool in ms.tools():
        meta = ms.tool_meta(tool)
        title = meta.get("title", tool.replace("_", " ").title())
        base = _tidy(meta.get("description", ""))
        matrix = ms.method_matrix_text(tool)
        method_line = f"Methods: {matrix}." if matrix else ""
        description = " ".join(part for part in (base, method_line, _BEHAVIOR) if part).strip()
        specs.append(
            ToolSpec(
                name=tool,
                title=title,
                description=description,
                input_schema=ms.input_schema(tool),
                output_schema=_ENVELOPE_OUTPUT,
                handler=f"engine:{tool}",
                annotations=_annotations(),
            )
        )
    return tuple(specs)


TOOL_SURFACE: Tuple[ToolSpec, ...] = _build_surface()

_BY_NAME: Dict[str, ToolSpec] = {spec.name: spec for spec in TOOL_SURFACE}


def tool_names() -> List[str]:
    """Return the surface tool names in registration order."""
    return [spec.name for spec in TOOL_SURFACE]


def list_tools() -> List[ToolSpec]:
    """Return the surface :class:`ToolSpec` list."""
    return list(TOOL_SURFACE)


def get_tool(name: str) -> ToolSpec:
    """Return the :class:`ToolSpec` for ``name`` (raises ``KeyError`` if absent)."""
    return _BY_NAME[name]


def resolve_handler(spec: ToolSpec) -> Callable[..., Any]:
    """Resolve a spec's handler to a callable.

    ``engine:<tool>`` resolves to the registry dispatcher; any other value is a
    dotted ``module:attr`` import path (kept for compatibility).
    """
    if spec.handler.startswith("engine:"):
        from .engine import dispatch

        tool = spec.handler.split(":", 1)[1]
        return lambda **kwargs: dispatch(tool, kwargs)
    module_name, _, attr = spec.handler.partition(":")
    module = importlib.import_module(module_name)
    return getattr(module, attr)


def validate_surface(surface: "Tuple[ToolSpec, ...] | None" = None) -> List[str]:
    """Return problems with ``surface`` (defaults to :data:`TOOL_SURFACE`)."""
    problems: List[str] = []
    seen = set()
    for spec in TOOL_SURFACE if surface is None else surface:
        if spec.name in seen:
            problems.append(f"duplicate tool: {spec.name}")
        seen.add(spec.name)
        if not _NAME_RE.match(spec.name):
            problems.append(f"invalid tool name: {spec.name}")
        if len(spec.title) <= len(spec.name):
            problems.append(f"{spec.name}: title must be longer than the name")
        if not spec.description:
            problems.append(f"{spec.name}: empty description")
        props = spec.input_schema.get("properties", {})
        if "method" not in props:
            problems.append(f"{spec.name}: input schema missing 'method'")
        for name, prop in props.items():
            if not prop.get("description") and name != "method":
                problems.append(f"{spec.name}.{name}: parameter missing description")
        for key in ("readOnlyHint", "idempotentHint", "destructiveHint", "openWorldHint"):
            if key not in spec.annotations:
                problems.append(f"{spec.name}: annotation {key} missing")
    return problems
