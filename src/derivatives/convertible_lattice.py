"""Convertible / exchangeable bond lattice (Tsiveriotis-Fernandes).

A Cox-Ross-Rubinstein tree on the share price. Coupons, issuer call, investor put
and conversion are applied on the grid with a two-component rollback: the
share-settled component ``E`` is discounted at the risk-free rate, the
cash-settled component ``B`` at the credit-adjusted rate ``r + s``. The node rule
is ``V = max(X, P, min(H, C))`` (conversion, put, issuer call curbing
continuation). Expected failures raise ``ValueError`` for the caller to surface
as an error envelope.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple


def _step_of(t: float, dt: float, n: int) -> int:
    return max(0, min(n, int(round(t / dt))))


def _schedule_steps(
    schedule: Optional[Sequence[Dict[str, Any]]], dt: float, n: int
) -> Dict[int, float]:
    steps: Dict[int, float] = {}
    for item in schedule or []:
        step = _step_of(float(item["date_years"]), dt, n)
        steps[step] = float(item["price"])
    return steps


def convertible_bond_value(
    spot: float,
    face: float,
    coupon_rate: float,
    maturity: float,
    conversion_ratio: float,
    volatility: float,
    risk_free: float,
    credit_spread: float,
    call_schedule: Optional[Sequence[Dict[str, Any]]] = None,
    put_schedule: Optional[Sequence[Dict[str, Any]]] = None,
    rights_priority: str = "holder",
    steps: int = 200,
    credit_model: str = "tsiveriotis_fernandes",
) -> Dict[str, Any]:
    """Return the convertible bond value and its components."""
    if maturity <= 0:
        raise ValueError("maturity must be positive")
    if spot <= 0 or face <= 0 or conversion_ratio <= 0:
        raise ValueError("spot, face and conversion_ratio must be positive")
    if volatility <= 0:
        raise ValueError("volatility must be positive")
    if rights_priority not in ("holder", "issuer"):
        raise ValueError("rights_priority must be 'holder' or 'issuer'")

    n = max(int(steps), 1)
    dt = maturity / n
    u = math.exp(volatility * math.sqrt(dt))
    d = 1.0 / u
    p = (math.exp(risk_free * dt) - d) / (u - d)
    disc_r = math.exp(-risk_free * dt)
    disc_cash = math.exp(-(risk_free + credit_spread) * dt)

    call_steps = _schedule_steps(call_schedule, dt, n)
    put_steps = _schedule_steps(put_schedule, dt, n)
    coupon_amount = face * coupon_rate
    coupon_years = range(1, int(math.floor(maturity + 1e-9)) + 1)
    coupon_steps = {_step_of(float(k), dt, n): coupon_amount for k in coupon_years}

    def node_spot(step: int, up: int) -> float:
        return spot * (u**up) * (d ** (step - up))

    def exercise(step: int, s: float, e_hold: float, b_hold: float) -> Tuple[float, float, float]:
        h = e_hold + b_hold
        # Issuer call caps the continuation value at the call price (min(H, C)).
        cont, cont_is_cash = h, False
        if step in call_steps and call_steps[step] < cont:
            cont, cont_is_cash = call_steps[step], True
        value, e, b = (cont, 0.0, cont) if cont_is_cash else (h, e_hold, b_hold)
        # Holder conversion.
        x = conversion_ratio * s
        if x > value:
            value, e, b = x, x, 0.0
        # Holder put.
        if step in put_steps and put_steps[step] > value:
            value, e, b = put_steps[step], 0.0, put_steps[step]
        return value, e, b

    # Maturity
    e_vals: List[float] = []
    b_vals: List[float] = []
    for up in range(n + 1):
        s_t = node_spot(n, up)
        redemption = face + (coupon_amount if n in coupon_steps else 0.0)
        conv = conversion_ratio * s_t
        if conv >= redemption:
            e_vals.append(conv)
            b_vals.append(0.0)
        else:
            e_vals.append(0.0)
            b_vals.append(redemption)

    for step in range(n - 1, -1, -1):
        e_prev: List[float] = []
        b_prev: List[float] = []
        for up in range(step + 1):
            # CRR: e_vals[up] is the down child, e_vals[up+1] the up child.
            e_hold = disc_r * (p * e_vals[up + 1] + (1 - p) * e_vals[up])
            b_hold = disc_cash * (p * b_vals[up + 1] + (1 - p) * b_vals[up])
            if step in coupon_steps:  # coupon paid at this node's time
                b_hold += coupon_amount
            _value, e, b = exercise(step, node_spot(step, up), e_hold, b_hold)
            e_prev.append(e)
            b_prev.append(b)
        e_vals, b_vals = e_prev, b_prev

    value = e_vals[0] + b_vals[0]

    # Straight bond floor: coupons + face discounted at r + s.
    bond_floor = sum(
        coupon_amount * math.exp(-(risk_free + credit_spread) * k)
        for k in range(1, int(math.floor(maturity + 1e-9)) + 1)
    ) + face * math.exp(-(risk_free + credit_spread) * maturity)
    conversion_value = conversion_ratio * spot

    return {
        "value": value,
        "bond_floor": bond_floor,
        "conversion_value": conversion_value,
        "option_premium": value - max(bond_floor, conversion_value),
        "credit_model": credit_model,
    }
