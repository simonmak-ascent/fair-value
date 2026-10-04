# Hosting (Streamable HTTP)

The server runs over **stdio** by default and over **Streamable HTTP** with
`--http`.

## Hosted endpoint (zero install)

A managed deployment on Vercel serves the Next.js frontage at the domain root,
the MCP Streamable HTTP endpoint at `/mcp`, and the REST API at `/v1`:

```
https://fair-value.ascent-partners.com/       # docs / landing (Next.js)
https://fair-value.ascent-partners.com/mcp    # MCP Streamable HTTP
https://fair-value.ascent-partners.com/v1/…   # REST API
```

The MCP endpoint moved from the root to `/mcp` when the frontage was added; a
client pointed at the old root should be updated to the `/mcp` path. The
`/api/mcp` path 308-redirects to `/mcp`. Generated from `api/index.py` →
`mcp_server.asgi:app` (MCP at `/mcp`, REST at `/v1`), served alongside the
Next.js app in one Vercel project.

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
