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


def test_dcf_market_result_is_timestamped(fake_provider, monkeypatch):
    import src.valuation.dcf as dcf_mod

    monkeypatch.setattr(
        dcf_mod,
        "dcf_from_market_data",
        lambda ticker, metrics, wacc=0.10, terminal_growth=0.025, years=5: {
            "value_per_share": 10.0,
            "enterprise_value": 1.0,
            "equity_value": 1.0,
            "wacc": wacc,
            "terminal_growth": terminal_growth,
        },
    )
    res = ve.run_valuation("T", "dcf", {})
    assert res["data_timestamp"]


def test_review_result_carries_disclaimer(monkeypatch, tmp_path):
    import src.report_review.excel_analyzer as ea

    monkeypatch.setattr(ea, "analyze_excel_model", lambda p: {"analyzer": "excel"})
    f = tmp_path / "m.xlsx"
    f.write_text("x")

    res = ve.review_report(str(f))
    assert res["analyzer"] == "excel"
    assert res["disclaimer"] == DISCLAIMER


def test_summary_carries_disclaimer_and_timestamp(fake_provider):
    res = fake_provider.get_valuation_summary("T")
    assert res["disclaimer"] == DISCLAIMER
    assert res["data_timestamp"]
