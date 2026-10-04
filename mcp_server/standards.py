"""Dual-standard taxonomy: IVS 2025 × IFRS/IAS method mappings (A-001).

Import-light by design (stdlib only — no ``fastmcp``, no ``pydantic``, no
network), because :mod:`mcp_server.method_spec` attaches the taxonomy at import.
The machine file ``standards/taxonomy.json`` is the single source of truth for
*standards alignment*; the method registry remains the source of truth for
*methods*. They are joined by ``method_id``.

Locked rule (VDD V-001): ``standard`` (IVS vs IFRS/IAS) is a runtime concern and
citations are data — never code branches that relabel an output. Where the two
regimes genuinely diverge the difference is recorded as a :class:`Divergence`
with a clause basis on each side.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

APPROACHES: Tuple[str, ...] = ("market", "income", "cost")
SOLUTION_TYPES: Tuple[str, ...] = ("closed_form", "numeric", "simulation")

DEFAULT_TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "standards" / "taxonomy.json"
_STANDARDS_ROOT = DEFAULT_TAXONOMY_PATH.parent
DEFAULT_PROVENANCE_PATH = _STANDARDS_ROOT / "provenance.json"

_HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*$")
# Markers that must never appear in a shipped (verbatim) extract (A-002).
_PLACEHOLDER_MARKERS = (
    "todo",
    "[placeholder]",
    "[needs clarification]",
    "to be added",
    "placeholder",
)


class TaxonomyError(ValueError):
    """Structural or semantic problem with the taxonomy / registry join."""


# --------------------------------------------------------------------------- #
# Data objects
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Standard:
    id: str
    title: str
    family: str
    version: str
    source_ref: str


@dataclass(frozen=True)
class Clause:
    id: str
    standard: str
    label: str
    summary: str
    source_ref: str


@dataclass(frozen=True)
class Provenance:
    file: str
    title: str
    rights_holder: str
    edition: str
    url: str
    retrieved: str
    note: str = ""


@dataclass(frozen=True)
class Divergence:
    parameter: str
    ivs_basis: str
    ifrs_basis: str


@dataclass(frozen=True)
class MethodMapping:
    method_id: str
    approach: str
    ivs: Tuple[str, ...]
    ifrs: Tuple[str, ...]
    solution_type: str
    divergences: Tuple[Divergence, ...] = ()

    @property
    def citations(self) -> Dict[str, Tuple[str, ...]]:
        return {"ivs": self.ivs, "ifrs": self.ifrs}


@dataclass(frozen=True)
class Taxonomy:
    version: str
    standards: Dict[str, Standard]
    clauses: Dict[str, Clause]
    methods: Dict[str, MethodMapping]
    # clause id -> sorted method ids that cite it (built at load).
    _by_clause: Dict[str, Tuple[str, ...]] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Loading / validation
# --------------------------------------------------------------------------- #
def _require(obj: Mapping[str, Any], key: str, where: str) -> Any:
    if key not in obj or obj[key] in (None, ""):
        raise TaxonomyError(f"{where}: missing required field '{key}'")
    return obj[key]


def _load_raw(path: Optional[Path]) -> Dict[str, Any]:
    target = Path(path) if path is not None else DEFAULT_TAXONOMY_PATH
    with open(target, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_taxonomy(path: Optional[Any] = None) -> Taxonomy:
    """Load and structurally validate ``standards/taxonomy.json``.

    Raises :class:`FileNotFoundError` when an explicit ``path`` is absent, and
    :class:`TaxonomyError` on duplicate ids, unknown references or bad enums.
    """
    raw = _load_raw(path)

    standards: Dict[str, Standard] = {}
    for item in _require(raw, "standards", "taxonomy"):
        sid = _require(item, "id", "standard")
        if sid in standards:
            raise TaxonomyError(f"TAXONOMY_DUPLICATE_ID: standard '{sid}'")
        standards[sid] = Standard(
            id=sid,
            title=_require(item, "title", f"standard {sid}"),
            family=_require(item, "family", f"standard {sid}"),
            version=str(_require(item, "version", f"standard {sid}")),
            source_ref=_require(item, "source_ref", f"standard {sid}"),
        )

    clauses: Dict[str, Clause] = {}
    for item in _require(raw, "clauses", "taxonomy"):
        cid = _require(item, "id", "clause")
        if cid in clauses:
            raise TaxonomyError(f"TAXONOMY_DUPLICATE_ID: clause '{cid}'")
        std = _require(item, "standard", f"clause {cid}")
        if std not in standards:
            raise TaxonomyError(
                f"TAXONOMY_UNKNOWN_CLAUSE: clause '{cid}' cites unknown standard '{std}'"
            )
        clauses[cid] = Clause(
            id=cid,
            standard=std,
            label=_require(item, "label", f"clause {cid}"),
            summary=_require(item, "summary", f"clause {cid}"),
            source_ref=_require(item, "source_ref", f"clause {cid}"),
        )

    methods: Dict[str, MethodMapping] = {}
    for item in _require(raw, "methods", "taxonomy"):
        mid = _require(item, "method_id", "method mapping")
        if mid in methods:
            raise TaxonomyError(f"TAXONOMY_DUPLICATE_ID: method mapping '{mid}'")
        approach = _require(item, "approach", f"method {mid}")
        if approach not in APPROACHES:
            raise TaxonomyError(
                f"TAXONOMY_BAD_APPROACH: {mid}.approach '{approach}' not in {APPROACHES}"
            )
        solution_type = _require(item, "solution_type", f"method {mid}")
        if solution_type not in SOLUTION_TYPES:
            raise TaxonomyError(
                f"TAXONOMY_BAD_SOLUTION_TYPE: {mid}.solution_type "
                f"'{solution_type}' not in {SOLUTION_TYPES}"
            )
        cites = _require(item, "citations", f"method {mid}")
        ivs = tuple(sorted(cites.get("ivs", ())))
        ifrs = tuple(sorted(cites.get("ifrs", ())))
        divergences = tuple(
            Divergence(
                parameter=_require(d, "parameter", f"method {mid} divergence"),
                ivs_basis=_require(d, "ivs_basis", f"method {mid} divergence"),
                ifrs_basis=_require(d, "ifrs_basis", f"method {mid} divergence"),
            )
            for d in item.get("divergences", ())
        )
        methods[mid] = MethodMapping(
            method_id=mid,
            approach=approach,
            ivs=ivs,
            ifrs=ifrs,
            solution_type=solution_type,
            divergences=divergences,
        )

    by_clause: Dict[str, List[str]] = {cid: [] for cid in clauses}
    for mapping in methods.values():
        for cid in (*mapping.ivs, *mapping.ifrs):
            if cid not in clauses:
                raise TaxonomyError(
                    f"TAXONOMY_UNKNOWN_CLAUSE: method '{mapping.method_id}' cites "
                    f"unknown clause '{cid}'"
                )
            by_clause[cid].append(mapping.method_id)

    return Taxonomy(
        version=str(_require(raw, "version", "taxonomy")),
        standards=standards,
        clauses=clauses,
        methods=methods,
        _by_clause={cid: tuple(sorted(ids)) for cid, ids in by_clause.items()},
    )


def _registry_method_ids(registry: Mapping[str, Mapping[str, Any]]) -> List[str]:
    return [name for table in registry.values() for name in table]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _sections(path: Path) -> Dict[str, str]:
    """Map heading slug -> verbatim text under that heading (to next heading)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    sections: Dict[str, List[str]] = {}
    current: Optional[str] = None
    for line in lines:
        match = _HEADING_RE.match(line)
        if match:
            current = _slug(match.group(1))
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {slug: _clean_extract(body) for slug, body in sections.items()}


