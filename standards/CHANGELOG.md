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

- IVS 220 Non-Financial Liabilities, IVS 230 Inventory, IVS 300 Plant/Equipment,
  IVS 400 Real Property, IVS 410 Development Property, IVS 500 Financial
  Instruments — bodies not yet extracted verbatim (IVS 410/220 were not cleanly
  available in the local extract). Add as data when sourced.
- IFRS 9 ECL, IFRS 17 FCF, IAS 19 PUC, IAS 37 — methods exist; corpus extracts to
  be added so their methods can be cited.
