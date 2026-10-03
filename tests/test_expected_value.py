"""Expected-value routines and the report-review rule engine."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.engine import dispatch
from src.valuation import expected_value as ev
from src.report_review.audit import audit_report


def test_continuous_normal_full_range_is_mean():
    res = ev.continuous("normal", 5.0, 2.0, -1e9, 1e9)
    assert abs(res["value"] - 5.0) < 1e-3
    assert res["probability"] == pytest.approx(1.0, abs=1e-6)


def test_continuous_uniform_mean():
    res = ev.continuous("uniform", 0.0, 1.0, 0.0, 1.0)
    assert res["value"] == pytest.approx(0.5)
    assert res["probability"] == pytest.approx(1.0)


def test_monte_carlo_mean_tracks_input():
    res = ev.monte_carlo(
        50000, [{"name": "x", "distribution": "normal", "mean": 10.0, "std": 0.0}], {}
    )
    assert res["value"] == pytest.approx(10.0)
    assert res["std"] == 0.0


def test_decision_tree_chance_and_decision():
    chance = {
        "type": "chance",
        "branches": [
            {"probability": 0.5, "node": {"type": "terminal", "value": 100.0}},
            {"probability": 0.5, "node": {"type": "terminal", "value": 200.0}},
        ],
    }
    assert ev.decision_tree(chance)["value"] == pytest.approx(150.0)
    decision = {
        "type": "decision",
        "branches": [
            {"node": {"type": "terminal", "value": 100.0}},
            {"node": {"type": "terminal", "value": 300.0}},
        ],
    }
    assert ev.decision_tree(decision)["value"] == pytest.approx(300.0)


def test_dispatch_expected_value_methods():
    cont = dispatch(
        "calculate_expected_value",
        {
            "method": "continuous",
            "distribution": "normal",
            "mean": 0.0,
            "std": 1.0,
            "lower": -1.0,
            "upper": 1.0,
        },
    )
    assert cont["status"] == "ok", cont
    mc = dispatch(
        "calculate_expected_value",
        {
            "method": "monte_carlo",
            "iterations": 1000,
            "distributions": [{"name": "x", "distribution": "normal", "mean": 1.0, "std": 0.1}],
            "base_params": {"c": 2.0},
        },
    )
    assert mc["status"] == "ok", mc


def test_report_audit_scores_complete_document(tmp_path):
    doc = tmp_path / "report.md"
    doc.write_text(
        "Methodology: DCF. Assumptions: growth and margins. Discount rate WACC. "
        "Standards: IFRS 13 and IVS 2025. Fair value conclusion HKD 12. "
        "Valuation date 2026-01-01. Hierarchy level 3.",
        encoding="utf-8",
    )
    res = audit_report(str(doc))
    assert res["value"] == pytest.approx(100.0)
    assert res["error_count"] == 0


def test_report_audit_flags_missing_conclusion(tmp_path):
    doc = tmp_path / "report.md"
    doc.write_text("Methodology: DCF. assumptions and discount rate given.", encoding="utf-8")
    res = audit_report(str(doc))
    assert res["value"] < 100.0
    assert res["error_count"] >= 1


def test_dispatch_report_review_requires_file_path():
    res = dispatch("calculate_report_review", {"method": "audit"})
    assert res["status"] == "error"
    assert "file_path" in res["error"]["message"]


def test_dispatch_company_profile(monkeypatch, tmp_path):
    import valuation_engine as ve

    monkeypatch.setattr(ve, "_get_company_info", lambda t: {"name": "Test Co"})
    monkeypatch.setattr(ve, "_get_market_metrics", lambda t: {"price": 12.5, "volatility": 0.3})
    res = dispatch("calculate_company_summary", {"method": "profile", "ticker": "0001.HK"})
    assert res["status"] == "ok", res
    assert res["value"] == 12.5
    assert res["profile"]["name"] == "Test Co"
