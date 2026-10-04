# Standards corpus changelog

Tracks editions of the IVS/IFRS/IAS corpus in `standards/` and the taxonomy
schema. When a standard is amended, refresh the corresponding extract in
`standards/source/`, update `standards/provenance.json` (edition + retrieval
date), bump `standards/versions.json`, and add an entry here. This is a
**data-only** change: no engine code changes (VDD I-005).

## 2025.1 — 2026-10-04

- Initial corpus established alongside the dual-standard taxonomy:
  - IVS 2025: IVS 103 (approaches; income/DCF; matrix pricing A10.05), IVS 105 (models), IVS 210 (excess earnings §60.08, relief-from-royalty §60.18).
  - IFRS 13: §61, §62, §69 (via the AASB 13 verbatim adoption).
  - IFRS 16: §26 (via the AASB 16 verbatim adoption).
  - IAS 36: §6, §18, §55 (via the AASB 136 verbatim adoption).
- Provenance manifest: `standards/provenance.json` (rights holder, edition, URL, retrieval date).
- Taxonomy schema `2025.1`: standards/clauses/methods with approach, citations, solution_type and divergence parameters.

### Pending (not yet in the corpus)

- IVS 500 Financial Instruments, and the IFRS liability/provision bodies
  (IFRS 9 ECL, IFRS 17 FCF, IAS 19 PUC, IAS 37) — methods exist but their
  corpus extracts are not yet added, so they are not yet cited. Add as data when
  sourced.

### Covered asset-standard methods (corpus + cited)

- IVS 210 intangibles (relief-from-royalty, MPEEM, with-and-without)
- IVS 220 non-financial liabilities (Bottom-Up, §60.04) — `liability_fulfilment`
- IVS 230 inventory (top-down residual, §60.03) — `inventory_residual`
- IVS 300 plant & equipment (depreciated replacement cost, A30.03) — `ppe_revaluation`
- IVS 400 real property (income capitalisation, A20.10) — `investment_property`
- IVS 410 development property (residual method, §100.03) — `development_residual`
- IVS 103 matrix pricing (A10.05) — `matrix_pricing`
- IAS 36 recoverable amount (§18) — `recoverable_amount`; IAS 36 VIU/pre-tax rate
