"""Engine handlers for the method-spec surface.

Each handler is pure, deterministic and network-free; it receives exactly the
parameters declared in :mod:`mcp_server.method_spec` and returns a value (or a
dict). :func:`mcp_server.engine.dispatch` validates arguments against the
registry, calls the handler, and wraps the result in the shared envelope.

Methods without a handler yet return ``NOT_IMPLEMENTED`` from dispatch (the
compositions and the two heaviest stochastic kernels are built in Phase 2).
"""

from __future__ import annotations

import math
from typing import Any, Callable, Dict, List

from scipy.stats import norm

from src.derivatives.options import black_scholes_price, binomial_tree_price

Handler = Callable[..., Any]
HANDLERS: Dict[str, Dict[str, Handler]] = {}


def _register(tool: str, methods: Dict[str, Handler]) -> None:
    HANDLERS.setdefault(tool, {}).update(methods)


def _sum_pv(flows: List[float], rate: float, *, start: int = 1) -> float:
    return sum(cf / (1.0 + rate) ** (i + start) for i, cf in enumerate(flows))


# ---------------------------------------------------------------------------
# calculate_dcf
# ---------------------------------------------------------------------------


def _dcf(cash_flows: List[float], discount_rate: float) -> Dict[str, Any]:
    return {"value": _sum_pv(cash_flows, discount_rate, start=1)}


def _npv(cash_flows: List[float], discount_rate: float) -> Dict[str, Any]:
    return {"value": _sum_pv(cash_flows, discount_rate, start=0)}


def _annuity(payment: float, discount_rate: float, periods: int) -> Dict[str, Any]:
    r = discount_rate
    value = payment * periods if r == 0 else payment * (1 - (1 + r) ** -periods) / r
    return {"value": value}


def _growing_annuity(
    payment: float, discount_rate: float, growth_rate: float, periods: int
) -> Dict[str, Any]:
    r, g = discount_rate, growth_rate
    if abs(r - g) < 1e-12:
        return {"value": payment * periods / (1 + r)}
    return {"value": payment * (1 - ((1 + g) / (1 + r)) ** periods) / (r - g)}


def _perpetuity(payment: float, discount_rate: float) -> Dict[str, Any]:
    return {"value": payment / discount_rate}


def _terminal_gordon(
    final_cash_flow: float, discount_rate: float, perpetual_growth: float
) -> Dict[str, Any]:
    if perpetual_growth >= discount_rate:
        raise ValueError("perpetual_growth must be below discount_rate")
    return {"value": final_cash_flow * (1 + perpetual_growth) / (discount_rate - perpetual_growth)}


def _terminal_multiple(final_cash_flow: float, exit_multiple: float) -> Dict[str, Any]:
    return {"value": final_cash_flow * exit_multiple}


def _margin_ramp(
    revenue: float,
    growth_rate: float,
    start_margin: float,
    target_margin: float,
    ramp_years: int,
    discount_rate: float,
    years: int,
) -> Dict[str, Any]:
    if years <= 0 or ramp_years <= 0:
        raise ValueError("years and ramp_years must be positive")
    rows = []
    total = 0.0
    for t in range(1, years + 1):
        margin = start_margin + (target_margin - start_margin) * min(t / ramp_years, 1.0)
        rev = revenue * (1 + growth_rate) ** t
        fcff = rev * margin
        pv = fcff / (1 + discount_rate) ** t
        total += pv
        rows.append({"year": t, "revenue": rev, "margin": margin, "fcff": fcff, "pv": pv})
    return {"value": total, "steps": rows}


def _viu_pre_tax(cash_flows: List[float], pre_tax_discount_rate: float) -> Dict[str, Any]:
    return {"value": _sum_pv(cash_flows, pre_tax_discount_rate, start=1)}


def _rnpv(
    cash_flows: List[float], discount_rate: float, probabilities: List[float]
) -> Dict[str, Any]:
    if len(cash_flows) != len(probabilities):
        raise ValueError("cash_flows and probabilities must be equal length")
    return {
        "value": sum(
            p * cf / (1 + discount_rate) ** (i + 1)
            for i, (cf, p) in enumerate(zip(cash_flows, probabilities))
        )
    }


