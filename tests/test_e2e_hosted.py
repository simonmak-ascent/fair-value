"""Opt-in end-to-end test against a deployed fair-value endpoint.

Skipped unless ``FAIR_VALUE_E2E_URL`` is set, so the default suite stays
offline (CI never hits the network). Point it at the hosted deploy or a local
``fair-value-mcp --http``:

    FAIR_VALUE_E2E_URL=https://fair-value.ascent-partners.com \
        python -m pytest tests/test_e2e_hosted.py -v

Covers the MCP Streamable-HTTP endpoint (``/mcp``) and the REST API (``/v1``)
over the wire with stdlib only: handshake identity, tool surface + annotations,
a real calculation, the error contract, resources, prompts, and REST.
"""

import json
import os
import urllib.error
import urllib.request

import pytest

BASE = os.environ.get("FAIR_VALUE_E2E_URL", "").rstrip("/")
MCP_URL = BASE + "/mcp"

pytestmark = pytest.mark.skipif(
    not BASE, reason="set FAIR_VALUE_E2E_URL to run the hosted E2E test"
)


def _parse_sse(body: str) -> dict:
    """Return the JSON object from an SSE ``data:`` stream or a JSON body."""
    for line in body.splitlines():
        if line.startswith("data:"):
            return json.loads(line[5:].strip())
    return json.loads(body)


class _MCP:
    """Minimal Streamable-HTTP MCP client (stateless-friendly)."""

    def __init__(self):
        self.session = None

    def post(self, payload):
        req = urllib.request.Request(MCP_URL, data=json.dumps(payload).encode(), method="POST")
        req.add_header("content-type", "application/json")
        req.add_header("accept", "application/json, text/event-stream")
        if self.session:
            req.add_header("mcp-session-id", self.session)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                sid = r.headers.get("mcp-session-id")
                if sid:
                    self.session = sid
                return r.status, _parse_sse(r.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, _parse_sse(e.read().decode())

    def notify(self, method):
        req = urllib.request.Request(
            MCP_URL,
            data=json.dumps({"jsonrpc": "2.0", "method": method}).encode(),
            method="POST",
        )
        req.add_header("content-type", "application/json")
        req.add_header("accept", "application/json, text/event-stream")
        if self.session:
            req.add_header("mcp-session-id", self.session)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status
        except urllib.error.HTTPError as e:
            return e.code


def _rest(path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data:
        req.add_header("content-type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def _envelope(result):
    """Unwrap the shared envelope from an MCP tools/call result."""
    return json.loads(result["result"]["content"][0]["text"])


def test_mcp_end_to_end():
    m = _MCP()
    code, init = m.post(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "e2e", "version": "0"},
            },
        }
    )
    assert code == 200, f"initialize HTTP {code}"
    si = init["result"]["serverInfo"]
    assert si["name"] == "fair-value"
    assert si["version"], "serverInfo.version must be non-empty"

    assert m.notify("notifications/initialized") in (200, 202)

    _, tl = m.post({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = tl["result"]["tools"]
    names = {t["name"] for t in tools}
    assert len(tools) == 14, f"expected 14 tools, got {len(tools)}"
    assert {
        "calculate_dcf",
        "calculate_discount_rate",
        "calculate_credit_loss",
        "calculate_option",
    } <= names
    for t in tools:
        assert {"readOnlyHint", "idempotentHint", "destructiveHint", "openWorldHint"} <= set(
            t.get("annotations", {})
        ), t["name"]

    _, call = m.post(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "calculate_dcf",
                "arguments": {
                    "method": "dcf",
                    "cash_flows": [100.0, 110.0],
                    "discount_rate": 0.1,
                },
            },
        }
    )
    env = _envelope(call)
    assert env["status"] == "ok", env
    assert env["value"] is not None
    assert env["citations"], "ok envelope should carry standards citations"

    _, bad = m.post(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "calculate_dcf", "arguments": {"method": "nope"}},
        }
    )
    assert bad["result"].get("isError") is True or _envelope(bad)["status"] == "error"

    _, res = m.post({"jsonrpc": "2.0", "id": 5, "method": "resources/list"})
    uris = {r["uri"] for r in res["result"]["resources"]}
    assert "valuation://methods" in uris and "valuation://standards" in uris

    _, rr = m.post(
        {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "resources/read",
            "params": {"uri": "valuation://methods"},
        }
    )
    assert rr["result"]["contents"], "valuation://methods should be readable"

    _, pl = m.post({"jsonrpc": "2.0", "id": 7, "method": "prompts/list"})
    assert pl["result"]["prompts"], "server should expose guided prompts"


def test_rest_end_to_end():
    code, body = _rest("/v1/health")
    assert code == 200
    health = json.loads(body)
    assert health["status"] == "ok"
    assert health["tools"] == 14

    code, body = _rest("/v1/tools")
    assert code == 200 and "calculate_dcf" in body

    code, body = _rest(
        "/v1/calculate/calculate_dcf",
        "POST",
        {"method": "dcf", "cash_flows": [100.0, 110.0], "discount_rate": 0.1},
    )
    assert code == 200
    assert json.loads(body)["status"] == "ok"

    code, body = _rest("/v1/openapi.json")
    assert code == 200 and '"openapi"' in body
