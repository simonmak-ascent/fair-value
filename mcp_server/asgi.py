"""Hosted ASGI entrypoint (A-014, extended A-007).

Streamable HTTP MCP served at the application root (``/``) plus a versioned REST
API under ``/v1``. Both share the same registry/engine.

Usage (ASGI servers / serverless platforms):

    uvicorn mcp_server.asgi:app --host 0.0.0.0 --port 8000

``app`` is ``None`` only when the optional ``fastmcp`` dependency is absent, so
importing this module never raises for the base install.
"""

from __future__ import annotations

from typing import Any

MCP_PATH = "/"


def _with_legacy_redirect(asgi_app: Any) -> Any:
    """Add a 308 redirect from the legacy ``/mcp`` path to the root endpoint."""
    try:
        from starlette.responses import RedirectResponse
        from starlette.routing import Route

        asgi_app.router.routes.insert(
            0,
            Route(
                "/mcp",
                lambda request: RedirectResponse("/", status_code=308),
                methods=["GET", "POST", "DELETE", "OPTIONS"],
            ),
        )
    except Exception:  # pragma: no cover - redirect is a nicety, not required
        pass
    return asgi_app


def create_app() -> Any:
    """Build the ASGI app: MCP at root + REST ``/v1`` from the shared core."""
    from starlette.applications import Starlette
    from starlette.routing import Mount

    from .rest import build_rest_routes
    from .server import build_server

    mcp_app = _with_legacy_redirect(build_server().http_app(path=MCP_PATH, stateless_http=True))
    routes = build_rest_routes() + [Mount("/", app=mcp_app)]
    return Starlette(routes=routes, lifespan=mcp_app.router.lifespan_context)


app: Any = None

try:  # optional: requires the ``[mcp]`` extra
    app = create_app()
except Exception:  # pragma: no cover - hosts import this only when deps exist
    app = None
