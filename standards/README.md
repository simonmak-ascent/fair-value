# Standards corpus

Source extracts and the dual-standard taxonomy that joins the method registry to
IVS 2025 and IFRS/IAS clauses.

- `taxonomy.json` — the single source of truth for standards alignment: standards,
  clauses, and per-method mappings (`approach`, `citations`, `solution_type`,
  `divergences`). Loaded and validated by `mcp_server/standards.py` at import.
- `source/*.md` — the human corpus keyed by the clause `source_ref` anchors.

**Adding a clause is a data-only change**: append it to `taxonomy.json` (and the
corpus), map it to a method, and the citation appears on that method with no
Python edit. A standards update must never require an engine rewrite.