def _lease_pv(lease_payments: List[float], incremental_borrowing_rate: float) -> Dict[str, Any]:
    return {"value": _sum_pv(lease_payments, incremental_borrowing_rate, start=1)}


# ---------------------------------------------------------------------------
# calculate_discount_rate
# ---------------------------------------------------------------------------


def _wacc(
    equity_weight: float, debt_weight: float, cost_equity: float, cost_debt: float, tax_rate: float
) -> Dict[str, Any]:
    if abs(equity_weight + debt_weight - 1.0) > 1e-6:
        raise ValueError("equity_weight and debt_weight must sum to 1")
    return {"value": equity_weight * cost_equity + debt_weight * cost_debt * (1 - tax_rate)}


def _capm(risk_free: float, beta: float, market_return: float) -> Dict[str, Any]:
    return {"value": risk_free + beta * (market_return - risk_free)}


def _startup_capm(
    risk_free: float,
    beta: float,
    market_risk_premium: float,
    size_premium: float,
    illiquidity_premium: float,
) -> Dict[str, Any]:
    return {"value": risk_free + beta * market_risk_premium + size_premium + illiquidity_premium}


def _build_up(
    risk_free: float,
    equity_risk_premium: float,
    size_premium: float,
    industry_premium: float,
    specific_premium: float,
) -> Dict[str, Any]:
    return {
        "value": risk_free
        + equity_risk_premium
        + size_premium
        + industry_premium
        + specific_premium
    }


def _currency_adjusted(
    base_rate: float, currency_risk_premium: float, country_risk_premium: float
) -> Dict[str, Any]:
    return {"value": base_rate + currency_risk_premium + country_risk_premium}


def _country_risk(sovereign_yield: float, us_risk_free: float) -> Dict[str, Any]:
    return {"value": sovereign_yield - us_risk_free}


def _esg(
    base_rate: float, esg_risk_premium: float, esg_opportunity_discount: float
) -> Dict[str, Any]:
    return {"value": base_rate + esg_risk_premium - esg_opportunity_discount}


def _portfolio_beta(weights: List[float], betas: List[float]) -> Dict[str, Any]:
    if len(weights) != len(betas):
        raise ValueError("weights and betas must be equal length")
    return {"value": sum(w * b for w, b in zip(weights, betas))}


def _ibr(risk_free: float, credit_spread: float, tenor_years: float) -> Dict[str, Any]:
    return {"value": risk_free + credit_spread}


# ---------------------------------------------------------------------------
# calculate_market_multiple
# ---------------------------------------------------------------------------


def _mul(metric: float, multiple: float) -> Dict[str, Any]:
    return {"value": metric * multiple}


def _regression(
    intercept: float,
    growth_rate: float,
    growth_coefficient: float,
    market_maturity: float,
    maturity_coefficient: float,
) -> Dict[str, Any]:
    return {
        "value": intercept
        + growth_rate * growth_coefficient
        + market_maturity * maturity_coefficient
    }


def _royalty_cap(revenue: float, royalty_rate: float, discount_rate: float) -> Dict[str, Any]:
    return {"value": revenue * royalty_rate / discount_rate}


def _ddm(dividend_per_share: float, cost_equity: float, growth_rate: float) -> Dict[str, Any]:
    if growth_rate >= cost_equity:
        raise ValueError("growth_rate must be below cost_equity")
    return {"value": dividend_per_share * (1 + growth_rate) / (cost_equity - growth_rate)}


def _residual_income(book_value: float, net_income: float, cost_equity: float) -> Dict[str, Any]:
    return {"value": book_value + (net_income - cost_equity * book_value) / cost_equity}


def _justified_pb(roe: float, cost_equity: float, growth_rate: float) -> Dict[str, Any]:
    if growth_rate >= cost_equity:
        raise ValueError("growth_rate must be below cost_equity")
    return {"value": (roe - growth_rate) / (cost_equity - growth_rate)}


# ---------------------------------------------------------------------------
# calculate_residual
# ---------------------------------------------------------------------------


def _goodwill(purchase_price: float, fair_value_net_identifiable_assets: float) -> Dict[str, Any]:
    return {"value": purchase_price - fair_value_net_identifiable_assets}


def _ppa(
    purchase_price: float, tangible_assets_fv: float, identified_intangibles_fv: float
) -> Dict[str, Any]:
    return {"value": purchase_price - (tangible_assets_fv + identified_intangibles_fv)}


