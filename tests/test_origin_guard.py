"""The Origin guard: an unapproved Origin is refused before any protocol dispatch.

The MCP transport specification requires Origin validation on every incoming connection and a 403
for a present-but-invalid one. These tests assert the three cases that matter: an unapproved origin
is refused, an allowed origin passes through, and a client that sends no Origin — every CLI and SDK
— is not broken by the check.
"""

from __future__ import annotations

import asyncio
import json

from src.mcp.asgi import MCP_PATH, _origin_guard


def _run(app, headers, path: str = MCP_PATH):
    """Drive the middleware once, synchronously.

    The suite has no async plugin configured, and adding a dependency to test one middleware is not
    a trade worth making — so the coroutine is driven directly.
    """
    return asyncio.run(_call(app, headers, path))


async def _call(app, headers: list[tuple[bytes, bytes]], path: str = MCP_PATH):
    """Drive an ASGI app once and collect the status and body it produces."""
    sent: list[dict] = []
    scope = {
        "type": "http",
        "path": path,
        "headers": headers,
        "method": "POST",
    }

    async def receive():
        return {"type": "http.request", "body": b"{}", "more_body": False}

    async def send(message):
        sent.append(message)

    await app(scope, receive, send)
    status = next(m["status"] for m in sent if m["type"] == "http.response.start")
    body = b"".join(m.get("body", b"") for m in sent if m["type"] == "http.response.body")
    return status, body


async def _downstream(scope, receive, send):
    """A stand-in for the real MCP app: it answers 200 with the path it received."""
    body = json.dumps({"reached": scope.get("path")}).encode()
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-length", str(len(body)).encode())],
        }
    )
    await send({"type": "http.response.body", "body": body})


def test_unapproved_origin_is_refused():
    status, body = _run(_origin_guard(_downstream), [(b"origin", b"https://audit-origin.invalid")])
    assert status == 403
    assert json.loads(body)["error"]["message"] == "Origin not allowed"


def test_opaque_origin_is_refused():
    status, _ = _run(_origin_guard(_downstream), [(b"origin", b"null")])
    assert status == 403


def test_allowed_origin_passes_through():
    status, body = _run(
        _origin_guard(_downstream), [(b"origin", b"https://fair-value.ascent-partners.com")]
    )
    assert status == 200
    assert json.loads(body)["reached"] == MCP_PATH


def test_absent_origin_passes_through():
    """A CLI or SDK sends no Origin. The requirement must not break them."""
    status, body = _run(_origin_guard(_downstream), [])
    assert status == 200
    assert json.loads(body)["reached"] == MCP_PATH


def test_alias_paths_are_guarded_too():
    """`/`, `/api/index*` are rewritten onto `/mcp`, so the guard must run after the rewrite.

    Composed the other way round — guard outside, rewrite inside — the guard tests the *raw* path,
    which never starts with `/mcp`, so every alias reaches the protocol unguarded.
    """
    from src.mcp.asgi import wrap_mcp_middleware

    for alias in ("/", "/api/index", "/api/index.py", "/api/index/"):
        status, _ = _run(
            wrap_mcp_middleware(_downstream),
            [(b"origin", b"https://audit-origin.invalid")],
            alias,
        )
        assert status == 403, f"{alias} reached the application with a foreign Origin"


def test_configured_origin_is_honoured(monkeypatch):
    monkeypatch.setenv("MCP_ALLOWED_ORIGINS", "https://example.test, http://localhost:7777")
    ok, _ = _run(_origin_guard(_downstream), [(b"origin", b"https://example.test")])
    refused, _ = _run(_origin_guard(_downstream), [(b"origin", b"http://localhost:7777")])
    default_now_refused, _ = _run(
        _origin_guard(_downstream), [(b"origin", b"https://fair-value.ascent-partners.com")]
    )
    assert ok == 200
    assert refused == 200
    # The env replaces the defaults rather than adding to them — one list, one place to reason about.
    assert default_now_refused == 403
