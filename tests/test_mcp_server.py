"""The FastMCP server adapter and entry point."""

import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from mcp_server import server as srv
from mcp_server import tool_surface as ts


def test_module_imports_and_flag_is_bool():
    assert isinstance(srv.FASTMCP_AVAILABLE, bool)


def test_build_server_errors_clearly_without_fastmcp(monkeypatch):
    monkeypatch.setattr(srv, "FASTMCP_AVAILABLE", False)
    monkeypatch.setattr(srv, "FastMCP", None)
    with pytest.raises(RuntimeError):
        srv.build_server()


def test_invoke_routes_to_registry_engine():
    spec = ts.get_tool("calculate_dcf")
    res = srv._invoke(spec, {"method": "dcf", "cash_flows": [100.0, 110.0], "discount_rate": 0.10})
    assert res["status"] == "ok", res
    assert res["value"] is not None
    assert res["formula_ref"]


def test_invoke_missing_method_returns_error_envelope():
    spec = ts.get_tool("calculate_dcf")
    res = srv._invoke(spec, {"cash_flows": [100.0]})
    assert res["status"] == "error"
    assert res["error"]["code"] == "INVALID_ARGUMENT"


def test_invoke_unknown_method_returns_error_envelope():
    spec = ts.get_tool("calculate_dcf")
    res = srv._invoke(spec, {"method": "nope"})
    assert res["status"] == "error"
    assert res["error"]["code"] == "INVALID_ARGUMENT"


def test_main_is_callable():
    assert callable(srv.main)


@pytest.mark.skipif(not srv.FASTMCP_AVAILABLE, reason="fastmcp not installed")
def test_build_server_registers_surface_tools():
    server = srv.build_server()
    assert server is not None
    for spec in ts.TOOL_SURFACE:
        fn = srv._make_tool(spec)
        assert fn.__name__ == spec.name
        params = inspect.signature(fn).parameters
        for prop in spec.input_schema.get("properties", {}):
            assert prop in params


@pytest.mark.skipif(not srv.FASTMCP_AVAILABLE, reason="fastmcp not installed")
def test_build_server_exposes_all_tools():
    import asyncio

    server = srv.build_server()
    tools = asyncio.run(server.list_tools())
    assert {t.name for t in tools} == set(ts.tool_names())
    assert len(tools) == 14


@pytest.mark.skipif(not srv.FASTMCP_AVAILABLE, reason="fastmcp not installed")
def test_build_server_tool_call_roundtrip():
    import asyncio
    import json

    from fastmcp import Client

    server = srv.build_server()

    async def go():
        async with Client(server) as client:
            result = await client.call_tool(
                "calculate_dcf",
                {"method": "dcf", "cash_flows": [100.0, 110.0], "discount_rate": 0.1},
            )
            return json.loads(result.content[0].text)

    res = asyncio.run(go())
    assert res["status"] == "ok", res
    assert res["value"] is not None
