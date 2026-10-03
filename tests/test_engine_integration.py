"""AC-8: end-to-end offline integration across all operations."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import valuation_engine as ve


def test_all_operations_offline(
    fake_provider, monkeypatch, peer_metrics, unlisted_holding
):
    import src.valuation.dcf as dcf_mod

    monkeypatch.setattr(
        dcf_mod,
        "dcf_from_market_data",
        lambda ticker, metrics, wacc=0.10, terminal_growth=0.025, years=5: {
            "value_per_share": 10.0,
            "enterprise_value": 1000.0,
            "equity_value": 900.0,
            "wacc": wacc,
            "terminal_growth": terminal_growth,
        },
    )

    dcf = ve.run_valuation("T", "dcf", {})
    nav = ve.run_valuation(
        "T",
        "nav",
        {"holdings": [unlisted_holding], "liabilities": 0, "shares_outstanding": 10},
    )
    cca = ve.run_valuation(
        "T",
        "cca",
        {"target_metrics": {"eps": 5.0}, "peer_metrics": peer_metrics},
    )

    assert dcf["status"] == "ok"
    assert nav["status"] == "ok"
    assert cca["status"] == "ok"
    assert ve.review_report("does-not-exist.pdf")["status"] == "error"
    assert ve.get_valuation_summary("T")["status"] == "ok"
