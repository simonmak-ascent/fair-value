"""Seed method tables for the method-spec registry (all 15 tools).

Phase 1 grows this file engine by engine. The DCF and option tables match the
definitions that scored 4.9 / 4.6 in the Phase-0 TDQS spike.
"""

from __future__ import annotations

from .method_spec import MethodSpec, register, register_tool_meta

_TOOL_META = {
    "calculate_dcf": (
        "Discounted cash flow valuation",
        "Discounted cash flow valuation engine. Choose a method and supply its exact inputs to value a business from projected free cash flows, dividends, residual income, or economic profit. Covers FCFF/FCFE DCF, NPV/IRR, terminal values, and multi-stage growth. Use this for going-concern cash-flow businesses; for asset-anchored or financial firms use calculate_residual, for peer-based pricing use calculate_market_multiple, and for pre-profit companies use calculate_loss_making_company.",
    ),
    "calculate_discount_rate": (
        "Cost of capital and discount rates",
        "Cost-of-capital engine. Compute WACC, cost of equity (CAPM), cost of debt, unlevered/relevered beta, and country or size premiums from an explicit capital structure and market inputs. Use this to derive the discount rate an income-approach valuation needs. Read-only and deterministic. Returns the shared result envelope.",
    ),
    "calculate_market_multiple": (
        "Market multiples and comparable pricing",
        "Market-multiple engine. Apply peer multiples (P/E, P/B, EV/EBITDA, EV/Sales, PEG and more) or derive implied multiples to price a company on a comparable basis. Use this for market-approach pricing where peers exist; for intrinsic value use calculate_dcf. Read-only and deterministic. Returns the shared result envelope.",
    ),
    "calculate_residual": (
        "IFRS measurement, residual income and non-financial fair value",
        "IFRS/HKFRS measurement engine. Compute goodwill and purchase-price allocation, impairment (IAS 36), inventory net realisable value, held-for-sale, debt waterfalls, cap tables, sum-of-the-parts and SPAC redemption; residual income and justified price-to-book; and non-financial asset fair value: investment property (IAS 40 / HKAS 40), PP&E revaluation via depreciated replacement cost (IAS 16) and biological assets at fair value less costs to sell (IAS 41). Use this for accounting-basis measurement of assets and equity; for going-concern cash flow use calculate_dcf and for peer multiples use calculate_market_multiple.",
    ),
    "calculate_option": (
        "Option and warrant pricing",
        "Option-pricing engine. Price European and American options and warrants (Black-Scholes, Black-76, CRR binomial, Garman-Kohlhagen FX, digital, range, share-based) and their greeks. Use this for contingent claims and option-based valuations; for equity-linked note structures use calculate_structured_product. Read-only and deterministic. Returns the shared result envelope.",
    ),
    "calculate_expected_value": (
        "Expected value and probability weighting",
        "Expected-value engine. Compute expected values over discrete, continuous, simulated, or tree-structured uncertainty, plus football-field ranges and discounted provisions. Use this to probability-weight scenarios and ranges inside a valuation; for regulated provisions and insurance or benefit obligations use calculate_actuarial_pv, and for path-dependent payoffs use calculate_structured_product.",
    ),
    "calculate_credit_loss": (
        "Credit loss and impairment",
        "Credit-risk engine (IFRS 9 / HKFRS 9). Compute 12-month, lifetime, and staged expected credit loss, PD/LGD/EAD, provision matrices, hazard rates, and CVA/DVA. Use this for impairment, fair-value credit adjustment, and loan-loss provisioning; for the credit component of a specific convertible bond use calculate_convertible_bond.",
    ),
    "calculate_actuarial_pv": (
        "Actuarial present value",
        "Actuarial present value engine. Discount expected cash flows with mortality, survival, and risk adjustment for insurance and benefit obligations, generalising IFRS 17 (fulfilment cash flows), IAS 19 (employee benefits), IFRS 2 (share-based payments), and IAS 37 (provisions). Use this for regulated actuarial obligations; for general scenario weighting use calculate_expected_value.",
    ),
    "calculate_sector_metrics": (
        "Sector-specific operating metrics",
        "Sector-metric engine. Compute the metrics that anchor valuation in specific industries: SaaS (ARR, NRR, magic number, Rule of 40), marketplaces (take rate, GMV multiple), lending (LTV/CAC), and crypto (NVT, Metcalfe). Use these as inputs to a multiple or DCF. Read-only and deterministic. Returns the shared result envelope.",
    ),
    "calculate_fair_value_adjustment": (
        "Fair value adjustments (IFRS 13)",
        "Fair-value-adjustment engine (IFRS 13). Compute exit-price adjustments including credit, liquidity, control and marketability discounts, blockage, and the fair-value hierarchy level. Use this to move from an indicated value to the fair value recognised in the accounts. Read-only and deterministic. Returns the shared result envelope.",
    ),
    "calculate_convertible_bond": (
        "Convertible and exchangeable bond valuation",
        "Convertible-bond engine. Value callable and puttable convertible or exchangeable bonds with credit risk using a Tsiveriotis-Fernandes lattice (equity discounted at the risk-free rate, debt at a credit spread), with conversion, issuer call, holder put, coupon schedule, and a straight-bond floor. Use this for HK-listed convertible and exchangeable bonds. Read-only and deterministic. Returns the shared result envelope.",
    ),
    "calculate_structured_product": (
        "Structured product and derivative pricing",
        "Structured-product engine. Value HKEX-listed and OTC structures: CBBCs, derivative and inline warrants, equity-linked notes and investments, autocallables, accumulators and decumulators, credit-linked notes, TRS, and CFDs. Use this for equity-linked and credit-linked payoff structures; for a plain option or warrant use calculate_option.",
    ),
    "calculate_loss_making_company": (
        "Loss-making and pre-profit company valuation",
        "Loss-making-company engine. Value currently unprofitable companies with margin-ramp DCF, revenue multiples, Merton structural equity, probability-weighted scenarios, the VC method, distressed waterfalls, bank residual income, and SPAC deals, each returning a central value plus a dispersion (sigma, percentiles, long-tail). Use this when earnings-based multiples break down. Read-only and deterministic. Returns the shared result envelope.",
    ),
    "calculate_report_review": (
        "Valuation report review and standards audit",
        "Report-review engine. Audit a valuation document against an IVS 2025 and IFRS/HKFRS checklist: methodology, assumptions, discount rate, standards basis, fair-value conclusion, valuation date, and fair-value hierarchy, each mapped to the governing standard. Macro-enabled files are refused. Read-only. Returns the shared result envelope with findings and a compliance score.",
    ),
    "calculate_company_summary": (
        "Company profile and market inputs",
        "Company-summary engine. Return a company profile with live market metrics (price, shares, beta, volatility, market capitalisation) to seed valuation inputs. Use this to seed inputs for the other calculate_* tools; it does not compute a valuation itself, and it omits missing fields rather than inventing them. Supplying a ticker performs a network fetch. Read-only. Returns the shared result envelope.",
    ),
    "calculate_fixed_income": (
        "Fixed income and term structure analytics",
        "Fixed-income engine. Price plain coupon bonds, solve for yield to maturity, measure interest-rate sensitivity via Macaulay and modified duration and convexity, and build a HIBOR/HKD-style term structure: bootstrap a zero curve from par rates, infer forward rates, and discount cash flows on the curve. Use this for vanilla bonds, rate risk and discount curves; for convertibles use calculate_convertible_bond and for structured payoffs use calculate_structured_product.",
    ),
}

