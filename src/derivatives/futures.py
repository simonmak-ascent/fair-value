"""
Futures and Forwards Pricing Module
"""

import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


def futures_price(spot: float, cost_of_carry: float, time_to_expiry: float) -> float:
    """
    Calculate futures price using cost of carry model

    F = S × e^(c × T)

    Args:
        spot: Spot price
        cost_of_carry: Cost of carry rate
        time_to_expiry: Time to expiry in years

    Returns:
        Futures price
    """
    return spot * np.exp(cost_of_carry * time_to_expiry)


def forward_price(spot: float, risk_free_rate: float, dividend_yield: float, time: float) -> float:
    """
    Calculate forward price for dividend-paying asset

    F = S × e^((r - d) × T)

    Args:
        spot: Current spot price
        risk_free_rate: Risk-free rate
        dividend_yield: Dividend yield
        time: Time to maturity

    Returns:
        Forward price
    """
    return spot * np.exp((risk_free_rate - dividend_yield) * time)


def futures_price_with_convexity(
    spot: float, risk_free_rate: float, convenience_yield: float, storage_cost: float, time: float
) -> float:
    """
    Futures price with convenience yield and storage cost

    F = S × e^((r + u - y) × T)

    Where:
    - r = risk-free rate
    - u = storage cost
    - y = convenience yield

    Args:
        spot: Spot price
        risk_free_rate: Risk-free rate
        convenience_yield: Convenience yield
        storage_cost: Storage cost rate
        time: Time to maturity

    Returns:
        Futures price
    """
    cost_of_carry = risk_free_rate + storage_cost - convenience_yield
    return spot * np.exp(cost_of_carry * time)


def currency_forward(
    spot_rate: float, domestic_rate: float, foreign_rate: float, time: float
) -> float:
    """
    Calculate currency forward rate

    F = S × e^((rd - rf) × T)

    Args:
        spot_rate: Spot exchange rate (domestic per foreign)
        domestic_rate: Domestic risk-free rate
        foreign_rate: Foreign risk-free rate
        time: Time to maturity

    Returns:
        Forward rate
    """
    return spot_rate * np.exp((domestic_rate - foreign_rate) * time)


def futures_value(
    futures_price: float, spot: float, cost_of_carry: float, time_elapsed: float, time_total: float
) -> float:
    """
    Calculate value of a futures contract

    Args:
        futures_price: Current futures price
        spot: Current spot price
        cost_of_carry: Cost of carry
        time_elapsed: Time since initiation
        time_total: Total contract duration

    Returns:
        Futures value
    """
    original_futures_price = spot * np.exp(cost_of_carry * time_total)
    return (futures_price - original_futures_price) * np.exp(-cost_of_carry * time_elapsed)


def implied_rate_from_futures(spot: float, futures_price: float, time: float) -> float:
    """
    Imply cost of carry from futures price

    r = (1/T) × ln(F/S)

    Args:
        spot: Spot price
        futures_price: Futures price
        time: Time to maturity

    Returns:
        Implied rate
    """
    if spot <= 0 or time <= 0:
        return 0.0
    return np.log(futures_price / spot) / time


def basis(futures_price: float, spot: float) -> float:
    """
    Calculate basis

    Basis = Spot - Futures

    Args:
        futures_price: Futures price
        spot: Spot price

    Returns:
        Basis
    """
    return spot - futures_price


def spread(
    futures_near: float, futures_far: float, time_near: float, time_far: float, cost_of_carry: float
) -> float:
    """
    Calculate calendar spread

    Args:
        futures_near: Near-term futures price
        futures_far: Far-term futures price
        time_near: Time to near expiry
        time_far: Time to far expiry
        cost_of_carry: Cost of carry

    Returns:
        Spread value
    """
    # Actual spread
    actual_spread = futures_near - futures_far

    return actual_spread


def contango_backwardation(futures_curve: Dict[float, float]) -> str:
    """
    Determine if market is in contango or backwardation

    Args:
        futures_curve: Dictionary of {time: futures_price}

    Returns:
        'contango', 'backwardation', or 'flat'
    """
    times = sorted(futures_curve.keys())
    if len(times) < 2:
        return "flat"

    prices = [futures_curve[t] for t in times]

    if prices[-1] > prices[0]:
        return "contango"
    elif prices[-1] < prices[0]:
        return "backwardation"
    else:
        return "flat"
