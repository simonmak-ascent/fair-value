"""Hosted ASGI entrypoint (A-014): Streamable HTTP over any ASGI host.

Usage (ASGI servers / serverless platforms):

    uvicorn mcp_server.asgi:app --host 0.0.0.0 --port 8000

The MCP endpoint is served at the application root (``/``) so a custom domain
can be the MCP root. ``app`` is ``None`` only when the optional ``fastmcp``
dependency is absent, so importing this module never raises for the base install.
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


app: Any = None

try:  # optional: requires the ``[mcp]`` extra
    from .server import build_server

    app = _with_legacy_redirect(build_server().http_app(path=MCP_PATH, stateless_http=True))
except Exception:  # pragma: no cover - hosts import this only when deps exist
    app = None


def create_app() -> Any:
    """Build and return a fresh Streamable HTTP ASGI app (mounted at the root)."""
    from .server import build_server

    return _with_legacy_redirect(build_server().http_app(path=MCP_PATH, stateless_http=True))
