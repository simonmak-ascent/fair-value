## Description

<!-- What does this change do and why? Link the issue. -->

## Type
- [ ] feat
- [ ] fix
- [ ] chore
- [ ] docs
- [ ] standards (taxonomy / corpus / coverage)

## Checklist
- [ ] `ruff check .` passes
- [ ] `mypy` passes
- [ ] `python -m pytest` passes
- [ ] `python scripts/check_conformance.py` passes (registry + surface + standards gate)
- [ ] Generated docs regenerated (`python scripts/gen_docs.py`) and committed
- [ ] No `print()` in `src/`; missing data stays absent (never synthesised)

## Standards (only if methods/taxonomy touched)
- [ ] Every new/changed method cites at least one IVS and one IFRS/IAS clause, or is added to `CITATION_EXEMPT`
- [ ] New clause text is **verbatim** in `standards/source/` with correct `provenance.json` edition/source
- [ ] `coverage-baseline.json` refreshed if intended

## Testing
<!-- How was this verified? Prefer the compute box: `cs run "..."`. -->

## Related issues
