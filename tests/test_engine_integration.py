"""AC-8: end-to-end offline integration across all operations."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import valuation_engine as ve


def test_all_operations_offline(dcf_inputs, peer_metrics, unlisted_holding):
    dcf = ve.run_valuation("T", "dcf", dcf_inputs)
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
