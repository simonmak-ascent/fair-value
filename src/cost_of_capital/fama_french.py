"""
Fama-French 5-Factor Model for cost of equity calculation
"""

import pandas as pd
from typing import Dict
import logging

logger = logging.getLogger(__name__)


def calculate_factor_betas(
    ticker: str, factors: pd.DataFrame, returns: pd.Series
) -> Dict[str, float]:
    """
    Calculate factor betas by regressing stock returns against FF5 factors

    Args:
        ticker: Stock ticker (for logging)
        factors: DataFrame with FF5 factors
        returns: Series with stock returns

    Returns:
        Dictionary with factor loadings
    """
    try:
        # Align dates
        aligned_data = pd.concat([returns, factors], axis=1).dropna()

        if len(aligned_data) < 30:
            logger.warning(f"Insufficient data points for {ticker}")
            return {}

        # Prepare regression data
        y = aligned_data["Returns"] - aligned_data["RF"]  # Excess returns
        X = aligned_data[["Mkt-RF", "SMB", "HML", "RMW", "CMA"]]

        # Add constant for regression
        X = sm.add_constant(X)

        # Run OLS regression
        model = sm.OLS(y, X).fit()

        return {
            "alpha": model.params.get("const", 0),
            "beta_mkt": model.params.get("Mkt-RF", 0),
            "beta_smb": model.params.get("SMB", 0),
            "beta_hml": model.params.get("HML", 0),
            "beta_rmw": model.params.get("RMW", 0),
            "beta_cma": model.params.get("CMA", 0),
            "r_squared": model.rsquared,
            "n_observations": len(aligned_data),
        }
    except Exception as e:
        logger.error(f"Error calculating betas for {ticker}: {e}")
        return {}


def calculate_cost_of_equity_ff5(
    risk_free_rate: float, factors: Dict, market_premium: float = None
) -> float:
    """
    Calculate cost of equity using Fama-French 5-Factor Model

    Formula:
    Re = Rf + β₁(RMRF) + β₂(SMB) + β₃(HML) + β₄(RMW) + β₅(CMA)

    Args:
        risk_free_rate: Risk-free rate (e.g., 0.04 for 4%)
        factors: Dictionary with factor betas
        market_premium: Optional override for market premium

    Returns:
        Cost of equity
    """
    if not factors:
        # Fallback to CAPM if no FF5 factors
        if market_premium:
            return risk_free_rate + market_premium
        return risk_free_rate + 0.055  # Default 5.5% market premium

    # Calculate using FF5
    re = (
        risk_free_rate
        + factors.get("beta_mkt", 1) * (market_premium or 0.055)
        + factors.get("beta_smb", 0) * 0.02  # SMB premium ~2%
        + factors.get("beta_hml", 0) * 0.03  # HML premium ~3%
        + factors.get("beta_rmw", 0) * 0.02  # RMW premium ~2%
        + factors.get("beta_cma", 0) * 0.01  # CMA premium ~1%
    )

    return re


def get_market_premium() -> float:
    """
    Get historical market risk premium

    Returns:
        Market risk premium (equity risk premium)
    """
    # Historical ERP estimates:
    # - Damodaran: ~5.5%
    # - Historical: ~4-6%
    return 0.055


def get_risk_free_rate() -> float:
    """
    Get current risk-free rate (10-year treasury yield proxy)

    Returns:
        Risk-free rate
    """
    # This should ideally be fetched from FRED or similar
    # Using a reasonable estimate
    return 0.04  # 4%


# Import statsmodels for regression
try:
    import statsmodels.api as sm
except ImportError:
    sm = None
    logger.warning("statsmodels not available for regression")
