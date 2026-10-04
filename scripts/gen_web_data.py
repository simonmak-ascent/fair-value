#!/usr/bin/env python3
"""Generate ``data/catalog.json`` for the Next.js frontage.

Offline and deterministic: reads the method-spec registry, the standards
taxonomy and the generated help records — the same single source of truth as
the MCP server and the docs generator. No ``src``/network import, so it is safe
to run as a Next.js ``prebuild`` step.

    python3 scripts/gen_web_data.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from mcp_server import docs as mdocs  # noqa: E402
from mcp_server import method_spec as ms  # noqa: E402
from mcp_server import standards as std  # noqa: E402
from mcp_server.deferred import deferred_method_ids  # noqa: E402

OUT = ROOT / "data" / "catalog.json"


def _clause_standard_map() -> dict[str, str]:
    return {c.id: c.standard for c in ms._TAXONOMY.clauses.values()}


def build() -> dict:
    catalog = ms.catalog()
    index = mdocs.standards_index()
    coverage = std.coverage_report(ms._REGISTRY, ms._TAXONOMY)
    clause_standard = _clause_standard_map()
    deferred = deferred_method_ids()

    tools = []
    methods = []
    for tool in ms.tools():
        meta = ms.tool_meta(tool)
        tool_methods = list(ms.methods_for(tool))
        tools.append(
            {
                "id": tool,
                "title": meta.get("title", tool),
                "description": meta.get("description", ""),
                "surface": ms.surface_kind(tool),
                "methods": tool_methods,
            }
        )
        for method in tool_methods:
            help_rec = mdocs.method_help(tool, method)
            citations = [
                {
                    "id": c.get("id", ""),
                    "standard": clause_standard.get(c.get("id", ""), ""),
                    "label": c.get("label", ""),
                    "summary": c.get("summary", ""),
                }
                for c in help_rec.get("citations", [])
            ]
            methods.append(
                {
                    "tool": tool,
                    "method": method,
                    "summary": help_rec.get("summary", ""),
                    "formula_ref": help_rec.get("formula_ref", ""),
                    "approach": help_rec.get("approach", ""),
                    "solution_type": help_rec.get("solution_type", ""),
                    "standards": help_rec.get("standards", []),
                    "inputs": help_rec.get("inputs", []),
                    "required": help_rec.get("required", []),
                    "citations": citations,
                    "risks": help_rec.get("risks", []),
                    "implemented": method not in deferred,
                }
            )

    clauses = []
    for clause in index.get("clauses", []):
        cid = clause["id"]
        clauses.append(
            {
                "id": cid,
                "standard": clause.get("standard") or clause_standard.get(cid, ""),
                "label": clause.get("label", ""),
                "summary": clause.get("summary", ""),
                "text": std.clause_text(ms._TAXONOMY, cid)["text"],
                "cited_by": clause.get("methods", []),
            }
        )

    total = coverage["total_methods"]
    return {
        "surface_version": catalog["surface_version"],
        "generated_from": "mcp_server.method_spec + standards.taxonomy",
        "counts": {
            "tools": catalog["tool_count"],
            "methods": total,
            "implemented": total - len(deferred),
            "deferred": len(deferred),
            "cited": coverage["cited_methods"],
            "uncited": len(coverage["uncited_methods"]),
            "orphan_clauses": len(coverage["orphan_clauses"]),
            "clauses": len(clauses),
        },
        "standards": index.get("standards", []),
        "clauses": clauses,
        "tools": tools,
        "methods": methods,
    }


def main() -> int:
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    c = data["counts"]
    print(
        f"wrote {OUT.relative_to(ROOT)}: {c['tools']} tools, {c['methods']} methods, "
        f"{c['cited']} cited, {c['clauses']} clauses"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
