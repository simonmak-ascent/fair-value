# REST API (`/v1`)

The same valuation core that backs the MCP tools is exposed as a versioned REST
API at `/v1`, served alongside the MCP endpoint (at `/mcp`) by the ASGI app
(`src.mcp.asgi:app`). No method logic is duplicated: every call goes through
the shared engine and returns the same envelope (centre value + `statistics` +
`solution_type` + `citations`).

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/health` | Service + surface version, tool count |
| GET | `/v1/tools` | Tools with titles, descriptions and methods |
| GET | `/v1/methods` | Full method catalog (parameters, formula refs, standards) |
| GET | `/v1/standards` | Standards, clauses, and the methods citing each |
| GET | `/v1/openapi.json` | OpenAPI 3.0 document for this API |
| GET | `/v1/docs` | Swagger UI for the API |
| GET | `/v1/help/{tool}` | Generated transparency record for a tool |
| POST | `/v1/calculate/{tool}` | Run a method: `{"method": "...", ...inputs}` |

## Examples

```bash
curl -s localhost:8000/v1/health

curl -s -X POST localhost:8000/v1/calculate/calculate_dcf \
  -H 'content-type: application/json' \
  -d '{"method":"dcf","cash_flows":[100,110],"discount_rate":0.1}'
```

The calculate response is the standard envelope:

```json
{
  "status": "ok",
  "method": "calculate_dcf.dcf",
  "value": 183.4,
  "statistics": {"solution_type": "closed_form", "distribution": "deterministic",
                 "centre": 183.4, "sigma": 0.0, "percentiles": {"p05":183.4,"p50":183.4,"p95":183.4},
                 "samples": null, "seed": null},
  "solution_type": "closed_form",
  "citations": {"ivs": ["IVS.103.A20"], "ifrs": ["IFRS.13.62"]},
  "disclaimer": "..."
}
```

Errors return `400` for **any** non-ok result — invalid method or body, a computation that cannot
produce a number, or a method that is not implemented — and `404` for an unknown tool, always with
a JSON envelope whose `error` is an object:

```json
{"status":"error","method":"calculate_dcf","ticker":null,
 "error":{"code":"INVALID_ARGUMENT","message":"..."},"disclaimer":"..."}
```

Codes on this surface: `INVALID_ARGUMENT`, `COMPUTATION_ERROR`, `UNKNOWN_TOOL`,
`NOT_IMPLEMENTED`. Branch on `error.code`, never on the message.

## Running locally

```bash
uvicorn src.mcp.asgi:app --host 0.0.0.0 --port 8000
```
