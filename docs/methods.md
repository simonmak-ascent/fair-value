# Methods

The canonical, machine-readable version of this catalogue is served by the MCP
server at `valuation://methods` (see `mcp_server/catalog.py`); the standards
taxonomy is served at `valuation://standards`. Both are derived from the
method-spec registry (`mcp_server/method_spec.py` + `method_spec_seed.py`).

Each `calculate_*` tool takes a required `method` plus exactly that method's
inputs (no defaults). 130 methods are registered across 16 tools.

| Tool | Methods | Standards |
|------|---------|-----------|
| `calculate_actuarial_pv` | 5 (`ifrs17_gmm`, `ifrs17_paa`, `ifrs17_vfa`, `ias19_puc`, `ias37_provision`) | IFRS 17, IAS 19, IAS 37 |
| `calculate_company_summary` | 1 (`profile`) | — |
| `calculate_convertible_bond` | 5 (`lattice_tsf`, `lattice_intensity`, `finite_difference`, `lsmc`, `quantlib`) | IFRS 9, IFRS 13 |
| `calculate_credit_loss` | 8 (`ecl_12m`, `ecl_lifetime`, `ecl_staged`, `provision_matrix`, `pd_from_spread`, `cumulative_pd`, `hazard`, `cva_dva`) | IFRS 9 |
| `calculate_dcf` | 10 (`dcf`, `npv`, `annuity`, `growing_annuity`, `perpetuity`, `terminal_gordon`, `terminal_multiple`, `viu_pre_tax`, `rnpv`, `lease_pv`) | IVS 2025, IFRS 13, IAS 36, IAS 38, IFRS 16 |
| `calculate_discount_rate` | 9 (`wacc`, `capm`, `startup_capm`, `build_up`, `currency_adjusted`, `country_risk`, `esg`, `portfolio_beta`, `ibr`) | IVS 2025, IFRS 16 |
| `calculate_expected_value` | 6 (`discrete`, `continuous`, `scenario`, `monte_carlo`, `decision_tree`, `football_field`) | — |
| `calculate_fair_value_adjustment` | 6 (`dlom`, `dloc`, `control_premium`, `minority_discount`, `highest_best_use`, `hierarchy_level`) | IFRS 13 |
| `calculate_fixed_income` | 8 (`bond_price`, `bond_yield`, `duration`, `convexity`, `discount_factor`, `zero_curve`, `forward_rate`, `pv_curve`) | IFRS 13 |
| `calculate_loss_making_company` | 8 (`margin_ramp_dcf`, `revenue_multiple`, `merton_equity`, `scenario`, `vc_method`, `distressed_waterfall`, `bank_residual_income`, `spac_deal`) | IFRS 13, IFRS 9, IAS 32 |
| `calculate_market_multiple` | 11 (`ev_revenue`, `ev_ebitda`, `ev_arr`, `ev_gmv`, `pe`, `pb`, `ps`, `cap_rate`, `regression`, `royalty_cap`, `ddm`) | IAS 40 |
| `calculate_option` | 9 (`black_scholes`, `black76`, `binomial_american`, `garman_kohlhagen`, `barrier_first_passage`, `asian_average`, `digital`, `range`, `share_based`) | IFRS 13, IFRS 2 |
| `calculate_report_review` | 1 (`audit`) | IVS 2025, IFRS 13 |
| `calculate_residual` | 15 (`goodwill`, `ppa`, `impairment_fvlcd`, `impairment_viu`, `inventory_nrv`, `held_for_sale`, `debt_waterfall`, `cap_table`, `sotp`, `spac_redemption`, `investment_property`, `ppe_revaluation`, `biological_asset`, `residual_income`, `justified_pb`) | IFRS 3, IAS 36, IAS 2, IFRS 5, IFRS 10, IAS 28, IAS 32, IAS 40, IAS 16, IAS 41 |
| `calculate_sector_metrics` | 15 (`ltv`, `cac`, `arr`, `nrr`, `magic_number`, `rule_of_40`, `take_rate`, `gmv_multiple`, `retention`, `trl`, `break_even`, `gross_margin`, `token`, `nvt`, `metcalfe`) | — |
| `calculate_structured_product` | 13 (`cbbc`, `cbbc_residual`, `derivative_warrant`, `inline_warrant`, `inline_warrant_avg`, `eli`, `eln`, `autocallable`, `credit_linked_note`, `accumulator`, `decumulator`, `trs`, `cfd`) | IFRS 9 |

Two convertible-bond discretizations (`finite_difference`, `quantlib`) are
registered but deferred to an optional engine and return a typed error envelope;
`lsmc` is available as a native Longstaff-Schwartz Monte-Carlo method.
