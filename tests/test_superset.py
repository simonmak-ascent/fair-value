"""A-005: superset baseline coverage and canonical (delegated) mapping."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from mcp_server import superset as ss
from mcp_server import superset_baseline as sb


def test_baseline_counts():
    assert len(sb.INTANGIBLE_TOOLS) == 14
    assert len(sb.STARTUP_TOOLS) == 14
    assert "valuation_time_value" in sb.INTANGIBLE_TOOLS
    assert "valuation_time_value" in sb.STARTUP_TOOLS


def test_union_is_unique_27():
    assert len(sb.UNION_TOOLS) == 27
    assert len(set(sb.UNION_TOOLS)) == 27


def test_mapping_complete_and_delegated():
    assert all(ss.CANONICAL_MAP.get(n) for n in sb.UNION_TOOLS)
    # every baseline tool with no native equivalent is delegated
    for name in sb.UNION_TOOLS:
        assert ss.CANONICAL_MAP[name].startswith("delegate:")


def test_coverage_has_no_missing():
    cov = ss.coverage()
    assert cov["missing"] == []
    assert cov["total"] == 27
    assert ss.missing_tools() == []


def test_missing_is_detected_when_unmapped():
    dropped = sb.UNION_TOOLS[0]
    trimmed = {k: v for k, v in ss.CANONICAL_MAP.items() if k != dropped}
    cov = ss.coverage_for(sb.UNION_TOOLS, trimmed)
    assert dropped in cov["missing"]


def test_overlap_has_canonical_owner():
    assert ss.OVERLAPS.get("valuation_time_value") == "intangible-valuation"


def test_strategy_and_dependencies_declared():
    assert ss.STRATEGY == "delegate"
    # Only namespaced startup-valuation is pip-installable; intangible-valuation
    # collides on the top-level ``mcp_server`` package and is source-loaded.
    assert any("startup-valuation" in d for d in ss.SUPERSET_DEPENDENCIES)
    assert not any("intangible-valuation" in d for d in ss.SUPERSET_DEPENDENCIES)
    assert ss.INTANGIBLE_SRC_HINT == "INTANGIBLE_VALUATION_SRC"


def test_delegate_call_wraps_result_in_envelope():
    def fake_call_tool(name, arguments):
        assert name == "valuation_ip"
        assert arguments == {"asset": "patent"}
        return {"value": 123.0, "method": "relief-from-royalty"}

    res = ss.delegate_call(
        "intangible-valuation",
        "valuation_ip",
        {"asset": "patent"},
        call_tool=fake_call_tool,
    )
    assert res["status"] == "ok"
    assert res["value"]["value"] == 123.0
    assert res["disclaimer"]


def test_delegate_call_error_becomes_error_envelope():
    def boom(name, arguments):
        raise RuntimeError("sibling down")

    res = ss.delegate_call("startup-valuation", "valuation_saas", {}, call_tool=boom)
    assert res["status"] == "error"
    assert res["error"]["code"] == "DATA_UNAVAILABLE"


def test_sibling_availability_is_boolean():
    assert isinstance(ss.sibling_available("startup-valuation"), bool)
    assert isinstance(ss.sibling_available("intangible-valuation"), bool)
    assert ss.sibling_available("nonexistent") is False


def test_intangible_availability_matches_source_path():
    # Availability must track whether a source file was actually located.
    p = ss._intangible_source_path()
    assert ss.sibling_available("intangible-valuation") is (p is not None)
