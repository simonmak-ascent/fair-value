"""Structured-product pricing (HKEX-listed and OTC).

Deterministic codes: Monte-Carlo routines take an explicit ``seed`` so results
reproduce. Barriers, autocallables and accumulators are path-dependent and are
valued by simulation; the remainder have closed forms.
"""

from __future__ import annotations

import math
from typing import Any, Dict

import numpy as np
from scipy.stats import norm

from src.derivatives.options import black_scholes_price

_SEED = 20101
_PATHS = 20000


def _annuity(rate: float, maturity: float) -> float:
    if rate == 0:
        return maturity
    return (1 - math.exp(-rate * maturity)) / rate


def geometric_asian(
    notional: float,
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str,
    average_type: str,
) -> Dict[str, Any]:
    """Kemna-Vorst continuous geometric-average price, scaled to notional/spot units."""
    if maturity <= 0:
        intrinsic = max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)
        return {"value": (notional / spot) * intrinsic}
    if average_type == "arithmetic":
        # Arithmetic Asian has no exact closed form; approximate with the geometric
        # price (a known lower bound that is close at typical vols).
        pass
    sigma_a = volatility / math.sqrt(3.0)
    d1 = (math.log(spot / strike) + 0.5 * sigma_a**2 * maturity) / (sigma_a * math.sqrt(maturity))
    d2 = d1 - sigma_a * math.sqrt(maturity)
    if option_type == "call":
        price = spot * float(norm.cdf(d1)) - strike * math.exp(-risk_free * maturity) * float(
            norm.cdf(d2)
        )
    else:
        price = strike * math.exp(-risk_free * maturity) * float(norm.cdf(-d2)) - spot * float(
            norm.cdf(-d1)
        )
    return {"value": (notional / spot) * price, "model": "geometric_asian"}


def range_digital(
    notional: float,
    spot: float,
    lower_strike: float,
    upper_strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    payout: float,
) -> Dict[str, Any]:
    def prob(bound: float) -> float:
        d = (math.log(spot / bound) + (risk_free - 0.5 * volatility**2) * maturity) / (
            volatility * math.sqrt(maturity)
        )
        return float(norm.cdf(d))

    within = max(prob(lower_strike) - prob(upper_strike), 0.0)
    return {
        "value": notional * payout * math.exp(-risk_free * maturity) * within,
        "probability": within,
    }


def barrier_mc(
    notional: float,
    spot: float,
    strike: float,
    barrier: float,
    barrier_type: str,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str,
    steps: int = 252,
) -> Dict[str, Any]:
    rng = np.random.default_rng(_SEED)
    dt = maturity / steps
    drift = (risk_free - 0.5 * volatility**2) * dt
    diff = volatility * math.sqrt(dt)
    log_paths = np.cumsum(drift + diff * rng.standard_normal((_PATHS, steps)), axis=1)
    prices = spot * np.exp(log_paths)
    down = barrier <= spot
    if barrier_type == "knock_out":
        touched = (prices.min(axis=1) <= barrier) if down else (prices.max(axis=1) >= barrier)
        alive = ~touched
    else:  # knock_in
        touched = (prices.min(axis=1) <= barrier) if down else (prices.max(axis=1) >= barrier)
        alive = touched
    s_t = prices[:, -1]
    payoff = (
        np.maximum(s_t - strike, 0.0) if option_type == "call" else np.maximum(strike - s_t, 0.0)
    )
    payoff = np.where(alive, payoff, 0.0)
    price = math.exp(-risk_free * maturity) * float(payoff.mean())
    return {"value": (notional / spot) * price, "model": "barrier_mc"}


def equity_linked_note(
    notional: float,
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    coupon_rate: float,
    coupon_rate_structured: float = 0.0,
) -> Dict[str, Any]:
    units = notional / strike
    put = black_scholes_price(spot, strike, maturity, risk_free, volatility, "put")
    funding = notional * math.exp(-risk_free * maturity)
    coupons = notional * coupon_rate * _annuity(risk_free, maturity)
    value = funding + coupons - units * put
    return {"value": value, "short_put": units * put}


def autocallable_mc(
    notional: float,
    spot: float,
    knock_out_level: float,
    observation_dates: list,
    coupon_rate_structured: float,
    maturity: float,
    risk_free: float,
    volatility: float,
) -> Dict[str, Any]:
    dates = sorted(float(d) for d in observation_dates if 0 < float(d) <= maturity)
    if not dates:
        dates = [maturity]
    rng = np.random.default_rng(_SEED)
    # Simulate to each observation date on a fine grid, reusing one path set.
    steps = 252
    dt = maturity / steps
    drift = (risk_free - 0.5 * volatility**2) * dt
    diff = volatility * math.sqrt(dt)
    paths = spot * np.exp(np.cumsum(drift + diff * rng.standard_normal((_PATHS, steps)), axis=1))
    time_grid = np.linspace(dt, maturity, steps)
    total = 0.0
    alive = np.ones(_PATHS, dtype=bool)
    for obs in dates:
        idx = int(np.argmin(np.abs(time_grid - obs)))
        s_obs = paths[:, idx]
        called = alive & (s_obs >= knock_out_level)
        coupon = notional * coupon_rate_structured * (1 + obs)
        total += float(np.sum(called * (notional + coupon) * math.exp(-risk_free * obs)))
        alive &= ~called
    s_end = paths[:, -1]
    maturity_payoff = notional * (s_end / spot) + notional * coupon_rate_structured
    total += float(np.sum(alive * maturity_payoff * math.exp(-risk_free * maturity)))
    return {"value": total / _PATHS, "model": "autocallable_mc"}


