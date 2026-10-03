"""Hosted ASGI entrypoint (A-014): Streamable HTTP over any ASGI host.

Usage (ASGI servers / serverless platforms):

    uvicorn mcp_server.asgi:app --host 0.0.0.0 --port 8000

``app`` is ``None`` only when the optional ``fastmcp`` dependency is absent, so
importing this module never raises for the base install.
"""

from __future__ import annotations

from typing import Any

app: Any = None

try:  # optional: requires the ``[mcp]`` extra
    from .server import build_server

    app = build_server().http_app(stateless_http=True)
except Exception:  # pragma: no cover - hosts import this only when deps exist
    app = None


def create_app() -> Any:
    """Build and return a fresh Streamable HTTP ASGI app."""
    from .server import build_server

    return build_server().http_app(stateless_http=True)
