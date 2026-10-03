# Observability & SLOs

## SLOs

Declared in `mcp_server/observability.py` and evaluated by
`evaluate_slo(name, observed_value)`.

| SLO | Target | Comparison | Window |
|-----|--------|------------|--------|
| `availability` | ≥ 0.995 | at least | 30 days |
| `tool_success_rate` | ≥ 0.99 | at least | 30 days |
| `p95_latency_ms` | ≤ 2000 | at most | 7 days |

## Sentry

Sentry is **optional and off by default**. Install and configure to enable:

```bash
pip install "fair-value[observability]"
export SENTRY_DSN="https://<key>@o0.ingest.sentry.io/0"
export SENTRY_ENVIRONMENT="production"
export SENTRY_RELEASE="fair-value@0.2.1"
fair-value-mcp
```

When `SENTRY_DSN` is unset (or `sentry-sdk` is not installed), `init_sentry()`
returns `False` and the server runs without telemetry — the base install makes
no network calls at import time.