_DCF = (
    MethodSpec(
        "dcf",
        "per-year FCFF plus a terminal value",
        ("cash_flows", "discount_rate"),
        "IVS 105 income approach; PV of projected FCFF",
        ("IVS 2025", "IFRS 13"),
    ),
    MethodSpec(
        "npv",
        "discount a cash-flow stream with no terminal value",
        ("cash_flows", "discount_rate"),
        "NPV = sum CF_t/(1+r)^t",
    ),
    MethodSpec(
        "annuity",
        "present value of a level payment for n periods",
        ("payment", "discount_rate", "periods"),
        "PV = PMT*[1-(1+r)^-n]/r",
    ),
    MethodSpec(
        "growing_annuity",
        "present value of a payment growing at a constant rate",
        ("payment", "discount_rate", "growth_rate", "periods"),
        "PV = PMT*[1-((1+g)/(1+r))^n]/(r-g)",
    ),
    MethodSpec(
        "perpetuity",
        "present value of a level perpetuity",
        ("payment", "discount_rate"),
        "PV = PMT/r",
    ),
    MethodSpec(
        "terminal_gordon",
        "Gordon-growth terminal value",
        ("final_cash_flow", "discount_rate", "perpetual_growth"),
        "TV = FCF*(1+g)/(r-g)",
    ),
    MethodSpec(
        "terminal_multiple",
        "exit-multiple terminal value",
        ("final_cash_flow", "exit_multiple"),
        "TV = FCF*exit_multiple",
    ),
    MethodSpec(
        "viu_pre_tax",
        "IAS 36 value in use with pre-tax cash flows and rate",
        ("cash_flows", "pre_tax_discount_rate"),
        "IAS 36 value in use",
        ("IAS 36",),
    ),
    MethodSpec(
        "rnpv",
        "each flow multiplied by its cumulative success probability",
        ("cash_flows", "discount_rate", "probabilities"),
        "rNPV = sum p_t*CF_t/(1+r)^t",
        ("IAS 38",),
    ),
    MethodSpec(
        "lease_pv",
        "IFRS 16 present value of lease payments at the incremental borrowing rate",
        ("lease_payments", "incremental_borrowing_rate"),
        "IFRS 16 lease liability",
        ("IFRS 16",),
    ),
)

