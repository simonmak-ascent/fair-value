"""AC-4: report review dispatch by file type."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import valuation_engine as ve


def test_review_routes_to_excel(monkeypatch, tmp_path):
    import src.report_review.excel_analyzer as ea

    monkeypatch.setattr(
        ea, "analyze_excel_model", lambda p: {"analyzer": "excel", "path": p}
    )
    f = tmp_path / "model.xlsx"
    f.write_text("x")

    res = ve.review_report(str(f))
    assert res.get("analyzer") == "excel"


def test_review_routes_to_pdf(monkeypatch, tmp_path):
    import src.report_review.pdf_analyzer as pa

    monkeypatch.setattr(pa, "analyze_pdf_report", lambda p: {"analyzer": "pdf"})
    f = tmp_path / "report.pdf"
    f.write_text("x")

    assert ve.review_report(str(f)).get("analyzer") == "pdf"


def test_review_routes_to_word(monkeypatch, tmp_path):
    import src.report_review.word_analyzer as wa

    monkeypatch.setattr(wa, "analyze_word_report", lambda p: {"analyzer": "word"})
    f = tmp_path / "report.docx"
    f.write_text("x")

    assert ve.review_report(str(f)).get("analyzer") == "word"


def test_review_routes_to_image(monkeypatch, tmp_path):
    import src.report_review.image_analyzer as ia

    monkeypatch.setattr(ia, "extract_valuation_data", lambda p: {"analyzer": "image"})
    f = tmp_path / "scan.png"
    f.write_text("x")

    assert ve.review_report(str(f)).get("analyzer") == "image"


def test_review_unsupported_type(tmp_path):
    f = tmp_path / "notes.txt"
    f.write_text("x")
    res = ve.review_report(str(f))
    assert res["status"] == "error"
    assert res["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_review_missing_file():
    res = ve.review_report("/no/such/file.xlsx")
    assert res["status"] == "error"
    assert res["error"]["code"] == "FILE_NOT_FOUND"


def test_review_empty_path():
    res = ve.review_report("")
    assert res["status"] == "error"
    assert res["error"]["code"] == "INVALID_ARGUMENT"