def _impairment(carrying_value: float, recoverable: float) -> Dict[str, Any]:
    return {"value": max(0.0, carrying_value - recoverable)}


def _dip(value: float, reference: float) -> Dict[str, Any]:
    return {"value": max(0.0, value - reference)}


def _debt_waterfall(enterprise_value: float, claims: List[Dict[str, Any]]) -> Dict[str, Any]:
    remaining = enterprise_value
    allocation = []
    for claim in claims:
        amount = float(claim.get("amount", 0.0))
        paid = min(remaining, amount)
        remaining -= paid
        allocation.append({"name": claim.get("name", ""), "paid": paid, "shortfall": amount - paid})
    return {
        "value": enterprise_value - max(remaining, 0.0),
        "allocation": allocation,
        "residual_to_equity": remaining,
    }


def _sotp(
    segments: List[Dict[str, Any]], net_debt: float, holding_discount: float
) -> Dict[str, Any]:
    gross = sum(float(seg.get("value", 0.0)) for seg in segments)
    equity = (gross - net_debt) * (1 - holding_discount)
    return {"value": equity}


def _spac_redemption(
    trust_cash: float, shares_outstanding: float, redemption_price: float
) -> Dict[str, Any]:
    return {"value": min(trust_cash / shares_outstanding, redemption_price)}


# ---------------------------------------------------------------------------
# calculate_option
# ---------------------------------------------------------------------------


def _bs(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str,
) -> Dict[str, Any]:
    return {
        "value": black_scholes_price(spot, strike, maturity, risk_free, volatility, option_type),
        "delta": float(
            norm.cdf(
                (math.log(spot / strike) + (risk_free + 0.5 * volatility**2) * maturity)
                / (volatility * maturity**0.5)
            )
        )
        if option_type == "call"
        else float(
            norm.cdf(
                (math.log(spot / strike) + (risk_free + 0.5 * volatility**2) * maturity)
                / (volatility * maturity**0.5)
            )
        )
        - 1,
    }


def _binomial_american(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str,
    steps: int,
) -> Dict[str, Any]:
    return {
        "value": binomial_tree_price(
            spot, strike, maturity, risk_free, volatility, steps, option_type, american=True
        )
    }


def _black76(
    forward: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str,
) -> Dict[str, Any]:
    price = black_scholes_price(forward, strike, maturity, risk_free, volatility, option_type)
    return {"value": price * math.exp(-risk_free * maturity)}


def _garman(
    spot: float,
    strike: float,
    maturity: float,
    domestic_rate: float,
    foreign_rate: float,
    volatility: float,
    option_type: str,
) -> Dict[str, Any]:
    from src.derivatives.options import garman_kohlhagen

    return {
        "value": garman_kohlhagen(
            spot, strike, maturity, domestic_rate, foreign_rate, volatility, option_type
        )
    }


def _digital(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    cash_payout: float,
) -> Dict[str, Any]:
    from math import log, sqrt

    d2 = (log(spot / strike) + (risk_free - 0.5 * volatility**2) * maturity) / (
        volatility * sqrt(maturity)
    )
    return {"value": cash_payout * math.exp(-risk_free * maturity) * float(norm.cdf(d2))}


def _range(
    spot: float,
    lower_strike: float,
    upper_strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    payout: float,
) -> Dict[str, Any]:
    from math import log, sqrt

    def prob(bound: float) -> float:
        d = (log(spot / bound) + (risk_free - 0.5 * volatility**2) * maturity) / (
            volatility * sqrt(maturity)
        )
        return float(norm.cdf(d))

    return {
        "value": payout
        * math.exp(-risk_free * maturity)
        * (prob(lower_strike) - prob(upper_strike))
    }


def _share_based(
    share_price: float,
    exercise_price: float,
    expected_life: float,
    volatility: float,
    risk_free: float,
    dividend_yield: float,
) -> Dict[str, Any]:
    from math import log, sqrt

    d1 = (
        log(share_price / exercise_price)
        + (risk_free - dividend_yield + 0.5 * volatility**2) * expected_life
    ) / (volatility * sqrt(expected_life))
    d2 = d1 - volatility * sqrt(expected_life)
    value = share_price * math.exp(-dividend_yield * expected_life) * float(
        norm.cdf(d1)
    ) - exercise_price * math.exp(-risk_free * expected_life) * float(norm.cdf(d2))
    return {"value": value}


