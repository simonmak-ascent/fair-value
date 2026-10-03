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
)


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string ending in ``Z``."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def ok(
    method: str,
    ticker: Optional[str] = None,
    value: Optional[float] = None,
    *,
    assumptions: Optional[Dict[str, Any]] = None,
    formula_ref: Optional[str] = None,
    data_timestamp: Optional[str] = None,
    steps: Optional[List[str]] = None,
    **extra: Any,
) -> Dict[str, Any]:
    """Build a complete success envelope; ``extra`` fields are merged in."""
    envelope: Dict[str, Any] = {
        "status": "ok",
        "method": method,
        "ticker": ticker,
        "value": value,
        "assumptions": assumptions if assumptions is not None else {},
        "formula_ref": formula_ref,
        "data_timestamp": data_timestamp,
        "steps": steps if steps is not None else [],
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