_DISCOUNT_RATE = (
    MethodSpec(
        "wacc",
        "weighted average cost of capital",
        ("equity_weight", "debt_weight", "cost_equity", "cost_debt", "tax_rate"),
        "WACC = we*ke + wd*kd*(1-t)",
        ("IVS 2025",),
    ),
    MethodSpec(
        "capm",
        "capital asset pricing model cost of equity",
        ("risk_free", "beta", "market_return"),
        "E(R) = Rf + beta*(Rm - Rf)",
    ),
    MethodSpec(
        "startup_capm",
        "CAPM plus size and illiquidity premiums",
        ("risk_free", "beta", "market_risk_premium", "size_premium", "illiquidity_premium"),
        "r = Rf + beta*MRP + size + illiquidity",
    ),
    MethodSpec(
        "build_up",
        "additive build-up of risk premiums",
        (
            "risk_free",
            "equity_risk_premium",
            "size_premium",
            "industry_premium",
            "specific_premium",
        ),
        "r = Rf + ERP + size + industry + specific",
    ),
    MethodSpec(
        "currency_adjusted",
        "base rate plus currency and country premiums",
        ("base_rate", "currency_risk_premium", "country_risk_premium"),
        "r = base + currency + country",
    ),
    MethodSpec(
        "country_risk",
        "country risk premium as a sovereign spread",
        ("sovereign_yield", "us_risk_free"),
        "CRP = sovereign yield - US risk-free",
    ),
    MethodSpec(
        "esg",
        "base rate adjusted for ESG risk and opportunity",
        ("base_rate", "esg_risk_premium", "esg_opportunity_discount"),
        "r = base + ESG risk premium - ESG opportunity discount",
    ),
    MethodSpec(
        "portfolio_beta",
        "weighted-average beta of a portfolio",
        ("weights", "betas"),
        "beta_p = sum w_i*beta_i",
    ),
    MethodSpec(
        "ibr",
        "incremental borrowing rate: risk-free plus credit spread",
        ("risk_free", "credit_spread", "tenor_years"),
        "IBR = Rf + credit spread",
        ("IFRS 16",),
    ),
)

_MARKET_MULTIPLE = (
    MethodSpec(
        "ev_revenue",
        "EV/Revenue multiple applied to revenue",
        ("revenue", "ev_revenue_multiple"),
        "EV = revenue * multiple",
    ),
    MethodSpec(
        "ev_ebitda",
        "EV/EBITDA multiple applied to EBITDA",
        ("ebitda", "ev_ebitda_multiple"),
        "EV = EBITDA * multiple",
    ),
    MethodSpec(
        "ev_arr",
        "EV/ARR multiple applied to ARR",
        ("arr", "ev_arr_multiple"),
        "EV = ARR * multiple",
    ),
    MethodSpec(
        "ev_gmv",
        "EV/GMV multiple applied to GMV",
        ("gmv", "ev_gmv_multiple"),
        "EV = GMV * multiple",
    ),
    MethodSpec(
        "pe", "price/earnings multiple applied to EPS", ("eps", "pe_multiple"), "P = EPS * P/E"
    ),
    MethodSpec(
        "pb",
        "price/book multiple applied to book value per share",
        ("book_value_per_share", "pb_multiple"),
        "P = BVPS * P/B",
    ),
    MethodSpec(
        "ps",
        "price/sales multiple applied to sales per share",
        ("sales_per_share", "ps_multiple"),
        "P = SPS * P/S",
    ),
    MethodSpec(
        "cap_rate",
        "income capitalisation at a cap rate (IAS 40 / REIT)",
        ("net_operating_income", "cap_rate"),
        "V = NOI / cap rate",
        ("IAS 40",),
    ),
    MethodSpec(
        "regression",
        "regression-adjusted multiple",
        (
            "intercept",
            "growth_rate",
            "growth_coefficient",
            "market_maturity",
            "maturity_coefficient",
        ),
        "M = b0 + b1*growth + b2*maturity",
    ),
    MethodSpec(
        "royalty_cap",
        "capitalised royalty stream",
        ("revenue", "royalty_rate", "discount_rate"),
        "V = revenue*royalty rate / r",
    ),
    MethodSpec(
        "ddm",
        "dividend discount model",
        ("dividend_per_share", "cost_equity", "growth_rate"),
        "V = D1/(ke - g)",
    ),
)

