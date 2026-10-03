"""Loss-making-company valuation and a shared dispersion kernel.

Each model returns a central value plus dispersion (mean, sigma, percentiles,
long-tail) so a single point estimate is never reported alone. ``range_method``
selects which statistic is returned as the headline ``value``; the full
distribution is always included.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from scipy.stats import norm

RANGE_METHODS = ("central", "mean", "median", "downside", "upside")


def _percentile(sorted_values: List[float], weights: Optional[List[float]], p: float) -> float:
    if weights is None:
        idx = min(max(int(round(p * (len(sorted_values) - 1))), 0), len(sorted_values) - 1)
        return sorted_values[idx]
    cum = 0.0
    for value, weight in zip(sorted_values, weights):
        cum += weight
        if cum >= p:
            return value
    return sorted_values[-1]


def dispersion(values: List[float], weights: Optional[List[float]] = None) -> Dict[str, Any]:
    """Summarize a value distribution (weighted mean, sigma, percentiles)."""
    if not values:
        raise ValueError("dispersion requires at least one value")
    if weights is not None:
        if len(weights) != len(values):
            raise ValueError("weights and values must have the same length")
        total = float(sum(weights))
        if total <= 0:
            raise ValueError("weights must sum to a positive number")
        w = [x / total for x in weights]
    else:
        w = [1.0 / len(values)] * len(values)

    mean = float(sum(v * wi for v, wi in zip(values, w)))
    variance = float(sum(wi * (v - mean) ** 2 for v, wi in zip(values, w)))
    order = sorted(range(len(values)), key=lambda i: values[i])
    sorted_values = [values[i] for i in order]
    sorted_w = [w[i] for i in order]
    return {
        "mean": mean,
        "std": math.sqrt(max(variance, 0.0)),
        "percentiles": {
            "p5": _percentile(sorted_values, sorted_w, 0.05),
            "p25": _percentile(sorted_values, sorted_w, 0.25),
            "p50": _percentile(sorted_values, sorted_w, 0.50),
            "p75": _percentile(sorted_values, sorted_w, 0.75),
            "p95": _percentile(sorted_values, sorted_w, 0.95),
        },
        "downside": _percentile(sorted_values, sorted_w, 0.05),
        "upside": _percentile(sorted_values, sorted_w, 0.95),
        "long_tail": sorted_values[0],
    }


def pick(stats: Dict[str, Any], range_method: str) -> float:
    if range_method not in RANGE_METHODS:
        raise ValueError(f"range_method must be one of {RANGE_METHODS}")
    if range_method == "mean":
        return stats["mean"]
    if range_method == "median":
        return stats["percentiles"]["p50"]
    if range_method == "downside":
        return stats["downside"]
    if range_method == "upside":
        return stats["upside"]
    return stats["mean"]


def margin_ramp_dcf(
    revenue: float,
    growth_rate: float,
    start_margin: float,
    target_margin: float,
    ramp_years: int,
    discount_rate: float,
    years: int,
    shares_outstanding: float,
    net_debt: float,
    range_method: str,
) -> Dict[str, Any]:
    def per_share(g: float, m_target: float, rate: float) -> float:
        rev = revenue
        pv = 0.0
        fcff = 0.0
        for t in range(1, int(years) + 1):
            rev *= 1 + g
            frac = min(t / ramp_years, 1.0) if ramp_years > 0 else 1.0
            margin = start_margin + (m_target - start_margin) * frac
            fcff = rev * margin
            pv += fcff / (1 + rate) ** t
        g_term = min(g, 0.5 * rate) if rate > 0 else 0.0
        if rate <= g_term:
            raise ValueError("discount_rate must exceed the terminal growth rate")
        tv = fcff * (1 + g_term) / (rate - g_term)
        ev = pv + tv / (1 + rate) ** years
        return (ev - net_debt) / shares_outstanding

    scenarios = {
        "bear": per_share(growth_rate - 0.02, target_margin * 0.8, discount_rate + 0.02),
        "base": per_share(growth_rate, target_margin, discount_rate),
        "bull": per_share(
            min(growth_rate + 0.02, 0.5), min(target_margin * 1.2, 0.6), discount_rate - 0.02
        ),
        "distressed": per_share(growth_rate - 0.04, start_margin, discount_rate + 0.05),
    }
    vals = list(scenarios.values())
    probs = [0.25, 0.4, 0.25, 0.10]
    stats = dispersion(vals, probs)
    return {"value": pick(stats, range_method), "dispersion": stats, "scenarios": scenarios}


def revenue_multiple(
    revenue: float,
    ev_revenue_multiple: float,
    net_debt: float,
    shares_outstanding: float,
    range_method: str,
) -> Dict[str, Any]:
    def per_share(mult: float) -> float:
        return (revenue * mult - net_debt) / shares_outstanding

    scenarios = {
        "bear": per_share(ev_revenue_multiple * 0.8),
        "base": per_share(ev_revenue_multiple),
        "bull": per_share(ev_revenue_multiple * 1.2),
    }
    stats = dispersion(list(scenarios.values()), [0.3, 0.4, 0.3])
    return {"value": pick(stats, range_method), "dispersion": stats, "scenarios": scenarios}


def merton_equity(
    firm_value: float,
    firm_volatility: float,
    debt: float,
    risk_free: float,
    maturity: float,
    range_method: str,
) -> Dict[str, Any]:
    def equity(vol: float) -> float:
        d1 = (math.log(firm_value / debt) + (risk_free + 0.5 * vol**2) * maturity) / (
            vol * math.sqrt(maturity)
        )
        d2 = d1 - vol * math.sqrt(maturity)
        return firm_value * float(norm.cdf(d1)) - debt * math.exp(-risk_free * maturity) * float(
            norm.cdf(d2)
        )

    scenarios = {
        "bear": equity(firm_volatility * 1.15),
        "base": equity(firm_volatility),
        "bull": equity(firm_volatility * 0.85),
    }
    stats = dispersion(list(scenarios.values()), [0.3, 0.4, 0.3])
    return {"value": pick(stats, range_method), "dispersion": stats, "scenarios": scenarios}


def scenario_weighted(scenarios: List[Dict[str, float]], range_method: str) -> Dict[str, Any]:
    values = [float(s["value"]) for s in scenarios]
    probs = [float(s.get("probability", 1.0)) for s in scenarios]
    stats = dispersion(values, probs)
    return {"value": pick(stats, range_method), "dispersion": stats}


def vc_method(
    terminal_value: float,
    target_return: float,
    investment: float,
    shares_outstanding: float,
    range_method: str,
) -> Dict[str, Any]:
    if target_return <= -1:
        raise ValueError("target_return must exceed -100%")
    post_money = terminal_value / (1 + target_return)
    base = post_money / shares_outstanding
    scenarios = {
        "bear": terminal_value * 0.5 / (1 + target_return) / shares_outstanding,
        "base": base,
        "bull": terminal_value * 1.5 / (1 + target_return) / shares_outstanding,
    }
    stats = dispersion(list(scenarios.values()), [0.3, 0.4, 0.3])
    return {
        "value": pick(stats, range_method),
        "dispersion": stats,
        "scenarios": scenarios,
        "multiple_on_investment": terminal_value / investment,
    }


def distressed_waterfall(
    enterprise_value: float, claims: List[Dict[str, Any]], range_method: str
) -> Dict[str, Any]:
    ordered = sorted(claims, key=lambda c: c["priority"])
    remaining = enterprise_value
    recoveries: List[Dict[str, Any]] = []
    for claim in ordered:
        amount = float(claim["amount"])
        recovery = max(min(remaining, amount), 0.0)
        remaining -= recovery
        recoveries.append(
            {
                "name": claim.get("name", "claim"),
                "amount": amount,
                "recovery": recovery,
                "recovery_rate": recovery / amount if amount else 0.0,
            }
        )
    equity = max(remaining, 0.0)
    return {
        "value": equity,
        "total_recovery": enterprise_value - equity,
        "residual_to_equity": equity,
        "recoveries": recoveries,
        "dispersion": dispersion(
            [
                max(enterprise_value * 0.7 - sum(float(c["amount"]) for c in ordered), 0.0),
                equity,
                max(enterprise_value * 1.3 - sum(float(c["amount"]) for c in ordered), 0.0),
            ]
        ),
    }


def bank_residual_income(
    book_value: float, net_income: float, cost_equity: float, growth_rate: float, range_method: str
) -> Dict[str, Any]:
    if cost_equity <= growth_rate:
        raise ValueError("cost_equity must exceed growth_rate")
    roe = net_income / book_value if book_value else 0.0
    value = book_value + book_value * (roe - cost_equity) / (cost_equity - growth_rate)
    scenarios = {
        "bear": book_value
        + book_value * (roe * 0.8 - cost_equity + 0.01) / (cost_equity + 0.01 - growth_rate),
        "base": value,
        "bull": book_value
        + book_value * (roe * 1.2 - cost_equity - 0.01) / (cost_equity - 0.01 - growth_rate),
    }
    stats = dispersion(list(scenarios.values()), [0.3, 0.4, 0.3])
    return {
        "value": pick(stats, range_method),
        "dispersion": stats,
        "scenarios": scenarios,
        "roe": roe,
        "justified_pb": value / book_value if book_value else 0.0,
    }


def spac_deal(
    trust_cash: float, shares_outstanding: float, redemption_price: float, range_method: str
) -> Dict[str, Any]:
    per_share_trust = trust_cash / shares_outstanding
    stats = dispersion([redemption_price, per_share_trust, per_share_trust * 1.1], [0.4, 0.4, 0.2])
    return {
        "value": min(pick(stats, range_method), per_share_trust),
        "dispersion": stats,
        "per_share_trust": per_share_trust,
        "redemption_floor": redemption_price,
    }
