"""A-007: versioned REST API (`/v1`) over the shared core."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

import pytest

httpx = pytest.importorskip("httpx")  # noqa: F841 - TestClient dependency


def _client():
    from starlette.testclient import TestClient

    from mcp_server.asgi import create_app

    app = create_app()
    return TestClient(app)


def test_health():
    with _client() as client:
        res = client.get("/v1/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["api_version"] == "v1"
    assert body["tools"] == 16


def test_tools_and_methods():
    with _client() as client:
        tools = client.get("/v1/tools").json()["tools"]
        methods = client.get("/v1/methods").json()
    assert "calculate_dcf" in tools
    assert tools["calculate_dcf"]["methods"]
    assert methods["method_count"] >= 134


def test_standards():
    with _client() as client:
        res = client.get("/v1/standards")
    assert res.status_code == 200
    ids = {c["id"] for c in res.json()["clauses"]}
    assert "IVS.210.A10" in ids


def test_help_and_calculate():
    with _client() as client:
        help_res = client.get("/v1/help/calculate_dcf")
        calc = client.post(
            "/v1/calculate/calculate_dcf",
            json={"method": "dcf", "cash_flows": [100.0, 110.0], "discount_rate": 0.1},
        )
    assert help_res.status_code == 200
    assert help_res.json()["help"]["tool"] == "calculate_dcf"
    assert calc.status_code == 200
    body = calc.json()
    assert body["status"] == "ok"
    assert body["value"] is not None
    assert "IVS.103.A20" in body["citations"]["ivs"]


def test_errors():
    with _client() as client:
        unknown = client.get("/v1/help/no_such_tool")
        bad_method = client.post("/v1/calculate/calculate_dcf", json={"method": "nope"})
        not_json = client.post(
            "/v1/calculate/calculate_dcf",
            content="not json",
            headers={"content-type": "application/json"},
        )
    assert unknown.status_code == 404
    assert bad_method.status_code == 400
    assert not_json.status_code == 400
