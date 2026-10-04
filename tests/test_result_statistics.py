"""A-003: statistical-characteristics envelope, solution_type and citations."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from src.output.result import (
    deterministic_statistics,
    missing_ok_fields,
    missing_statistics_fields,
    ok,
    summary_statistics,
)


def test_ok_defaults_to_deterministic_statistics():
    env = ok("calculate_dcf.dcf", "T", value=5.0)
    assert missing_ok_fields(env) == []
    assert missing_statistics_fields(env) == []
    stats = env["statistics"]
    assert stats["distribution"] == "deterministic"
    assert stats["centre"] == 5.0
    assert stats["sigma"] == 0.0
    assert stats["percentiles"] == {"p05": 5.0, "p50": 5.0, "p95": 5.0}
    assert env["solution_type"] == "closed_form"
    assert env["citations"] == {"ivs": [], "ifrs": []}


def test_ok_non_numeric_value_has_no_centre():
    env = ok("m", "T", value={"segments": [1, 2]})
    assert env["statistics"]["centre"] is None
    assert env["statistics"]["percentiles"] == {}
    assert missing_statistics_fields(env) == []


def test_ok_accepts_solution_type_and_citations():
    env = ok(
        "m",
        "T",
        value=1.0,
        solution_type="numeric",
        citations={"ivs": ["IVS.103.A20"], "ifrs": ["IFRS.13.62"]},
    )
    assert env["solution_type"] == "numeric"
    assert env["statistics"]["solution_type"] == "numeric"
    assert env["citations"]["ivs"] == ["IVS.103.A20"]


def test_summary_statistics_from_samples():
    stats = summary_statistics([1.0, 2.0, 3.0, 4.0, 5.0], seed=1234)
    assert stats["solution_type"] == "simulation"
    assert stats["distribution"] == "empirical"
    assert stats["centre"] == pytest.approx(3.0)
    assert stats["sigma"] == pytest.approx(2.0**0.5, rel=1e-6)
    assert stats["percentiles"]["p50"] == pytest.approx(3.0)
    assert stats["samples"] == 5
    assert stats["seed"] == 1234


def test_summary_statistics_requires_seed():
    with pytest.raises(ValueError):
        summary_statistics([1.0, 2.0, 3.0])


def test_summary_statistics_empty_raises():
    with pytest.raises(ValueError):
        summary_statistics([], seed=1)


def test_ok_simulation_without_seed_raises():
    with pytest.raises(ValueError):
        ok("m", "T", value=1.0, solution_type="simulation")


def test_ok_accepts_seeded_simulation():
    stats = summary_statistics([10.0, 12.0, 14.0], seed=7)
    env = ok("m", "T", value=stats["centre"], statistics=stats)
    assert env["solution_type"] == "simulation"
    assert env["statistics"]["seed"] == 7


def test_unknown_solution_type_raises():
    with pytest.raises(ValueError):
        deterministic_statistics(1.0, solution_type="bogus")
    with pytest.raises(ValueError):
        ok("m", "T", value=1.0, solution_type="bogus")


def test_missing_statistics_fields_detects_incomplete():
    assert "centre" in missing_statistics_fields({"statistics": {"solution_type": "x"}})


def test_engine_dispatch_attaches_registry_metadata():
    from mcp_server import method_spec  # noqa: F401 - import attaches the taxonomy
    from mcp_server.engine import dispatch

    res = dispatch(
        "calculate_dcf",
        {"method": "dcf", "cash_flows": [100.0, 110.0], "discount_rate": 0.1},
    )
    assert res["status"] == "ok"
    assert res["solution_type"] == "closed_form"
    assert "IVS.103.A20" in res["citations"]["ivs"]
    assert "IFRS.13.62" in res["citations"]["ifrs"]
    assert missing_ok_fields(res) == []
    assert missing_statistics_fields(res) == []
