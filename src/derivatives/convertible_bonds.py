"""
Convertible Bond Valuation Module
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)


def straight_bond_value(
    face: float,
    coupon_rate: float,
    maturity: float,
    yield_to_maturity: float
) -> float:
    """
    Calculate straight bond value (bond floor)
    
    Args:
        face: Face value
        coupon_rate: Annual coupon rate
        maturity: Years to maturity
        yield_to_maturity: YTM
    
    Returns:
        Straight bond value
    """
    if maturity <= 0:
        return face
    
    coupon = face * coupon_rate
    
    # PV of coupons
    pv_coupons = 0.0
    for t in range(1, int(maturity) + 1):
        pv_coupons += coupon / (1 + yield_to_maturity) ** t
    
    # PV of face value
    pv_face = face / (1 + yield_to_maturity) ** maturity
    
    return pv_coupons + pv_face


def conversion_value(
    stock_price: float,
    conversion_ratio: float,
    face_value: float = 100
) -> float:
    """
    Calculate conversion value
    
    Conversion Value = Stock Price × Conversion Ratio
    
    Args:
        stock_price: Current stock price
        conversion_ratio: Number of shares per bond
        face_value: Bond face value
    
    Returns:
        Conversion value
    """
    return stock_price * conversion_ratio


def conversion_premium(
    convertible_price: float,
    conversion_value: float
) -> float:
    """
    Calculate conversion premium
    
    Premium = (Convertible Price - Conversion Value) / Conversion Value
    
    Args:
        convertible_price: Price of convertible bond
        conversion_value: Conversion value
    
    Returns:
        Conversion premium
    """
    if conversion_value <= 0:
        return 0.0
    return (convertible_price - conversion_value) / conversion_value


def conversion_parity_price(
    conversion_ratio: float,
    bond_price: float
) -> float:
    """
    Calculate stock price at which conversion is profitable
    
    Args:
        conversion_ratio: Conversion ratio
        bond_price: Bond price
    
    Returns:
        Parity stock price
    """
    if conversion_ratio <= 0:
        return 0.0
    return bond_price / conversion_ratio


def convertible_bond_price(
    straight_value: float,
    option_value: float,
    discount: float = 0.0
) -> float:
    """
    Calculate convertible bond price
    
    CB = Straight Bond + Call Option - Discount
    
    Args:
        straight_value: Value as straight bond
        option_value: Value of conversion option
        discount: Discount for illiquidity/risks
    
    Returns:
        Convertible bond price
    """
    return straight_value + option_value - discount


def option_adjusted_spread(
    convertible_price: float,
    straight_bond_value: float,
    stock_price: float,
    volatility: float,
    maturity: float,
    risk_free: float
) -> float:
    """
    Calculate option-adjusted spread (OAS)
    
    Args:
        convertible_price: Market price of convertible
        straight_bond_value: Straight bond value
        stock_price: Current stock price
        volatility: Stock volatility
        maturity: Years to maturity
        risk_free: Risk-free rate
    
    Returns:
        OAS in basis points
    """
    from .options import black_scholes_price
    
    # Estimate option component
    # Simplified: use call option on stock
    strike = straight_bond_value  # Approximate
    
    option_value = black_scholes_price(
        stock_price, strike, maturity, risk_free, volatility, "call"
    )
    
    # OAS = difference between market and model
    model_price = straight_bond_value + option_value
    spread = (convertible_price - model_price) * 10000
    
    return max(spread, 0)


def binomial_convertible(
    spot: float,
    strike: float,
    maturity: float,
    coupon: float,
    volatility: float,
    risk_free: float,
    conversion_ratio: float,
    steps: int = 50
) -> float:
    """
    Binomial tree valuation for convertible bond
    
    Args:
        spot: Current stock price
        strike: Conversion price (bond value)
        maturity: Years to maturity
        coupon: Annual coupon
        volatility: Stock volatility
        risk_free: Risk-free rate
        conversion_ratio: Conversion ratio
        steps: Number of binomial steps
    
    Returns:
        Convertible bond value
    """
    dt = maturity / steps
    u = np.exp(volatility * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(risk_free * dt) - d) / (u - d)
    discount = np.exp(-risk_free * dt)
    
    # Initialize stock prices at maturity
    prices = [spot * (u ** (steps - i)) * (d ** i) for i in range(steps + 1)]
    
    # Initialize bond-conversion values at maturity
    values = []
    for price in prices:
        bond_value = straight_bond_value(100, coupon / 100, 0, risk_free)
        conv_value = conversion_value(price, conversion_ratio, 100)
        values.append(max(bond_value, conv_value))
    
    # Backward induction
    for j in range(steps - 1, -1, -1):
        for i in range(j + 1):
            # Expected value
            expected = p * values[i] + (1 - p) * values[i + 1]
            bond_value = expected * discount
            
            # Add coupon
            bond_value += coupon * dt * 100
            
            # Check conversion
            price_at_node = spot * (u ** (j - i)) * (d ** i)
            conv_value = conversion_value(price_at_node, conversion_ratio, 100)
            
            values[i] = max(bond_value, conv_value)
    
    return values[0]


def yield_to_maturity_convertible(
    market_price: float,
    face: float,
    coupon_rate: float,
    maturity: float,
    conversion_ratio: float,
    stock_price: float,
    tolerance: float = 1e-6
) -> float:
    """
    Calculate YTM for convertible bond (iterative)
    
    Args:
        market_price: Market price
        face: Face value
        coupon_rate: Coupon rate
        maturity: Years to maturity
        conversion_ratio: Conversion ratio
        stock_price: Current stock price
    
    Returns:
        Yield to maturity
    """
    ytm = coupon_rate  # Initial guess
    
    for _ in range(100):
        bond_value = straight_bond_value(face, coupon_rate, maturity, ytm)
        
        # Estimate option value (simplified)
        from .options import black_scholes_price
        option_value = black_scholes_price(
            stock_price, face / conversion_ratio, maturity, ytm, 0.3, "call"
        )
        
        model_price = bond_value + option_value
        
        diff = market_price - model_price
        if abs(diff) < tolerance:
            break
        
        ytm = ytm + diff / 1000
    
    return max(ytm, 0.001)
