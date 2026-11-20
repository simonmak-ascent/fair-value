"""Method specification registry (single source of truth for per-method inputs).

Locked design rule: **no implicit defaults**. Every input a method uses is
declared here as required. ``validate_arguments`` rejects both missing and
extraneous inputs, so a caller must make every choice consciously.

This module is import-light: no ``fastmcp``, no network, and no handler
execution at import time. It drives the MCP tool surface, the
``valuation://methods`` resource, generated CLI ``--help``, docs, and tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple


def _n(desc: str) -> Dict[str, Any]:
    return {"type": "number", "description": desc}


def _i(desc: str) -> Dict[str, Any]:
    return {"type": "integer", "description": desc}


def _s(desc: str) -> Dict[str, Any]:
    return {"type": "string", "description": desc}


def _nums(desc: str) -> Dict[str, Any]:
    return {"type": "array", "items": {"type": "number"}, "description": desc}


def _objs(desc: str) -> Dict[str, Any]:
    return {"type": "array", "items": {"type": "object"}, "description": desc}


def _enum(values: List[str], desc: str) -> Dict[str, Any]:
    return {"type": "string", "enum": values, "description": desc}


# ---------------------------------------------------------------------------
# Shared parameter vocabulary (name -> JSON-schema fragment). Every field is
# documented; the description prose adds interactions the schema cannot express.
# ---------------------------------------------------------------------------
PARAMS: Dict[str, Dict[str, Any]] = {
    # DCF / income
    "cash_flows": _nums("Projected cash flows in reporting currency, indexed t=1..n."),
    "discount_rate": _n(
        "Discount rate as a decimal (0.10 = 10%); pre-tax when method=viu_pre_tax."
    ),
    "pre_tax_discount_rate": _n(
        "Pre-tax discount rate (decimal), required by viu_pre_tax (IAS 36)."
    ),
    "terminal_growth": _n(
        "Perpetuity growth after the horizon (decimal); strictly below discount_rate."
    ),
    "perpetual_growth": _n("Gordon growth rate (decimal); strictly below discount_rate."),
    "exit_multiple": _n("Exit multiple on the final flow, e.g. 8.0 for 8x."),
    "final_cash_flow": _n("Final-period cash flow for the terminal value."),
    "payment": _n("Level periodic payment in reporting currency."),
    "growth_rate": _n("Periodic growth rate as a decimal (0.03 = 3%)."),
    "periods": _i("Number of periods n (>=1)."),
    "years": _i("Number of projection years n; equal len(cash_flows) when both are supplied."),
    "revenue": _n("Base-year revenue in reporting currency."),
    "start_margin": _n("Opening operating margin (decimal, may be negative); margin_ramp."),
    "target_margin": _n("Normalized margin reached after ramp_years; margin_ramp."),
    "ramp_years": _i("Years to move from start_margin to target_margin (>=1)."),
    "probabilities": _nums(
        "Cumulative success probability per period in [0,1], aligned with cash_flows."
    ),
    "lease_payments": _nums("Contractual lease payments in reporting currency, t=1..n."),
    "incremental_borrowing_rate": _n("Lessee incremental borrowing rate (decimal), IFRS 16."),
    # Discount rate
    "equity_weight": _n("Market-value weight of equity (decimal); with debt_weight must sum to 1."),
    "debt_weight": _n("Market-value weight of debt (decimal); with equity_weight must sum to 1."),
    "cost_equity": _n("Cost of equity as a decimal (0.12 = 12%)."),
    "cost_debt": _n("Pre-tax cost of debt as a decimal."),
    "tax_rate": _n("Marginal corporate tax rate as a decimal."),
    "beta": _n("Equity beta (market = 1.0)."),
    "market_return": _n("Expected market return (decimal)."),
    "market_risk_premium": _n("Market risk premium (decimal)."),
    "size_premium": _n("Small-size premium (decimal)."),
    "illiquidity_premium": _n("Illiquidity premium (decimal)."),
    "equity_risk_premium": _n("Equity risk premium (decimal)."),
    "industry_premium": _n("Industry risk premium (decimal)."),
    "specific_premium": _n("Company-specific risk premium (decimal)."),
    "base_rate": _n("Base rate before currency/country/ESG adjustment (decimal)."),
    "currency_risk_premium": _n("Currency risk premium (decimal)."),
    "country_risk_premium": _n("Country risk premium (decimal)."),
    "sovereign_yield": _n("Sovereign bond yield (decimal)."),
    "us_risk_free": _n("US Treasury risk-free yield (decimal)."),
    "esg_risk_premium": _n("ESG risk premium added to the base rate (decimal)."),
    "esg_opportunity_discount": _n(
        "ESG opportunity discount subtracted from the base rate (decimal)."
    ),
    "weights": _nums("Weights that must sum to 1."),
    "betas": _nums("Asset/segment betas aligned with weights."),
    "credit_spread": _n("Credit spread over the risk-free rate (decimal)."),
    "tenor_years": _n("Tenor in years (>0)."),
    # Market multiples
    "ev": _n("Enterprise value in reporting currency."),
    "ev_revenue_multiple": _n("EV/Revenue multiple."),
    "ebitda": _n("EBITDA in reporting currency."),
    "ev_ebitda_multiple": _n("EV/EBITDA multiple."),
    "arr": _n("Annual recurring revenue in reporting currency."),
    "ev_arr_multiple": _n("EV/ARR multiple."),
    "gmv": _n("Gross merchandise value in reporting currency."),
    "ev_gmv_multiple": _n("EV/GMV multiple."),
    "eps": _n("Earnings per share."),
    "pe_multiple": _n("Price/Earnings multiple."),
    "book_value_per_share": _n("Book value per share."),
    "pb_multiple": _n("Price/Book multiple."),
    "sales_per_share": _n("Sales per share."),
    "ps_multiple": _n("Price/Sales multiple."),
    "net_operating_income": _n("Stabilised net operating income in reporting currency."),
    "cap_rate": _n("Capitalisation rate as a decimal (0.06 = 6%)."),
    "intercept": _n("Regression intercept (base multiple)."),
    "growth_coefficient": _n("Regression slope on growth."),
    "market_maturity": _n("Market maturity indicator."),
    "maturity_coefficient": _n("Regression slope on market maturity."),
    "royalty_rate": _n("Royalty rate as a decimal (0.05 = 5% of revenue)."),
    "dividend_per_share": _n("Dividend per share in reporting currency."),
    "book_value": _n("Book value of equity in reporting currency."),
    "net_income": _n("Net income in reporting currency."),
    "roe": _n("Return on equity (decimal)."),
    # Residual / waterfall
    "purchase_price": _n("Consideration transferred in reporting currency."),
    "fair_value_net_identifiable_assets": _n("Fair value of net identifiable assets."),
    "tangible_assets_fv": _n("Fair value of tangible assets."),
    "identified_intangibles_fv": _n("Fair value of separately identified intangibles."),
    "carrying_value": _n("Carrying amount before the test."),
    "fair_value_less_costs_to_dispose": _n("FVLCD in reporting currency."),
    "value_in_use": _n("Value in use in reporting currency."),
    "contributory_charges": _nums(
        "Contributory-asset charges (economic rent) per period, aligned with cash_flows "
        "(IVS 210 MPEEM)."
    ),
    "with_cash_flows": _nums(
        "After-tax cash flows with the asset in use (IVS 210 with-and-without)."
    ),
    "without_cash_flows": _nums(
        "After-tax cash flows absent the asset (IVS 210 with-and-without), aligned with "
        "with_cash_flows."
    ),
    "fulfilment_costs": _nums(
        "Costs required to fulfil the performance obligation per period (IVS 220 Bottom-Up)."
    ),
    "mark_up": _n("Reasonable mark-up on fulfilment costs (decimal, IVS 220 Bottom-Up)."),
    "selling_price": _n("Estimated selling price of the finished inventory (IVS 230 top-down)."),
    "costs_to_complete": _n("Remaining costs to complete work-in-process inventory (IVS 230)."),
    "profit_allowance": _n("Estimated profit allowance on the completion/disposal effort."),
    "gross_development_value": _n(
        "Anticipated value of the completed development (IVS 410 residual method)."
    ),
    "development_costs": _n("All known/anticipated costs to complete the development."),
    "developer_profit": _n("Required developer's profit/risk allowance (IVS 410)."),
    "net_realisable_value": _n("Estimated NRV in reporting currency."),
    "fair_value_less_costs_to_sell": _n("FV less costs to sell in reporting currency."),
    "claims": _objs("Ordered claims [{name, amount, priority}] for a waterfall."),
    "enterprise_value": _n("Enterprise value distributed across claims."),
    "segments": _objs("Segments [{name, value}] for a sum-of-the-parts."),
    "holding_discount": _n("Holding-company discount as a decimal."),
    "net_debt": _n("Total debt minus cash and equivalents."),
    "trust_cash": _n("SPAC trust cash available for redemption."),
    "shares_outstanding": _n("Shares outstanding."),
    "redemption_price": _n("SPAC redemption price per share."),
    # Expected value
    "outcomes": _nums("Outcome values aligned with probabilities."),
    "distribution": _enum(
        ["normal", "lognormal", "uniform"],
        "Continuous distribution to integrate over.",
    ),
    "mean": _n("Distribution mean."),
    "std": _n("Distribution standard deviation (>0)."),
    "lower": _n("Lower integration bound."),
    "upper": _n("Upper integration bound."),
    "scenarios": _objs("Scenarios [{probability, value}] with probabilities summing to 1."),
    "iterations": _i("Monte-Carlo iterations (>=1000)."),
    "seed": _i("Deterministic RNG seed (required by simulation methods for reproducibility)."),
    "distributions": _objs("Input distributions [{parameter, type, mean, std}]."),
    "base_params": {"type": "object", "description": "Base parameter values for simulation."},
    "tree": {"type": "object", "description": "Decision tree with chance/decision nodes."},
    "estimates": _objs("Estimates [{method, central, low, high}] for a football field."),
    # Credit loss
    "ead": _n("Exposure at default in currency units."),
    "pd": _n("Probability of default over the horizon, in [0,1]."),
    "lgd": _n("Loss given default in [0,1] (1 - recovery rate)."),
    "pd_12m": _n("12-month PD in [0,1]."),
    "pd_lifetime": _n("Lifetime PD in [0,1]."),
    "stage": _i("IFRS 9 stage (1, 2 or 3)."),
    "receivables_ageing": _objs("Ageing buckets [{bucket, amount}]."),
    "loss_rates": _nums("Loss rate per ageing bucket."),
    "annual_pd": _n("Annual PD in [0,1]."),
    "exposure_profile": _nums("Expected exposure per period."),
    "recovery": _n("Recovery rate in [0,1]."),
    # Actuarial
    "risk_adjustment": _n("Explicit risk adjustment for non-financial risk."),
    "premiums": _n("Premiums in reporting currency."),
    "claims_cash": _n("Expected claims in reporting currency."),
    "acquisition_cash_flows": _n("Acquisition cash flows in reporting currency."),
    "coverage_periods": _i("Coverage periods for the PAA (>=1)."),
    "underlying_items_return": _n("Return on underlying items (decimal)."),
    "projected_benefits": _nums("Projected benefits per service year."),
    "attribution_years": _i("Years of service for attribution (>=1)."),
    # Sector metrics
    "arpu": _n("Average revenue per user per period."),
    "churn_rate": _n("Periodic churn rate as a decimal."),
    "sales_marketing_expense": _n("Sales and marketing spend for the period."),
    "new_customers": _i("Customers acquired in the period."),
    "subscription_values": _nums("Subscription revenue per customer."),
    "starting_revenue": _n("Revenue from the cohort at period start."),
    "ending_revenue": _n("Revenue from the cohort at period end."),
    "expansion_revenue": _n("Expansion revenue from the cohort."),
    "net_new_arr": _n("Net new ARR in the period."),
    "sales_marketing_expense_prior": _n("Prior-period sales and marketing spend."),
    "profit_margin": _n("Profit margin as a decimal."),
    "retained_customers": _i("Customers retained at period end."),
    "starting_customers": _i("Customers at period start."),
    "market_size": _n("Total addressable market in reporting currency."),
    "market_share": _n("Achievable market share as a decimal."),
    "margin": _n("Operating margin as a decimal."),
    "trl_discount": _n("Technology-readiness risk discount as a decimal."),
    "fixed_costs": _n("Period fixed costs."),
    "asp": _n("Average selling price per unit."),
    "variable_cost": _n("Variable cost per unit."),
    "transaction_volume": _n("Transaction volume for the period."),
    "price_per_tx": _n("Value per transaction."),
    "velocity": _n("Token velocity."),
    "supply": _n("Token supply."),
    "market_cap": _n("Market capitalisation."),
    "coefficient": _n("Scaling coefficient (Metcalfe)."),
    "n": _i("Node/participant count n (>=0)."),
    "gross_margin": _n("Gross margin as a decimal (0.80 = 80%)."),
    "hazard_rate": _n("Default hazard rate as a decimal."),
    # Fair-value adjustments
    "base_value": _n("Base valuation before the adjustment."),
    "restricted_period": _n("Restricted/marketability period in years (>=0)."),
    "transaction_cost_pct": _n("Transaction cost as a fraction of value."),
    "control_premium_pct": _n("Control premium as a fraction of value."),
    "minority_discount_pct": _n("Minority discount as a fraction of value."),
    "alternative_use_values": _nums("Financially feasible alternative-use values."),
    "inputs": _objs("Inputs [{value, level}] used to determine the hierarchy level."),
    # Options / contingent claims
    "spot": _n("Spot price of the underlying (or FX rate for garman_kohlhagen)."),
    "forward": _n("Forward/futures price of the underlying."),
    "strike": _n("Strike or exercise price in the same currency as spot."),
    "maturity": _n("Time to expiry in years (0.5 = six months); > 0."),
    "risk_free": _n("Continuously-compounded risk-free rate (decimal)."),
    "volatility": _n("Annualized volatility (decimal, 0.30 = 30%); > 0."),
    "option_type": _enum(["call", "put"], "Option right."),
    "steps": _i("Lattice steps for binomial_american (>=50)."),
    "barrier": _n("Knock level for barrier_first_passage."),
    "barrier_type": _enum(["knock_in", "knock_out"], "Barrier direction."),
    "average_type": _enum(["arithmetic", "geometric"], "Averaging convention."),
    "domestic_rate": _n("Domestic continuously-compounded rate (decimal)."),
    "foreign_rate": _n("Foreign continuously-compounded rate (decimal)."),
    "cash_payout": _n("Fixed cash amount paid when the digital condition is met."),
    "lower_strike": _n("Lower strike of the range."),
    "upper_strike": _n("Upper strike of the range."),
    "payout": _n("Fixed payout when the range condition is met."),
    "share_price": _n("Grant-date share price (IFRS 2)."),
    "exercise_price": _n("Exercise price of the award (IFRS 2)."),
    "expected_life": _n("Expected life of the award in years (IFRS 2)."),
    "dividend_yield": _n("Continuous dividend yield (decimal)."),
    # Convertible bond
    "face": _n("Bond face value."),
    "coupon_rate": _n("Annual coupon rate (decimal)."),
    "frequency": _i("Coupon payments per year (1=annual, 2=semi-annual)."),
    "ytm": _n("Yield to maturity (decimal, annualised)."),
    "price": _n("Dirty price of the instrument in reporting currency."),
    "par_rates": _nums("Par (coupon) rates per tenor, aligned with tenors (decimal)."),
    "tenors": _nums("Tenors in years, aligned with par_rates or zero_rates."),
    "target_tenor": _n("Target tenor in years for matrix pricing (interpolated)."),
    "benchmark_tenors": _nums("Benchmark tenors in years, sorted, aligned with benchmark_yields."),
    "benchmark_yields": _nums("Benchmark yields (decimal) at each benchmark tenor."),
    "zero_rates": _nums("Zero (spot) rates per tenor, decimal, annual compounding."),
    "times": _nums("Cash-flow times in years, aligned with cash_flows."),
    "t1": _n("Forward period start in years (>=0)."),
    "t2": _n("Forward period end in years (> t1)."),
    "rate": _n("A single interest/zero rate (decimal)."),
    "replacement_cost": _n("Depreciated-replacement-cost gross value of PP&E (IAS 16)."),
    "accumulated_depreciation": _n("Accumulated depreciation to deduct (IAS 16)."),
    "expected_price": _n("Expected market price per biological-asset unit (IAS 41)."),
    "quantity": _n("Number of units (biological assets)."),
    "costs_to_sell": _n("Incremental costs to sell / dispose (IAS 41)."),
    "noi": _n("Net operating income of the property (IAS 40)."),
    "call_price": _n("CBBC call price (mandatory-call trigger level)."),
    "entitlement": _n("CBBC entitlement: units of underlying per contract."),
    "fixing_days": _i("Number of closing fixings averaged for settlement (>=1)."),
    "conversion_ratio": _n("Shares received per bond on conversion."),
    "call_schedule": _objs(
        "Issuer call schedule [{date_years, price}]; pass [] when there is none."
    ),
    "put_schedule": _objs(
        "Investor put schedule [{date_years, price}]; pass [] when there is none."
    ),
    "rights_priority": _enum(
        ["holder", "issuer"], "Which right prevails when call and put coincide."
    ),
    # Structured product
    "product": _enum(
        [
            "cbbc",
            "derivative_warrant",
            "inline_warrant",
            "eli",
            "eln",
            "autocallable",
            "credit_linked_note",
            "accumulator",
            "decumulator",
            "trs",
            "cfd",
        ],
        "Structured-product family.",
    ),
    "observation_dates": _nums("Observation dates in years for path-dependent products."),
    "knock_out_level": _n("Knock-out level for autocallables and accumulators."),
    "coupon_rate_structured": _n("Conditional coupon rate (decimal)."),
    "notional": _n("Contract notional/face amount in reporting currency."),
    # Loss-making company
    "model": _enum(
        [
            "margin_ramp_dcf",
            "revenue_multiple",
            "merton_equity",
            "scenario",
            "vc_method",
            "distressed_waterfall",
            "bank_residual_income",
            "spac_deal",
        ],
        "Model to apply.",
    ),
    "range_method": _enum(
        ["central", "mean", "median", "downside", "upside"],
        "Statistic returned as the headline value; the full dispersion is always included.",
    ),
    "firm_value": _n("Firm/asset value for the Merton equity model."),
    "firm_volatility": _n("Asset volatility for the Merton equity model (decimal)."),
    "debt": _n("Debt face value (default point) for the Merton equity model."),
    "survival_probability": _n("Probability the company survives, in [0,1]."),
    "target_return": _n("VC target return multiple."),
    "investment": _n("Amount invested (VC method)."),
    "terminal_value": _n("Exit/terminal value (VC method)."),
    # Orthogonal
    "file_path": _s("Path to the report (.xlsx/.xls/.pdf/.docx/image)."),
    "ticker": _s("Equity ticker, e.g. '9988.HK'."),
}


@dataclass(frozen=True)
class MethodSpec:
    """Immutable specification of one method within a tool."""

    method: str
    summary: str
    required: Tuple[str, ...]
    formula_ref: str = ""
    standards: Tuple[str, ...] = ()
    # Dual-standard taxonomy (A-001): attached from ``standards/taxonomy.json``.
    approach: Optional[str] = None
    citations: Dict[str, Tuple[str, ...]] = field(default_factory=dict)
    solution_type: Optional[str] = None
    divergences: Tuple[Any, ...] = ()


_REGISTRY: Dict[str, Dict[str, MethodSpec]] = {}
_TOOL_META: Dict[str, Dict[str, str]] = {}


def register(tool: str, specs: Iterable[MethodSpec]) -> None:
    """Register (or replace) the method specs for ``tool``."""
    table = _REGISTRY.setdefault(tool, {})
    for spec in specs:
        table[spec.method] = spec


def register_tool_meta(tool: str, title: str, description: str) -> None:
    """Register the human-facing title and description for ``tool``."""
    _TOOL_META[tool] = {"title": title, "description": description}


def tool_meta(tool: str) -> Dict[str, str]:
    """Return the title/description for ``tool`` (empty when unset)."""
    return dict(_TOOL_META.get(tool, {}))


# Every registered tool is a valuation *calculation*. Report review was
# extracted to its own service (valuation-report-review), so the surface is now
# homogeneous; ``surface_kind`` is retained for the catalog schema.
SURFACE_KINDS: Dict[str, str] = {}


def surface_kind(tool: str) -> str:
    """Return the surface kind for ``tool`` (always ``"calculation"`` now)."""
    return SURFACE_KINDS.get(tool, "calculation")


def tools() -> List[str]:
    """Return the registered tool names, sorted."""
    return sorted(_REGISTRY)


def methods_for(tool: str) -> List[str]:
    """Return the method names for ``tool`` in registration order."""
    return list(_REGISTRY.get(tool, {}))


def get(tool: str, method: str) -> Optional[MethodSpec]:
    """Return the spec for ``tool``/``method``, or ``None``."""
    return _REGISTRY.get(tool, {}).get(method)


def spec_for_tool(tool: str) -> Dict[str, MethodSpec]:
    """Return a copy of the method table for ``tool``."""
    return dict(_REGISTRY.get(tool, {}))


def validate_arguments(tool: str, method: str, arguments: Dict[str, Any]) -> List[str]:
    """Return problems with ``arguments`` for a call (empty when valid).

    Enforces the locked no-defaults contract: a method's inputs are exactly its
    declared ``required`` parameters. Missing inputs are errors (no silent
    default); extraneous inputs are errors (no accidental parameter).
    """
    spec = get(tool, method)
    if spec is None:
        known = ", ".join(methods_for(tool)) or "(none registered)"
        return [f"unknown method '{method}' for {tool}; choose one of: {known}"]

    problems: List[str] = []
    missing = [name for name in spec.required if arguments.get(name) is None]
    if missing:
        problems.append(f"method '{method}' requires: {', '.join(missing)}")

    allowed = set(spec.required)
    extra = sorted(
        name for name in arguments if name not in allowed and arguments[name] is not None
    )
    if extra:
        problems.append(f"unexpected arguments for method '{method}': {', '.join(extra)}")
    return problems


def input_schema(tool: str) -> Dict[str, Any]:
    """Build the JSON input schema for ``tool`` from its method specs.

    ``method`` is required; the union of every method's parameters is
    documented; ``additionalProperties`` is false. Per-method required sets are
    enforced at call time by :func:`validate_arguments` and stated in the tool
    description and the ``valuation://methods`` resource.
    """
    table = spec_for_tool(tool)
    properties: Dict[str, Any] = {
        "method": {
            "type": "string",
            "enum": list(table),
            "description": "Formula to apply; the tool description lists the exact inputs each value requires.",
        }
    }
    for spec in table.values():
        for name in spec.required:
            if name in properties or name not in PARAMS:
                continue
            properties[name] = dict(PARAMS[name])
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["method"],
        "properties": properties,
    }


def method_matrix_text(tool: str) -> str:
    """Render a compact per-tool input matrix, grouping methods by required set."""
    groups: Dict[Tuple[str, ...], List[str]] = {}
    for name, spec in spec_for_tool(tool).items():
        groups.setdefault(spec.required, []).append(name)
    return "; ".join(
        f"{'/'.join(names)}: {', '.join(required)}" for required, names in groups.items()
    )


def validate_registry() -> List[str]:
    """Return problems with the registered tables (empty when sound)."""
    problems: List[str] = []
    for tool in _REGISTRY:
        if not methods_for(tool):
            problems.append(f"{tool}: no methods")
        meta = _TOOL_META.get(tool)
        if not meta:
            problems.append(f"{tool}: missing tool metadata (title/description)")
        elif len(meta.get("title", "")) <= len(tool):
            problems.append(f"{tool}: title must be longer than the tool name")
        for name, spec in spec_for_tool(tool).items():
            if spec.method != name:
                problems.append(f"{tool}.{name}: key/method mismatch")
            if not spec.required:
                problems.append(f"{tool}.{name}: no required inputs")
            for param in spec.required:
                if param not in PARAMS:
                    problems.append(f"{tool}.{name}: '{param}' missing from PARAMS")
    return problems


def register_seed() -> None:
    """Register the seed method tables (extended per engine in Phase 1)."""
    from .method_spec_seed import register_all

    register_all()


def catalog() -> Dict[str, Any]:
    """Return the machine-readable method catalog for the whole surface."""
    entries: List[Dict[str, Any]] = []
    for tool in tools():
        for name, spec in spec_for_tool(tool).items():
            entries.append(
                {
                    "tool": tool,
                    "method": name,
                    "summary": spec.summary,
                    "required": list(spec.required),
                    "formula_ref": spec.formula_ref,
                    "standards": list(spec.standards),
                    "approach": spec.approach,
                    "solution_type": spec.solution_type,
                    "surface": surface_kind(tool),
                    "citations": {k: list(v) for k, v in spec.citations.items()},
                    "divergences": [getattr(d, "parameter", d) for d in spec.divergences],
                }
            )
    return {
        "surface_version": "3.0",
        "tool_count": len(tools()),
        "method_count": len(entries),
        "methods": entries,
    }


def catalog_json() -> str:
    """Return :func:`catalog` serialized as deterministic JSON."""
    import json

    return json.dumps(catalog(), indent=2, sort_keys=True)


def methods_resource() -> Dict[str, Any]:
    """Canonical cross-service methods resource (see apdb-etl ``docs/boundary.md``).

    Shape::

        {server, version, tools:[{tool, title, methods:[
            {method, label, summary, required, optional}]}]}

    The apdb-etl data plane reads this from ``fair-value://methods``.
    """
    tools_out: List[Dict[str, Any]] = []
    for tool in tools():
        meta = tool_meta(tool)
        title = meta.get("title", tool.replace("_", " ").title())
        methods_out: List[Dict[str, Any]] = []
        for name, spec in spec_for_tool(tool).items():
            methods_out.append(
                {
                    "method": name,
                    # Per-method label (was the tool title for every method, which
                    # made every label identical); fall back to the tool title.
                    "label": spec.summary or title,
                    "summary": spec.summary,
                    "required": list(spec.required),
                    # fair-value's locked no-defaults contract: every listed
                    # parameter is required, so `optional` is intentionally empty
                    # (see validate_arguments). Consumers must not read this as
                    # "optional params were omitted".
                    "optional": [],
                }
            )
        tools_out.append({"tool": tool, "title": title, "methods": methods_out})
    return {
        "server": "fair-value",
        "version": catalog()["surface_version"],
        "tools": tools_out,
    }


def methods_resource_json() -> str:
    """Return :func:`methods_resource` serialized as deterministic JSON."""
    import json

    return json.dumps(methods_resource(), indent=2, sort_keys=True)


register_seed()


def attach_standards_registry(path: Optional[str] = None) -> Optional[Any]:
    """Load, validate and attach the dual-standard taxonomy to the registry.

    Returns the attached taxonomy, or ``None`` when no taxonomy file is present.
    An invalid taxonomy raises, so import and CI fail fast (a shallow or wrong
    taxonomy must never pass silently).
    """
    from .standards import attach_standards, load_taxonomy, validate_taxonomy

    taxonomy = load_taxonomy(path)
    validate_taxonomy(taxonomy, _REGISTRY)
    attach_standards(_REGISTRY, taxonomy)
    return taxonomy


try:  # pragma: no cover - absent-file path is the only tolerated failure
    _TAXONOMY: Optional[Any] = attach_standards_registry()
except FileNotFoundError:
    _TAXONOMY = None
