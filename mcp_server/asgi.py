"""Hosted ASGI entrypoint (A-014, extended A-007).

Streamable HTTP MCP served at ``/mcp`` plus a versioned REST API under ``/v1``.
Both share the same registry/engine.

Usage (ASGI servers / serverless platforms):

    uvicorn mcp_server.asgi:app --host 0.0.0.0 --port 8000

On Vercel the Next.js frontage owns ``/`` and rewrites ``/mcp`` and ``/v1/*`` to
the Python function (``api/index.py``); Vercel preserves the request path, so the
same routing applies. A normalize middleware maps a bare function path
(``/`` or ``/api/index*``) onto ``/mcp`` so direct function invocations also
reach MCP.

``app`` is ``None`` only when the optional ``fastmcp`` dependency is absent, so
importing this module never raises for the base install.
"""

from __future__ import annotations

from typing import Any, Callable

MCP_PATH = "/mcp"

#: Paths that should be treated as the MCP root (function-invocation aliases).
_MCP_ALIASES = frozenset({"/", "", "/api/index", "/api/index/", "/api/index.py"})


def _normalize_mcp_path(app: Any) -> Any:
    """Pure-ASGI middleware: map aliases onto ``MCP_PATH`` (streaming-safe)."""

    async def middleware(scope: dict, receive: Callable, send: Callable) -> None:
        if scope.get("type") == "http" and scope.get("path") in _MCP_ALIASES:
            scope = dict(scope)
            scope["path"] = MCP_PATH
            scope["raw_path"] = MCP_PATH.encode("ascii")
        await app(scope, receive, send)

    return middleware


def create_app() -> Any:
    """Build the ASGI app: MCP at ``/mcp`` + REST ``/v1`` from the shared core."""
    from starlette.applications import Starlette
    from starlette.routing import Mount

    from .rest import build_rest_routes
    from .server import build_server

    mcp_app = build_server().http_app(path=MCP_PATH, stateless_http=True)
    routes = build_rest_routes() + [Mount("/", app=mcp_app)]
    return Starlette(routes=routes, lifespan=mcp_app.router.lifespan_context)


app: Any = None

try:  # optional: requires the ``[mcp]`` extra
    app = _normalize_mcp_path(create_app())
except Exception:  # pragma: no cover - hosts import this only when deps exist
    app = None
