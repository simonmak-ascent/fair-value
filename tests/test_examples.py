"""The worked HK examples run and return successful envelopes."""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "examples"))

import hk_examples  # noqa: E402


def test_hk_convertible_bond_example():
    res = hk_examples.hk_convertible_bond()
    assert res["status"] == "ok", res
    assert res["value"] > 0


def test_hk_inline_warrant_example():
    res = hk_examples.hk_inline_warrant()
    assert res["status"] == "ok", res
    assert res["value"] > 0


def test_hk_loss_making_example():
    res = hk_examples.hk_loss_making_company()
    assert res["status"] == "ok", res
    assert "dispersion" in res
