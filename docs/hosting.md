# Hosting (Streamable HTTP)

The server runs over **stdio** by default and over **Streamable HTTP** with
`--http`.

## Hosted endpoint (zero install)

The hosted deployment serves the Next.js frontage at the domain root, the MCP
Streamable HTTP endpoint at `/mcp`, and the REST API at `/v1`:

```
https://fair-value.ascent-partners.com/       # docs / landing (Next.js)
https://fair-value.ascent-partners.com/mcp    # MCP Streamable HTTP
https://fair-value.ascent-partners.com/v1/…   # REST API
```

It runs as two containers on the estate, both pinned by digest in
`container.json`: `fair-value` (Next.js standalone, port 3101) and
`fair-value-mcp` (`src.mcp.asgi:app` under uvicorn, port 8011). Images are built
by `image.yml`, pinned by pull request, and rolled out by `deploy-digest.yml`.
The declarations themselves are `container.json` (digests, ports, health) and
`compliance.json` (workflow, converge timer, e2e probes).

There is no `/api/mcp` path. An earlier Vercel deployment routed everything
through `api/index.py` and 308-redirected `/api/mcp` to `/mcp`; that surface is
retired and the directory is gone.

## Docker

```bash
docker build -t fair-value-mcp .
docker run --rm -p 8000:8000 fair-value-mcp
# endpoint: http://localhost:8000/mcp
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
