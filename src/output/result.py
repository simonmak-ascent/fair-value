"""Shared result envelope and disclaimer (A-006).

Every tool/capability result uses this envelope so outputs are uniform and
auditable: they carry the method, a canonical value, assumptions, a formula
reference, a data timestamp (only when market data was used), calculation
steps, and a mandatory "not investment advice" disclaimer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

DISCLAIMER = (
    "Decision-support only - this is not investment advice. Values are "
    "estimates that depend on the stated assumptions; verify before use."
)

OK_REQUIRED_FIELDS = (
    "status",
    "method",
    "value",
    "assumptions",
    "formula_ref",
    "data_timestamp",
    "steps",
    "disclaimer",
    "statistics",
    "solution_type",
    "citations",
)

# Solution classes: a closed-form/numeric model is deterministic; a simulation
# (Monte-Carlo) model must be seeded and return a distribution (VDD I-006).
SOLUTION_TYPES = ("closed_form", "numeric", "simulation")

# Fields that make up the statistical-characteristics block.
STAT_REQUIRED_FIELDS = (
    "solution_type",
    "distribution",
    "centre",
    "sigma",
    "percentiles",
    "samples",
    "seed",
)


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string ending in ``Z``."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def deterministic_statistics(value: Any, *, solution_type: str = "closed_form") -> Dict[str, Any]:
    """Statistical characteristics for a deterministic (closed-form/numeric) result.

    The centre is the value; there is no dispersion, so the percentiles collapse
    onto the centre and ``sigma`` is 0. Non-numeric values keep ``centre=None``.
    """
    if solution_type not in SOLUTION_TYPES:
        raise ValueError(f"unknown solution_type '{solution_type}'")
    numeric = isinstance(value, (int, float)) and not isinstance(value, bool)
    centre = float(value) if numeric else None
    percentiles = {"p05": centre, "p50": centre, "p95": centre} if centre is not None else {}
    return {
        "solution_type": solution_type,
        "distribution": "deterministic",
        "centre": centre,
        "sigma": 0.0 if centre is not None else None,
        "percentiles": percentiles,
        "samples": None,
        "seed": None,
    }


def summary_statistics(
    samples: Any,
    *,
    centre: Optional[float] = None,
    distribution: str = "empirical",
    seed: Optional[int] = None,
    solution_type: str = "simulation",
) -> Dict[str, Any]:
    """Summarise a sample of outcomes into centre + dispersion + percentiles.

    Used by stochastic methods (``solution_type="simulation"``); a seed is
    required so the result is reproducible.
    """
    import numpy as np

    arr = np.asarray(list(samples), dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        raise ValueError("summary_statistics requires at least one finite sample")
    if solution_type == "simulation" and seed is None:
        raise ValueError("a simulation result requires an explicit seed")
    c = float(centre) if centre is not None else float(np.mean(arr))
    return {
        "solution_type": solution_type,
        "distribution": distribution,
        "centre": c,
        "sigma": float(np.std(arr, ddof=0)),
        "percentiles": {
            "p05": float(np.percentile(arr, 5)),
            "p50": float(np.percentile(arr, 50)),
            "p95": float(np.percentile(arr, 95)),
        },
        "samples": int(arr.size),
        "seed": seed,
    }


def ok(
    method: str,
    ticker: Optional[str] = None,
    value: Any = None,
    *,
    assumptions: Optional[Dict[str, Any]] = None,
    formula_ref: Optional[str] = None,
    data_timestamp: Optional[str] = None,
    steps: Optional[List[str]] = None,
    statistics: Optional[Dict[str, Any]] = None,
    solution_type: Optional[str] = None,
    citations: Optional[Dict[str, Any]] = None,
    **extra: Any,
) -> Dict[str, Any]:
    """Build a complete success envelope; ``extra`` fields are merged in.

    Every envelope carries a ``statistics`` block (centre value + dispersion +
    percentiles), a ``solution_type`` and standard ``citations``. Deterministic
    results default to a closed-form marker; stochastic callers pass
    ``summary_statistics(...)``.
    """
    if statistics is None:
        statistics = deterministic_statistics(value, solution_type=solution_type or "closed_form")
    elif solution_type is not None:
        statistics = {**statistics, "solution_type": solution_type}
    resolved_type = solution_type or statistics.get("solution_type") or "closed_form"
    if resolved_type not in SOLUTION_TYPES:
        raise ValueError(f"unknown solution_type '{resolved_type}'")
    if resolved_type == "simulation" and statistics.get("seed") is None:
        raise ValueError("a simulation result requires an explicit seed")
    if citations is None:
        citations = {"ivs": [], "ifrs": []}

    envelope: Dict[str, Any] = {
        "status": "ok",
        "method": method,
        "ticker": ticker,
        "value": value,
        "assumptions": assumptions if assumptions is not None else {},
        "formula_ref": formula_ref,
        "data_timestamp": data_timestamp,
        "steps": steps if steps is not None else [],
        "statistics": statistics,
        "solution_type": resolved_type,
        "citations": citations,
        "disclaimer": DISCLAIMER,
    }
    envelope.update(extra)
    return envelope


def error(
    code: str,
    message: object,
    method: Optional[str] = None,
    ticker: Optional[str] = None,
) -> Dict[str, Any]:
    """Build an error envelope; ``message`` is coerced to a string."""
    return {
        "status": "error",
        "method": method,
        "ticker": ticker,
        "error": {"code": code, "message": str(message)},
        "disclaimer": DISCLAIMER,
    }


def missing_ok_fields(envelope: Dict[str, Any]) -> List[str]:
    """Return the required success fields absent from ``envelope``."""
    return [field for field in OK_REQUIRED_FIELDS if field not in envelope]


def missing_statistics_fields(envelope: Dict[str, Any]) -> List[str]:
    """Return the statistics-block fields absent from an ok ``envelope``."""
    stats = envelope.get("statistics") or {}
    return [field for field in STAT_REQUIRED_FIELDS if field not in stats]