def _clean_extract(body: List[str]) -> str:
    """Drop editorial (blockquote) lines, leaving the verbatim extract."""
    kept = [line for line in body if not line.lstrip().startswith(">")]
    return "\n".join(kept).strip()


def _read_source(source_ref: str) -> Tuple[Path, str, Dict[str, str]]:
    rel, _, anchor = source_ref.partition("#")
    path = _STANDARDS_ROOT / rel
    if not path.is_file():
        raise TaxonomyError(f"TAXONOMY_UNRESOLVABLE_SOURCE: '{source_ref}' (no file)")
    return path, anchor, _sections(path)


def _check_source(source_ref: str) -> str:
    """Validate a source ref and return its verbatim (non-placeholder) text.

    An anchor-less reference (a whole standard/source file) only needs the file
    to exist; an anchored reference must resolve to non-placeholder text.
    """
    _, anchor, sections = _read_source(source_ref)
    if not anchor:
        return ""
    if anchor not in sections:
        raise TaxonomyError(f"TAXONOMY_UNRESOLVABLE_SOURCE: '{source_ref}' (no anchor)")
    text = sections.get(anchor, "")
    if not text:
        raise TaxonomyError(f"TAXONOMY_MISSING_SOURCE: '{source_ref}' (no text)")
    low = text.lower()
    if any(marker in low for marker in _PLACEHOLDER_MARKERS):
        raise TaxonomyError(f"TAXONOMY_PLACEHOLDER_SOURCE: '{source_ref}'")
    return text


def load_provenance(path: Optional[Any] = None) -> Dict[str, Provenance]:
    """Load ``standards/provenance.json`` into ``{file: Provenance}``."""
    target = Path(path) if path is not None else DEFAULT_PROVENANCE_PATH
    with open(target, "r", encoding="utf-8") as handle:
        raw = json.load(handle)
    records: Dict[str, Provenance] = {}
    for item in _require(raw, "sources", "provenance"):
        f = _require(item, "file", "provenance record")
        if f in records:
            raise TaxonomyError(f"TAXONOMY_DUPLICATE_ID: provenance '{f}'")
        records[f] = Provenance(
            file=f,
            title=_require(item, "title", f"provenance {f}"),
            rights_holder=_require(item, "rights_holder", f"provenance {f}"),
            edition=str(_require(item, "edition", f"provenance {f}")),
            url=_require(item, "url", f"provenance {f}"),
            retrieved=_require(item, "retrieved", f"provenance {f}"),
            note=item.get("note", ""),
        )
    return records


