# Hosting (Streamable HTTP)

The server runs over **stdio** by default and over **Streamable HTTP** with
`--http`.

## Hosted endpoint (zero install)

A managed Streamable HTTP endpoint is deployed on Vercel:

```
https://fair-value-two.vercel.app/mcp
```

Point any MCP client at it (transport: `streamable-http`). It is generated from
`api/index.py` → `mcp_server.asgi:app`.

## Docker

```bash
docker build -t fair-value-mcp .
docker run --rm -p 8000:8000 fair-value-mcp
# endpoint: http://localhost:8000/mcp
```

## Docker Compose

```bash
SENTRY_DSN="" docker compose up --build
```

## Configuration

| Variable | Purpose | Default |
|----------|---------|---------|
| `SENTRY_DSN` | Enable Sentry error/tracing when set | unset (disabled) |
| `SENTRY_ENVIRONMENT` | Sentry environment tag | `production` |
| `SENTRY_RELEASE` | Sentry release tag | unset |

## Notes

- The HTTP transport is stateless per request; run behind a normal load
  balancer / reverse proxy for TLS.
- Managed deployment (Vercel / Cloudflare) is out of scope here because the
  server is a long-running Python process; use the container or `fair-value-mcp
  --http` on any host.
