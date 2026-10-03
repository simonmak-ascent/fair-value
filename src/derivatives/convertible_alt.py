"""Longstaff-Schwartz Monte-Carlo valuation for convertibles.

Single-factor American Monte-Carlo: equity-like continuation is discounted at
the risk-free rate and the bond floor at ``risk_free + credit_spread`` (a
Tsiveriotis-Fernandes-style split), with conversion, issuer call and holder put.
Deterministic given ``seed``. Complements the lattice engine.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

import numpy as np


def _coupon_amounts(
    face: float, coupon_rate: float, maturity: float, dt: float, steps: int
) -> Dict[int, float]:
    amount = face * coupon_rate
    years = [y for y in range(1, int(math.floor(maturity + 1e-9)) + 1) if y <= maturity + 1e-9]
    return {min(int(round(y / dt)), steps - 1): amount for y in years}


def convertible_lsmc(
    spot: float,
    face: float,
    coupon_rate: float,
    maturity: float,
    conversion_ratio: float,
    volatility: float,
    risk_free: float,
    credit_spread: float,
    call_schedule: List[Dict[str, float]],
    put_schedule: List[Dict[str, float]],
    rights_priority: str = "debt",
    steps: int = 100,
    paths: int = 40000,
    seed: int = 20260101,
) -> Dict[str, Any]:
    dt = maturity / steps
    rng = np.random.default_rng(seed)
    drift = (risk_free - 0.5 * volatility**2) * dt
    diff = volatility * math.sqrt(dt)
    prices = spot * np.exp(np.cumsum(drift + diff * rng.standard_normal((paths, steps)), axis=1))

    coupons = _coupon_amounts(face, coupon_rate, maturity, dt, steps)
    call_by_step = {
        min(int(round(float(c["date_years"]) / dt)), steps - 1): float(c["price"])
        for c in call_schedule
    }
    put_by_step = {
        min(int(round(float(p["date_years"]) / dt)), steps - 1): float(p["price"])
        for p in put_schedule
    }

    disc = math.exp(-risk_free * dt)
    coupon_floor_disc = math.exp(-(risk_free + credit_spread) * dt)

    last_coupon = coupons.get(steps - 1, 0.0)
    s_end = prices[:, -1]
    conversion = conversion_ratio * s_end
    bond = face + last_coupon
    cash = np.maximum(conversion, bond)

    for step in range(steps - 2, -1, -1):
        cash *= disc
        if step in coupons:
            cash += coupons[step]
        s_i = prices[:, step]
        conv = conversion_ratio * s_i
        design = np.vstack([np.ones_like(s_i), s_i, s_i * s_i]).T
        coeff, *_ = np.linalg.lstsq(design, cash, rcond=None)
        continuation = design @ coeff
        cash = np.where(conv > continuation, conv, cash)
        if step in call_by_step:
            cash = np.minimum(cash, np.maximum(conv, call_by_step[step]))
        if step in put_by_step:
            cash = np.maximum(cash, put_by_step[step])

    value = float(cash.mean()) * disc

    # Straight bond floor, discounted at r + spread.
    floor = 0.0
    for step, amount in coupons.items():
        floor += amount * coupon_floor_disc ** (step + 1)
    floor += face * coupon_floor_disc**steps
    return {"value": value, "bond_floor": floor, "model": "longstaff_schwartz"}
