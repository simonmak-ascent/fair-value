# Standards corpus changelog

Tracks editions of the IVS/IFRS/IAS corpus in `standards/` and the taxonomy
schema. When a standard is amended, refresh the corresponding extract in
`standards/source/`, update `standards/provenance.json` (edition + retrieval
date), bump `standards/versions.json`, and add an entry here. This is a
**data-only** change: no engine code changes (VDD I-005).

## 2025.2 — 2026-10-04

Paragraph-level review of the corpus against the **HKICPA Members' Handbook
Volume II** (HKFRS/HKAS, verbatim IFRS/IAS adoptions; recorded in
`provenance.json` `verified_against`). Three clause references were corrected:

- **IFRS 9** — the measurement wording quoted as `§5.5.5` is actually `§5.5.17`;
  `§5.5.5` is the 12-month-ECL rule. Split into `IFRS.9.5.5.5` (12-month) and
  `IFRS.9.5.5.17` (measurement); ECL/PD methods now cite `§5.5.17`, `ecl_12m`
  cites `§5.5.5`.
- **IFRS 17** — the `§32` extract was a paraphrase that omitted the contractual
  service margin; replaced with the verbatim `§32` initial-recognition text.
- **IAS 19** — the definition quoted as `§67` is `§68`; `§67` is the requirement
  to use the method. Restored `§67` and added `IAS.19.68`.

Verified unchanged: IFRS 13 §61/§62/§69, IFRS 16 §26, IAS 36 §6/§18/§55,
IAS 37 §36/§39 (HKFRS 13/16/9, HKAS 36/37 match the AASB extracts verbatim; the
only difference is HK naming, e.g. "HKFRS" for "Standard" in IFRS 13 §69).

## 2025.1 — 2026-10-04

- Initial corpus established alongside the dual-standard taxonomy:
  - IVS 2025: IVS 103 (approaches; income/DCF; matrix pricing A10.05), IVS 105 (models), IVS 210 (excess earnings §60.08, relief-from-royalty §60.18).
  - IFRS 13: §61, §62, §69 (via the AASB 13 verbatim adoption).
  - IFRS 16: §26 (via the AASB 16 verbatim adoption).
  - IAS 36: §6, §18, §55 (via the AASB 136 verbatim adoption).
- Provenance manifest: `standards/provenance.json` (rights holder, edition, URL, retrieval date).
- Taxonomy schema `2025.1`: standards/clauses/methods with approach, citations, solution_type and divergence parameters.

### Pending (not yet in the corpus)

- None. Every clause in the taxonomy is cited by at least one method (remaining
  orphans are declared-but-unused clauses pending a matching method, tracked by
  the coverage ratchet).

### Covered asset-standard & financial-method corpus (cited)

- IVS 210 intangibles (relief-from-royalty, MPEEM, with-and-without)
- IVS 220 non-financial liabilities (Bottom-Up, §60.04) — `liability_fulfilment`
- IVS 230 inventory (top-down residual, §60.03) — `inventory_residual`
- IVS 300 plant & equipment (depreciated replacement cost, A30.03) — `ppe_revaluation`
- IVS 400 real property (income capitalisation, A20.10) — `investment_property`
- IVS 410 development property (residual method, §100.03) — `development_residual`
- IVS 103 matrix pricing (A10.05) — `matrix_pricing`
- IAS 36 recoverable amount (§18) — `recoverable_amount`; IAS 36 VIU/pre-tax rate
- IAS 37 provisions (best estimate, §36) — `ias37_provision`
- IFRS 9 expected credit losses (§5.5.5 12-month, §5.5.17 measurement) — `ecl_12m`, `ecl_lifetime`, `ecl_staged`, PD methods
- IFRS 17 initial recognition + fulfilment cash flows (§32) — `ifrs17_gmm`, `ifrs17_paa`, `ifrs17_vfa`
- IAS 19 projected unit credit (§67 requirement, §68 definition) — `ias19_puc`
- IVS 500 financial instruments (model fit-for-use, §100.02) — `bond_price`, `black_scholes`
