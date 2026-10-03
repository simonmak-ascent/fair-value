"""Vercel Python entrypoint (A-014): exposes the MCP Streamable HTTP ASGI app."""

from mcp_server.asgi import app  # noqa: F401  (Vercel looks for `app`/`handler`)

__all__ = ["app"]
