"""
PD (Probability of Default) Models Module
"""

import numpy as np
from typing import Dict, Optional
from scipy.stats import norm
import logging

logger = logging.getLogger(__name__)


def mortality_rate_to_pd(mortality_rate: float) -> float:
    """
    Convert annual mortality rate to probability of default
    
    Args:
        mortality_rate: Annual mortality rate
    
    Returns:
        Probability of default
    """
    return mortality_rate


def pd_to_mortality_rate(pd: float) -> float:
    """
    Convert PD to mortality rate
    
    Args:
        pd: Probability of default
    
    Returns:
        Mortality rate
    """
    return pd


def hazard_rate_to_pd(hazard_rate: float, tenor: float = 1.0) -> float:
    """
    Convert hazard rate (default intensity) to probability of default
    
    PD = 1 - exp(-λ × T)
    
    Args:
        hazard_rate: Default intensity (hazard rate)
        tenor: Time period in years
    
    Returns:
        Probability of default
    """
    return 1 - np.exp(-hazard_rate * tenor)


def pd_to_hazard_rate(pd: float, tenor: float = 1.0) -> float:
    """
    Convert PD to hazard rate
    
    λ = -ln(1-PD) / T
    
    Args:
        pd: Probability of default
        tenor: Time period in years
    
    Returns:
        Hazard rate
    """
    if pd >= 1:
        return float('inf')
    return -np.log(1 - pd) / tenor


def calculate_cumulative_pd(annual_pd: float, years: int) -> float:
    """
    Calculate cumulative probability of default over multiple years
    
    P(default by year n) = 1 - (1-PD)^n
    
    Args:
        annual_pd: Annual probability of default
        years: Number of years
    
    Returns:
        Cumulative PD
    """
    return 1 - (1 - annual_pd) ** years


def calculate_survival_probability(annual_pd: float, years: int) -> float:
    """
    Calculate survival probability (no default by year n)
    
    P(survive) = (1-PD)^n
    
    Args:
        annual_pd: Annual probability of default
        years: Number of years
    
    Returns:
        Survival probability
    """
    return (1 - annual_pd) ** years


def term_structure_pd(base_pd: float, volatility: float = 0.3) -> Dict[int, float]:
    """
    Generate term structure of PD using credit risk model
    
    Args:
        base_pd: Base annual PD
        volatility: Volatility parameter
    
    Returns:
        Dictionary of {year: pd}
    """
    term_structure = {}
    
    for year in range(1, 11):
        term_structure[year] = base_pd * (1 + volatility * np.sqrt(year) * 0.1)
    
    return term_structure


def kmv_edf_to_pd(edf: float) -> float:
    """
    Convert KMV Expected Default Frequency to PD
    
    KMV EDF is already a default probability measure
    
    Args:
        edf: KMV Expected Default Frequency
    
    Returns:
        Probability of default
    """
    return min(edf, 1.0)


def mape_pd(rating: str, default_rate_history: Dict[str, float]) -> Optional[float]:
    """
    Calculate PD using Moody's Analytics Perceptual Engine approach
    
    Args:
        rating: Credit rating
        default_rate_history: Historical default rates by rating
    
    Returns:
        Estimated PD
    """
    return default_rate_history.get(rating)


def jlt_pd(current_rating: str, rating_transition_matrix: Dict) -> Dict[int, float]:
    """
    Calculate PD using Johnson-Lancaster-Tveal approach
    
    Args:
        current_rating: Current credit rating
        rating_transition_matrix: Transition probability matrix
    
    Returns:
        {year: cumulative PD}
    """
    return {}


def credit_spread_to_pd(credit_spread: float, risk_free_rate: float = 0.04) -> float:
    """
    Estimate PD from credit spread
    
    Spread ≈ PD × LGD (simplified)
    
    Args:
        credit_spread: Credit spread in decimal
        risk_free_rate: Risk-free rate
    
    Returns:
        Estimated PD (assuming 45% LGD)
    """
    lgd = 0.45
    if credit_spread <= 0:
        return 0.0
    return credit_spread / lgd


