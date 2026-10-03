"""Plain fixed-income analytics: price, yield, duration, convexity."""

from __future__ import annotations

from typing import Any, Dict, List


def _cashflows(face: float, coupon_rate: float, years: float, frequency: int) -> List[float]:
    if frequency <= 0:
        raise ValueError("frequency must be >= 1")
    periods = int(round(years * frequency))
    if periods <= 0:
        raise ValueError("years must be positive")
    coupon = face * coupon_rate / frequency
    flows = [coupon] * periods
    flows[-1] += face
    return flows


def bond_price(
    face: float, coupon_rate: float, years: float, ytm: float, frequency: int
) -> Dict[str, Any]:
    flows = _cashflows(face, coupon_rate, years, frequency)
    r = ytm / frequency
    pv = sum(cf / (1 + r) ** t for t, cf in enumerate(flows, start=1))
    return {"value": pv, "periods": len(flows)}


def bond_yield(
    face: float, coupon_rate: float, years: float, price: float, frequency: int
) -> Dict[str, Any]:
    low, high = -0.99, 5.0
    for _ in range(200):
        mid = (low + high) / 2
        value = bond_price(face, coupon_rate, years, mid, frequency)["value"]
        if value > price:
            low = mid
        else:
            high = mid
    return {"value": (low + high) / 2}


def duration(
    face: float, coupon_rate: float, years: float, ytm: float, frequency: int
) -> Dict[str, Any]:
    flows = _cashflows(face, coupon_rate, years, frequency)
    r = ytm / frequency
    pv = [(cf / (1 + r) ** t, t) for t, cf in enumerate(flows, start=1)]
    price = sum(x for x, _ in pv)
    macaulay_periods = sum(x * t for x, t in pv) / price
    macaulay = macaulay_periods / frequency
    modified = macaulay / (1 + r)
    return {"value": modified, "macaulay_duration": macaulay, "modified_duration": modified}


def convexity(
    face: float, coupon_rate: float, years: float, ytm: float, frequency: int
) -> Dict[str, Any]:
    flows = _cashflows(face, coupon_rate, years, frequency)
    r = ytm / frequency
    price = sum(cf / (1 + r) ** t for t, cf in enumerate(flows, start=1))
    total = sum(t * (t + 1) * cf / (1 + r) ** (t + 2) for t, cf in enumerate(flows, start=1))
    return {"value": total / price / frequency**2}
