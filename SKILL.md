# Financial Valuation Skill

## Overview

Turn a valuation question into a validated number: choose a method, supply its exact inputs, and
read the result out of a shared envelope that carries the formula, the assumptions, the statistics
and the IVS/IFRS clauses it satisfies.

This repository is a **pure computation library** plus the MCP server and REST API that expose it.
It holds **14 `calculate_*` tools covering 135 methods**. It does not fetch market data and does not
review reports — see [Out of scope](#out-of-scope).

## Trigger Conditions

Use it when a request needs a computed valuation figure or a modelled metric, for example:

- "What is this company worth on a DCF / NAV / comparable-multiples basis?"
- "What discount rate should I use — CAPM, build-up, country risk, currency-adjusted?"
- "Price this option, warrant, convertible or structured product."
- "What is the expected credit loss under HKFRS 9, or the PD from a structural model?"
- "Apply a DLOM / control premium, or measure a residual / IFRS 13 adjustment."
- "What are the sector KPIs for a SaaS or marketplace business?"

Do not use it for data acquisition, precedent-transaction search, or document review.

## Standards Compliance

Every result carries `citations` resolved from `standards/taxonomy.json`, whose clause text is
verbatim in `standards/source/`. Citations are returned, never invented. A method with no clause
carries empty `citations` (`{"ivs": [], "ifrs": []}`); `scripts/check_conformance.py` fails the build
on an uncited method outside its sector-KPI exemption, and on any regression past
`standards/coverage-baseline.json` (15 methods are uncited today, all of them sector KPIs).

### IVS 2025

Income, market and cost approaches under IVS 103, the IVS 105 model-fit requirement, and the
IVS 500 financial-instrument clauses.

### IFRS Standards

IFRS 13 fair value (hierarchy, DLOM/DLOC, highest and best use), IFRS 9 / HKFRS 9 impairment,
IAS 19 and IAS 37 provisions, IFRS 17 insurance contracts.

## Capabilities

Fourteen tools, 135 methods. The tool is the entry point; the `method` argument selects the
computation. `GET /v1/help/{tool}` returns the exact inputs each method requires.

| tool | what it covers | methods | examples |
|---|---|---|---|
| `calculate_dcf` | Discounted cash flow valuation | 10 | `dcf`, `npv`, `annuity`, `lease_pv` |
| `calculate_market_multiple` | Market multiples and comparable pricing | 11 | `ev_ebitda`, `ev_arr`, `ddm`, `cap_rate` |
| `calculate_residual` | IFRS measurement, residual income, non-financial fair value | 22 | `goodwill`, `development_residual`, `debt_waterfall` |
| `calculate_discount_rate` | Cost of capital and discount rates | 9 | `capm`, `build_up`, `country_risk`, `esg` |
| `calculate_fair_value_adjustment` | IFRS 13 adjustments | 6 | `dlom`, `dloc`, `control_premium`, `hierarchy_level` |
| `calculate_sector_metrics` | Sector-specific operating metrics | 15 | `arr`, `cac`, `gmv_multiple`, `break_even` |
| `calculate_expected_value` | Probability-weighted value | 6 | `decision_tree`, `monte_carlo`, `football_field` |
| `calculate_loss_making_company` | Pre-profit and distressed companies | 7 | `margin_ramp_dcf`, `distressed_waterfall`, `merton_equity` |
| `calculate_option` | Options and warrants | 9 | `black_scholes`, `binomial_american`, `barrier_first_passage` |
| `calculate_convertible_bond` | Convertible and exchangeable bonds | 5 | `lattice_tsf`, `lsmc`, `lattice_intensity` |
| `calculate_structured_product` | Structured products | 13 | `autocallable`, `cbbc`, `accumulator`, `cfd` |
| `calculate_fixed_income` | Fixed income and term structure | 9 | `bond_price`, `duration`, `convexity`, `discount_factor` |
| `calculate_credit_loss` | Credit loss and impairment | 8 | `ecl_12m`, `ecl_lifetime`, `cva_dva`, `cumulative_pd` |
| `calculate_actuarial_pv` | Actuarial present value | 5 | `ifrs17_gmm`, `ifrs17_paa`, `ias19_puc`, `ias37_provision` |

Two convertible-bond methods are registered but deliberately unimplemented and listed in
`src/mcp/deferred.py`: `quantlib` and `finite_difference`. Those return a typed `NOT_IMPLEMENTED`
error, not a wrong number.

## Usage Examples

### A valuation figure

```
calculate_dcf(method="dcf", cash_flows=[100, 110, 121], discount_rate=0.10)
→ {"status":"ok", "method":"calculate_dcf.dcf", "value":…, "statistics":{…},
   "citations":{"ivs":["IVS.103.A20"],"ifrs":["IFRS.13.62"]}, …}
```

Over HTTP: `POST /v1/calculate/calculate_dcf` with `{"method":"dcf", …}`.
Over MCP: `tools/call` with `{"name":"calculate_dcf","arguments":{…}}`.

### A cost of capital

```
calculate_discount_rate(method="capm", risk_free=0.04, beta=1.2, market_return=0.09)
```

### A credit loss

```
calculate_credit_loss(method="ecl_12m", ead=1_000_000, pd=0.02, lgd=0.45)
```

## Output

Every result uses one envelope (`src/output/result.py`): `status`, `method`, `ticker`, `value`, `assumptions`,
`formula_ref`, `data_timestamp`, `steps`, `statistics`, `solution_type`, `citations`, `disclaimer`.
Stochastic methods (`solution_type="simulation"`) take a seed and return summary statistics.

Failures are typed, never raised: `INVALID_ARGUMENT`, `COMPUTATION_ERROR`, `NOT_IMPLEMENTED`,
`UNKNOWN_TOOL`, and a missing input returns `MISSING_INPUT` on `valuation_engine.run_valuation` but
`INVALID_ARGUMENT` on the MCP/REST surface. Branch on `error.code`, never on the message.

## Inputs

The computation path performs no network or database I/O. Every input is supplied explicitly by the
caller; market data and reference prices come from `apdb-etl`, which is a separate service. The only
outbound HTTP in the Python package and the served API is the hosted end-to-end test
(`tests/test_e2e_hosted.py`) and the Swagger UI asset URLs that `/v1/docs` emits. The frontage fetches
Google Fonts at build time — a concern of the web app, not of this engine.

Missing inputs are never synthesised — the call returns a typed error naming what it wanted.

## Out of scope

These belong to other repositories and are **not** available here:

| capability | owner |
|---|---|
| Market data, reference prices, ETL | `apdb-etl` |
| Excel model review, document review, image review | `valuation-report-review` |
| Precedent transactions and deal screening | not in this estate |

An earlier version of this file listed report review and market-data sources as capabilities of this
package. It does not have them, and an agent that trusted it would have called tools that do not
exist.

## Limitations

- Results are estimates; assumptions travel in the envelope and are not defaults to be trusted.
- Convertible-bond methods need a credit spread; `quantlib` also needs the optional engine.
- Two convertible methods are unimplemented (see above).
- Not investment advice.