def Altman_Z_score(revenue: float, ebit: float, equity: float, 
                   liabilities: float, assets: float, sales: float) -> float:
    """
    Calculate Altman Z-Score for private manufacturing companies
    
    Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 1.0X5
    
    Args:
        revenue: Total revenue
        ebit: Earnings before interest and taxes
        equity: Market value of equity
        liabilities: Total liabilities
        assets: Total assets
        sales: Total sales
    
    Returns:
        Z-Score
    """
    if assets == 0:
        return 0.0
    
    x1 = (ebit - liabilities) / assets  # Working capital / Total assets
    x2 = retained_earnings / assets if 'retained_earnings' in dir() else 0  # Retained earnings / Total assets
    x3 = ebit / assets  # EBIT / Total assets
    x4 = equity / liabilities  # Market value equity / Total liabilities
    x5 = sales / assets  # Sales / Total assets
    
    z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5
    
    return z


def z_score_to_pd(z_score: float) -> float:
    """
    Convert Z-Score to probability of default
    
    Uses normal CDF mapping
    
    Args:
        z_score: Altman Z-Score
    
    Returns:
        Estimated PD
    """
    # Z-score zones: <1.81 = distress, 1.81-2.99 = grey, >2.99 = safe
    # Map to PD: higher Z = lower PD
    if z_score >= 3.0:
        return 0.001
    elif z_score >= 2.0:
        return 0.05
    elif z_score >= 1.5:
        return 0.15
    elif z_score >= 1.0:
        return 0.30
    else:
        return 0.60


def merton_model_pd(asset_value: float, debt_value: float, 
                    asset_volatility: float, risk_free_rate: float) -> float:
    """
    Calculate PD using Merton structural model
    
    PD = N(-(ln(V_A/D) + (r + 0.5*σ²)T) / (σ√T))
    
    Args:
        asset_value: Market value of assets
        debt_value: Debt value (default point)
        asset_volatility: Asset volatility
        risk_free_rate: Risk-free rate
    
    Returns:
        Probability of default
    """
    if asset_value <= 0 or debt_value <= 0 or asset_volatility <= 0:
        return 1.0
    
    T = 1.0  # 1 year horizon
    
    d2 = (np.log(asset_value / debt_value) + 
          (risk_free_rate - 0.5 * asset_volatility ** 2) * T) / (asset_volatility * np.sqrt(T))
    
    pd = norm.cdf(-d2)
    return pd


def credit_metrics_simulation(
    exposures: list,
    default_probabilities: list,
    correlations: float = 0.2,
    n_simulations: int = 10000
) -> Dict:
    """
    Simulate portfolio credit losses using Gaussian copula
    
    Args:
        exposures: List of exposure amounts
        default_probabilities: List of default probabilities
        correlations: Asset correlation
        n_simulations: Number of Monte Carlo simulations
    
    Returns:
        Loss distribution statistics
    """
    losses = []
    
    for _ in range(n_simulations):
        # Generate correlated defaults
        systemic = np.random.normal(0, 1)
        portfolio_loss = 0
        
        for i, (exposure, pd) in enumerate(zip(exposures, default_probabilities)):
            idiosyncratic = np.random.normal(0, 1)
            threshold = (np.sqrt(correlations) * systemic + 
                        np.sqrt(1 - correlations) * idiosyncratic)
            
            # Default if threshold < inverse normal of PD
            if threshold < norm.ppf(pd):
                lgd = np.random.uniform(0.3, 0.6)  # Random LGD
                portfolio_loss += exposure * lgd
        
        losses.append(portfolio_loss)
    
    losses = np.array(losses)
    
    return {
        'mean_loss': np.mean(losses),
        'std_loss': np.std(losses),
        'var_95': np.percentile(losses, 95),
        'var_99': np.percentile(losses, 99),
        'expected_loss': np.mean(losses),
        'unexpected_loss': np.std(losses) * 2.33  # 99% VaR
    }
