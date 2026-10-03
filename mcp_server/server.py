"""FastMCP server rendering the tool surface (A-004).

Builds a FastMCP server from :mod:`mcp_server.tool_surface` (the single source
of truth), adapts flat MCP arguments to the engine's ``(ticker, params)``
signature, and returns the shared A-006 result envelope.

Import is side-effect free and does not require ``fastmcp`` to be installed;
``build_server`` raises a clear error if it is missing.
"""

from __future__ import annotations

import argparse
import inspect
from typing import Any, Callable, Dict, List, Optional

from .tool_surface import (
    SERVER_NAME,
    TOOL_SURFACE,
    ToolSpec,
    resolve_handler,
    tool_names,
)

try:  # optional dependency (the ``[mcp]`` extra)
    from fastmcp import FastMCP

    FASTMCP_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised when extra is absent
    FastMCP = None  # type: ignore[assignment,misc]
    FASTMCP_AVAILABLE = False


_ENGINE_PARAM_TOOLS = {"valuation_dcf", "valuation_nav", "valuation_cca"}
_ENGINE_KWARG_TOOLS = {"review_report", "get_valuation_summary"}


def _invoke(spec: ToolSpec, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch one tool call by family, always returning a dict.

    Engine tools keep their own envelope; direct ``src`` functions are wrapped
    in an A-006 success envelope. Expected failures become error envelopes and
    never raise.
    """
    from src.output.result import error as _error

    handler = resolve_handler(spec)
    args = dict(arguments or {})

    try:
        if spec.name in _ENGINE_PARAM_TOOLS:
            ticker = args.pop("ticker", None)
            return handler(ticker, args)
        if spec.name in _ENGINE_KWARG_TOOLS:
            return handler(**args)

        # direct src function -> wrap scalar/dict in the shared envelope
        from src.output.result import ok as _ok

        value = handler(**args)
        return _ok(spec.name, value=value, formula_ref=spec.handler)
    except TypeError as exc:
        return _error(
            "INVALID_ARGUMENT",
            f"invalid arguments for {spec.name}: {exc}",
            method=spec.name,
        )
    except Exception as exc:
        return _error("DATA_UNAVAILABLE", f"{spec.name} failed: {exc}", method=spec.name)


def _make_tool(spec: ToolSpec) -> Callable[..., Dict[str, Any]]:
    """Build a tool with an explicit signature derived from the input schema.

    FastMCP rejects ``**kwargs`` functions, so we attach an explicit
    ``__signature__`` (keyword-only params from ``input_schema``) to a thin
    dispatcher.
    """
    props = spec.input_schema.get("properties", {}) or {}
    required = set(spec.input_schema.get("required", []) or [])
    parameters = [
        inspect.Parameter(
            name,
            inspect.Parameter.KEYWORD_ONLY,
            default=inspect.Parameter.empty if name in required else None,
        )
        for name in props
    ]

    def tool(**kwargs: Any) -> Dict[str, Any]:
        return _invoke(spec, kwargs)

    tool.__name__ = spec.name
    tool.__doc__ = spec.description
    tool.__signature__ = inspect.Signature(parameters)  # type: ignore[attr-defined]
    return tool


def _make_delegated_tool(name: str, owner: str) -> Callable[..., Dict[str, Any]]:
    """Build a tool that delegates a baseline tool to a sibling (A-005)."""
    from .superset import delegate_call

    def tool(arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return delegate_call(owner, name, arguments or {})

    tool.__name__ = name
    tool.__doc__ = f"Superset tool delegated to {owner} (A-005)."
    tool.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
        [
            inspect.Parameter(
                "arguments",
                inspect.Parameter.KEYWORD_ONLY,
                default=None,
                annotation=Optional[Dict[str, Any]],
            )
        ]
    )
    return tool


def register_delegated_tools(server: Any) -> List[str]:
    """Register one delegated tool per non-native baseline tool (A-005).

    Makes the live server a strict superset: native tools plus every sibling
    tool, delegated to the sibling's ``call_tool``. Returns the names added.
    """
    from .superset import CANONICAL_MAP

    native = set(tool_names())
    registered: List[str] = []
    for name, resolution in CANONICAL_MAP.items():
        if name in native or not resolution.startswith("delegate:"):
            continue
        owner = resolution.split(":", 2)[1]
        fn = _make_delegated_tool(name, owner)
        try:
            server.tool(name=name, description=fn.__doc__)(fn)
        except TypeError:  # older FastMCP signature
            server.add_tool(fn, name=name, description=fn.__doc__)
        registered.append(name)
    return registered


def build_server() -> Any:
    """Build a FastMCP server with one tool per :data:`TOOL_SURFACE` entry."""
    if not FASTMCP_AVAILABLE:
        raise RuntimeError(
            "fastmcp is not installed; install the 'mcp' extra: pip install 'fair-value[mcp]'"
        )

    server: Any = FastMCP(SERVER_NAME)  # type: ignore[misc]
    for spec in TOOL_SURFACE:
        fn = _make_tool(spec)
        try:
            server.tool(name=spec.name, description=spec.description)(fn)
        except TypeError:  # older FastMCP signature
            server.add_tool(fn, name=spec.name, description=spec.description)
    register_delegated_tools(server)
    return server


def main(argv: Optional[List[str]] = None) -> int:
    """Run the MCP server: stdio by default, Streamable HTTP with ``--http``."""
    parser = argparse.ArgumentParser(description="fair-value MCP server")
    parser.add_argument(
        "--http", action="store_true", help="serve Streamable HTTP instead of stdio"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    server = build_server()
    if args.http:
        server.run(transport="http", host=args.host, port=args.port)
    else:
        server.run()
    return 0


__all__ = [
    "build_server",
    "register_delegated_tools",
    "main",
    "tool_names",
    "FASTMCP_AVAILABLE",
]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
