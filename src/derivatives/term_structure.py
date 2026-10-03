"""Interest-rate term structure: bootstrap, discounting, forward rates.

Tenor-grid conventions match HIBOR/HKD money-market curves: par rates at an
aligned coupon grid (e.g. quarterly or semi-annual), bootstrapped to zero rates
under annual compounding, with linear interpolation on zero rates for
off-grid cash-flow times.
"""

from __future__ import annotations

from typing import Any, Dict, List


def discount_factor(rate: float, years: float, frequency: int) -> Dict[str, Any]:
    if frequency <= 0:
        raise ValueError("frequency must be >= 1")
    if years < 0:
        raise ValueError("years must be >= 0")
    df = (1 + rate / frequency) ** (-frequency * years)
    return {"value": df}


def zero_curve(par_rates: List[float], tenors: List[float], frequency: int) -> Dict[str, Any]:
    if len(par_rates) != len(tenors) or not tenors:
        raise ValueError("par_rates and tenors must be non-empty and equal length")
    if frequency <= 0:
        raise ValueError("frequency must be >= 1")
    dfs: List[float] = [1.0]
    zeros: List[float] = [0.0]
    for tenor, par in zip(tenors, par_rates):
        c = par / frequency
        prior = sum(dfs[1:])  # coupons at earlier grid dates
        df = (1 - c * prior) / (1 + c)
        if df <= 0:
            raise ValueError("par_rates produce a non-positive discount factor")
        zeros.append(df ** (-1.0 / tenor) - 1.0)
        dfs.append(df)
    return {
        "value": zeros[-1],
        "tenors": list(tenors),
        "zero_rates": zeros[1:],
        "discount_factors": dfs[1:],
        "frequency": frequency,
    }


def _interp_zero(zero_rates: List[float], tenors: List[float], t: float) -> float:
    if t <= 0:
        return zero_rates[0]
    xs = [0.0, *tenors]
    ys = [zero_rates[0], *zero_rates]
    if t <= tenors[0]:
        return ys[0] + (t - xs[0]) * (ys[1] - ys[0]) / (xs[1] - xs[0])
    if t >= tenors[-1]:
        return ys[-1]
    for i in range(1, len(xs)):
        if t <= xs[i]:
            return ys[i - 1] + (t - xs[i - 1]) * (ys[i] - ys[i - 1]) / (xs[i] - xs[i - 1])
    return ys[-1]


def forward_rate(
    zero_rates: List[float], tenors: List[float], t1: float, t2: float
) -> Dict[str, Any]:
    if t2 <= t1:
        raise ValueError("t2 must be greater than t1")
    z1 = _interp_zero(zero_rates, tenors, t1)
    z2 = _interp_zero(zero_rates, tenors, t2)
    growth = (1 + z2) ** t2 / (1 + z1) ** t1
    rate = growth ** (1.0 / (t2 - t1)) - 1.0
    return {"value": rate}


def pv_curve(
    cash_flows: List[float], times: List[float], zero_rates: List[float], tenors: List[float]
) -> Dict[str, Any]:
    if len(cash_flows) != len(times) or not times:
        raise ValueError("cash_flows and times must be non-empty and equal length")
    total = 0.0
    for cf, t in zip(cash_flows, times):
        z = _interp_zero(zero_rates, tenors, t)
        total += cf * (1 + z) ** (-t)
    return {"value": total}
