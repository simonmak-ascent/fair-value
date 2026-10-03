"""
Option Greeks Calculation Module
"""

import numpy as np
from scipy.stats import norm
from typing import Dict
import logging

logger = logging.getLogger(__name__)


def delta(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str = "call",
) -> float:
    """
    Calculate Delta - sensitivity to underlying price

    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility
        option_type: 'call' or 'put'

    Returns:
        Delta
    """
    if maturity <= 0:
        if option_type.lower() == "call":
            return 1.0 if spot > strike else 0.0
        else:
            return -1.0 if spot < strike else 0.0

    d1 = (np.log(spot / strike) + (risk_free + 0.5 * volatility**2) * maturity) / (
        volatility * np.sqrt(maturity)
    )

    if option_type.lower() == "call":
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1


def gamma(
    spot: float, strike: float, maturity: float, risk_free: float, volatility: float
) -> float:
    """
    Calculate Gamma - second derivative of price to underlying

    Gamma = d²V/dS²

    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility

    Returns:
        Gamma
    """
    if maturity <= 0:
        return 0.0

    d1 = (np.log(spot / strike) + (risk_free + 0.5 * volatility**2) * maturity) / (
        volatility * np.sqrt(maturity)
    )

    return norm.pdf(d1) / (spot * volatility * np.sqrt(maturity))


def theta(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str = "call",
) -> float:
    """
    Calculate Theta - time decay (per day)

    Theta = dV/dt

    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility
        option_type: 'call' or 'put'

    Returns:
        Theta (per day)
    """
    if maturity <= 0:
        return 0.0

    d1 = (np.log(spot / strike) + (risk_free + 0.5 * volatility**2) * maturity) / (
        volatility * np.sqrt(maturity)
    )
    d2 = d1 - volatility * np.sqrt(maturity)

    term1 = -spot * norm.pdf(d1) * volatility / (2 * np.sqrt(maturity))

    if option_type.lower() == "call":
        term2 = -risk_free * strike * np.exp(-risk_free * maturity) * norm.cdf(d2)
    else:
        term2 = risk_free * strike * np.exp(-risk_free * maturity) * norm.cdf(-d2)

    theta = term1 + term2

    return theta / 365  # Convert to per-day


def vega(spot: float, strike: float, maturity: float, risk_free: float, volatility: float) -> float:
    """
    Calculate Vega - sensitivity to volatility

    Vega = dV/dσ

    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility

    Returns:
        Vega (per 1% change in vol)
    """
    if maturity <= 0:
        return 0.0

    d1 = (np.log(spot / strike) + (risk_free + 0.5 * volatility**2) * maturity) / (
        volatility * np.sqrt(maturity)
    )

    vega = spot * norm.pdf(d1) * np.sqrt(maturity)

    return vega / 100  # Per 1% change


def rho(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str = "call",
) -> float:
    """
    Calculate Rho - sensitivity to interest rate

    Rho = dV/dr

    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility
        option_type: 'call' or 'put'

    Returns:
        Rho (per 1% change in rate)
    """
    if maturity <= 0:
        return 0.0

    d1 = (np.log(spot / strike) + (risk_free + 0.5 * volatility**2) * maturity) / (
        volatility * np.sqrt(maturity)
    )
    d2 = d1 - volatility * np.sqrt(maturity)

    if option_type.lower() == "call":
        rho = strike * maturity * np.exp(-risk_free * maturity) * norm.cdf(d2)
    else:
        rho = -strike * maturity * np.exp(-risk_free * maturity) * norm.cdf(-d2)

    return rho / 100  # Per 1% change


def charm(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str = "call",
) -> float:
    """
    Calculate Charm - delta decay over time

    Charm = d²V/dSdt

    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility
        option_type: 'call' or 'put'

    Returns:
        Charm
    """
    if maturity <= 0:
        return 0.0

    d1 = (np.log(spot / strike) + (risk_free + 0.5 * volatility**2) * maturity) / (
        volatility * np.sqrt(maturity)
    )

    charm = -norm.pdf(d1) * (risk_free + 0.5 * volatility**2) / (volatility * np.sqrt(maturity))

    if option_type.lower() == "put":
        charm += 1

    return charm / 365


def speed(
    spot: float, strike: float, maturity: float, risk_free: float, volatility: float
) -> float:
    """
    Calculate Speed - third derivative of price to underlying

    Speed = d³V/dS³

    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility

    Returns:
        Speed
    """
    if maturity <= 0:
        return 0.0

    d1 = (np.log(spot / strike) + (risk_free + 0.5 * volatility**2) * maturity) / (
        volatility * np.sqrt(maturity)
    )

    gamma_val = gamma(spot, strike, maturity, risk_free, volatility)

    return -gamma_val / spot * (1 + d1 / (volatility * np.sqrt(maturity)))


def all_greeks(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str = "call",
) -> Dict:
    """
    Calculate all Greeks

    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility
        option_type: 'call' or 'put'

    Returns:
        Dictionary of all Greeks
    """
    return {
        "delta": delta(spot, strike, maturity, risk_free, volatility, option_type),
        "gamma": gamma(spot, strike, maturity, risk_free, volatility),
        "theta": theta(spot, strike, maturity, risk_free, volatility, option_type),
        "vega": vega(spot, strike, maturity, risk_free, volatility),
        "rho": rho(spot, strike, maturity, risk_free, volatility, option_type),
        "charm": charm(spot, strike, maturity, risk_free, volatility, option_type),
        "speed": speed(spot, strike, maturity, risk_free, volatility),
    }


def portfolio_greeks(positions: list) -> Dict:
    """
    Calculate Greeks for portfolio of options

    Args:
        positions: List of dicts with {spot, strike, maturity, risk_free, volatility, option_type, quantity}

    Returns:
        Portfolio Greeks
    """
    total = {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}

    for pos in positions:
        greeks = all_greeks(
            pos["spot"],
            pos["strike"],
            pos["maturity"],
            pos["risk_free"],
            pos["volatility"],
            pos.get("option_type", "call"),
        )

        quantity = pos.get("quantity", 1)

        for greek in total:
            total[greek] += greeks.get(greek, 0) * quantity

    return total