_RESIDUAL = (
    MethodSpec(
        "goodwill",
        "goodwill as consideration less net identifiable assets",
        ("purchase_price", "fair_value_net_identifiable_assets"),
        "IFRS 3 goodwill residual",
        ("IFRS 3",),
    ),
    MethodSpec(
        "ppa",
        "purchase price allocation residual",
        ("purchase_price", "tangible_assets_fv", "identified_intangibles_fv"),
        "goodwill = price - (tangible + intangibles)",
        ("IFRS 3",),
    ),
    MethodSpec(
        "impairment_fvlcd",
        "impairment against fair value less costs to dispose",
        ("carrying_value", "fair_value_less_costs_to_dispose"),
        "IAS 36: loss = max(0, CV - FVLCD)",
        ("IAS 36",),
    ),
    MethodSpec(
        "impairment_viu",
        "impairment against value in use",
        ("carrying_value", "value_in_use"),
        "IAS 36: loss = max(0, CV - VIU)",
        ("IAS 36",),
    ),
    MethodSpec(
        "inventory_nrv",
        "inventory write-down to net realisable value",
        ("carrying_value", "net_realisable_value"),
        "IAS 2: write-down = max(0, cost - NRV)",
        ("IAS 2",),
    ),
    MethodSpec(
        "held_for_sale",
        "measure at lower of carrying amount and FV less costs to sell",
        ("carrying_value", "fair_value_less_costs_to_sell"),
        "IFRS 5 held-for-sale",
        ("IFRS 5",),
    ),
    MethodSpec(
        "debt_waterfall",
        "distribute enterprise value across ordered claims",
        ("enterprise_value", "claims"),
        "priority waterfall",
    ),
    MethodSpec(
        "cap_table",
        "allocate equity across the cap table",
        ("enterprise_value", "claims"),
        "cap-table allocation",
    ),
    MethodSpec(
        "sotp",
        "sum-of-the-parts less net debt and a holding discount",
        ("segments", "net_debt", "holding_discount"),
        "SOTP = sum(parts) - net debt, less holding discount",
        ("IFRS 10", "IAS 28"),
    ),
    MethodSpec(
        "spac_redemption",
        "SPAC trust redemption value per share",
        ("trust_cash", "shares_outstanding", "redemption_price"),
        "redemption value = min(trust cash / shares, redemption price)",
        ("IAS 32",),
    ),
    MethodSpec(
        "investment_property",
        "investment property at fair value",
        ("noi", "cap_rate"),
        "V = NOI / cap rate (IAS 40 / HKAS 40 income approach)",
        ("IAS 40",),
    ),
    MethodSpec(
        "ppe_revaluation",
        "PP&E revaluation via depreciated replacement cost",
        ("replacement_cost", "accumulated_depreciation"),
        "V = replacement cost - accumulated depreciation (IAS 16)",
        ("IAS 16",),
    ),
    MethodSpec(
        "biological_asset",
        "biological assets at fair value less costs to sell",
        ("expected_price", "quantity", "costs_to_sell"),
        "V = price * quantity - costs to sell (IAS 41)",
        ("IAS 41",),
    ),
    MethodSpec(
        "residual_income",
        "residual income model",
        ("book_value", "net_income", "cost_equity"),
        "V = BV + (NI - ke*BV)/ke",
    ),
    MethodSpec(
        "justified_pb",
        "justified price-to-book from ROE",
        ("roe", "cost_equity", "growth_rate"),
        "P/B = (ROE - g)/(ke - g)",
    ),
)

_OPTION = (
    MethodSpec(
        "black_scholes",
        "European analytic price",
        ("spot", "strike", "maturity", "risk_free", "volatility", "option_type"),
        "Black-Scholes-Merton",
        ("IFRS 13",),
    ),
    MethodSpec(
        "black76",
        "European price on a forward/futures",
        ("forward", "strike", "maturity", "risk_free", "volatility", "option_type"),
        "Black-76",
    ),
    MethodSpec(
        "binomial_american",
        "CRR lattice with early exercise",
        ("spot", "strike", "maturity", "risk_free", "volatility", "option_type", "steps"),
        "Cox-Ross-Rubinstein; early exercise",
    ),
    MethodSpec(
        "garman_kohlhagen",
        "European FX option price",
        (
            "spot",
            "strike",
            "maturity",
            "domestic_rate",
            "foreign_rate",
            "volatility",
            "option_type",
        ),
        "Garman-Kohlhagen",
    ),
    MethodSpec(
        "barrier_first_passage",
        "knock-in/knock-out with continuous monitoring (e.g. HKEX CBBCs)",
        (
            "spot",
            "strike",
            "maturity",
            "risk_free",
            "volatility",
            "option_type",
            "barrier",
            "barrier_type",
        ),
        "First-passage/barrier under GBM",
    ),
    MethodSpec(
        "asian_average",
        "settlement averaging (e.g. HKEX derivative warrants)",
        ("spot", "strike", "maturity", "risk_free", "volatility", "option_type", "average_type"),
        "Asian option",
    ),
    MethodSpec(
        "digital",
        "fixed payout when the condition is met",
        ("spot", "strike", "maturity", "risk_free", "volatility", "cash_payout"),
        "Cash-or-nothing digital",
    ),
    MethodSpec(
        "range",
        "fixed payout when settlement is inside two strikes (e.g. HKEX inline warrants)",
        ("spot", "lower_strike", "upper_strike", "maturity", "risk_free", "volatility", "payout"),
        "Difference of two range probabilities",
    ),
    MethodSpec(
        "share_based",
        "IFRS 2 grant-date fair value of an equity-settled award",
        (
            "share_price",
            "exercise_price",
            "expected_life",
            "volatility",
            "risk_free",
            "dividend_yield",
        ),
        "IFRS 2 fair-value-based measurement",
        ("IFRS 2",),
    ),
)