def accumulator_mc(
    notional: float,
    spot: float,
    strike: float,
    knock_out_level: float,
    observation_dates: list,
    risk_free: float,
    volatility: float,
    direction: int,
    maturity: float,
) -> Dict[str, Any]:
    dates = sorted(float(d) for d in observation_dates if 0 < float(d) <= maturity)
    if not dates:
        dates = [maturity]
    rng = np.random.default_rng(_SEED)
    steps = 252
    dt = maturity / steps
    drift = (risk_free - 0.5 * volatility**2) * dt
    diff = volatility * math.sqrt(dt)
    paths = spot * np.exp(np.cumsum(drift + diff * rng.standard_normal((_PATHS, steps)), axis=1))
    time_grid = np.linspace(dt, maturity, steps)
    units = notional / strike / len(dates)
    total = np.zeros(_PATHS)
    alive = np.ones(_PATHS, dtype=bool)
    for obs in dates:
        idx = int(np.argmin(np.abs(time_grid - obs)))
        s_obs = paths[:, idx]
        knocked = alive & (
            (s_obs >= knock_out_level) if direction > 0 else (s_obs <= knock_out_level)
        )
        active = alive & ~knocked
        total += np.where(active, direction * units * (s_obs - strike), 0.0) * math.exp(
            -risk_free * obs
        )
        alive &= ~knocked
    return {"value": float(total.mean()), "model": "accumulator_mc"}


def credit_linked_note(
    notional: float,
    credit_spread: float,
    recovery: float,
    maturity: float,
    risk_free: float,
    coupon_rate_structured: float,
) -> Dict[str, Any]:
    pd = 1 - math.exp(-credit_spread * maturity)
    funding = notional * math.exp(-risk_free * maturity)
    coupons = notional * coupon_rate_structured * _annuity(risk_free, maturity)
    value = (funding + coupons) * (1 - pd) + recovery * notional * math.exp(
        -risk_free * maturity
    ) * pd
    return {"value": value, "default_probability": pd}


def total_return_swap(
    notional: float, spot: float, maturity: float, risk_free: float, dividend_yield: float
) -> Dict[str, Any]:
    # Receiver's value: PV of equity leg (dividends) minus PV of financing leg.
    value = (
        notional
        / spot
        * (spot * (math.exp(-dividend_yield * maturity) - math.exp(-risk_free * maturity)))
    )
    return {"value": value}


def cfd(
    notional: float, spot: float, strike: float, maturity: float, risk_free: float
) -> Dict[str, Any]:
    units = notional / spot
    return {"value": units * (spot - strike * math.exp(-risk_free * maturity))}


def cbbc_residual(
    notional: float,
    spot: float,
    call_price: float,
    entitlement: float,
    barrier: float,
    barrier_type: str,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str,
) -> Dict[str, Any]:
    """CBBC including the HKEX knock-out residual value.

    Bull (call): payoff = max((S - call)/entitlement, 0); residual on knock-out
    = max((barrier - call)/entitlement, 0). Bear (put) is symmetric.
    """
    if entitlement <= 0:
        raise ValueError("entitlement must be positive")
    rng = np.random.default_rng(_SEED)
    steps = 252
    dt = maturity / steps
    drift = (risk_free - 0.5 * volatility ** 2) * dt
    diff = volatility * math.sqrt(dt)
    paths = spot * np.exp(np.cumsum(drift + diff * rng.standard_normal((_PATHS, steps)), axis=1))
    down = barrier <= spot
    if barrier_type == "knock_out":
        touched = (paths.min(axis=1) <= barrier) if down else (paths.max(axis=1) >= barrier)
    else:
        touched = (paths.min(axis=1) <= barrier) if down else (paths.max(axis=1) >= barrier)
    s_t = paths[:, -1]
    if option_type == "call":
        expiry = np.maximum((s_t - call_price) / entitlement, 0.0)
        residual = max((barrier - call_price) / entitlement, 0.0)
    else:
        expiry = np.maximum((call_price - s_t) / entitlement, 0.0)
        residual = max((call_price - barrier) / entitlement, 0.0)
    payoff = np.where(touched, residual, expiry)
    value = notional * math.exp(-risk_free * maturity) * float(payoff.mean())
    return {"value": value, "model": "cbbc_residual", "knock_out_residual": residual}


def range_digital_average(
    notional: float,
    spot: float,
    lower_strike: float,
    upper_strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    payout: float,
    fixing_days: int,
) -> Dict[str, Any]:
    """Inline range warrant settled on the average of ``fixing_days`` closes."""
    if fixing_days < 1:
        raise ValueError("fixing_days must be >= 1")
    rng = np.random.default_rng(_SEED)
    dt = maturity / fixing_days
    drift = (risk_free - 0.5 * volatility ** 2) * dt
    diff = volatility * math.sqrt(dt)
    paths = spot * np.exp(np.cumsum(drift + diff * rng.standard_normal((_PATHS, fixing_days)), axis=1))
    average = paths.mean(axis=1)
    inside = (average >= lower_strike) & (average <= upper_strike)
    probability = float(inside.mean())
    value = notional * payout * math.exp(-risk_free * maturity) * probability
    return {"value": value, "probability": probability, "model": "inline_average"}
