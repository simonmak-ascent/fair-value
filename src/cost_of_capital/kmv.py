"""
KMV Model for credit risk and cost of debt calculation
Based on Merton structural model
"""

import numpy as np
from scipy.stats import norm
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def estimate_asset_value(equity_value: float, debt_value: float, 
                        risk_free: float, time_to_debt: float) -> float:
    """
    Estimate market value of assets using Merton model
    Solves for V_A where:
    E = V_A * N(d1) - D * e^(-rT) * N(d2)
    
    Args:
        equity_value: Market value of equity
        debt_value: Book value of debt (default point)
        risk_free: Risk-free rate
        time_to_debt: Time to debt maturity
    
    Returns:
        Estimated asset value
    """
    from scipy.optimize import brentq
    
    if equity_value <= 0 or debt_value <= 0:
        return 0.0
    
    def equity_equation(asset_value):
        d1 = (np.log(asset_value / debt_value) + 
              (risk_free + 0.5 * 0.3**2) * time_to_debt) / (0.3 * np.sqrt(time_to_debt))
        d2 = d1 - 0.3 * np.sqrt(time_to_debt)
        
        computed_equity = (asset_value * norm.cdf(d1) - 
                          debt_value * np.exp(-risk_free * time_to_debt) * norm.cdf(d2))
        return computed_equity - equity_value
    
    try:
        # Search for solution
        asset_value = brentq(equity_equation, equity_value, equity_value + debt_value * 2)
        return asset_value
    except:
        # Fallback: approximate as equity + debt
        return equity_value + debt_value * 0.5


def estimate_asset_volatility(equity_vol: float, equity_value: float,
                             asset_value: float, debt_value: float) -> float:
    """
    Estimate asset volatility from equity volatility
    σ_E = (V_A / E) * σ_A * N(d1)
    
    Args:
        equity_vol: Volatility of equity
        equity_value: Market value of equity
        asset_value: Estimated asset value
        debt_value: Debt value
    
    Returns:
        Asset volatility
    """
    if asset_value <= 0 or equity_value <= 0:
        return 0.0
    
    # Approximation: σ_A ≈ σ_E * (E / V_A)
    # More precise solution requires iteration
    d1 = np.log(asset_value / debt_value) / equity_vol + 0.5 * equity_vol
    
    # Iterative solution
    asset_vol = equity_vol * equity_value / asset_value / norm.cdf(d1)
    
    return min(asset_vol, 1.0)  # Cap at 100%


def distance_to_default(asset_value: float, debt_default_point: float,
                       asset_volatility: float) -> float:
    """
    Calculate Distance to Default
    
    DD = (V_A - D) / (V_A * σ_A)
    
    Args:
        asset_value: Market value of assets
        debt_default_point: Default point (typically short-term debt)
        asset_volatility: Volatility of assets
    
    Returns:
        Distance to default
    """
    if asset_value <= 0 or asset_volatility <= 0:
        return 0.0
    
    dd = (asset_value - debt_default_point) / (asset_value * asset_volatility)
    return dd


def expected_default_frequency(distance_to_default: float) -> float:
    """
    Convert Distance to Default to Expected Default Frequency (EDF)
    EDF = N(-DD)
    
    Args:
        distance_to_default: Distance to default
    
    Returns:
        Expected default frequency (probability of default)
    """
    edf = norm.cdf(-distance_to_default)
    return edf


def cost_of_debt_from_kmv(edf: float, risk_free_rate: float,
                         market_spread: float = 0.03) -> float:
    """
    Derive cost of debt from KMV EDF
    
    Rd = Rf + EDF * Spread
    
    Args:
        edf: Expected default frequency
        risk_free_rate: Risk-free rate
        market_spread: Default spread (e.g., 3% for B-rated)
    
    Returns:
        Cost of debt (after-tax)
    """
    # Simple approximation
    # More sophisticated: use EDF to lookup credit spread
    spread = min(edf * 10, 0.30)  # Cap spread at 30%
    
    return risk_free_rate + spread


def kmv_credit_analysis(ticker: str, equity_value: float, 
                       debt_value: float, equity_volatility: float,
                       risk_free_rate: float = 0.04,
                       time_to_debt: float = 1.0) -> Dict:
    """
    Complete KMV credit analysis
    
    Args:
        ticker: Stock ticker (for reference)
        equity_value: Market value of equity
        debt_value: Total debt (book value)
        equity_volatility: Historical volatility of equity
        risk_free_rate: Risk-free rate
        time_to_debt: Average time to debt maturity
    
    Returns:
        Complete KMV analysis results
    """
    # Default point: typically short-term debt + 0.5 * long-term debt
    # Simplified: use 50% of total debt
    default_point = debt_value * 0.5
    
    # Step 1: Estimate asset value
    asset_value = estimate_asset_value(equity_value, debt_value, 
                                       risk_free_rate, time_to_debt)
    
    # Step 2: Estimate asset volatility
    asset_vol = estimate_asset_volatility(equity_volatility, equity_value,
                                          asset_value, debt_value)
    
    # Step 3: Calculate distance to default
    dd = distance_to_default(asset_value, default_point, asset_vol)
    
    # Step 4: Calculate EDF
    edf = expected_default_frequency(dd)
    
    # Step 5: Derive cost of debt
    cost_of_debt = cost_of_debt_from_kmv(edf, risk_free_rate)
    
    return {
        'ticker': ticker,
        'equity_value': equity_value,
        'debt_value': debt_value,
        'default_point': default_point,
        'asset_value': asset_value,
        'equity_volatility': equity_volatility,
        'asset_volatility': asset_vol,
        'distance_to_default': dd,
        'expected_default_frequency': edf,
        'cost_of_debt': cost_of_debt,
        'credit_rating_estimate': _edf_to_rating(edf)
    }


def _edf_to_rating(edf: float) -> str:
    """
    Map EDF to approximate credit rating
    
    Args:
        edf: Expected default frequency
    
    Returns:
        Estimated credit rating
    """
    if edf < 0.002:
        return "AAA"
    elif edf < 0.005:
        return "AA"
    elif edf < 0.01:
        return "A"
    elif edf < 0.03:
        return "BBB"
    elif edf < 0.08:
        return "BB"
    elif edf < 0.15:
        return "B"
    else:
        return "CCC or below"


def calculate_after_tax_cost_of_debt(cost_of_debt: float, tax_rate: float = 0.25) -> float:
    """
    Calculate after-tax cost of debt
    
    Args:
        cost_of_debt: Pre-tax cost of debt
        tax_rate: Corporate tax rate
    
    Returns:
        After-tax cost of debt
    """
    return cost_of_debt * (1 - tax_rate)