def _check_provenance(taxonomy: Taxonomy, path: Optional[Any] = None) -> None:
    records = load_provenance(path)
    refs = list(taxonomy.standards.values()) + list(taxonomy.clauses.values())
    for ref in refs:
        rel = ref.source_ref.partition("#")[0]
        if rel not in records:
            raise TaxonomyError(f"TAXONOMY_NO_PROVENANCE: '{rel}'")


def validate_taxonomy(
    taxonomy: Taxonomy,
    registry: Mapping[str, Mapping[str, Any]],
    *,
    check_sources: bool = True,
    provenance_path: Optional[Any] = None,
) -> None:
    """Validate the taxonomy against the method registry (join integrity)."""
    known = set(_registry_method_ids(registry))

    for mapping in taxonomy.methods.values():
        if mapping.method_id not in known:
            raise TaxonomyError(
                f"TAXONOMY_UNKNOWN_METHOD: '{mapping.method_id}' is not in the registry"
            )
        if not mapping.ivs or not mapping.ifrs:
            raise TaxonomyError(
                f"TAXONOMY_MISSING_CITATION: '{mapping.method_id}' needs >=1 IVS "
                f"and >=1 IFRS/IAS citation"
            )

    if check_sources:
        for standard in taxonomy.standards.values():
            _check_source(standard.source_ref)
        for clause in taxonomy.clauses.values():
            _check_source(clause.source_ref)
        _check_provenance(taxonomy, provenance_path)


def attach_standards(registry: Dict[str, Dict[str, Any]], taxonomy: Taxonomy) -> None:
    """Attach taxonomy fields to every matching ``MethodSpec`` (in place).

    Non-destructive: a method with no mapping is left untouched, so the registry
    keeps working (and the A-005 audit can flag it as uncovered).
    """
    for table in registry.values():
        for name, spec in list(table.items()):
            mapping = taxonomy.methods.get(name)
            if mapping is None:
                continue
            table[name] = replace(
                spec,
                approach=mapping.approach,
                citations={
                    "ivs": tuple(mapping.ivs),
                    "ifrs": tuple(mapping.ifrs),
                },
                solution_type=mapping.solution_type,
                divergences=mapping.divergences,
            )


# --------------------------------------------------------------------------- #
# Queries
# --------------------------------------------------------------------------- #
def citations_for(taxonomy: Taxonomy, method_id: str) -> Dict[str, List[str]]:
    """Return the IVS and IFRS/IAS clause ids for ``method_id`` (sorted)."""
    mapping = taxonomy.methods.get(method_id)
    if mapping is None:
        raise KeyError(f"unknown method '{method_id}'")
    return {"ivs": list(mapping.ivs), "ifrs": list(mapping.ifrs)}


def methods_for(taxonomy: Taxonomy, clause_id: str) -> List[str]:
    """Return the sorted method ids that cite ``clause_id`` (``[]`` if none)."""
    return list(taxonomy._by_clause.get(clause_id, ()))


def clause_text(
    taxonomy: Taxonomy, clause_id: str, *, provenance_path: Optional[Any] = None
) -> Dict[str, Any]:
    """Return the verbatim wording and provenance for ``clause_id``."""
    clause = taxonomy.clauses.get(clause_id)
    if clause is None:
        raise KeyError(f"unknown clause '{clause_id}'")
    text = _check_source(clause.source_ref)
    rel = clause.source_ref.partition("#")[0]
    provenance = load_provenance(provenance_path).get(rel)
    if provenance is None:
        raise TaxonomyError(f"TAXONOMY_NO_PROVENANCE: '{rel}'")
    return {
        "clause_id": clause_id,
        "text": text,
        "source_ref": clause.source_ref,
        "provenance": provenance,
    }


def audit_citations(registry: Mapping[str, Mapping[str, Any]]) -> List[str]:
    """Return sorted method ids lacking a full IVS + IFRS/IAS citation set.

    Hook consumed by the A-005 conformance gate; read-only.
    """
    uncovered: List[str] = []
    for table in registry.values():
        for name, spec in table.items():
            cites = getattr(spec, "citations", None) or {}
            if not cites.get("ivs") or not cites.get("ifrs"):
                uncovered.append(name)
    return sorted(uncovered)


def coverage_report(
    registry: Mapping[str, Mapping[str, Any]], taxonomy: Taxonomy
) -> Dict[str, Any]:
    """Summarise standards-citation coverage for the A-005 gate.

    Returns the count of fully-cited methods, the uncited method ids (citation
    debt) and the orphan clause ids (declared but cited by no method).
    """
    uncited = audit_citations(registry)
    total = sum(len(table) for table in registry.values())
    orphans = sorted(cid for cid in taxonomy.clauses if not taxonomy._by_clause.get(cid))
    return {
        "total_methods": total,
        "cited_methods": total - len(uncited),
        "uncited_methods": uncited,
        "orphan_clauses": orphans,
    }
