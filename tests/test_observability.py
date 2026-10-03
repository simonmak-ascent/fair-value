"""A-016: observability + SLO evaluation (offline)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server import observability as obs  # noqa: E402


def test_sentry_is_off_without_dsn(monkeypatch):
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    assert obs.init_sentry() is False


def test_sentry_off_with_blank_dsn(monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "")
    assert obs.init_sentry() is False


def test_slo_at_least():
    assert obs.evaluate_slo("tool_success_rate", 0.995)["met"] is True
    assert obs.evaluate_slo("tool_success_rate", 0.90)["met"] is False


def test_slo_at_most():
    assert obs.evaluate_slo("p95_latency_ms", 1500)["met"] is True
    assert obs.evaluate_slo("p95_latency_ms", 5000)["met"] is False


def test_unknown_slo_raises():
    with pytest.raises(KeyError):
        obs.evaluate_slo("nope", 1.0)


def test_all_slos_met():
    assert obs.all_slos_met({"availability": 0.999, "tool_success_rate": 0.999})
    assert not obs.all_slos_met({"availability": 0.5})


def test_slo_declarations_complete():
    for name, slo in obs.SLOS.items():
        assert slo["comparison"] in {"at_least", "at_most"}
        assert isinstance(slo["target"], (int, float))
        assert slo["description"]
