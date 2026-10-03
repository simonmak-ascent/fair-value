"""Contract completeness: scan_directory behavior (TASK-017)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import valuation_engine as ve


def test_scan_finds_files(tmp_path):
    (tmp_path / "model.xlsx").write_text("x")
    (tmp_path / "report.pdf").write_text("x")

    results = ve.scan_directory(str(tmp_path))
    names = {Path(r["path"]).name for r in results if "path" in r}
    assert {"model.xlsx", "report.pdf"} <= names


def test_scan_missing_directory_returns_error_entry():
    results = ve.scan_directory("/no/such/dir/xyz-123")
    assert isinstance(results, list)
    assert results
    assert results[0]["error"]["code"] == "INVALID_ARGUMENT"
