"""Machine-readable MCP resources: method catalog and standards taxonomy.

Served as ``valuation://methods`` and ``valuation://standards`` so agents can
discover the methods, formula references, and standards each tool implements
without guessing from prose. Both are derived from the method-spec registry and
the report-review taxonomy — never hand-maintained separately.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from . import method_spec as ms

_STANDARDS = {
    "IVS 2025": "International Valuation Standards 2025 (IVS 101-105): scope of work, bases of value, valuation approaches and methods.",
    "IFRS 13": "Fair value measurement: exit price, market participants, valuation techniques, and the fair-value hierarchy.",
    "IFRS 9": "Financial instruments: classification and measurement, expected credit losses, and fair value.",
    "IAS 36": "Impairment of assets: recoverable amount is the higher of value in use and fair value less costs of disposal.",
    "IAS 37": "Provisions, contingent liabilities and contingent assets: best estimate, risks, and discounting.",
    "IAS 32": "Financial instruments: presentation, including puttable instruments and redemption features.",
    "IFRS 2": "Share-based payment: fair value measured at grant date.",
    "IFRS 17": "Insurance contracts: fulfilment cash flows, risk adjustment, and contractual service margin.",
    "HKFRS": "Hong Kong Financial Reporting Standards, the local IFRS-equivalent reporting basis.",
}


def build_catalog() -> Dict[str, Any]:
    """Return the full method catalog (delegates to the registry)."""
    return ms.catalog()


def standards() -> Dict[str, Any]:
    """Return the standards taxonomy referenced by the tools."""
    return {"standards": _STANDARDS}


def catalog_json() -> str:
    """Return :func:`build_catalog` as deterministic JSON."""
    return json.dumps(build_catalog(), indent=2, sort_keys=True)


def standards_json() -> str:
    """Return :func:`standards` as deterministic JSON."""
    return json.dumps(standards(), indent=2, sort_keys=True)