_EXPECTED_VALUE = (
    MethodSpec(
        "discrete",
        "expected value of a discrete distribution",
        ("outcomes", "probabilities"),
        "E[X] = sum p_i*x_i",
    ),
    MethodSpec(
        "continuous",
        "expected value under a normal distribution over a range",
        ("distribution", "mean", "std", "lower", "upper"),
        "E[X] over [a,b]",
    ),
    MethodSpec(
        "scenario", "probability-weighted scenario value", ("scenarios",), "E[V] = sum p_i*V_i"
    ),
    MethodSpec(
        "monte_carlo",
        "simulated distribution of an outcome",
        ("iterations", "distributions", "base_params"),
        "Monte-Carlo; mean/median/std/percentiles",
    ),
    MethodSpec(
        "decision_tree",
        "expected value over a decision tree",
        ("tree",),
        "roll back chance/decision nodes",
    ),
    MethodSpec(
        "football_field",
        "blend model estimates into a range",
        ("estimates",),
        "football-field range; no mechanical average",
    ),
)

_CREDIT_LOSS = (
    MethodSpec(
        "ecl_12m",
        "12-month expected credit loss",
        ("ead", "pd", "lgd"),
        "ECL = EAD*PD*LGD",
        ("IFRS 9",),
    ),
    MethodSpec(
        "ecl_lifetime",
        "lifetime expected credit loss",
        ("ead", "pd_lifetime", "lgd"),
        "ECL = EAD*PD_lifetime*LGD",
        ("IFRS 9",),
    ),
    MethodSpec(
        "ecl_staged",
        "staged ECL by IFRS 9 stage",
        ("ead", "pd_12m", "pd_lifetime", "lgd", "stage"),
        "IFRS 9 staging: 12m for stage 1, lifetime for stages 2-3",
        ("IFRS 9",),
    ),
    MethodSpec(
        "provision_matrix",
        "provision matrix over ageing buckets",
        ("receivables_ageing", "loss_rates"),
        "sum(bucket amount * loss rate)",
        ("IFRS 9",),
    ),
    MethodSpec(
        "pd_from_spread",
        "derive PD from a credit spread",
        ("credit_spread", "recovery", "tenor_years"),
        "PD approx spread/(1-recovery)",
    ),
    MethodSpec(
        "cumulative_pd",
        "cumulative PD from annual PD over years",
        ("annual_pd", "years"),
        "1-(1-pd)^n",
    ),
    MethodSpec(
        "hazard",
        "PD from a hazard rate over a tenor",
        ("hazard_rate", "tenor_years"),
        "PD = 1 - exp(-lambda*T)",
    ),
    MethodSpec(
        "cva_dva",
        "credit valuation adjustment on an exposure profile",
        ("exposure_profile", "pd", "lgd", "discount_rate"),
        "CVA = sum DF*EE*PD*LGD",
    ),
)

_ACTUARIAL = (
    MethodSpec(
        "ifrs17_gmm",
        "IFRS 17 general measurement model",
        ("cash_flows", "discount_rate", "risk_adjustment"),
        "fulfilment cash flows + risk adjustment + CSM",
        ("IFRS 17",),
    ),
    MethodSpec(
        "ifrs17_paa",
        "IFRS 17 premium allocation approach",
        ("premiums", "claims_cash", "acquisition_cash_flows", "coverage_periods"),
        "PAA liability for remaining coverage",
        ("IFRS 17",),
    ),
    MethodSpec(
        "ifrs17_vfa",
        "IFRS 17 variable fee approach",
        ("cash_flows", "discount_rate", "underlying_items_return", "risk_adjustment"),
        "VFA fulfilment cash flows",
        ("IFRS 17",),
    ),
    MethodSpec(
        "ias19_puc",
        "IAS 19 projected unit credit defined-benefit obligation",
        ("projected_benefits", "discount_rate", "attribution_years"),
        "PV of benefit obligation",
        ("IAS 19",),
    ),
    MethodSpec(
        "ias37_provision",
        "IAS 37 provision: expected value, discounted",
        ("outcomes", "probabilities", "discount_rate", "periods"),
        "IAS 37 best estimate, discounted",
        ("IAS 37",),
    ),
)

