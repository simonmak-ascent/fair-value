"""Method dispatch for the registry-driven engine.

``dispatch`` resolves aliases, validates the arguments against the method-spec
registry (rejecting missing and extraneous inputs), calls the handler, and wraps
the outcome in the shared envelope. Expected failures become error envelopes;
handlers never raise to the caller.
"""

from __future__ import annotations

from typing import Any, Dict

from src.output.result import error as _error
from src.output.result import ok as _ok

from . import aliases as al
from . import method_spec as ms
from .handlers import HANDLERS


def is_implemented(tool: str, method: str) -> bool:
    """Whether a handler is registered for ``tool``/``method``."""
    canonical_tool, canonical_method = al.resolve(tool, method)
    return canonical_method is not None and canonical_method in HANDLERS.get(canonical_tool, {})


def dispatch(tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and execute a registry method; always return an envelope."""
    args = dict(arguments or {})
    method = args.pop("method", None)
    if not method:
        return _error("INVALID_ARGUMENT", f"{tool} requires 'method'", method=tool)
    # Transparency: `method="-help"` (or `help=true`) returns the generated docs.
    if method in ("-help", "help") or args.get("help") is True:
        from .docs import tool_help, tool_help_markdown

        return _ok(
            f"{tool}.-help",
            value=None,
            help=tool_help(tool),
            text=tool_help_markdown(tool),
        )
    # Absent optional parameters arrive as explicit ``None`` from the MCP layer;
    # treat them as omitted (the no-defaults contract requires real values only).
    args = {name: value for name, value in args.items() if value is not None}

    canonical_tool, canonical_method = al.resolve(tool, method)
    assert canonical_method is not None  # method is truthy above
    problems = ms.validate_arguments(canonical_tool, canonical_method, args)
    if problems:
        return _error("INVALID_ARGUMENT", "; ".join(problems), method=canonical_tool)

    handler = HANDLERS.get(canonical_tool, {}).get(canonical_method)
    if handler is None:
        return _error(
            "NOT_IMPLEMENTED",
            f"{canonical_tool}.{canonical_method} is not implemented yet",
            method=canonical_tool,
        )

    try:
        value = handler(**args)
    except TypeError as exc:
        return _error(
            "INVALID_ARGUMENT", f"{canonical_tool}.{canonical_method}: {exc}", method=canonical_tool
        )
    except Exception as exc:  # noqa: BLE001 - surfaced as a typed error envelope
        return _error(
            "COMPUTATION_ERROR",
            f"{canonical_tool}.{canonical_method}: {exc}",
            method=canonical_tool,
        )

    spec = ms.get(canonical_tool, canonical_method)
    formula_ref = spec.formula_ref if spec else None
    solution_type = getattr(spec, "solution_type", None) if spec else None
    citations = (
        {key: list(val) for key, val in spec.citations.items()}
        if spec and getattr(spec, "citations", None)
        else None
    )
    name = f"{canonical_tool}.{canonical_method}"

    if isinstance(value, dict) and value.get("status") in ("ok", "error"):
        if value.get("status") == "ok":
            if solution_type:
                value.setdefault("solution_type", solution_type)
            if citations:
                value.setdefault("citations", citations)
        return value
    if isinstance(value, dict):
        payload = dict(value)
        primary = payload.pop("value", None)
        return _ok(
            name,
            value=primary,
            formula_ref=formula_ref,
            solution_type=solution_type,
            citations=citations,
            **payload,
        )
    return _ok(
        name,
        value=value,
        formula_ref=formula_ref,
        solution_type=solution_type,
        citations=citations,
    )
