"""A-006: registry-driven transparency docs and the `-help` argument."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from mcp_server import docs  # noqa: E402
from mcp_server.engine import dispatch  # noqa: E402


def test_tool_help_shape():
    record = docs.tool_help("calculate_dcf")
    assert record["tool"] == "calculate_dcf"
    assert record["title"]
    assert record["methods"]
    assert "flowchart" in record["mermaid"]
    dcf = next(m for m in record["methods"] if m["method"] == "dcf")
    assert dcf["approach"] == "income"
    assert dcf["solution_type"] == "closed_form"
    assert dcf["risks"]
    assert {i["name"] for i in dcf["inputs"]} == {"cash_flows", "discount_rate"}


def test_tool_help_markdown_has_equation_clause_and_mermaid():
    text = docs.tool_help_markdown("calculate_dcf")
    assert "```mermaid" in text
    assert "**Formula:**" in text
    assert "IVS.103.A20" in text
    # Verbatim clause wording from the corpus is quoted.
    assert "income approach provides an indication of value" in text


def test_divergence_surfaces_in_risks():
    record = docs.tool_help("calculate_dcf")
    viu = next(m for m in record["methods"] if m["method"] == "viu_pre_tax")
    assert viu["divergences"]
    assert any("discount_rate" in r for r in viu["risks"])


def test_dispatch_help_returns_generated_docs():
    res = dispatch("calculate_dcf", {"method": "-help"})
    assert res["status"] == "ok"
    assert res["help"]["tool"] == "calculate_dcf"
    assert "```mermaid" in res["text"]

    res2 = dispatch("calculate_dcf", {"method": "dcf", "help": True})
    assert res2["status"] == "ok"
    assert res2["help"]["tool"] == "calculate_dcf"


def test_standards_index_lists_clauses():
    rec = docs.standards_index()
    ids = {c["id"] for c in rec["clauses"]}
    assert "IVS.210.A10" in ids and "IAS.36.18" in ids
    asm = next(c for c in rec["clauses"] if c["id"] == "IAS.36.18")
    assert "recoverable_amount" in asm["methods"]


def test_generated_docs_present():
    assert (_ROOT / "docs" / "methods" / "index.md").is_file()
    assert (_ROOT / "docs" / "standards.md").is_file()
    assert "IVS.210.A10" in (_ROOT / "docs" / "standards.md").read_text(encoding="utf-8")
