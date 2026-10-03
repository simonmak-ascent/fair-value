"""A-011: report-review guards (input validation, macro rejection, injection scan)."""

import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.report_review import guards  # noqa: E402


# --- validate_path ---------------------------------------------------------


def test_validate_path_missing(tmp_path):
    with pytest.raises(guards.InputValidationError) as ei:
        guards.validate_path(str(tmp_path / "nope.xlsx"))
    assert ei.value.code == "FILE_NOT_FOUND"


def test_validate_path_empty(tmp_path):
    f = tmp_path / "e.xlsx"
    f.write_bytes(b"")
    with pytest.raises(guards.InputValidationError) as ei:
        guards.validate_path(str(f))
    assert ei.value.code == "EMPTY_FILE"


def test_validate_path_directory(tmp_path):
    with pytest.raises(guards.InputValidationError) as ei:
        guards.validate_path(str(tmp_path))
    # A symlinked temp dir may resolve differently; accept either safe rejection.
    assert ei.value.code in {"NOT_A_FILE", "SYMLINK_REJECTED"}


def test_validate_path_too_large(tmp_path):
    f = tmp_path / "big.xlsx"
    f.write_bytes(b"xx")
    with pytest.raises(guards.InputValidationError) as ei:
        guards.validate_path(str(f), max_bytes=1)
    assert ei.value.code == "FILE_TOO_LARGE"


def test_validate_path_unsupported_type(tmp_path):
    f = tmp_path / "x.txt"
    f.write_bytes(b"x")
    with pytest.raises(guards.InputValidationError) as ei:
        guards.validate_path(str(f), allowed_exts={".xlsx"})
    assert ei.value.code == "UNSUPPORTED_FILE_TYPE"


def test_validate_path_ok(tmp_path):
    f = tmp_path / "ok.xlsx"
    f.write_bytes(b"x")
    assert (
        guards.validate_path(str(f)) == f.resolve()
        or guards.validate_path(str(f)).name == "ok.xlsx"
    )


def test_validate_path_rejects_symlink(tmp_path):
    target = tmp_path / "real.xlsx"
    target.write_bytes(b"x")
    link = tmp_path / "link.xlsx"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not supported on this platform")
    with pytest.raises(guards.InputValidationError) as ei:
        guards.validate_path(str(link))
    assert ei.value.code == "SYMLINK_REJECTED"


# --- detect_macros ---------------------------------------------------------


def _ooxml(path: Path, extra_member: str | None = None) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        if extra_member:
            zf.writestr(extra_member, b"\x00")
    return path


def test_detect_macros_clean(tmp_path):
    f = _ooxml(tmp_path / "clean.xlsx")
    res = guards.detect_macros(str(f))
    assert res["has_macros"] is False
    assert res["is_macro_capable"] is False


def test_detect_macros_embedded_vba(tmp_path):
    f = _ooxml(tmp_path / "evil.xlsx", extra_member="xl/vbaProject.bin")
    res = guards.detect_macros(str(f))
    assert res["has_macros"] is True
    assert res["sources"] == ["xl/vbaProject.bin"]


def test_detect_macros_capable_extension(tmp_path):
    # A .xlsm without a parseable container is still flagged macro-capable.
    f = tmp_path / "sheet.xlsm"
    f.write_bytes(b"not-a-zip")
    res = guards.detect_macros(str(f))
    assert res["is_macro_capable"] is True


# --- find_injection_indicators ---------------------------------------------


@pytest.mark.parametrize(
    "value,token",
    [
        ('=WEBSERVICE("http://evil")', "WEBSERVICE"),
        ('=IMPORTDATA("http://x")', "IMPORTDATA"),
        ('=HYPERLINK("http://x")', "HYPERLINK("),
        ('=RTD("prog","server")', "RTD("),
    ],
)
def test_find_injection_indicators(value, token):
    assert token in guards.find_injection_indicators(value)


def test_find_injection_indicators_clean():
    assert guards.find_injection_indicators("=SUM(A1:A5)") == []
    assert guards.find_injection_indicators(42) == []


# --- engine integration ----------------------------------------------------


def test_engine_rejects_macro_enabled_workbook(tmp_path):
    import valuation_engine as ve

    f = _ooxml(tmp_path / "model.xlsx", extra_member="xl/vbaProject.bin")
    res = ve.review_report(str(f))
    assert res["status"] == "error"
    assert res["error"]["code"] == "MACROS_DETECTED"


def test_engine_rejects_empty_file(tmp_path):
    import valuation_engine as ve

    f = tmp_path / "empty.xlsx"
    f.write_bytes(b"")
    res = ve.review_report(str(f))
    assert res["status"] == "error"
    assert res["error"]["code"] == "EMPTY_FILE"


# --- excel analyzer integration -------------------------------------------


def test_excel_analyzer_flags_injection(tmp_path):
    pytest.importorskip("openpyxl")
    from openpyxl import Workbook

    from src.report_review import excel_analyzer as ea

    f = tmp_path / "model.xlsx"
    wb = Workbook()
    ws = wb.active
    ws["A1"] = '=WEBSERVICE("http://evil")'
    wb.save(f)

    res = ea.analyze_excel_model(str(f))
    assert res["status"] == "success"
    tokens = [t for item in res["security"]["injection_indicators"] for t in item["tokens"]]
    assert "WEBSERVICE" in tokens


def test_excel_analyzer_rejects_macro(tmp_path):
    pytest.importorskip("openpyxl")
    from src.report_review import excel_analyzer as ea

    f = _ooxml(tmp_path / "m.xlsx", extra_member="xl/vbaProject.bin")
    res = ea.analyze_excel_model(str(f))
    assert res["status"] == "error"
    assert res["code"] == "MACROS_DETECTED"
