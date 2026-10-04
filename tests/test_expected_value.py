"""Expected-value routines (dispatch + computation)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.engine import dispatch
from src.valuation import expected_value as ev


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
        50000, [{"name": "x", "distribution": "normal", "mean": 10.0, "std": 0.0}], {}, 1234
    )
    assert res["value"] == pytest.approx(10.0)
    assert res["std"] == 0.0
    assert res["statistics"]["seed"] == 1234
    assert res["statistics"]["solution_type"] == "simulation"
    assert res["statistics"]["samples"] == 50000


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
            "seed": 42,
        },
    )
    assert mc["status"] == "ok", mc
    assert mc["solution_type"] == "simulation"
    assert mc["statistics"]["seed"] == 42
    assert mc["statistics"]["distribution"] == "empirical"


def test_monte_carlo_requires_seed():
    res = dispatch(
        "calculate_expected_value",
        {
            "method": "monte_carlo",
            "iterations": 1000,
            "distributions": [{"name": "x", "distribution": "normal", "mean": 1.0, "std": 0.1}],
            "base_params": {"c": 2.0},
        },
    )
    assert res["status"] == "error"
    assert "seed" in res["error"]["message"]
