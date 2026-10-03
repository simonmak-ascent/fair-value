"""AC-9: the shared result/error envelope shape."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from valuation_engine import _error, _ok


def test_ok_envelope_shape():
    env = _ok("DCF", "AAPL", value_per_share=1.0)
    assert env["status"] == "ok"
    assert env["method"] == "DCF"
    assert env["ticker"] == "AAPL"
    assert env["value_per_share"] == 1.0


def test_ok_envelope_allows_no_ticker():
    env = _ok("review")
    assert env["status"] == "ok"
    assert env["ticker"] is None


def test_error_envelope_shape():
    env = _error("UNKNOWN_METHOD", "bad method", method="DCF", ticker="X")
    assert env["status"] == "error"
    assert env["method"] == "DCF"
    assert env["ticker"] == "X"
    assert env["error"]["code"] == "UNKNOWN_METHOD"
    assert env["error"]["message"] == "bad method"


def test_error_envelope_message_is_string():
    value: object = 123
    env = _error("INVALID_ARGUMENT", value)
    assert isinstance(env["error"]["message"], str)
