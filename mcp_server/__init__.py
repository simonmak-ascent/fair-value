"""MCP surface package for fair-value.

The declarative tool definitions live in :mod:`mcp_server.tool_surface`; the
FastMCP server (A-004) renders them. Importing this package has no side effects.
"""

# Reported as the MCP ``serverInfo.version``. Kept in lockstep with
# ``pyproject.toml`` and both ``server.json`` version fields;
# ``tests/test_manifest.py`` fails if they drift.
__version__ = "0.2.6"

__all__ = ["tool_surface", "__version__"]
