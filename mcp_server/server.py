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


def _py_type(prop: Dict[str, Any]) -> Any:
    """Map a JSON-schema property to a Python type for the function signature."""
    enum = prop.get("enum")
    if enum:
        from typing import Literal

        return Literal[tuple(enum)]  # type: ignore[valid-type]
    schema_type = prop.get("type")
    if isinstance(schema_type, list):
        schema_type = next((t for t in schema_type if t != "null"), "string")
    elif not isinstance(schema_type, str):
        schema_type = "string"
    mapping: Dict[str, Any] = {
        "number": float,
        "integer": int,
        "string": str,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    return mapping.get(schema_type, Any)


def _annotated_param(name: str, prop: Dict[str, Any], required: bool) -> inspect.Parameter:
    """Build a keyword-only parameter carrying its schema description (TDQS)."""
    from typing import Annotated

    from pydantic import Field

    base = _py_type(prop)
    description = prop.get("description")
    if required:
        annotation = Annotated[base, Field(description=description)] if description else base
        return inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY, annotation=annotation)
    optional_base = Optional[base]  # type: ignore[valid-type]
    annotation = (
        Annotated[optional_base, Field(description=description)] if description else optional_base
    )
    return inspect.Parameter(
        name, inspect.Parameter.KEYWORD_ONLY, default=None, annotation=annotation
    )


def _make_tool(spec: ToolSpec) -> Callable[..., Dict[str, Any]]:
    """Build a tool with an explicit signature derived from the input schema.

    FastMCP rejects ``**kwargs`` functions, so we attach an explicit
    ``__signature__`` (keyword-only params from ``input_schema``) to a thin
    dispatcher. Each parameter carries its JSON-schema ``description`` via
    ``Annotated[..., Field(...)]`` so per-parameter documentation survives
    into ``tools/list`` (TDQS: schema description coverage).
    """
    props = spec.input_schema.get("properties", {}) or {}
    required = set(spec.input_schema.get("required", []) or [])
    parameters = [_annotated_param(name, prop, name in required) for name, prop in props.items()]

    def tool(**kwargs: Any) -> Dict[str, Any]:
        return _invoke(spec, kwargs)

    signature = inspect.Signature(parameters)
    tool.__name__ = spec.name
    tool.__doc__ = spec.description
    tool.__signature__ = signature  # type: ignore[attr-defined]
    # FastMCP reads type hints as well as the signature; supply both.
    tool.__annotations__ = {p.name: p.annotation for p in parameters}
    tool.__annotations__["return"] = Dict[str, Any]
    return tool


_DELEGATED_ANNOTATIONS = {
    "readOnlyHint": True,
    "idempotentHint": True,
    "destructiveHint": False,
    "openWorldHint": False,
}


def _delegated_title(name: str) -> str:
    return name.replace("_", " ").strip().title()


def _make_delegated_tool(name: str, owner: str) -> Callable[..., Dict[str, Any]]:
    """Build a tool that delegates a baseline tool to a sibling (A-005)."""
    from typing import Annotated

    from pydantic import Field

    from .superset import delegate_call

    human_owner = owner.replace("-", " ")
    title = _delegated_title(name)

    def tool(arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return delegate_call(owner, name, arguments or {})

    tool.__name__ = name
    tool.__doc__ = (
        f"{title} ({name}) — a {human_owner} valuation capability, exposed through "
        f"this server so one endpoint covers corporate, startup, and intangible "
        f"valuation. Use it only for the {human_owner} '{name}' case that the native "
        f"tools do not handle; prefer the native tool (valuation_dcf, valuation_nav, "
        f"valuation_cca, calculate_wacc, calculate_ecl, or black_scholes_price) "
        f"whenever it applies. Read-only, deterministic computation: no external "
        f"calls and no authentication required. Pass an 'arguments' object matching "
        f"that tool's schema; unsupported fields return an error envelope rather than "
        f"raising. Returns the shared result envelope."
    )
    arg_annotation: Any = Annotated[
        Optional[Dict[str, Any]],
        Field(
            description=(
                f"Arguments forwarded to {human_owner} '{name}'; see that "
                "tool's schema for supported fields."
            )
        ),
    ]
    tool.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
        [
            inspect.Parameter(
                "arguments",
                inspect.Parameter.KEYWORD_ONLY,
                default=None,
                annotation=arg_annotation,
            )
        ]
    )
    tool.__annotations__ = {"arguments": arg_annotation, "return": Dict[str, Any]}
    return tool


def register_delegated_tools(server: Any) -> List[str]:
    """Register one delegated tool per non-native baseline tool (A-005).

    Makes the live server a strict superset: native tools plus every sibling
    tool, delegated to the sibling's ``call_tool``. Returns the names added.
    """
    from .superset import CANONICAL_MAP
    from .tool_surface import ENVELOPE_OUTPUT

    native = set(tool_names())
    registered: List[str] = []
    for name, resolution in CANONICAL_MAP.items():
        if name in native or not resolution.startswith("delegate:"):
            continue
        owner = resolution.split(":", 2)[1]
        fn = _make_delegated_tool(name, owner)
        try:
            server.tool(
                name=name,
                title=_delegated_title(name),
                description=fn.__doc__,
                annotations=_DELEGATED_ANNOTATIONS,
                output_schema=ENVELOPE_OUTPUT,
            )(fn)
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
            server.tool(
                name=spec.name,
                title=spec.title,
                description=spec.description,
                annotations=spec.annotations,
                output_schema=spec.output_schema,
            )(fn)
        except TypeError:  # older FastMCP signature
            server.add_tool(fn, name=spec.name, description=spec.description)
    register_delegated_tools(server)
    register_prompts(server)
    register_resources(server)
    return server


def register_prompts(server: Any) -> List[str]:
    """Register the guided prompts (A-013) on ``server``; return registered names."""
    from . import prompts as _prompts

    registered: List[str] = []
    for name, fn in _prompts.GUIDED_PROMPTS.items():
        try:
            server.prompt(name=name, description=fn.__doc__)(fn)
        except TypeError:  # older FastMCP signature
            server.prompt(fn)
        registered.append(name)
    return registered


def register_resources(server: Any) -> List[str]:
    """Register the machine-readable method catalog (A-013); return URIs."""
    from .catalog import catalog_json

    def method_catalog() -> str:
        """Machine-readable catalog of valuation methods, formulas, and standards."""
        return catalog_json()

    uri = "valuation://methods"
    try:
        server.resource(uri, name="valuation_methods", description=method_catalog.__doc__)(
            method_catalog
        )
    except TypeError:  # older FastMCP signature
        server.resource(uri)(method_catalog)
    return [uri]


def main(argv: Optional[List[str]] = None) -> int:
    """Run the MCP server: stdio by default, Streamable HTTP with ``--http``."""
    parser = argparse.ArgumentParser(description="fair-value MCP server")
    parser.add_argument(
        "--http", action="store_true", help="serve Streamable HTTP instead of stdio"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    from .observability import init_sentry

    init_sentry()  # no-op unless sentry_sdk is installed and SENTRY_DSN is set

    server = build_server()
    if args.http:
        server.run(transport="http", host=args.host, port=args.port)
    else:
        server.run()
    return 0


__all__ = [
    "build_server",
    "register_delegated_tools",
    "register_prompts",
    "register_resources",
    "main",
    "tool_names",
    "FASTMCP_AVAILABLE",
]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
