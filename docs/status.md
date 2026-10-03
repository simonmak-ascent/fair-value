# Status & Roadmap

## Summary

The `fair-value` MCP server was redesigned around a single **method-spec
registry** and expanded into **16 native `calculate_*` tools / 123 methods**
covering corporate, startup, and intangible valuation, derivatives, credit
risk, fixed income, actuarial PV, and report review — aligned to **IVS 2025**
and IFRS. The previous sibling-delegation model was retired.

## Success (as of 2026-10-03)

| Area | Result |
|------|--------|
| Tools / methods | 16 tools, 129 methods |
| Implemented | 127/129 (2 deferred: `finite_difference`, `quantlib`) |
| Lint / types | ruff clean; mypy clean (17 files) |
| Tests | 284 passed, 2 skipped |
| Conformance | `16 tools; 127/129 implemented, 2 explicitly deferred` |
| TDQS overall | **~4.4–4.5 A** (was 3.6 A) |
| TDQS mean tool | **4.7** (min 4.3) |
| TDQS coherence | 4.3–4.5 (naming 5, completeness 4–5, disambiguation 4, tool_count 4) |

### What was built

- **Registry-derived surface** — `mcp_server/method_spec.py` +
  `method_spec_seed.py` define every tool/method/parameter; `tool_surface.py`
  derives the MCP surface; `engine.py` enforces a strict **no-defaults**
  contract (missing input, unknown method, or extra field → typed error).
- **Convertible bonds** — Tsiveriotis-Fernandes lattice and a
  Longstaff-Schwartz Monte-Carlo engine (two independent methods that agree to
  ~4%). Fixed a real issuer-call bug that returned ~3.9 instead of ~89.
- **Structured products** — CBBC, derivative/inline warrants, ELI/ELN,
  autocallable, accumulator/decumulator, CLN, TRS, CFD.
- **Loss-making companies** — margin-ramp DCF, revenue multiple, Merton,
  scenario, VC, distressed waterfall, bank residual income, SPAC, each with a
  dispersion kernel (mean, σ, percentiles, long-tail).
- **Fixed income**, including a **HIBOR/HKD-style term structure** (par-rate
  bootstrap, forward rates, curve discounting), **expected value**
  (continuous/MC/decision tree), **report review** (IVS/IFRS rule engine) and a
  **standards taxonomy** served at `valuation://standards`.

### TDQS progression

`3.6 A` (old, delegated surface) → `4.2` → `4.5 A` (registry surface + grouped
method matrix + behaviour footer + per-tool disambiguation + fixed-income tool).
Repeat runs of the identical surface score 4.4–4.5 (LLM variance ±0.1).

## Further development (prioritised)

### P0 — Lift `parameter_semantics`
The dimension is capped at ~4 because the schema is already ~100% documented
and the description's added value is the method→input map. A **discriminated
`oneOf` input schema** (per-method required sets expressed in the emitted
schema) is the main untried lever; validate against a TDQS run and keep a
rollback.

### P1 — `finite_difference` convertible engine
A Crank-Nicolson TF solver was prototyped but dipped below the straight-bond
floor (the debt grid diffuses the terminal conversion step). Needs a
regime-aware or smoother treatment before it can replace the deferral.

### P1 — QuantLib parity tests
Add `pytest.importorskip("QuantLib")` parity checks for options and convertibles
so the optional path is exercised when QuantLib is present (it is not on the
compute box).

### P2 — HK-market depth
- HIBOR/HKD curve construction — **done**: `calculate_fixed_income`
  `zero_curve`/`forward_rate`/`pv_curve` (and `discount_factor`).
- HKEX structured-product conventions — **done**: `cbbc_residual` (knock-out
  residual value) and `inline_warrant_avg` (averaged fixings).
- HKFRS-specific report-review checks — **done**: HKAS 40 / HKAS 36 / HKFRS 9
  gap rules and `reporting_basis` detection in `calculate_report_review`.

### P2 — Release & deployment
Version lockstep is ready (`pyproject.toml` ↔ `server.json`). Release is
tag-triggered (`release.yml` → PyPI → MCP Registry); redeploy the hosted ASGI
app and re-run any deployed-surface audit. **Not yet performed.**

### P3 — Docs & examples
- Worked HK examples — **done**: `examples/hk_examples.py` (convertible, inline
  warrant, loss-making listing), rendered in `docs/examples.md` and covered by
  the test suite. Keep `valuation://methods` as the source of truth.
