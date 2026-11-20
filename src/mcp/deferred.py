"""Methods registered but not implemented (stdlib-only, import-light).

Kept separate from :mod:`scripts.check_conformance` so tooling that must not
import the computation stack (e.g. the web data generator) can read the
deferral list without pulling in ``src``/``yfinance``.
"""

from __future__ import annotations

#: tool -> set of method ids that are registered but deliberately not
#: implemented (missing optional engine or a pending numerical fix).
DEFERRED: dict[str, set[str]] = {
    "calculate_convertible_bond": {"quantlib", "finite_difference"},
}


def deferred_method_ids() -> set[str]:
    """Flatten ``DEFERRED`` to the set of deferred method ids."""
    return {method for methods in DEFERRED.values() for method in methods}
