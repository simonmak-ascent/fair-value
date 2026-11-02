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

import json
import os
from typing import Any, Callable

MCP_PATH = "/mcp"

#: Origins a browser may call from. The MCP transport specification (2025-06-18 and later) says a
#: server MUST validate the Origin header on every incoming connection to prevent DNS rebinding,
#: and MUST answer 403 when a present Origin is not allowed. A non-browser client sends no Origin
#: at all, which stays allowed — that is the case the requirement is careful not to break.
#:
#: Configurable, because the published host differs per environment: ``MCP_ALLOWED_ORIGINS`` is a
#: comma-separated list. The default is this service's own public origin plus loopback, so a
#: local inspector keeps working without opening the endpoint to every website.
_DEFAULT_ALLOWED_ORIGINS = frozenset(
    {
        "https://fair-value.ascent-partners.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    }
)

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


def allowed_origins() -> frozenset[str]:
    """The browser origins permitted to call the MCP endpoint."""
    raw = os.environ.get("MCP_ALLOWED_ORIGINS", "").strip()
    if not raw:
        return _DEFAULT_ALLOWED_ORIGINS
    return frozenset(o.strip() for o in raw.split(",") if o.strip())


def _origin_of(scope: dict) -> str | None:
    for key, value in scope.get("headers") or []:
        if key == b"origin":
            return value.decode("latin-1")
    return None


def _origin_guard(app: Any) -> Any:
    """Pure-ASGI middleware: refuse an unapproved Origin before any protocol dispatch.

    Checking here rather than in CORS is deliberate — the requirement is about who may *speak*
    to the server, not merely whether a browser may read the reply, and a wildcard
    ``Access-Control-Allow-Origin`` would not satisfy it.
    """

    async def middleware(scope: dict, receive: Callable, send: Callable) -> None:
        if scope.get("type") == "http" and str(scope.get("path", "")).startswith(MCP_PATH):
            origin = _origin_of(scope)
            if origin is not None and origin not in allowed_origins():
                body = json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32600, "message": "Origin not allowed"},
                    }
                ).encode()
                await send(
                    {
                        "type": "http.response.start",
                        "status": 403,
                        "headers": [
                            (b"content-type", b"application/json"),
                            (b"content-length", str(len(body)).encode()),
                        ],
                    }
                )
                await send({"type": "http.response.body", "body": body})
                return
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
    app = _origin_guard(_normalize_mcp_path(create_app()))
except Exception:  # pragma: no cover - hosts import this only when deps exist
    app = None
