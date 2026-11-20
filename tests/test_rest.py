"""A-007: versioned REST API (`/v1`) over the shared core."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

import pytest

httpx = pytest.importorskip("httpx")  # noqa: F841 - TestClient dependency


def _client():
    from starlette.testclient import TestClient

    from src.mcp.asgi import create_app

    app = create_app()
    return TestClient(app)


def test_health():
    with _client() as client:
        res = client.get("/v1/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["api_version"] == "v1"
    assert body["tools"] == 14


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
        # The two `calculate`-route guards are separate branches from the parse failure above, and
        # each used to emit its own string shape — cover them or a revert of either stays green.
        post_unknown = client.post("/v1/calculate/no_such_tool", json={"method": "x"})
        not_an_object = client.post("/v1/calculate/calculate_dcf", json=[1, 2, 3])
    assert unknown.status_code == 404
    assert bad_method.status_code == 400
    assert not_json.status_code == 400
    assert post_unknown.status_code == 404
    assert not_an_object.status_code == 400

    # Transport-level failures must carry the same envelope shape as the engine's, not a bare
    # string in `error`: a client branches on `error.code` and cannot do that when it is a string.
    for res in (unknown, bad_method, not_json, post_unknown, not_an_object):
        body = res.json()
        assert body["status"] == "error"
        assert isinstance(body["error"], dict), (
            f"{res.request.url} returned error={body['error']!r}"
        )
        assert body["error"]["code"]
        assert "disclaimer" in body


def test_non_finite_result_is_a_typed_400_not_a_500():
    """The live 500 reproduced over the wire: `/v1/calculate` must answer with an envelope."""
    with _client() as client:
        res = client.post(
            "/v1/calculate/calculate_option",
            json={
                "method": "binomial_american",
                "spot": 100.0,
                "strike": 100.0,
                "maturity": 1.0,
                "risk_free": 0.05,
                "volatility": 1000.0,
                "option_type": "call",
                "steps": 100,
            },
        )
    assert res.status_code == 400, res.text[:200]
    body = res.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "COMPUTATION_ERROR"


def test_openapi_and_docs():
    with _client() as client:
        spec = client.get("/v1/openapi.json")
        docs = client.get("/v1/docs")
    assert spec.status_code == 200
    body = spec.json()
    assert body["openapi"].startswith("3.")
    assert "/v1/calculate/{tool}" in body["paths"]
    enum = body["paths"]["/v1/help/{tool}"]["get"]["parameters"][0]["schema"]["enum"]
    assert "calculate_dcf" in enum
    assert docs.status_code == 200
    assert "swagger-ui" in docs.text
