"""A-016: observability (Sentry) and service-level objectives.

Sentry is optional and off by default: :func:`init_sentry` is a no-op unless
``sentry_sdk`` is installed *and* ``SENTRY_DSN`` is set. This keeps the offline
contract (no network at import) and the base library dependency-free.

SLOs are declared here as data and evaluated by the pure :func:`evaluate_slo`,
so they can be checked in tests and reported by any monitoring backend.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

SERVICE_NAME = "fair-value-mcp"

# Service-level objectives. ``comparison`` says how to interpret the target:
# "at_least" (value must be >= target) or "at_most" (value must be <= target).
SLOS: Dict[str, Dict[str, Any]] = {
    "availability": {
        "target": 0.995,
        "comparison": "at_least",
        "window_days": 30,
        "description": "Fraction of successful server starts / health probes.",
    },
    "tool_success_rate": {
        "target": 0.99,
        "comparison": "at_least",
        "window_days": 30,
        "description": "Fraction of tool calls returning status='ok' (excludes invalid input).",
    },
    "p95_latency_ms": {
        "target": 2000.0,
        "comparison": "at_most",
        "window_days": 7,
        "description": "95th-percentile tool-call latency in milliseconds.",
    },
}


def evaluate_slo(name: str, observed_value: float) -> Dict[str, Any]:
    """Evaluate ``observed_value`` against the SLO ``name``; raise ``KeyError`` if unknown."""
    slo = SLOS[name]
    target = slo["target"]
    if slo["comparison"] == "at_least":
        met = observed_value >= target
    else:
        met = observed_value <= target
    return {
        "name": name,
        "target": target,
        "observed": observed_value,
        "comparison": slo["comparison"],
        "met": met,
    }


def all_slos_met(observed: Dict[str, float]) -> bool:
    """Return True when every observed SLO in ``observed`` is met."""
    return all(evaluate_slo(name, value)["met"] for name, value in observed.items())


def init_sentry(
    dsn: Optional[str] = None,
    service: str = SERVICE_NAME,
    traces_sample_rate: float = 0.0,
) -> bool:
    """Initialize Sentry when a DSN is available; return True iff initialized.

    No-op (returns False) when ``sentry_sdk`` is not installed or no DSN is
    configured via argument or the ``SENTRY_DSN`` environment variable.
    """
    dsn = dsn or os.environ.get("SENTRY_DSN")
    if not dsn:
        return False

    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=traces_sample_rate,
            environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
            release=os.environ.get("SENTRY_RELEASE"),
        )
        sentry_sdk.set_tag("service", service)
        return True
    except ImportError:
        return False
