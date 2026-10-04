"""Generate transparency docs from the registry + standards corpus (A-006).

Writes, deterministically:
  - docs/methods/<tool>.md   (per-tool help page, with a mermaid diagram)
  - docs/methods/index.md    (index of tools)
  - docs/standards.md        (standards, clauses and the methods that cite them)

Run from the repo root: ``python scripts/gen_docs.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mcp_server import docs as docs_mod  # noqa: E402
from mcp_server import method_spec as ms  # noqa: E402

OUT = ROOT / "docs" / "methods"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def generate() -> list:
    written = []
    index_lines = ["# Method reference", "", "Generated from the method registry.", ""]
    for tool in ms.tools():
        meta = ms.tool_meta(tool)
        text = docs_mod.tool_help_markdown(tool)
        path = OUT / f"{tool}.md"
        _write(path, text)
        written.append(path)
        index_lines.append(
            f"- [{meta.get('title', tool)}]({tool}.md) — {meta.get('description', '')}"
        )
    _write(OUT / "index.md", "\n".join(index_lines) + "\n")
    written.append(OUT / "index.md")

    rec = docs_mod.standards_index()
    std_lines = ["# Standards reference", "", "## Standards", ""]
    std_lines += ["| Standard | Title | Edition |", "|----------|-------|---------|"]
    for s in rec["standards"]:
        std_lines.append(f"| {s['id']} | {s['title']} | {s['edition']} |")
    std_lines += [
        "",
        "## Clauses",
        "",
        "| Clause | Label | Cited by |",
        "|--------|-------|----------|",
    ]
    for c in rec["clauses"]:
        methods = ", ".join(f"`{m}`" for m in c["methods"]) or "—"
        std_lines.append(f"| `{c['id']}` | {c['label']} | {methods} |")
    _write(ROOT / "docs" / "standards.md", "\n".join(std_lines) + "\n")
    written.append(ROOT / "docs" / "standards.md")
    return written


if __name__ == "__main__":
    paths = generate()
    print(f"generated {len(paths)} files")
