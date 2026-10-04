"""Tests for the dual-standard taxonomy and citation registry (VDD A-001).

Covers spec `vdd/specs/A-001/spec.md`: AC-1, AC-E1, AC-2, AC-3, AC-4, AC-E2,
AC-5, plus the registry integration (TASK-006).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcp_server import method_spec
from mcp_server.method_spec import MethodSpec
from mcp_server.standards import (
    TaxonomyError,
    attach_standards,
    audit_citations,
    citations_for,
    load_taxonomy,
    methods_for,
    validate_taxonomy,
)

REPO = Path(__file__).resolve().parent.parent
TAXONOMY_PATH = REPO / "standards" / "taxonomy.json"


def _write(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "taxonomy.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _base(standards, clauses, methods) -> dict:
    return {
        "version": "test.1",
        "standards": standards,
        "clauses": clauses,
        "methods": methods,
    }


IVS_STD = {
    "id": "IVS",
    "title": "IVS",
    "family": "IVS",
    "version": "2025",
    "source_ref": "source/ivs-2025.md",
}
IFRS_STD = {
    "id": "IFRS",
    "title": "IFRS 13",
    "family": "IFRS",
    "version": "2025",
    "source_ref": "source/ifrs-13.md",
}
IVS_CLAUSE = {
    "id": "IVS.103.A20",
    "standard": "IVS",
    "label": "DCF",
    "summary": "PV of cash flows",
    "source_ref": "source/ivs-2025.md#ivs-103-income-approach",
}
IFRS_CLAUSE = {
    "id": "IFRS.13.61",
    "standard": "IFRS",
    "label": "Techniques",
    "summary": "Approaches",
    "source_ref": "source/ifrs-13.md#paragraph-61",
}


# --------------------------------------------------------------------------- #
# AC-1 / AC-5: load + validate + determinism
# --------------------------------------------------------------------------- #
def test_default_taxonomy_loads_and_validates():
    taxonomy = load_taxonomy()
    assert taxonomy.version
    assert "IVS" in taxonomy.standards
    assert "IVS.103.A20" in taxonomy.clauses
    # AC-1: joins cleanly against the real registry, sources resolvable.
    validate_taxonomy(taxonomy, method_spec._REGISTRY)


def test_load_missing_explicit_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_taxonomy(tmp_path / "nope.json")


def test_duplicate_clause_id_raises(tmp_path):
    data = _base(
        [IVS_STD, IFRS_STD],
        [IVS_CLAUSE, dict(IVS_CLAUSE)],
        [],
    )
    with pytest.raises(TaxonomyError) as exc:
        load_taxonomy(_write(tmp_path, data))
    assert "TAXONOMY_DUPLICATE_ID" in str(exc.value)


def test_load_is_deterministic():
    a = load_taxonomy()
    b = load_taxonomy()
    assert json.dumps({k: v.ivs for k, v in a.methods.items()}, sort_keys=True) == json.dumps(
        {k: v.ivs for k, v in b.methods.items()}, sort_keys=True
    )
    assert methods_for(a, "IVS.103.A20") == methods_for(b, "IVS.103.A20")


# --------------------------------------------------------------------------- #
# AC-E1: unknown references / bad enums
# --------------------------------------------------------------------------- #
def test_unknown_clause_reference_raises_on_load(tmp_path):
    data = _base(
        [IVS_STD, IFRS_STD],
        [IVS_CLAUSE, IFRS_CLAUSE],
        [
            {
                "method_id": "dcf",
                "approach": "income",
                "citations": {"ivs": ["IVS.999.9"], "ifrs": ["IFRS.13.61"]},
                "solution_type": "closed_form",
            }
        ],
    )
    with pytest.raises(TaxonomyError) as exc:
        load_taxonomy(_write(tmp_path, data))
    assert "TAXONOMY_UNKNOWN_CLAUSE" in str(exc.value)


def test_unknown_method_reference_raises_on_validate(tmp_path):
    data = _base(
        [IVS_STD, IFRS_STD],
        [IVS_CLAUSE, IFRS_CLAUSE],
        [
            {
                "method_id": "no_such_method_xyz",
                "approach": "income",
                "citations": {"ivs": ["IVS.103.A20"], "ifrs": ["IFRS.13.61"]},
                "solution_type": "closed_form",
            }
        ],
    )
    taxonomy = load_taxonomy(_write(tmp_path, data))
    with pytest.raises(TaxonomyError) as exc:
        validate_taxonomy(taxonomy, {"calculate_dcf": {"dcf": MethodSpec("dcf", "s", ("a",))}})
    assert "TAXONOMY_UNKNOWN_METHOD" in str(exc.value)


def test_missing_citation_raises_on_validate(tmp_path):
    data = _base(
        [IVS_STD, IFRS_STD],
        [IVS_CLAUSE, IFRS_CLAUSE],
        [
            {
                "method_id": "dcf",
                "approach": "income",
                "citations": {"ivs": ["IVS.103.A20"], "ifrs": []},
                "solution_type": "closed_form",
            }
        ],
    )
    taxonomy = load_taxonomy(_write(tmp_path, data))
    with pytest.raises(TaxonomyError) as exc:
        validate_taxonomy(taxonomy, {"calculate_dcf": {"dcf": MethodSpec("dcf", "s", ("a",))}})
    assert "TAXONOMY_MISSING_CITATION" in str(exc.value)


def test_bad_solution_type_raises_on_load(tmp_path):
    data = _base(
        [IVS_STD, IFRS_STD],
        [IVS_CLAUSE, IFRS_CLAUSE],
        [
            {
                "method_id": "dcf",
                "approach": "income",
                "citations": {"ivs": ["IVS.103.A20"], "ifrs": ["IFRS.13.61"]},
                "solution_type": "magic",
            }
        ],
    )
    with pytest.raises(TaxonomyError) as exc:
        load_taxonomy(_write(tmp_path, data))
    assert "TAXONOMY_BAD_SOLUTION_TYPE" in str(exc.value)


# --------------------------------------------------------------------------- #
# AC-2 / AC-3: attach + bidirectional query
# --------------------------------------------------------------------------- #
def test_attach_sets_registry_fields(tmp_path):
    data = _base(
        [IVS_STD, IFRS_STD],
        [IVS_CLAUSE, IFRS_CLAUSE],
        [
            {
                "method_id": "dcf",
                "approach": "income",
                "citations": {"ivs": ["IVS.103.A20"], "ifrs": ["IFRS.13.61"]},
                "solution_type": "closed_form",
                "divergences": [
                    {
                        "parameter": "discount_rate",
                        "ivs_basis": "IVS 105",
                        "ifrs_basis": "IAS 36.30",
                    }
                ],
            }
        ],
    )
    taxonomy = load_taxonomy(_write(tmp_path, data))
    registry = {"calculate_dcf": {"dcf": MethodSpec("dcf", "s", ("a",))}}
    validate_taxonomy(taxonomy, registry)
    attach_standards(registry, taxonomy)

    spec = registry["calculate_dcf"]["dcf"]
    assert spec.approach == "income"
    assert spec.solution_type == "closed_form"
    assert spec.citations["ivs"] == ("IVS.103.A20",)
    assert spec.citations["ifrs"] == ("IFRS.13.61",)
    assert spec.divergences[0].parameter == "discount_rate"


def test_bidirectional_queries():
    taxonomy = load_taxonomy()
    cites = citations_for(taxonomy, "dcf")
    assert "IVS.103.A20" in cites["ivs"]
    assert "IFRS.13.62" in cites["ifrs"]
    assert "dcf" in methods_for(taxonomy, "IVS.103.A20")
    assert methods_for(taxonomy, "IVS.103.A20") == sorted(methods_for(taxonomy, "IVS.103.A20"))
    assert methods_for(taxonomy, "no.such.clause") == []


def test_citations_for_unknown_method_raises():
    with pytest.raises(KeyError):
        citations_for(load_taxonomy(), "no_such_method")


# --------------------------------------------------------------------------- #
# AC-4: data-only standards update
# --------------------------------------------------------------------------- #
def test_new_clause_is_data_only(tmp_path):
    raw = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    raw["clauses"].append(
        {
            "id": "IVS.105.A30",
            "standard": "IVS",
            "label": "Terminal value",
            "summary": "Terminal value within the DCF.",
            "source_ref": "source/ivs-2025.md#ivs-105-valuation-models",
        }
    )
    for mapping in raw["methods"]:
        if mapping["method_id"] == "dcf":
            mapping["citations"]["ivs"].append("IVS.105.A30")
    taxonomy = load_taxonomy(_write(tmp_path, raw))
    # No Python change: the new clause immediately appears on the method.
    assert "IVS.105.A30" in citations_for(taxonomy, "dcf")["ivs"]
    assert "dcf" in methods_for(taxonomy, "IVS.105.A30")


# --------------------------------------------------------------------------- #
# AC-E2: citation audit
# --------------------------------------------------------------------------- #
def test_audit_citations_reports_uncovered():
    registry = {
        "toolA": {
            "cited": MethodSpec(
                "cited", "s", ("a",), citations={"ivs": ("IVS.103.A20",), "ifrs": ("IFRS.13.61",)}
            ),
            "uncited": MethodSpec("uncited", "s", ("a",)),
            "half": MethodSpec("half", "s", ("a",), citations={"ivs": ("IVS.103.A20",)}),
        }
    }
    assert audit_citations(registry) == ["half", "uncited"]


# --------------------------------------------------------------------------- #
# TASK-006: registry integration end-to-end
# --------------------------------------------------------------------------- #
def test_real_registry_carries_citations():
    spec = method_spec.get("calculate_dcf", "dcf")
    assert spec is not None
    assert spec.approach == "income"
    assert spec.solution_type == "closed_form"
    assert "IVS.103.A20" in spec.citations["ivs"]
    assert "IFRS.13.62" in spec.citations["ifrs"]

    viu = method_spec.get("calculate_dcf", "viu_pre_tax")
    assert viu is not None and viu.divergences, "viu_pre_tax must record its IVS/IFRS divergence"


def test_catalog_exposes_standard_fields():
    entry = next(m for m in method_spec.catalog()["methods"] if m["method"] == "dcf")
    assert entry["approach"] == "income"
    assert entry["solution_type"] == "closed_form"
    assert entry["citations"]["ivs"]