_SECTOR = (
    MethodSpec(
        "ltv",
        "SaaS customer lifetime value",
        ("arpu", "gross_margin", "churn_rate"),
        "LTV = ARPU*margin/churn",
    ),
    MethodSpec(
        "cac",
        "customer acquisition cost",
        ("sales_marketing_expense", "new_customers"),
        "CAC = S&M/new customers",
    ),
    MethodSpec(
        "arr",
        "annual recurring revenue from subscriptions",
        ("subscription_values",),
        "ARR = sum(subscriptions)",
    ),
    MethodSpec(
        "nrr",
        "net revenue retention",
        ("starting_revenue", "ending_revenue", "expansion_revenue"),
        "NRR = (ending+expansion)/starting",
    ),
    MethodSpec(
        "magic_number",
        "SaaS magic number",
        ("net_new_arr", "sales_marketing_expense_prior"),
        "net new ARR / prior S&M",
    ),
    MethodSpec(
        "rule_of_40", "growth plus margin", ("growth_rate", "profit_margin"), "growth + margin"
    ),
    MethodSpec("take_rate", "marketplace take rate", ("revenue", "gmv"), "take rate = revenue/GMV"),
    MethodSpec(
        "gmv_multiple",
        "GMV multiple valuation",
        ("gmv", "ev_gmv_multiple"),
        "value = GMV * multiple",
    ),
    MethodSpec(
        "retention",
        "customer retention rate",
        ("retained_customers", "starting_customers"),
        "retention = retained/starting",
    ),
    MethodSpec(
        "trl",
        "technology-readiness risk-adjusted value",
        ("market_size", "market_share", "margin", "exit_multiple", "trl_discount"),
        "value = market*share*margin*multiple*(1-discount)",
    ),
    MethodSpec(
        "break_even",
        "break-even volume",
        ("fixed_costs", "asp", "variable_cost"),
        "volume = FC/(ASP-VC)",
    ),
    MethodSpec("gross_margin", "unit gross margin", ("asp", "variable_cost"), "(ASP-VC)/ASP"),
    MethodSpec(
        "token",
        "equation-of-exchange token value",
        ("transaction_volume", "price_per_tx", "velocity", "supply"),
        "V = (volume*price)/(velocity*supply)",
    ),
    MethodSpec(
        "nvt",
        "network value to transactions ratio",
        ("market_cap", "transaction_volume"),
        "NVT = market cap / volume",
    ),
    MethodSpec("metcalfe", "Metcalfe network value", ("n", "coefficient"), "value = k*n^2"),
)

_ADJUST = (
    MethodSpec(
        "dlom",
        "discount for lack of marketability (Finnerty put)",
        ("base_value", "restricted_period", "volatility", "risk_free"),
        "IFRS 13 DLOM via average-strike put",
        ("IFRS 13",),
    ),
    MethodSpec(
        "dloc",
        "discount for lack of control",
        ("base_value", "transaction_cost_pct"),
        "value*(1-cost)",
        ("IFRS 13",),
    ),
    MethodSpec(
        "control_premium",
        "control premium over the minority value",
        ("base_value", "control_premium_pct"),
        "value*(1+premium)",
        ("IFRS 13",),
    ),
    MethodSpec(
        "minority_discount",
        "minority discount",
        ("base_value", "minority_discount_pct"),
        "value*(1-discount)",
        ("IFRS 13",),
    ),
    MethodSpec(
        "highest_best_use",
        "highest-and-best-use value",
        ("base_value", "alternative_use_values"),
        "max(base, financially feasible alternatives)",
        ("IFRS 13",),
    ),
    MethodSpec(
        "hierarchy_level",
        "IFRS 13 hierarchy level of an input",
        ("inputs",),
        "lowest significant input level",
        ("IFRS 13",),
    ),
)

_CONVERTIBLE_BOND = tuple(
    MethodSpec(
        engine,
        "callable/puttable convertible or exchangeable bond with credit",
        (
            "spot",
            "face",
            "coupon_rate",
            "maturity",
            "conversion_ratio",
            "volatility",
            "risk_free",
            "credit_spread",
            "call_schedule",
            "put_schedule",
            "rights_priority",
        ),
        "Tsiveriotis-Fernandes lattice / intensity / finite-difference / LSMC",
        ("IFRS 9", "IFRS 13"),
    )
    for engine in ("lattice_tsf", "lattice_intensity", "finite_difference", "lsmc", "quantlib")
)

