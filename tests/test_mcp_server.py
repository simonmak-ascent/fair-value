"""A-004: the FastMCP server adapter and entry point."""

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


def test_invoke_routes_valuation_tool_to_engine(monkeypatch):
    import valuation_engine as ve

    captured = {}

    def fake_run_dcf(ticker, params):
        captured["ticker"] = ticker
        captured["params"] = params
        return {"status": "ok", "method": "DCF", "ticker": ticker, "disclaimer": "x"}

    monkeypatch.setattr(ve, "run_dcf", fake_run_dcf)

    spec = ts.get_tool("valuation_dcf")
    res = srv._invoke(spec, {"ticker": "AAPL", "revenue": 100.0})
    assert captured["ticker"] == "AAPL"
    assert captured["params"] == {"revenue": 100.0}
    assert res["disclaimer"] == "x"


def test_invoke_wraps_direct_src_function_in_envelope():
    spec = ts.get_tool("calculate_wacc")
    res = srv._invoke(
        spec,
        {
            "equity_weight": 0.5,
            "debt_weight": 0.5,
            "cost_equity": 0.10,
            "cost_debt": 0.05,
            "tax_rate": 0.25,
        },
    )
    assert res["status"] == "ok"
    assert res["value"] is not None
    assert res["disclaimer"]


def test_invoke_bad_args_returns_error_envelope(monkeypatch):
    # missing required args for calculate_wacc -> TypeError -> error envelope
    spec = ts.get_tool("calculate_wacc")
    res = srv._invoke(spec, {})
    assert res["status"] == "error"
    assert res["error"]["code"] == "INVALID_ARGUMENT"


def test_main_is_callable():
    assert callable(srv.main)


@pytest.mark.skipif(not srv.FASTMCP_AVAILABLE, reason="fastmcp not installed")
def test_build_server_registers_surface_tools():
    server = srv.build_server()
    assert server is not None
    # every surface tool builds a callable whose name + params come from the spec
    for spec in ts.TOOL_SURFACE:
        fn = srv._make_tool(spec)
        assert fn.__name__ == spec.name
        params = inspect.signature(fn).parameters
        for prop in spec.input_schema.get("properties", {}):
            assert prop in params
