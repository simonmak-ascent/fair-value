"""
Fama-French 5-Factor Model for cost of equity calculation
"""

import pandas as pd
from typing import Dict
import logging

logger = logging.getLogger(__name__)

# Try to import pandas_datareader, fallback to manual download
try:
    import pandas_datareader as pdr
    from pandas_datareader.famafrench import get_available_datasets  # noqa: F401

    PANDAS_DATAREADER_AVAILABLE = True
except ImportError:
    PANDAS_DATAREADER_AVAILABLE = False
    logger.warning("pandas_datareader not available, using manual FF5 download")


def fetch_ff_factors(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch Fama-French 5 factors from Kenneth French data library

    Args:
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format

    Returns:
        DataFrame with FF5 factors
    """
    if not PANDAS_DATAREADER_AVAILABLE:
        logger.warning("pandas_datareader not available")
        return pd.DataFrame()

    try:
        # FF5 factors dataset (Fama-French 5 Factors (2x3))
        ff5 = pdr.get_data_famafrench(
            "F-F_Research_Data_5_Factors_2x3", start=start_date[:4], end=end_date[:4]
        )

        # Main factors are in the first table
        factors = ff5[0]

        # Rename columns for clarity
        factors.columns = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"]

        return factors
    except Exception as e:
        logger.error(f"Error fetching FF5 factors: {e}")
        return pd.DataFrame()


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


def full_ff5_analysis(
    ticker: str, risk_free_rate: float = None, market_premium: float = None
) -> Dict:
    """
    Complete FF5 cost of equity analysis

    Args:
        ticker: Stock ticker
        risk_free_rate: Risk-free rate (default: 4%)
        market_premium: Market risk premium (default: 5.5%)

    Returns:
        Complete analysis results
    """
    from .fetch_data import get_historical_prices

    # Defaults
    if risk_free_rate is None:
        risk_free_rate = get_risk_free_rate()
    if market_premium is None:
        market_premium = get_market_premium()

    # Fetch FF5 factors
    import datetime

    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=365 * 3)  # 3 years

    factors = fetch_ff_factors(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    if factors.empty:
        return {
            "error": "Could not fetch FF5 factors",
            "fallback_cost_of_equity": risk_free_rate + market_premium,
        }

    # Get stock returns
    prices = get_historical_prices(ticker, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    if prices.empty:
        return {
            "error": "Could not fetch price data",
            "fallback_cost_of_equity": risk_free_rate + market_premium,
        }

    # Calculate returns
    returns = prices["Close"].pct_change().dropna()

    # Align with factors
    common_dates = returns.index.intersection(factors.index)
    returns = returns.loc[common_dates]

    # Calculate betas
    betas = calculate_factor_betas(ticker, factors, returns)

    if not betas:
        return {
            "error": "Could not calculate factor betas",
            "fallback_cost_of_equity": risk_free_rate + market_premium,
        }

    # Calculate cost of equity
    cost_of_equity = calculate_cost_of_equity_ff5(risk_free_rate, betas, market_premium)

    return {
        "ticker": ticker,
        "risk_free_rate": risk_free_rate,
        "market_premium": market_premium,
        "factor_betas": betas,
        "cost_of_equity": cost_of_equity,
        "r_squared": betas.get("r_squared", 0),
        "n_observations": betas.get("n_observations", 0),
    }


# Import statsmodels for regression
try:
    import statsmodels.api as sm
except ImportError:
    sm = None
    logger.warning("statsmodels not available for regression")