_STRUCTURED = (
    MethodSpec(
        "cbbc",
        "callable bull/bear contract with mandatory call",
        (
            "notional",
            "spot",
            "strike",
            "barrier",
            "barrier_type",
            "maturity",
            "risk_free",
            "volatility",
            "option_type",
        ),
        "First-passage barrier with mandatory call and residual value",
    ),
    MethodSpec(
        "cbbc_residual",
        "CBBC with HKEX knock-out residual value",
        (
            "notional",
            "spot",
            "call_price",
            "entitlement",
            "barrier",
            "barrier_type",
            "maturity",
            "risk_free",
            "volatility",
            "option_type",
        ),
        "First-passage barrier; residual = (trigger-call)/entitlement on knock-out",
    ),
    MethodSpec(
        "derivative_warrant",
        "cash-settled derivative warrant (averaged settlement)",
        (
            "notional",
            "spot",
            "strike",
            "maturity",
            "risk_free",
            "volatility",
            "average_type",
            "option_type",
        ),
        "Asian-settled European warrant",
    ),
    MethodSpec(
        "inline_warrant",
        "range digital inline warrant (HKEX)",
        (
            "notional",
            "spot",
            "lower_strike",
            "upper_strike",
            "maturity",
            "risk_free",
            "volatility",
            "payout",
        ),
        "Range digital",
    ),
    MethodSpec(
        "inline_warrant_avg",
        "inline range warrant settled on an n-day average",
        (
            "notional",
            "spot",
            "lower_strike",
            "upper_strike",
            "maturity",
            "risk_free",
            "volatility",
            "payout",
            "fixing_days",
        ),
        "Range digital on averaged fixings (HKEX settlement)",
    ),
    MethodSpec(
        "eli",
        "equity-linked investment",
        ("notional", "spot", "strike", "maturity", "risk_free", "volatility", "coupon_rate"),
        "Debt plus short equity option",
    ),
    MethodSpec(
        "eln",
        "equity-linked note",
        ("notional", "spot", "strike", "maturity", "risk_free", "volatility", "coupon_rate"),
        "Debt plus embedded equity option",
    ),
    MethodSpec(
        "autocallable",
        "autocallable note",
        (
            "notional",
            "spot",
            "knock_out_level",
            "observation_dates",
            "coupon_rate_structured",
            "maturity",
            "risk_free",
            "volatility",
        ),
        "Correlated Monte-Carlo with autocall/knock-out",
    ),
    MethodSpec(
        "credit_linked_note",
        "credit-linked note",
        (
            "notional",
            "credit_spread",
            "recovery",
            "maturity",
            "risk_free",
            "coupon_rate_structured",
        ),
        "Debt plus reference-credit hazard",
        ("IFRS 9",),
    ),
    MethodSpec(
        "accumulator",
        "accumulator (periodic obligation to buy)",
        (
            "notional",
            "spot",
            "strike",
            "knock_out_level",
            "observation_dates",
            "risk_free",
            "volatility",
        ),
        "Multi-date lattice/Monte-Carlo with knock-out and multiplier",
    ),
    MethodSpec(
        "decumulator",
        "decumulator (periodic obligation to sell)",
        (
            "notional",
            "spot",
            "strike",
            "knock_out_level",
            "observation_dates",
            "risk_free",
            "volatility",
        ),
        "Multi-date lattice/Monte-Carlo with knock-out and multiplier",
    ),
    MethodSpec(
        "trs",
        "equity total-return swap",
        ("notional", "spot", "maturity", "risk_free", "dividend_yield"),
        "Forward/DCF plus CVA/DVA",
    ),
    MethodSpec(
        "cfd",
        "contract for difference",
        ("notional", "spot", "strike", "maturity", "risk_free"),
        "Cash-settled price difference",
    ),
)

