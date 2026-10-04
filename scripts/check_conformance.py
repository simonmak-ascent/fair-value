"""CI conformance check.

Fails (exit 1) unless:
  - the method-spec registry and the derived MCP tool surface are sound;
  - every registered method is implemented or explicitly deferred;
  - the standards taxonomy + corpus validate (citations resolvable, provenance); and
  - citation coverage does not regress (uncited methods / orphan clauses, A-005).

Pure and offline. `--update-baseline` refreshes the coverage ratchet.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp_server import method_spec as ms
from mcp_server import standards as std
from mcp_server import tool_surface as ts
from mcp_server.deferred import DEFERRED
from mcp_server.engine import is_implemented

ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "standards" / "coverage-baseline.json"

#: Methods deliberately left uncited because they are not framed by a
#: valuation standard: proprietary sector KPIs (calculate_sector_metrics). Every
#: other method must cite at least one clause.
CITATION_EXEMPT = {
    # calculate_sector_metrics — SaaS/marketplace/token KPIs
    "ltv",
    "cac",
    "arr",
    "nrr",
    "magic_number",
    "rule_of_40",
    "take_rate",
    "gmv_multiple",
    "retention",
    "trl",
    "break_even",
    "gross_margin",
    "token",
    "nvt",
    "metcalfe",
}


def _coverage(problems: list) -> dict:
    """Validate the taxonomy and compute coverage; append problems on failure."""
    taxonomy = getattr(ms, "_TAXONOMY", None)
    if taxonomy is None:
        problems.append("standards taxonomy not loaded")
        return {}
    try:
        std.validate_taxonomy(taxonomy, ms._REGISTRY)
    except std.TaxonomyError as exc:  # noqa: PERF203 - single call site
        problems.append(f"taxonomy invalid: {exc}")
        return {}
    return std.coverage_report(ms._REGISTRY, taxonomy)


def _check_coverage_ratchet(report: dict, problems: list) -> None:
    if not report:
        return
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    uncited = len(report["uncited_methods"])
    orphans = len(report["orphan_clauses"])
    if uncited > baseline["uncited_methods"]:
        problems.append(
            f"citation-coverage regression: {uncited} uncited methods > "
            f"baseline {baseline['uncited_methods']}"
        )
    if orphans > baseline["orphan_clauses"]:
        problems.append(
            f"orphan clauses ({orphans} > baseline {baseline['orphan_clauses']}): "
            f"{report['orphan_clauses']}"
        )
    unexpected = sorted(set(report["uncited_methods"]) - CITATION_EXEMPT)
    if unexpected:
        problems.append(f"uncited methods not in CITATION_EXEMPT: {unexpected}")


def _write_baseline(report: dict) -> None:
    BASELINE_PATH.write_text(
        json.dumps(
            {
                "uncited_methods": len(report["uncited_methods"]),
                "orphan_clauses": len(report["orphan_clauses"]),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _duplicate_methods(registry: dict) -> list:
    """Return messages for method names registered under more than one tool."""
    seen: dict = {}
    dups: list = []
    for tool, table in registry.items():
        for method in table:
            if method in seen and seen[method] != tool:
                dups.append(f"duplicate method name '{method}' in {seen[method]} and {tool}")
            seen[method] = tool
    return dups


def main(argv: list) -> int:
    problems = list(ms.validate_registry())
    problems += list(ts.validate_surface())
    problems += _duplicate_methods(ms._REGISTRY)

    total = implemented = 0
    for tool in ms.tools():
        for method in ms.methods_for(tool):
            total += 1
            if is_implemented(tool, method):
                implemented += 1
            elif method not in DEFERRED.get(tool, set()):
                problems.append(f"unimplemented method: {tool}.{method}")

    report = _coverage(problems)
    if "--update-baseline" in argv and report:
        _write_baseline(report)
        print("coverage baseline updated")
    else:
        _check_coverage_ratchet(report, problems)

    if problems:
        print("CONFORMANCE FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    cited = report.get("cited_methods", 0)
    print(
        f"conformance ok: {len(ts.TOOL_SURFACE)} tools; "
        f"{implemented}/{total} methods implemented, "
        f"{total - implemented} explicitly deferred; "
        f"citations {cited}/{total} methods, "
        f"{len(report.get('orphan_clauses', []))} orphan clauses"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