# ---------------------------------------------------------------------------
# calculate_credit_loss
# ---------------------------------------------------------------------------


def _ecl(ead: float, pd: float, lgd: float) -> Dict[str, Any]:
    return {"value": ead * pd * lgd}


def _ecl_lifetime(ead: float, pd_lifetime: float, lgd: float) -> Dict[str, Any]:
    return {"value": ead * pd_lifetime * lgd}


def _ecl_staged(
    ead: float, pd_12m: float, pd_lifetime: float, lgd: float, stage: int
) -> Dict[str, Any]:
    pd = pd_12m if stage == 1 else pd_lifetime
    return {"value": ead * pd * lgd, "stage": stage, "pd_used": pd}


def _provision_matrix(
    receivables_ageing: List[Dict[str, Any]], loss_rates: List[float]
) -> Dict[str, Any]:
    if len(receivables_ageing) != len(loss_rates):
        raise ValueError("receivables_ageing and loss_rates must be equal length")
    value = sum(
        float(b.get("amount", 0.0)) * rate for b, rate in zip(receivables_ageing, loss_rates)
    )
    return {"value": value}


def _pd_from_spread(credit_spread: float, recovery: float, tenor_years: float) -> Dict[str, Any]:
    return {"value": credit_spread / (1 - recovery) if recovery < 1 else 1.0}


def _cumulative_pd(annual_pd: float, years: int) -> Dict[str, Any]:
    return {"value": 1 - (1 - annual_pd) ** years}


def _hazard(hazard_rate: float, tenor_years: float) -> Dict[str, Any]:
    import math

    return {"value": 1 - math.exp(-hazard_rate * tenor_years)}


def _cva(
    exposure_profile: List[float], pd: float, lgd: float, discount_rate: float
) -> Dict[str, Any]:
    value = sum(
        ee / (1 + discount_rate) ** (i + 1) * pd * lgd for i, ee in enumerate(exposure_profile)
    )
    return {"value": value}


# ---------------------------------------------------------------------------
# calculate_sector_metrics
# ---------------------------------------------------------------------------


def _ltv(arpu: float, gross_margin: float, churn_rate: float) -> Dict[str, Any]:
    return {"value": arpu * gross_margin / churn_rate}


def _cac(sales_marketing_expense: float, new_customers: int) -> Dict[str, Any]:
    return {"value": sales_marketing_expense / new_customers}


def _arr(subscription_values: List[float]) -> Dict[str, Any]:
    return {"value": sum(subscription_values)}


def _nrr(
    starting_revenue: float, ending_revenue: float, expansion_revenue: float
) -> Dict[str, Any]:
    return {"value": (ending_revenue + expansion_revenue) / starting_revenue}


def _magic_number(net_new_arr: float, sales_marketing_expense_prior: float) -> Dict[str, Any]:
    return {"value": net_new_arr / sales_marketing_expense_prior}


def _rule_of_40(growth_rate: float, profit_margin: float) -> Dict[str, Any]:
    return {"value": growth_rate + profit_margin}


def _take_rate(revenue: float, gmv: float) -> Dict[str, Any]:
    return {"value": revenue / gmv}


def _retention(retained_customers: int, starting_customers: int) -> Dict[str, Any]:
    return {"value": retained_customers / starting_customers}


def _trl(
    market_size: float,
    market_share: float,
    margin: float,
    exit_multiple: float,
    trl_discount: float,
) -> Dict[str, Any]:
    return {"value": market_size * market_share * margin * exit_multiple * (1 - trl_discount)}


def _break_even(fixed_costs: float, asp: float, variable_cost: float) -> Dict[str, Any]:
    return {"value": fixed_costs / (asp - variable_cost)}


def _gross_margin(asp: float, variable_cost: float) -> Dict[str, Any]:
    return {"value": (asp - variable_cost) / asp}


def _token(
    transaction_volume: float, price_per_tx: float, velocity: float, supply: float
) -> Dict[str, Any]:
    return {"value": (transaction_volume * price_per_tx) / (velocity * supply)}


def _nvt(market_cap: float, transaction_volume: float) -> Dict[str, Any]:
    return {"value": market_cap / transaction_volume}