_LOSS_MAKING = (
    MethodSpec(
        "margin_ramp_dcf",
        "margin-ramp DCF for a currently loss-making company",
        (
            "revenue",
            "growth_rate",
            "start_margin",
            "target_margin",
            "ramp_years",
            "discount_rate",
            "years",
            "shares_outstanding",
            "net_debt",
            "range_method",
        ),
        "FCFF with margin ramp; central value + dispersion",
        ("IFRS 13",),
    ),
    MethodSpec(
        "revenue_multiple",
        "revenue/ARR multiple value",
        ("revenue", "ev_revenue_multiple", "net_debt", "shares_outstanding", "range_method"),
        "Equity = EV - net debt",
        ("IFRS 13",),
    ),
    MethodSpec(
        "merton_equity",
        "equity as a call on firm assets",
        ("firm_value", "firm_volatility", "debt", "risk_free", "maturity", "range_method"),
        "Merton structural model",
        ("IFRS 13",),
    ),
    MethodSpec(
        "scenario",
        "probability-weighted scenario value",
        ("scenarios", "range_method"),
        "E[V] = sum p_i*V_i",
    ),
    MethodSpec(
        "vc_method",
        "venture-capital exit method",
        ("terminal_value", "target_return", "investment", "shares_outstanding", "range_method"),
        "Exit value discounted at the target return; dilution-aware",
    ),
    MethodSpec(
        "distressed_waterfall",
        "distressed/recovery waterfall",
        ("enterprise_value", "claims", "range_method"),
        "Priority waterfall, recovery values",
    ),
    MethodSpec(
        "bank_residual_income",
        "bank residual-income/justified P/B",
        ("book_value", "net_income", "cost_equity", "growth_rate", "range_method"),
        "Residual income over equity",
        ("IFRS 9",),
    ),
    MethodSpec(
        "spac_deal",
        "SPAC redemption and deal-outcome value",
        ("trust_cash", "shares_outstanding", "redemption_price", "range_method"),
        "Redemption value plus probability-weighted outcome",
        ("IAS 32",),
    ),
)

_REPORT = (
    MethodSpec(
        "audit",
        "audit a valuation document against methodology, assumptions and IFRS/HKFRS basis",
        ("file_path",),
        "IVS 2025 review; standards decision tree",
        ("IVS 2025", "IFRS 13"),
    ),
)

_COMPANY = (
    MethodSpec(
        "profile",
        "company profile and live market metrics for valuation inputs",
        ("ticker",),
        "market data",
    ),
)


_FIXED_INCOME = (
    MethodSpec(
        "bond_price",
        "present value of coupons and face from a yield",
        ("face", "coupon_rate", "years", "ytm", "frequency"),
        "Discounted cash flows at ytm/frequency",
        ("IFRS 13",),
    ),
    MethodSpec(
        "bond_yield",
        "yield to maturity implied by a price",
        ("face", "coupon_rate", "years", "price", "frequency"),
        "Bisection on ytm",
        ("IFRS 13",),
    ),
    MethodSpec(
        "duration",
        "Macaulay and modified duration",
        ("face", "coupon_rate", "years", "ytm", "frequency"),
        "PV-weighted time to cash flows",
        ("IFRS 13",),
    ),
    MethodSpec(
        "convexity",
        "second-order price sensitivity",
        ("face", "coupon_rate", "years", "ytm", "frequency"),
        "Convexity of the price-yield curve",
        ("IFRS 13",),
    ),
    MethodSpec(
        "discount_factor",
        "present value of one unit at a single rate",
        ("rate", "years", "frequency"),
        "DF = (1 + r/m)^(-m t)",
        ("IFRS 13",),
    ),
    MethodSpec(
        "zero_curve",
        "bootstrap zero rates from par rates on a tenor grid",
        ("par_rates", "tenors", "frequency"),
        "Sequential par-bond bootstrap, annual compounding",
        ("IFRS 13",),
    ),
    MethodSpec(
        "forward_rate",
        "implied forward rate between two tenors",
        ("zero_rates", "tenors", "t1", "t2"),
        "Forward from two bootstrapped zero rates",
        ("IFRS 13",),
    ),
    MethodSpec(
        "pv_curve",
        "discount cash flows on a zero curve",
        ("cash_flows", "times", "zero_rates", "tenors"),
        "Curve interpolation and discounting",
        ("IFRS 13",),
    ),
)


def register_all() -> None:
    """Register every tool's method table."""
    register("calculate_dcf", _DCF)
    register("calculate_discount_rate", _DISCOUNT_RATE)
    register("calculate_market_multiple", _MARKET_MULTIPLE)
    register("calculate_residual", _RESIDUAL)
    register("calculate_option", _OPTION)
    register("calculate_expected_value", _EXPECTED_VALUE)
    register("calculate_credit_loss", _CREDIT_LOSS)
    register("calculate_actuarial_pv", _ACTUARIAL)
    register("calculate_sector_metrics", _SECTOR)
    register("calculate_fair_value_adjustment", _ADJUST)
    register("calculate_convertible_bond", _CONVERTIBLE_BOND)
    register("calculate_structured_product", _STRUCTURED)
    register("calculate_loss_making_company", _LOSS_MAKING)
    register("calculate_report_review", _REPORT)
    register("calculate_company_summary", _COMPANY)
    register("calculate_fixed_income", _FIXED_INCOME)
    for tool, (title, description) in _TOOL_META.items():
        register_tool_meta(tool, title, description)
