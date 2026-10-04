"""A-005: citation/coverage conformance gate."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

import check_conformance as gate  # noqa: E402
from mcp_server import method_spec as ms  # noqa: E402
from mcp_server import standards as std  # noqa: E402


def test_coverage_report_shape():
    report = std.coverage_report(ms._REGISTRY, ms._TAXONOMY)
    assert report["total_methods"] == report["cited_methods"] + len(report["uncited_methods"])
    assert isinstance(report["orphan_clauses"], list)
    # The methods added in A-001/A-004 are cited.
    for cited in ("dcf", "viu_pre_tax", "relief_from_royalty", "recoverable_amount"):
        assert cited not in report["uncited_methods"]
        assert cited in {m for t in ms._REGISTRY.values() for m in t}


def test_gate_passes_on_current_repo():
    assert gate.main([]) == 0


def test_ratchet_flags_new_uncited_method():
    import json

    report = std.coverage_report(ms._REGISTRY, ms._TAXONOMY)
    # Pretend the baseline was zero: the existing citation debt is a regression.
    baseline = {"uncited_methods": 0, "orphan_clauses": len(report["orphan_clauses"])}
    original = gate.BASELINE_PATH.read_text(encoding="utf-8")
    try:
        gate.BASELINE_PATH.write_text(json.dumps(baseline), encoding="utf-8")
        problems: list = []
        gate._check_coverage_ratchet(report, problems)
        assert any("coverage regression" in p for p in problems)
    finally:
        gate.BASELINE_PATH.write_text(original, encoding="utf-8")


def test_ratchet_flags_new_orphan_clause():
    report = dict(std.coverage_report(ms._REGISTRY, ms._TAXONOMY))
    report["orphan_clauses"] = [*report["orphan_clauses"], "FAKE.999"]
    baseline = {"uncited_methods": len(report["uncited_methods"]), "orphan_clauses": 0}
    import json

    original = gate.BASELINE_PATH.read_text(encoding="utf-8")
    try:
        gate.BASELINE_PATH.write_text(json.dumps(baseline), encoding="utf-8")
        problems = []
        gate._check_coverage_ratchet(report, problems)
        assert any("orphan clauses" in p for p in problems)
    finally:
        gate.BASELINE_PATH.write_text(original, encoding="utf-8")


def test_duplicate_method_detection():
    fake = {"tool_a": {"x": object()}, "tool_b": {"x": object()}}
    dups = gate._duplicate_methods(fake)
    assert dups and "'x'" in dups[0]
    assert gate._duplicate_methods({"tool_a": {"x": object()}}) == []


def test_uncited_methods_are_exactly_the_exempt_set():
    report = std.coverage_report(ms._REGISTRY, ms._TAXONOMY)
    assert report["orphan_clauses"] == []
    assert set(report["uncited_methods"]) == gate.CITATION_EXEMPT
    assert len(report["uncited_methods"]) == 15
