"""A-006: shared result envelope, disclaimer, and provenance timestamp."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from src.output.result import (
    DISCLAIMER,
    error,
    missing_ok_fields,
    ok,
    utc_now_iso,
)

import valuation_engine as ve


def test_ok_has_all_required_fields():
    env = ok("DCF", "T", value=1.0)
    assert missing_ok_fields(env) == []
    assert env["disclaimer"] == DISCLAIMER


def test_ok_keeps_extra_fields():
    env = ok("DCF", "T", value=1.0, value_per_share=1.0)
    assert env["value_per_share"] == 1.0


def test_error_coerces_message_and_carries_code():
    env = error("MISSING_INPUT", 123)
    assert env["error"]["code"] == "MISSING_INPUT"
    assert isinstance(env["error"]["message"], str)
    assert env["disclaimer"] == DISCLAIMER


def test_missing_ok_fields_detects_incomplete():
    assert "value" in missing_ok_fields({"status": "ok"})


def test_utc_now_iso_format():
    stamp = utc_now_iso()
    assert stamp.endswith("Z") and "T" in stamp


def test_dcf_explicit_envelope_is_complete(dcf_inputs):
    res = ve.run_valuation("T", "dcf", dcf_inputs)
    assert missing_ok_fields(res) == []
    assert res["disclaimer"] == DISCLAIMER
