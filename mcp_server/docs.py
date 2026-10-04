"""Registry-driven transparency documentation (VDD A-006).

Builds a per-tool help record and Markdown page from the method registry
(`method_spec`) joined with the standards taxonomy + corpus (`standards`): tool
description, each method's inputs, formula reference, approach, solution type,
**verbatim** IVS/IFRS clause quotes with provenance, divergence parameters,
model risks/limits, a required-input example, and a mermaid diagram.

Consumed by the `-help` argument (via the engine) and by `scripts/gen_docs.py`
(GitHub docs). Offline and deterministic.
"""

from __future__ import annotations

from typing import Any, Dict, List

from . import method_spec as ms
from . import standards as std


def _clause_help(clause_id: str) -> Dict[str, Any]:
    taxonomy = getattr(ms, "_TAXONOMY", None)
    if taxonomy is None:
        return {"id": clause_id, "label": "", "text": "", "rights_holder": ""}
    try:
        info = std.clause_text(taxonomy, clause_id)
    except (KeyError, std.TaxonomyError, FileNotFoundError):
        return {"id": clause_id, "label": "", "text": "", "rights_holder": ""}
    clause = taxonomy.clauses[clause_id]
    return {
        "id": clause_id,
        "label": clause.label,
        "summary": clause.summary,
        "text": info["text"],
        "source_ref": clause.source_ref,
        "rights_holder": info["provenance"].rights_holder,
        "url": info["provenance"].url,
    }


def _risks(spec: Any) -> List[str]:
    risks: List[str] = []
    if spec.solution_type == "simulation":
        risks.append(
            "Monte-Carlo (simulation): the value is an estimate from a seeded sample; "
            "re-run with the same seed to reproduce, and treat the distribution, not the "
            "point value, as the result."
        )
    elif spec.solution_type in ("closed_form", "numeric"):
        risks.append(
            "Deterministic model: the result is a point value with no modelled "
            "distribution; input error and model error are not quantified here."
        )
    for div in spec.divergences or ():
        param = getattr(div, "parameter", div)
        risks.append(
            f"IVS/IFRS divergence on '{param}': the two regimes treat this differently "
            f"({getattr(div, 'ivs_basis', '')} vs {getattr(div, 'ifrs_basis', '')}); "
            "the choice is the caller's, not a default."
        )
    if spec.standards:
        risks.append("Standards alignment is declared per method; see the cited clauses.")
    return risks


def method_help(tool: str, method: str) -> Dict[str, Any]:
    """Return the transparency record for one method."""
    spec = ms.get(tool, method)
    if spec is None:
        raise KeyError(f"unknown method '{method}' for {tool}")
    citations = getattr(spec, "citations", None) or {}
    clause_ids = list(citations.get("ivs", ())) + list(citations.get("ifrs", ()))
    inputs = []
    for name in spec.required:
        schema = ms.PARAMS.get(name, {})
        inputs.append(
            {
                "name": name,
                "type": schema.get("type", "any"),
                "description": schema.get("description", ""),
            }
        )
    return {
        "tool": tool,
        "method": method,
        "summary": spec.summary,
        "formula_ref": spec.formula_ref,
        "approach": getattr(spec, "approach", None),
        "solution_type": getattr(spec, "solution_type", None),
        "standards": list(spec.standards),
        "inputs": inputs,
        "required": list(spec.required),
        "citations": [_clause_help(cid) for cid in clause_ids],
        "divergences": [
            {
                "parameter": getattr(d, "parameter", str(d)),
                "ivs_basis": getattr(d, "ivs_basis", ""),
                "ifrs_basis": getattr(d, "ifrs_basis", ""),
            }
            for d in (spec.divergences or ())
        ],
        "risks": _risks(spec),
        "example": {"method": method, "arguments": {name: None for name in spec.required}},
    }


def _mermaid(tool: str, methods: List[Dict[str, Any]]) -> str:
    lines = ["flowchart TD", f"  T[{' '.join(tool.split('_')).title()}]"]
    for entry in methods:
        mid = f"{tool}_{entry['method']}"
        approach = entry.get("approach") or "n/a"
        lines.append(f'  T --> {mid}["{entry["method"]} ({approach})"]')
        for cite in entry["citations"]:
            cid = cite["id"].replace(".", "_")
            lines.append(f"  {mid} -. cites .-> {cid}[{cite['id']}]")
    return "\n".join(lines)


def tool_help(tool: str) -> Dict[str, Any]:
    """Return the transparency record for a whole tool."""
    methods = [method_help(tool, m) for m in ms.methods_for(tool)]
    meta = ms.tool_meta(tool)
    return {
        "tool": tool,
        "title": meta.get("title", tool),
        "description": meta.get("description", ""),
        "surface": ms.surface_kind(tool),
        "methods": methods,
        "mermaid": _mermaid(tool, methods),
    }


def tool_help_markdown(tool: str) -> str:
    """Render a tool's help record as a Markdown page (with a mermaid block)."""
    record = tool_help(tool)
    out: List[str] = [f"# {record['title']}", "", record["description"], ""]
    out += ["```mermaid", record["mermaid"], "```", ""]
    for entry in record["methods"]:
        out.append(f"## `{entry['method']}`")
        out.append("")
        out.append(entry["summary"])
        out.append("")
        if entry["formula_ref"]:
            out.append(f"**Formula:** {entry['formula_ref']}")
            out.append("")
        out.append(f"**Approach:** {entry.get('approach') or 'n/a'}  ")
        out.append(f"**Solution:** {entry.get('solution_type') or 'n/a'}")
        out.append("")
        out.append("**Inputs**")
        out.append("")
        out.append("| Name | Type | Description |")
        out.append("|------|------|-------------|")
        for inp in entry["inputs"]:
            out.append(f"| `{inp['name']}` | {inp['type']} | {inp['description']} |")
        out.append("")
        if entry["citations"]:
            out.append("**Standards (verbatim)**")
            out.append("")
            for cite in entry["citations"]:
                out.append(f"- **{cite['id']}** — {cite.get('label', '')}")
                if cite.get("text"):
                    quote = " ".join(cite["text"].split())
                    out.append(f"  > {quote}")
                if cite.get("rights_holder"):
                    out.append(f"  > — {cite['rights_holder']} ({cite.get('source_ref', '')})")
            out.append("")
        if entry["divergences"]:
            out.append("**IVS ↔ IFRS/IAS divergences**")
            out.append("")
            for div in entry["divergences"]:
                out.append(
                    f"- `{div['parameter']}`: IVS — {div['ivs_basis']}; "
                    f"IFRS/IAS — {div['ifrs_basis']}"
                )
            out.append("")
        out.append("**Risks & limits**")
        out.append("")
        for risk in entry["risks"]:
            out.append(f"- {risk}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def standards_index() -> Dict[str, Any]:
    """Return the standards/clause/method index for the docs."""
    taxonomy = getattr(ms, "_TAXONOMY", None)
    if taxonomy is None:
        return {"standards": [], "clauses": []}
    clauses = []
    for cid, clause in sorted(taxonomy.clauses.items()):
        clauses.append(
            {
                "id": cid,
                "standard": clause.standard,
                "label": clause.label,
                "summary": clause.summary,
                "source_ref": clause.source_ref,
                "methods": std.methods_for(taxonomy, cid),
            }
        )
    standards = [
        {
            "id": s.id,
            "title": s.title,
            "family": s.family,
            "edition": s.version,
            "source_ref": s.source_ref,
        }
        for s in sorted(taxonomy.standards.values(), key=lambda x: x.id)
    ]
    return {"standards": standards, "clauses": clauses}
