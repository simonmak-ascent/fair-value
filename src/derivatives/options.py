"""
Options Pricing Module
Black-Scholes-Merton, Binomial Tree, and Monte Carlo methods
"""

import numpy as np
from scipy.stats import norm
import logging

logger = logging.getLogger(__name__)

# Try to import QuantLib
try:
    import QuantLib as ql
    QUANTLIB_AVAILABLE = True
except ImportError:
    QUANTLIB_AVAILABLE = False
    logger.warning("QuantLib not available, using native Python implementations")


def black_scholes_price(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str = "call"
) -> float:
    """
    Black-Scholes-Merton option pricing
    
    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity in years
        risk_free: Risk-free rate
        volatility: Volatility (annualized)
        option_type: 'call' or 'put'
    
    Returns:
        Option price
    """
    if maturity <= 0:
        if option_type.lower() == "call":
            return max(spot - strike, 0)
        else:
            return max(strike - spot, 0)
    
    d1 = (np.log(spot / strike) + 
          (risk_free + 0.5 * volatility ** 2) * maturity) / (volatility * np.sqrt(maturity))
    d2 = d1 - volatility * np.sqrt(maturity)
    
    if option_type.lower() == "call":
        price = (spot * norm.cdf(d1) - 
                strike * np.exp(-risk_free * maturity) * norm.cdf(d2))
    else:  # put
        price = (strike * np.exp(-risk_free * maturity) * norm.cdf(-d2) - 
                spot * norm.cdf(-d1))
    
    return price


