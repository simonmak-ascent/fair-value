# Status & Roadmap

## Summary

The `fair-value` server was redesigned through a spec-driven (VDD) process around
a single **method-spec registry** and a **standards taxonomy**, then expanded to
**14 native `calculate_*` tools / 135 methods** covering corporate, startup, and
intangible valuation, derivatives, credit risk, fixed income, and actuarial PV —
aligned to **IVS 2025** and **IFRS/IAS**. Every result carries a
deterministic-first envelope (`value` + `statistics` + `citations`), and a
conformance gate enforces standard citations in CI. The previous
sibling-delegation model was retired.

## Success (as of 2026-10-04)

| Area | Result |
|------|--------|
| Tools / methods | 14 tools, 135 methods |
| Implemented | 133/135 (2 deferred: `finite_difference`, `quantlib`) |
| Standards citations | 120/135 methods, **0 orphan clauses** |
| Lint / types | ruff clean; mypy clean (21 files) |
| Tests | 312 passed, 0 skipped (CI, with QuantLib); 306 passed, 6 skipped without |
| Conformance | `14 tools; 133/135 implemented, 2 deferred; citations 120/135, 0 orphan clauses` |
| TDQS overall | **~4.4–4.5 A** (was 3.6 A) |
| TDQS mean tool | **4.7** (min 4.3) |

### Redesign (A-001 … A-012)

- **A-001 — dual-standard taxonomy** (`standards/taxonomy.json`,
  `mcp_server/standards.py`): one clause per IVS/IFRS rule, mapped from methods;
  `citations_for` / `methods_for` / `coverage_report`; clause ids like
  `IVS.103.A20`, `IFRS.13.62`, `IVS.500.A10`.
- **A-002 — verbatim corpus** (`standards/source/*.md`, `standards/provenance.json`):
  the clause text with edition, rights holder, and retrieval provenance.
- **A-003 — envelope** (`src/output/result.py`): `statistics` / `solution_type` /
  `citations`; `engine.py` attaches the registry's solution type and citations.
- **A-004 — coverage**: asset-standard methods (relief-from-royalty, MPEEM,
  with/without, recoverable amount, liability fulfilment, inventory/development
  residuals) and `matrix_pricing`.
- **A-005 — conformance gate** (`scripts/check_conformance.py`): taxonomy/corpus
  validation, coverage ratchet, orphan check, and an absolute
  `CITATION_EXEMPT` check (only the sector KPIs may be uncited).
- **A-006 — transparency docs** (`mcp_server/docs.py`, `scripts/gen_docs.py`):
  `-help` records and a generated method reference.
- **A-007 — REST API** (`mcp_server/rest.py`): `/v1/…`, served with MCP by the
  ASGI app.
- **A-008 — surface boundary**: report review (a document-audit capability, not a
  valuation calculation) was extracted to the `valuation-report-review` service.
- **A-009 — deterministic-first**: `monte_carlo` requires a `seed` and returns a
  reproducible distribution.
- **A-010 — duplicate-method guard** (none currently).
- **A-011 — OpenAPI** (`mcp_server/openapi.py`): no new dependency.
- **A-012 — versioning** (`standards/versions.json`, `standards/CHANGELOG.md`).
- **A-013 — DB persistence**: deliberately out of scope (WON'T).

### Coverage

The taxonomy cites **IVS 103, 105, 210, 220, 230, 300, 400, 410, 500** and
**IFRS 13/9/16/17, IAS 36/19/37** (verbatim clause text in `standards/source/`).
The 18 uncited methods are the deliberate exception set. See
[Standards reference](standards.md) and [Methods](methods.md).

## Further development (prioritised)

### P1 — `finite_difference` convertible engine
A Crank-Nicolson Tsiveriotis-Fernandes solver was prototyped but dipped below the
straight-bond floor (the debt grid diffuses the terminal conversion step). Needs a
regime-aware or smoother treatment before it can replace the deferral. `quantlib`
is deferred only for the optional engine.

### P1 — `quantlib` conditional implementation
`quantlib` is registered but returns a typed error envelope. On a host with the
optional engine (CI installs QuantLib), it can be enabled behind a handler
guarded by `QUANTLIB_AVAILABLE`.

### P2 — Release & deployment
Version lockstep is ready (`pyproject.toml` ↔ `server.json`, both `0.2.6`).
Release is tag-triggered (`release.yml` → PyPI → MCP Registry); the hosted ASGI
app (MCP + REST) is deployed on Vercel. Tag `v0.2.6` cut; the MCP Registry remote
is the dedicated `/mcp` endpoint.

### P3 — Docs & examples
Method reference is generated (`scripts/gen_docs.py`); worked HK examples live in
`examples/hk_examples.py` and render in [Examples](examples.md). Keep
`valuation://methods` / `valuation://standards` as the source of truth.
