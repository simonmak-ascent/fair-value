"""REST API (`/v1`) over the shared core (VDD A-007).

The same registry/engine that backs the MCP tools is exposed as a versioned REST
surface so non-MCP consumers can embed valuation calculations. Served alongside
the MCP endpoint by the ASGI app (``mcp_server.asgi``).

Routes (all JSON):
    GET  /v1/health
    GET  /v1/tools
    GET  /v1/methods
    GET  /v1/standards
    GET  /v1/help/{tool}
    POST /v1/calculate/{tool}      body: {"method": "...", ...inputs}
"""

from __future__ import annotations

from typing import Any, List

from . import docs as docs_mod
from . import method_spec as ms
from .engine import dispatch

API_VERSION = "v1"


def _json(data: Any, status: int = 200) -> Any:
    from starlette.responses import JSONResponse

    return JSONResponse(data, status_code=status)


def build_rest_routes() -> List[Any]:
    """Return the Starlette routes for the `/v1` REST surface."""
    from starlette.routing import Route

    async def health(request: Any) -> Any:
        return _json(
            {
                "status": "ok",
                "service": "fair-value",
                "api_version": API_VERSION,
                "surface_version": ms.catalog()["surface_version"],
                "tools": len(ms.tools()),
            }
        )

    async def tools(request: Any) -> Any:
        payload = {}
        for tool in ms.tools():
            meta = ms.tool_meta(tool)
            payload[tool] = {
                "title": meta.get("title", tool),
                "description": meta.get("description", ""),
                "methods": ms.methods_for(tool),
            }
        return _json({"api_version": API_VERSION, "tools": payload})

    async def methods(request: Any) -> Any:
        catalog = ms.catalog()
        catalog["api_version"] = API_VERSION
        return _json(catalog)

    async def standards(request: Any) -> Any:
        index = docs_mod.standards_index()
        index["api_version"] = API_VERSION
        return _json(index)

    async def help_tool(request: Any) -> Any:
        tool = request.path_params["tool"]
        if tool not in ms.tools():
            return _json({"status": "error", "error": f"unknown tool '{tool}'"}, 404)
        return _json({"api_version": API_VERSION, "help": docs_mod.tool_help(tool)})

    async def calculate(request: Any) -> Any:
        tool = request.path_params["tool"]
        if tool not in ms.tools():
            return _json({"status": "error", "error": f"unknown tool '{tool}'"}, 404)
        try:
            body = await request.json()
        except Exception:  # noqa: BLE001 - treat any parse failure as a bad request
            return _json({"status": "error", "error": "invalid JSON body"}, 400)
        if not isinstance(body, dict):
            return _json({"status": "error", "error": "body must be a JSON object"}, 400)
        result = dispatch(tool, body)
        return _json(result, 200 if result.get("status") == "ok" else 400)

    async def openapi_spec(request: Any) -> Any:
        from .openapi import build_openapi

        return _json(build_openapi())

    async def api_docs(request: Any) -> Any:
        from starlette.responses import HTMLResponse

        html = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>Fair Value API</title>"
            "<link rel='stylesheet' href='https://unpkg.com/swagger-ui-dist@5/swagger-ui.css'>"
            "</head><body><div id='swagger-ui'></div>"
            "<script src='https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js'></script>"
            "<script>SwaggerUIBundle({url:'/v1/openapi.json',dom_id:'#swagger-ui'});</script>"
            "</body></html>"
        )
        return HTMLResponse(html)

    return [
        Route("/v1/health", health),
        Route("/v1/tools", tools),
        Route("/v1/methods", methods),
        Route("/v1/standards", standards),
        Route("/v1/openapi.json", openapi_spec),
        Route("/v1/docs", api_docs),
        Route("/v1/help/{tool}", help_tool),
        Route("/v1/calculate/{tool}", calculate, methods=["POST"]),
    ]
