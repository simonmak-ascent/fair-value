"""Tests for the standards corpus + provenance manifest (VDD A-002).

Covers spec `vdd/specs/A-002/spec.md`: AC-1, AC-E1, AC-2, AC-3, AC-4, AC-5.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcp_server import method_spec, standards
from mcp_server.method_spec import MethodSpec
from mcp_server.standards import (
    Taxonomy,
    TaxonomyError,
    citations_for,
    clause_text,
    load_provenance,
    load_taxonomy,
    validate_taxonomy,
)

REPO = Path(__file__).resolve().parent.parent
TAXONOMY_PATH = REPO / "standards" / "taxonomy.json"


def _taxonomy_for(
    tmp_path: Path,
    standard_ref: str,
    clause_id: str,
    clause_ref: str,
    ifrs_ref: str = "source/ifrs-13.md#paragraph-62",
) -> Taxonomy:
    data = {
        "version": "test.1",
        "standards": [
            {
                "id": "IVS",
                "title": "IVS",
                "family": "IVS",
                "version": "2025",
                "source_ref": standard_ref,
            }
        ],
        "clauses": [
            {
                "id": clause_id,
                "standard": "IVS",
                "label": "x",
                "summary": "x",
                "source_ref": clause_ref,
            },
            {
                "id": "IFRS.13.62",
                "standard": "IVS",
                "label": "y",
                "summary": "y",
                "source_ref": ifrs_ref,
            },
        ],
        "methods": [
            {
                "method_id": "dcf",
                "approach": "income",
                "citations": {"ivs": [clause_id], "ifrs": ["IFRS.13.62"]},
                "solution_type": "closed_form",
            }
        ],
    }
    path = tmp_path / "taxonomy.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return load_taxonomy(path)


REGISTRY = {"calculate_dcf": {"dcf": MethodSpec("dcf", "s", ("a",))}}


# --------------------------------------------------------------------------- #
# AC-1 / AC-3 / AC-5: real corpus coverage, provenance, verbatim spot-check
# --------------------------------------------------------------------------- #
def test_real_corpus_validates_with_sources_and_provenance():
    taxonomy = load_taxonomy()
    validate_taxonomy(taxonomy, method_spec._REGISTRY)


def test_provenance_manifest_complete():
    taxonomy = load_taxonomy()
    records = load_provenance()
    referenced = {s.source_ref.partition("#")[0] for s in taxonomy.standards.values()}
    referenced |= {c.source_ref.partition("#")[0] for c in taxonomy.clauses.values()}
    assert referenced <= set(records)
    for record in records.values():
        assert record.title and record.rights_holder and record.edition
        assert record.url.startswith("http") and record.retrieved


def test_every_clause_has_text_and_provenance():
    taxonomy = load_taxonomy()
    for clause_id in taxonomy.clauses:
        result = clause_text(taxonomy, clause_id)
        assert result["text"], clause_id
        assert result["provenance"].rights_holder


def test_verbatim_spot_checks():
    taxonomy = load_taxonomy()
    checks = {
        "IAS.36.6": "present value of the future cash flows",
        "IAS.36.55": "pre-tax rate",
        "IFRS.13.62": "market approach",
        "IFRS16.26": "incremental borrowing rate",
        "IVS.103.A10": "valuation approaches",
    }
    for clause_id, phrase in checks.items():
        assert phrase.lower() in clause_text(taxonomy, clause_id)["text"].lower(), clause_id


def test_clause_text_is_deterministic():
    taxonomy = load_taxonomy()
    a = clause_text(taxonomy, "IFRS.13.62")
    b = clause_text(taxonomy, "IFRS.13.62")
    assert a["text"] == b["text"]


# --------------------------------------------------------------------------- #
# AC-E1: missing / placeholder / no-provenance errors
# --------------------------------------------------------------------------- #
def test_missing_anchor_raises(tmp_path):
    taxonomy = _taxonomy_for(
        tmp_path, "source/ivs-2025.md", "IVS.999", "source/ivs-2025.md#does-not-exist"
    )
    with pytest.raises(TaxonomyError) as exc:
        validate_taxonomy(taxonomy, REGISTRY)
    assert "TAXONOMY_UNRESOLVABLE_SOURCE" in str(exc.value)


def test_placeholder_source_raises(tmp_path, monkeypatch):
    src = tmp_path / "source"
    src.mkdir()
    (src / "x.md").write_text("# Standard X\n\n## Clause A\n\nTODO: fill me in.\n")
    prov = tmp_path / "provenance.json"
    prov.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "file": "source/x.md",
                        "title": "t",
                        "rights_holder": "r",
                        "edition": "1",
                        "url": "https://example.org",
                        "retrieved": "2026-10-04",
                    }
                ]
            }
        )
    )
    monkeypatch.setattr(standards, "_STANDARDS_ROOT", tmp_path)
    taxonomy = _taxonomy_for(
        tmp_path,
        "source/x.md",
        "IVS.103.A20",
        "source/x.md#clause-a",
        ifrs_ref="source/x.md#clause-a",
    )
    with pytest.raises(TaxonomyError) as exc:
        validate_taxonomy(taxonomy, REGISTRY, provenance_path=prov)
    assert "TAXONOMY_PLACEHOLDER_SOURCE" in str(exc.value)


def test_missing_provenance_raises(tmp_path, monkeypatch):
    src = tmp_path / "source"
    src.mkdir()
    (src / "x.md").write_text("# Standard X\n\n## Clause A\n\nReal wording here.\n")
    prov = tmp_path / "provenance.json"
    prov.write_text(json.dumps({"sources": []}))
    monkeypatch.setattr(standards, "_STANDARDS_ROOT", tmp_path)
    taxonomy = _taxonomy_for(
        tmp_path,
        "source/x.md",
        "IVS.103.A20",
        "source/x.md#clause-a",
        ifrs_ref="source/x.md#clause-a",
    )
    with pytest.raises(TaxonomyError) as exc:
        validate_taxonomy(taxonomy, REGISTRY, provenance_path=prov)
    assert "TAXONOMY_NO_PROVENANCE" in str(exc.value)


def test_clause_text_unknown_clause_raises():
    with pytest.raises(KeyError):
        clause_text(load_taxonomy(), "no.such.clause")


def test_ias37_corpus_and_citation():
    taxonomy = load_taxonomy()
    text = clause_text(taxonomy, "IAS.37.36")["text"]
    assert "best estimate of the expenditure" in text

    from mcp_server.engine import dispatch

    res = dispatch(
        "calculate_actuarial_pv",
        {
            "method": "ias37_provision",
            "outcomes": [100.0, 200.0],
            "probabilities": [0.5, 0.5],
            "discount_rate": 0.0,
            "periods": 1,
        },
    )
    assert res["status"] == "ok", res
    assert "IAS.37.36" in res["citations"]["ifrs"]


def test_new_ifrs_corpus_and_citations():
    taxonomy = load_taxonomy()
    # Corrected paragraph ids (HKICPA HKFRS/HKAS cross-check, corpus 2025.2):
    assert "unbiased and probability-weighted" in clause_text(taxonomy, "IFRS.9.5.5.17")["text"]
    assert "12-month expected credit losses" in clause_text(taxonomy, "IFRS.9.5.5.5")["text"]
    assert "risk adjustment for non-financial risk" in clause_text(taxonomy, "IFRS.17.32")["text"]
    assert "contractual service margin" in clause_text(taxonomy, "IFRS.17.32")["text"]
    assert (
        "shall use the projected unit credit method" in clause_text(taxonomy, "IAS.19.67")["text"]
    )
    assert "additional unit of benefit entitlement" in clause_text(taxonomy, "IAS.19.68")["text"]
    for method in ("ecl_lifetime", "ecl_staged", "ias19_puc", "ifrs17_gmm"):
        cites = citations_for(taxonomy, method)
        assert cites["ivs"] and cites["ifrs"], method
    # ecl_12m cites the 12-month rule; the other ECL methods cite the measurement basis.
    assert citations_for(taxonomy, "ecl_12m")["ifrs"] == ["IFRS.9.5.5.5"]
    assert citations_for(taxonomy, "ecl_lifetime")["ifrs"] == ["IFRS.9.5.5.17"]


def test_ivs500_corpus_and_citations():
    taxonomy = load_taxonomy()
    assert "fit for use" in clause_text(taxonomy, "IVS.500.A10")["text"]
    for method in ("bond_price", "black_scholes"):
        cites = citations_for(taxonomy, method)
        assert "IVS.500.A10" in cites["ivs"] and cites["ifrs"]
