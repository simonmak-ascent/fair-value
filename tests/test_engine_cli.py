"""AC-6 / AC-6E: command-line parity and error handling."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def _run(args):
    return subprocess.run(
        [sys.executable, "valuation_engine.py", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_help_exits_zero():
    res = _run(["--help"])
    assert res.returncode == 0


def test_cli_no_args_nonzero_no_traceback():
    res = _run([])
    assert res.returncode != 0
    assert "Traceback" not in res.stderr


def test_cli_unknown_method_no_traceback():
    res = _run(["--ticker", "X", "--method", "bogus"])
    assert res.returncode == 0
    assert "Traceback" not in res.stdout
    assert "Traceback" not in res.stderr
    assert "UNKNOWN_METHOD" in res.stdout