def _metcalfe(n: int, coefficient: float) -> Dict[str, Any]:
    return {"value": coefficient * n * n}


# ---------------------------------------------------------------------------
# calculate_expected_value
# ---------------------------------------------------------------------------


def _ev_discrete(outcomes: List[float], probabilities: List[float]) -> Dict[str, Any]:
    if len(outcomes) != len(probabilities):
        raise ValueError("outcomes and probabilities must be equal length")
    return {"value": sum(o * p for o, p in zip(outcomes, probabilities))}


def _ev_scenario(scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "value": sum(
            float(s.get("probability", 0.0)) * float(s.get("value", 0.0)) for s in scenarios
        )
    }


def _ev_provision(
    outcomes: List[float], probabilities: List[float], discount_rate: float, periods: int
) -> Dict[str, Any]:
    expected = sum(o * p for o, p in zip(outcomes, probabilities))
    return {"value": expected / (1 + discount_rate) ** periods}


def _ev_football_field(estimates: List[Dict[str, Any]]) -> Dict[str, Any]:
    centrals = [float(e.get("central", 0.0)) for e in estimates]
    lows = [float(e.get("low", 0.0)) for e in estimates]
    highs = [float(e.get("high", 0.0)) for e in estimates]
    centrals.sort()
    mid = (
        centrals[len(centrals) // 2]
        if len(centrals) % 2
        else (centrals[len(centrals) // 2 - 1] + centrals[len(centrals) // 2]) / 2
    )
    return {"value": mid, "low": min(lows), "high": max(highs)}


# ---------------------------------------------------------------------------
# calculate_actuarial_pv
# ---------------------------------------------------------------------------


def _actuarial_pv(flows: List[float], rate: float, risk_adjustment: float = 0.0) -> Dict[str, Any]:
    return {"value": _sum_pv(flows, rate, start=1) + risk_adjustment}


def _ifrs17_paa(
    premiums: float, claims_cash: float, acquisition_cash_flows: float, coverage_periods: int
) -> Dict[str, Any]:
    return {
        "value": premiums - claims_cash - acquisition_cash_flows,
        "per_period": (premiums - claims_cash - acquisition_cash_flows) / coverage_periods,
    }


def _ias19_puc(
    projected_benefits: List[float], discount_rate: float, attribution_years: int
) -> Dict[str, Any]:
    benefit = sum(projected_benefits) / attribution_years
    return {
        "value": sum(benefit / (1 + discount_rate) ** (t + 1) for t in range(attribution_years))
    }


def _ias37(
    outcomes: List[float], probabilities: List[float], discount_rate: float, periods: int
) -> Dict[str, Any]:
    expected = sum(o * p for o, p in zip(outcomes, probabilities))
    return {"value": expected / (1 + discount_rate) ** periods}


# ---------------------------------------------------------------------------
# calculate_fair_value_adjustment
# ---------------------------------------------------------------------------


def _dlom(
    base_value: float, restricted_period: float, volatility: float, risk_free: float
) -> Dict[str, Any]:
    import math

    if restricted_period <= 0:
        return {"value": base_value, "dlom": 0.0}
    d1 = volatility * math.sqrt(restricted_period) / 2
    d2 = -d1
    put = (1 / (risk_free * restricted_period)) * (
        risk_free * restricted_period * float(norm.cdf(-d2))
        - (math.exp(risk_free * restricted_period) - 1) * float(norm.cdf(-d1))
    )
    dlom = min(max(put, 0.0), 1.0)
    return {"value": base_value * (1 - dlom), "dlom": dlom}


def _pct_adjust(base_value: float, pct: float, sign: int) -> Dict[str, Any]:
    return {"value": base_value * (1 + sign * pct)}


def _hbu(base_value: float, alternative_use_values: List[float]) -> Dict[str, Any]:
    return {"value": max([base_value, *alternative_use_values])}


def _hierarchy(inputs: List[Dict[str, Any]]) -> Dict[str, Any]:
    levels = [int(i.get("level", 3)) for i in inputs] or [3]
    return {"value": max(levels), "level": max(levels)}


# ---------------------------------------------------------------------------
# registration
# ---------------------------------------------------------------------------

_register(
    "calculate_dcf",
    {
        "dcf": _dcf,
        "npv": _npv,
        "annuity": _annuity,
        "growing_annuity": _growing_annuity,
        "perpetuity": _perpetuity,
        "terminal_gordon": _terminal_gordon,
        "terminal_multiple": _terminal_multiple,
        "margin_ramp": _margin_ramp,
        "viu_pre_tax": _viu_pre_tax,
        "rnpv": _rnpv,
        "lease_pv": _lease_pv,
    },
)
_register(
    "calculate_discount_rate",
    {
        "wacc": _wacc,
        "capm": _capm,
        "startup_capm": _startup_capm,
        "build_up": _build_up,
        "currency_adjusted": _currency_adjusted,
        "country_risk": _country_risk,
        "esg": _esg,
        "portfolio_beta": _portfolio_beta,
        "ibr": _ibr,
    },
)
_register(
    "calculate_market_multiple",
    {
        "ev_revenue": lambda revenue, ev_revenue_multiple: _mul(revenue, ev_revenue_multiple),
        "ev_ebitda": lambda ebitda, ev_ebitda_multiple: _mul(ebitda, ev_ebitda_multiple),
        "ev_arr": lambda arr, ev_arr_multiple: _mul(arr, ev_arr_multiple),
        "ev_gmv": lambda gmv, ev_gmv_multiple: _mul(gmv, ev_gmv_multiple),
        "pe": lambda eps, pe_multiple: _mul(eps, pe_multiple),
        "pb": lambda book_value_per_share, pb_multiple: _mul(book_value_per_share, pb_multiple),
        "ps": lambda sales_per_share, ps_multiple: _mul(sales_per_share, ps_multiple),
        "cap_rate": lambda net_operating_income, cap_rate: {
            "value": net_operating_income / cap_rate
        },
        "regression": _regression,
        "royalty_cap": _royalty_cap,
        "ddm": _ddm,
        "residual_income": _residual_income,
        "justified_pb": _justified_pb,
    },
)
_register(
    "calculate_residual",
    {
        "goodwill": _goodwill,
        "ppa": _ppa,
        "impairment_fvlcd": lambda carrying_value, fair_value_less_costs_to_dispose: _impairment(
            carrying_value, fair_value_less_costs_to_dispose
        ),
        "impairment_viu": lambda carrying_value, value_in_use: _impairment(
            carrying_value, value_in_use
        ),
        "inventory_nrv": lambda carrying_value, net_realisable_value: _impairment(
            carrying_value, net_realisable_value
        ),
        "held_for_sale": lambda carrying_value, fair_value_less_costs_to_sell: _dip(
            carrying_value, fair_value_less_costs_to_sell
        ),
        "debt_waterfall": _debt_waterfall,
        "cap_table": _debt_waterfall,
        "sotp": _sotp,
        "spac_redemption": _spac_redemption,
    },
)


def _asian_average(spot, strike, maturity, risk_free, volatility, option_type, average_type):
    from src.derivatives import structured_products as sp

    return sp.geometric_asian(
        spot, spot, strike, maturity, risk_free, volatility, option_type, average_type
    )


def _barrier_first_passage(
    spot, strike, barrier, barrier_type, maturity, risk_free, volatility, option_type
):
    from src.derivatives import structured_products as sp

    return sp.barrier_mc(
        spot, spot, strike, barrier, barrier_type, maturity, risk_free, volatility, option_type
    )


_register(
    "calculate_option",
    {
        "black_scholes": _bs,
        "black76": _black76,
        "binomial_american": _binomial_american,
        "garman_kohlhagen": _garman,
        "digital": _digital,
        "range": _range,
        "share_based": _share_based,
        "asian_average": _asian_average,
        "barrier_first_passage": _barrier_first_passage,
    },
)
_register(
    "calculate_credit_loss",
    {
        "ecl_12m": _ecl,
        "ecl_lifetime": _ecl_lifetime,
        "ecl_staged": _ecl_staged,
        "provision_matrix": _provision_matrix,
        "pd_from_spread": _pd_from_spread,
        "cumulative_pd": _cumulative_pd,
        "hazard": _hazard,
        "cva_dva": _cva,
    },
)
_register(
    "calculate_sector_metrics",
    {
        "ltv": _ltv,
        "cac": _cac,
        "arr": _arr,
        "nrr": _nrr,
        "magic_number": _magic_number,
        "rule_of_40": _rule_of_40,
        "take_rate": _take_rate,
        "gmv_multiple": lambda gmv, ev_gmv_multiple: _mul(gmv, ev_gmv_multiple),
        "retention": _retention,
        "trl": _trl,
        "break_even": _break_even,
        "gross_margin": _gross_margin,
        "token": _token,
        "nvt": _nvt,
        "metcalfe": _metcalfe,
    },
)


def _ev_continuous(distribution, mean, std, lower, upper):
    from src.valuation import expected_value as ev

    return ev.continuous(distribution, mean, std, lower, upper)


def _ev_monte_carlo(iterations, distributions, base_params):
    from src.valuation import expected_value as ev

    return ev.monte_carlo(iterations, distributions, base_params)


def _ev_decision_tree(tree):
    from src.valuation import expected_value as ev

    return ev.decision_tree(tree)


_register(
    "calculate_expected_value",
    {
        "discrete": _ev_discrete,
        "scenario": _ev_scenario,
        "provision": _ev_provision,
        "football_field": _ev_football_field,
        "continuous": _ev_continuous,
        "monte_carlo": _ev_monte_carlo,
        "decision_tree": _ev_decision_tree,
    },
)
_register(
    "calculate_actuarial_pv",
    {
        "ifrs17_gmm": lambda cash_flows, discount_rate, risk_adjustment: _actuarial_pv(
            cash_flows, discount_rate, risk_adjustment
        ),
        "ifrs17_paa": _ifrs17_paa,
        "ifrs17_vfa": lambda cash_flows, discount_rate, underlying_items_return, risk_adjustment: (
            _actuarial_pv(cash_flows, discount_rate, risk_adjustment)
        ),
        "ias19_puc": _ias19_puc,
        "ias37_provision": _ias37,
    },
)
_register(
    "calculate_fair_value_adjustment",
    {
        "dlom": _dlom,
        "dloc": lambda base_value, transaction_cost_pct: _pct_adjust(
            base_value, transaction_cost_pct, -1
        ),
        "control_premium": lambda base_value, control_premium_pct: _pct_adjust(
            base_value, control_premium_pct, +1
        ),
        "minority_discount": lambda base_value, minority_discount_pct: _pct_adjust(
            base_value, minority_discount_pct, -1
        ),
        "highest_best_use": _hbu,
        "hierarchy_level": _hierarchy,
    },
)


# ---------------------------------------------------------------------------
# calculate_convertible_bond
# ---------------------------------------------------------------------------


def _convertible(
    spot: float,
    face: float,
    coupon_rate: float,
    maturity: float,
    conversion_ratio: float,
    volatility: float,
    risk_free: float,
    credit_spread: float,
    call_schedule: List[Dict[str, Any]],
    put_schedule: List[Dict[str, Any]],
    rights_priority: str,
    credit_model: str,
) -> Dict[str, Any]:
    from src.derivatives.convertible_lattice import convertible_bond_value

    return convertible_bond_value(
        spot=spot,
        face=face,
        coupon_rate=coupon_rate,
        maturity=maturity,
        conversion_ratio=conversion_ratio,
        volatility=volatility,
        risk_free=risk_free,
        credit_spread=credit_spread,
        call_schedule=call_schedule,
        put_schedule=put_schedule,
        rights_priority=rights_priority,
        credit_model=credit_model,
    )


def _convertible_mc(**kw: Any) -> Dict[str, Any]:
    from src.derivatives.convertible_alt import convertible_lsmc

    return convertible_lsmc(
        spot=kw["spot"],
        face=kw["face"],
        coupon_rate=kw["coupon_rate"],
        maturity=kw["maturity"],
        conversion_ratio=kw["conversion_ratio"],
        volatility=kw["volatility"],
        risk_free=kw["risk_free"],
        credit_spread=kw["credit_spread"],
        call_schedule=list(kw.get("call_schedule") or []),
        put_schedule=list(kw.get("put_schedule") or []),
        rights_priority=kw.get("rights_priority", "holder"),
    )


_register(
    "calculate_convertible_bond",
    {
        "lattice_tsf": lambda **kw: _convertible(**kw, credit_model="tsiveriotis_fernandes"),
        "lattice_intensity": lambda **kw: _convertible(**kw, credit_model="intensity"),
        "lsmc": lambda **kw: _convertible_mc(**kw),
    },
)


def _structured(method: str, **kw):
    from src.derivatives import structured_products as sp

    if method == "cbbc":
        return sp.barrier_mc(
            kw["notional"],
            kw["spot"],
            kw["strike"],
            kw["barrier"],
            kw["barrier_type"],
            kw["maturity"],
            kw["risk_free"],
            kw["volatility"],
            kw["option_type"],
        )
    if method == "derivative_warrant":
        return sp.geometric_asian(
            kw["notional"],
            kw["spot"],
            kw["strike"],
            kw["maturity"],
            kw["risk_free"],
            kw["volatility"],
            kw["option_type"],
            kw["average_type"],
        )
    if method == "inline_warrant":
        return sp.range_digital(
            kw["notional"],
            kw["spot"],
            kw["lower_strike"],
            kw["upper_strike"],
            kw["maturity"],
            kw["risk_free"],
            kw["volatility"],
            kw["payout"],
        )
    if method in ("eli", "eln"):
        return sp.equity_linked_note(
            kw["notional"],
            kw["spot"],
            kw["strike"],
            kw["maturity"],
            kw["risk_free"],
            kw["volatility"],
            kw["coupon_rate"],
        )
    if method == "autocallable":
        return sp.autocallable_mc(
            kw["notional"],
            kw["spot"],
            kw["knock_out_level"],
            kw["observation_dates"],
            kw["coupon_rate_structured"],
            kw["maturity"],
            kw["risk_free"],
            kw["volatility"],
        )
    if method == "credit_linked_note":
        return sp.credit_linked_note(
            kw["notional"],
            kw["credit_spread"],
            kw["recovery"],
            kw["maturity"],
            kw["risk_free"],
            kw["coupon_rate_structured"],
        )
    if method in ("accumulator", "decumulator"):
        dates = [float(d) for d in kw["observation_dates"]]
        maturity = max(dates)
        return sp.accumulator_mc(
            kw["notional"],
            kw["spot"],
            kw["strike"],
            kw["knock_out_level"],
            dates,
            kw["risk_free"],
            kw["volatility"],
            1 if method == "accumulator" else -1,
            maturity,
        )
    if method == "trs":
        return sp.total_return_swap(
            kw["notional"], kw["spot"], kw["maturity"], kw["risk_free"], kw["dividend_yield"]
        )
    if method == "cfd":
        return sp.cfd(kw["notional"], kw["spot"], kw["strike"], kw["maturity"], kw["risk_free"])
    raise KeyError(method)


_register(
    "calculate_structured_product",
    {
        m: (lambda m=m, **kw: _structured(m, **kw))
        for m in (
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
        )
    },
)


def _loss_making(method: str, **kw):
    from src.valuation import loss_making as lm

    if method == "scenario":
        return lm.scenario_weighted(kw["scenarios"], kw["range_method"])
    return getattr(lm, method)(**kw)


_register(
    "calculate_loss_making_company",
    {
        m: (lambda m=m, **kw: _loss_making(m, **kw))
        for m in (
            "margin_ramp_dcf",
            "revenue_multiple",
            "merton_equity",
            "scenario",
            "vc_method",
            "distressed_waterfall",
            "bank_residual_income",
            "spac_deal",
        )
    },
)


def _company_profile(ticker):
    import valuation_engine as ve

    info = ve._get_company_info(ticker) or {}
    metrics = ve._get_market_metrics(ticker) or {}
    profile = {"ticker": ticker, **info, **metrics}
    price = profile.get("price", profile.get("current_price"))
    return {"value": price, "profile": profile}


_register(
    "calculate_company_summary",
    {"profile": _company_profile},
)


def _report_audit(file_path):
    from src.report_review.audit import audit_report

    return audit_report(file_path)


_register(
    "calculate_report_review",
    {"audit": _report_audit},
)


def _fixed_income(method: str, **kw):
    from src.derivatives import fixed_income as fi

    return getattr(fi, method)(**kw)


_register(
    "calculate_fixed_income",
    {
        m: (lambda m=m, **kw: _fixed_income(m, **kw))
        for m in ("bond_price", "bond_yield", "duration", "convexity")
    },
)
