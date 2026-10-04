# Methods

The canonical, machine-readable version of this catalogue is served by the MCP
server at `valuation://methods` (see `mcp_server/catalog.py`); the standards
taxonomy is served at `valuation://standards`. Both are derived from the
method-spec registry (`mcp_server/method_spec.py` + `method_spec_seed.py`).

Each `calculate_*` tool takes a required `method` plus exactly that method's
inputs (no defaults). **138 methods are registered across 16 tools**; every
result carries `statistics` (centre, σ, percentiles, and — for stochastic
methods — the simulation samples) plus `citations` resolving to the clauses
below.

**Citation coverage: 120 / 138 methods.** The 18 uncited methods are the
deliberate exception set — proprietary sector KPIs (`calculate_sector_metrics`),
the report-review surface (a boundary, not a calculation), and the company
profile — and the conformance gate fails if any *other* method is uncited
(`scripts/check_conformance.py`, `CITATION_EXEMPT`). The taxonomy has **0 orphan
clauses**.

| Tool | Methods | Cited | IVS clauses | IFRS / IAS clauses |
|------|--------:|------:|-------------|--------------------|
| `calculate_actuarial_pv` | 5 | 5 | `IVS.105.A10`, `IVS.220.A10` | `IAS.19.67`, `IAS.37.36`, `IFRS.17.32` |
| `calculate_company_summary` | 1 | 0 | — | — |
| `calculate_convertible_bond` | 5 | 5 | `IVS.500.A10` | `IFRS.13.62` |
| `calculate_credit_loss` | 8 | 8 | `IVS.105.A10` | `IFRS.9.5.5.5`, `IFRS.13.62` |
| `calculate_dcf` | 10 | 10 | `IVS.103.A20` | `IFRS.13.61`, `IFRS.13.62`, `IAS.36.6`, `IAS.36.55`, `IFRS16.26` |
| `calculate_discount_rate` | 9 | 9 | `IVS.103.A20`, `IVS.105.A10` | `IFRS.13.61`, `IFRS16.26` |
| `calculate_expected_value` | 6 | 6 | `IVS.103.A20` | `IFRS.13.61`, `IFRS.13.62` |
| `calculate_fair_value_adjustment` | 6 | 6 | `IVS.103.A10` | `IFRS.13.61`, `IFRS.13.69` |
| `calculate_fixed_income` | 9 | 9 | `IVS.103.A05`, `IVS.500.A10` | `IFRS.13.62` |
| `calculate_loss_making_company` | 7 | 7 | `IVS.103.A10`, `IVS.103.A20` | `IFRS.13.61`, `IFRS.13.62` |
| `calculate_market_multiple` | 11 | 11 | `IVS.103.A10`, `IVS.103.A20`, `IVS.210.A10` | `IFRS.13.62` |
| `calculate_option` | 9 | 9 | `IVS.500.A10` | `IFRS.13.62` |
| `calculate_report_review` | 2 | 0 | — | — |
| `calculate_residual` | 22 | 22 | `IVS.103.A10`, `IVS.103.A20`, `IVS.210.A10`, `IVS.220.A10`, `IVS.230.A10`, `IVS.300.A10`, `IVS.400.A10`, `IVS.410.A10` | `IFRS.13.61`, `IFRS.13.62`, `IAS.36.6`, `IAS.36.18` |
| `calculate_sector_metrics` | 15 | 0 | — | — |
| `calculate_structured_product` | 13 | 13 | `IVS.500.A10` | `IFRS.13.62` |

Two convertible-bond discretizations (`finite_difference`, `quantlib`) are
registered but deferred — `quantlib` needs the optional engine, `finite_difference`
waits on a solver fix — and return a typed error envelope; `lattice_tsf`,
`lattice_intensity`, and `lsmc` (native Longstaff-Schwartz Monte-Carlo) are
available. The per-clause cross-reference (which methods cite each clause) is in
the generated [Standards reference](standards.md).
