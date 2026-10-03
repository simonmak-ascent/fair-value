"""Report-review rule engine.

Audits a valuation document against an IVS 2025 / IFRS(HKFRS) checklist. Plain
text and Markdown are checked with a dependency-free keyword engine; PDF, Word
and Excel files are routed to the existing analyzers when their optional
dependencies are installed. Macro-enabled Office files are refused.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Tuple

from . import guards

#: Minimal standards taxonomy referenced by findings.
STANDARDS: Dict[str, str] = {
    "IVS 2025": "International Valuation Standards 2025 (IVS 101-105).",
    "IFRS 13": "Fair value measurement: exit price, market participants, hierarchy.",
    "IFRS 9": "Financial instruments: classification, impairment (ECL), fair value.",
    "IAS 36": "Impairment of assets: recoverable amount = max(value in use, fair value less costs).",
    "IAS 37": "Provisions, contingent liabilities: best estimate, discounting.",
    "IAS 32": "Financial instruments: presentation (puttables, SPAC redemption).",
    "IFRS 2": "Share-based payment: fair value at grant date.",
    "IFRS 17": "Insurance contracts: fulfilment cash flows, risk adjustment.",
    "HKFRS": "Hong Kong Financial Reporting Standards (local IFRS equivalent).",
}

_REQUIRED = (
    ("methodology", "error", "Name the valuation methodology (DCF/NAV/CCA/market).", "IVS 2025"),
    ("assumptions", "error", "State key assumptions (growth, margins, discount rate).", "IVS 2025"),
    ("discount", "error", "Provide the discount/cost-of-capital basis (WACC/Ke).", "IVS 2025"),
    ("standards", "warning", "Cite the reporting basis (IFRS/HKFRS/IVS).", "IFRS 13"),
    ("fair value", "error", "Give a primary value conclusion / fair value range.", "IFRS 13"),
    ("date", "warning", "State the valuation date and data timestamp.", "IVS 2025"),
    ("hierarchy", "info", "Describe the fair-value hierarchy level for key inputs.", "IFRS 13"),
)


#: HKFRS-specific disclosures checked in addition to the base checklist.
_HKFRS = (
    (
        "investment property",
        "HKAS 40",
        "Investment property should be stated at fair value (HKAS 40).",
    ),
    ("goodwill", "HKAS 36", "Goodwill impairment testing should reference HKAS 36."),
    (
        "expected credit loss",
        "HKFRS 9",
        "Financial assets should be assessed for expected credit losses (HKFRS 9).",
    ),
)


def _text_rules(text: str) -> Tuple[List[Dict[str, Any]], float]:
    low = text.lower()
    findings: List[Dict[str, Any]] = []
    present = 0
    for token, severity, message, standard in _REQUIRED:
        found = token in low
        present += int(found)
        findings.append(
            {
                "rule": token,
                "status": "present" if found else "missing",
                "severity": severity if not found else "info",
                "message": message if not found else f"Found reference to '{token}'.",
                "standard": standard,
            }
        )
    hkfrs = ("hkfrs" in low) or ("hkas" in low)
    if hkfrs:
        for topic, standard, message in _HKFRS:
            if topic in low and standard.lower() not in low:
                findings.append(
                    {
                        "rule": f"hkfrs:{topic}",
                        "status": "missing",
                        "severity": "warning",
                        "message": message,
                        "standard": standard,
                    }
                )
    score = round(100 * present / len(_REQUIRED), 1)
    return findings, score


def _route(path: str) -> Dict[str, Any]:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md", ".markdown"):
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            text = handle.read()
        findings, score = _text_rules(text)
        low = text.lower()
        basis = "HKFRS" if ("hkfrs" in low or "hkas" in low) else "IFRS/unspecified"
        return {
            "file_type": ext.lstrip("."),
            "score": score,
            "reporting_basis": basis,
            "findings": findings,
            "text_length": len(text),
        }
    if ext == ".pdf":
        from . import pdf_analyzer

        result = pdf_analyzer.analyze_pdf_report(path)
        return {"file_type": "pdf", "score": None, "analysis": result}
    if ext in (".docx", ".doc"):
        from . import word_analyzer

        result = word_analyzer.analyze_word_report(path)
        return {"file_type": "word", "score": None, "analysis": result}
    if ext in (".xlsx", ".xlsm", ".xls"):
        from . import excel_analyzer

        result = excel_analyzer.analyze_excel_model(path)
        return {"file_type": "excel", "score": None, "analysis": result}
    raise ValueError(f"unsupported report type {ext!r}")


def audit_report(file_path: str) -> Dict[str, Any]:
    resolved = str(guards.validate_path(file_path))
    macros = guards.detect_macros(resolved)
    if macros.get("has_macros"):
        raise ValueError("macro-enabled Office files are refused")
    outcome = _route(resolved)
    findings = outcome.get("findings", [])
    errors = [f for f in findings if f.get("severity") == "error" and f.get("status") == "missing"]
    return {
        "value": outcome.get("score"),
        "findings": findings,
        "error_count": len(errors),
        "standards": STANDARDS,
        **outcome,
    }


_OUTLINES: Dict[str, List[str]] = {
    "dcf": [
        "Scope and basis of value (IVS 101-102)",
        "Company and industry overview",
        "Financial projections and drivers",
        "Discount rate (WACC) build-up",
        "Terminal value and assumptions",
        "Fair value per share and sensitivity",
        "Sources of data and valuation date",
    ],
    "market": [
        "Scope and basis of value",
        "Peer selection and screening",
        "Multiples applied and justification",
        "Implied value range",
        "Control/illiquidity adjustments (IFRS 13)",
        "Conclusion and valuation date",
    ],
    "credit": [
        "Scope and reporting basis (IFRS 9 / HKFRS 9)",
        "Exposure, PD, LGD and EAD",
        "Staging and lifetime vs 12-month ECL",
        "Forward-looking information and scenarios",
        "Resulting provision and disclosure",
    ],
    "report_review": [
        "Document identification and valuation date",
        "Methodology identified",
        "Assumption and input checks",
        "Discount-rate and terminal-value checks",
        "Standards basis (IVS / IFRS / HKFRS)",
        "Findings, severities and conclusion",
    ],
}


def draft_report(report_type: str) -> Dict[str, Any]:
    """Return the required section structure for a valuation report type."""
    sections = _OUTLINES.get(report_type)
    if sections is None:
        raise ValueError(f"report_type must be one of {sorted(_OUTLINES)}")
    markdown = "\n".join(f"## {i + 1}. {name}" for i, name in enumerate(sections))
    return {"value": markdown, "report_type": report_type, "sections": sections}