def black_scholes_delta(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str = "call"
) -> float:
    """
    Calculate option Delta
    
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
    d1 = (np.log(spot / strike) + 
          (risk_free + 0.5 * volatility ** 2) * maturity) / (volatility * np.sqrt(maturity))
    
    if option_type.lower() == "call":
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1


def black_scholes_gamma(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float
) -> float:
    """
    Calculate option Gamma
    
    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility
    
    Returns:
        Gamma
    """
    d1 = (np.log(spot / strike) + 
          (risk_free + 0.5 * volatility ** 2) * maturity) / (volatility * np.sqrt(maturity))
    
    return norm.pdf(d1) / (spot * volatility * np.sqrt(maturity))


def black_scholes_vega(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float
) -> float:
    """
    Calculate option Vega
    
    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility
    
    Returns:
        Vega
    """
    d1 = (np.log(spot / strike) + 
          (risk_free + 0.5 * volatility ** 2) * maturity) / (volatility * np.sqrt(maturity))
    
    return spot * norm.pdf(d1) * np.sqrt(maturity) / 100


def black_scholes_theta(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str = "call"
) -> float:
    """
    Calculate option Theta
    
    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility
        option_type: 'call' or 'put'
    
    Returns:
        Theta (annualized)
    """
    d1 = (np.log(spot / strike) + 
          (risk_free + 0.5 * volatility ** 2) * maturity) / (volatility * np.sqrt(maturity))
    d2 = d1 - volatility * np.sqrt(maturity)
    
    term1 = -spot * norm.pdf(d1) * volatility / (2 * np.sqrt(maturity))
    
    if option_type.lower() == "call":
        term2 = -risk_free * strike * np.exp(-risk_free * maturity) * norm.cdf(d2)
        theta = term1 + term2
    else:
        term2 = risk_free * strike * np.exp(-risk_free * maturity) * norm.cdf(-d2)
        theta = term1 + term2
    
    return theta / 365


def black_scholes_rho(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str = "call"
) -> float:
    """
    Calculate option Rho
    
    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility
        option_type: 'call' or 'put'
    
    Returns:
        Rho
    """
    d1 = (np.log(spot / strike) + 
          (risk_free + 0.5 * volatility ** 2) * maturity) / (volatility * np.sqrt(maturity))
    d2 = d1 - volatility * np.sqrt(maturity)
    
    if option_type.lower() == "call":
        return strike * maturity * np.exp(-risk_free * maturity) * norm.cdf(d2) / 100
    else:
        return -strike * maturity * np.exp(-risk_free * maturity) * norm.cdf(-d2) / 100


def binomial_tree_price(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    steps: int = 100,
    option_type: str = "call",
    american: bool = False
) -> float:
    """
    Binomial tree option pricing (Cox-Ross-Rubinstein)
    
    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility
        steps: Number of binomial steps
        option_type: 'call' or 'put'
        american: Whether American option
    
    Returns:
        Option price
    """
    dt = maturity / steps
    u = np.exp(volatility * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(risk_free * dt) - d) / (u - d)
    discount = np.exp(-risk_free * dt)
    
    # Initialize asset prices at maturity
    prices = np.zeros(steps + 1)
    for i in range(steps + 1):
        prices[i] = spot * (u ** (steps - i)) * (d ** i)
    
    # Initialize option values at maturity
    values = np.zeros(steps + 1)
    for i in range(steps + 1):
        if option_type.lower() == "call":
            values[i] = max(prices[i] - strike, 0)
        else:
            values[i] = max(strike - prices[i], 0)
    
    # Backward induction
    for j in range(steps - 1, -1, -1):
        for i in range(j + 1):
            # Expected value
            expected = p * values[i] + (1 - p) * values[i + 1]
            values[i] = expected * discount
            
            # Early exercise for American options
            if american:
                spot_at_node = spot * (u ** (j - i)) * (d ** i)
                if option_type.lower() == "call":
                    exercise = max(spot_at_node - strike, 0)
                else:
                    exercise = max(strike - spot_at_node, 0)
                values[i] = max(values[i], exercise)
    
    return values[0]


def monte_carlo_option(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    simulations: int = 100000,
    option_type: str = "call"
) -> float:
    """
    Monte Carlo option pricing
    
    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        volatility: Volatility
        simulations: Number of simulations
        option_type: 'call' or 'put'
    
    Returns:
        Option price
    """
    dt = maturity
    
    # Generate random price paths
    z = np.random.normal(0, 1, simulations)
    final_prices = spot * np.exp((risk_free - 0.5 * volatility**2) * dt + 
                                  volatility * np.sqrt(dt) * z)
    
    # Calculate option values at maturity
    if option_type.lower() == "call":
        payoffs = np.maximum(final_prices - strike, 0)
    else:
        payoffs = np.maximum(strike - final_prices, 0)
    
    # Discount and average
    price = np.exp(-risk_free * maturity) * np.mean(payoffs)
    
    return price


def garman_kohlhagen(
    spot: float,
    strike: float,
    maturity: float,
    domestic_rf: float,
    foreign_rf: float,
    volatility: float,
    option_type: str = "call"
) -> float:
    """
    Garman-Kohlhagen formula for FX options
    
    Args:
        spot: Spot exchange rate (domestic per foreign)
        strike: Strike rate
        maturity: Time to maturity
        domestic_rf: Domestic risk-free rate
        foreign_rf: Foreign risk-free rate
        volatility: FX volatility
        option_type: 'call' or 'put'
    
    Returns:
        FX option price
    """
    # Adjust rates for foreign currency
    r = domestic_rf
    rf = foreign_rf
    
    d1 = (np.log(spot / strike) + 
          (r - rf + 0.5 * volatility ** 2) * maturity) / (volatility * np.sqrt(maturity))
    d2 = d1 - volatility * np.sqrt(maturity)
    
    discount_domestic = np.exp(-r * maturity)
    discount_foreign = np.exp(-rf * maturity)
    
    if option_type.lower() == "call":
        price = (spot * discount_foreign * norm.cdf(d1) - 
                strike * discount_domestic * norm.cdf(d2))
    else:
        price = (strike * discount_domestic * norm.cdf(-d2) - 
                spot * discount_foreign * norm.cdf(-d1))
    
    return price


def implied_volatility(
    market_price: float,
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    option_type: str = "call",
    tolerance: float = 1e-6
) -> float:
    """
    Calculate implied volatility using Newton-Raphson
    
    Args:
        market_price: Observed option price
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity
        risk_free: Risk-free rate
        option_type: 'call' or 'put'
        tolerance: Convergence tolerance
    
    Returns:
        Implied volatility
    """
    sigma = 0.3  # Initial guess
    
    for _ in range(100):
        price = black_scholes_price(spot, strike, maturity, risk_free, sigma, option_type)
        vega = black_scholes_vega(spot, strike, maturity, risk_free, sigma)
        
        if abs(vega) < 1e-10:
            break
        
        diff = market_price - price
        if abs(diff) < tolerance:
            break
        
        sigma = sigma + diff / vega
    
    return max(min(sigma, 3.0), 0.01)


def quantlib_option_price(
    spot: float,
    strike: float,
    maturity: float,
    risk_free: float,
    volatility: float,
    option_type: str = "call"
) -> float:
    """
    Price option using QuantLib
    
    Args:
        spot: Current stock price
        strike: Option strike price
        maturity: Time to maturity in years
        risk_free: Risk-free rate
        volatility: Volatility
        option_type: 'call' or 'put'
    
    Returns:
        Option price (or 0 if QuantLib unavailable)
    """
    if not QUANTLIB_AVAILABLE:
        return black_scholes_price(spot, strike, maturity, risk_free, volatility, option_type)
    
    try:
        # Set up QuantLib instruments
        payoff = ql.PlainVanillaPayoff(
            ql.Option.Call if option_type.lower() == "call" else ql.Option.Put,
            strike
        )
        
        exercise = ql.EuropeanExercise(ql.Date.todaysDate() + int(maturity * 365))
        option = ql.VanillaOption(payoff, exercise)
        
        # Set pricing engine (Black-Scholes)
        spot_ql = ql.SimpleQuote(spot)
        risk_free_ql = ql.SimpleQuote(risk_free)
        vol_ql = ql.SimpleQuote(volatility)
        
        process = ql.BlackScholesProcess(
            ql.QuoteHandle(spot_ql),
            ql.YieldTermStructureHandle(ql.FlatForward(ql.Date.todaysDate(), risk_free_ql, ql.Actual365Fixed())),
            ql.BlackVolTermStructureHandle(ql.BlackConstantVol(ql.Date.todaysDate(), ql.NullCalendar(), vol_ql, ql.Actual365Fixed()))
        )
        
        engine = ql.AnalyticEuropeanEngine(process)
        option.setPricingEngine(engine)
        
        return option.NPV()
    except Exception as e:
        logger.error(f"QuantLib pricing failed: {e}")
        return black_scholes_price(spot, strike, maturity, risk_free, volatility, option_type)
