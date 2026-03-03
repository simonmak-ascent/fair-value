"""
Data fetching module using yfinance
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_ticker(ticker: str) -> yf.Ticker:
    """Get yfinance ticker object"""
    return yf.Ticker(ticker)


def get_stock_price(ticker: str, date: Optional[str] = None) -> float:
    """
    Get current or historical stock price
    
    Args:
        ticker: Stock ticker (e.g., '9988.HK', 'AAPL')
        date: Optional date in 'YYYY-MM-DD' format
    
    Returns:
        Stock price as float
    """
    try:
        stock = yf.Ticker(ticker)
        if date:
            hist = stock.history(start=date, end=date)
            if len(hist) > 0:
                return float(hist['Close'].iloc[0])
            return 0.0
        else:
            info = stock.info
            return float(info.get('currentPrice', info.get('previousClose', 0)))
    except Exception as e:
        logger.error(f"Error fetching price for {ticker}: {e}")
        return 0.0


def get_company_info(ticker: str) -> Dict:
    """
    Get company information
    
    Args:
        ticker: Stock ticker
    
    Returns:
        Dictionary with company info
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'name': info.get('longName', info.get('shortName', '')),
            'sector': info.get('sector', ''),
            'industry': info.get('industry', ''),
            'market_cap': info.get('marketCap', 0),
            'shares_outstanding': info.get('sharesOutstanding', 0),
            'beta': info.get('beta', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0),
            '52w_high': info.get('fiftyTwoWeekHigh', 0),
            '52w_low': info.get('fiftyTwoWeekLow', 0)
        }
    except Exception as e:
        logger.error(f"Error fetching info for {ticker}: {e}")
        return {}


def get_income_statement(ticker: str, period: str = "annual") -> pd.DataFrame:
    """
    Get income statement
    
    Args:
        ticker: Stock ticker
        period: 'annual' or 'quarterly'
    
    Returns:
        DataFrame with income statement
    """
    try:
        stock = yf.Ticker(ticker)
        if period == "annual":
            return stock.financials
        else:
            return stock.quarterly_financials
    except Exception as e:
        logger.error(f"Error fetching income statement for {ticker}: {e}")
        return pd.DataFrame()


def get_balance_sheet(ticker: str, period: str = "annual") -> pd.DataFrame:
    """
    Get balance sheet
    
    Args:
        ticker: Stock ticker
        period: 'annual' or 'quarterly'
    
    Returns:
        DataFrame with balance sheet
    """
    try:
        stock = yf.Ticker(ticker)
        if period == "annual":
            return stock.balance_sheet
        else:
            return stock.quarterly_balance_sheet
    except Exception as e:
        logger.error(f"Error fetching balance sheet for {ticker}: {e}")
        return pd.DataFrame()


def get_cash_flow(ticker: str, period: str = "annual") -> pd.DataFrame:
    """
    Get cash flow statement
    
    Args:
        ticker: Stock ticker
        period: 'annual' or 'quarterly'
    
    Returns:
        DataFrame with cash flow
    """
    try:
        stock = yf.Ticker(ticker)
        if period == "annual":
            return stock.cashflow
        else:
            return stock.quarterly_cashflow
    except Exception as e:
        logger.error(f"Error fetching cash flow for {ticker}: {e}")
        return pd.DataFrame()


def get_key_metrics(ticker: str) -> Dict:
    """
    Get key financial metrics
    
    Args:
        ticker: Stock ticker
    
    Returns:
        Dictionary with key metrics
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'market_cap': info.get('marketCap', 0),
            'enterprise_value': info.get('enterpriseValue', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'forward_pe': info.get('forwardPE', 0),
            'peg_ratio': info.get('pegRatio', 0),
            'pb_ratio': info.get('priceToBook', 0),
            'ps_ratio': info.get('priceToSalesTrailing12Months', 0),
            'ev_ebitda': info.get('enterpriseToRevenue', 0) / max(info.get('ebitdaMargin', 0.01), 0.01),
            'ev_sales': info.get('enterpriseToRevenue', 0),
            'revenue': info.get('totalRevenue', 0),
            'revenue_growth': info.get('revenueGrowth', 0),
            'ebitda': info.get('ebitda', 0),
            'ebitda_margin': info.get('ebitdaMargin', 0),
            'profit_margin': info.get('profitMargins', 0),
            'roe': info.get('returnOnEquity', 0),
            'roa': info.get('returnOnAssets', 0),
            'debt_equity': info.get('debtToEquity', 0),
            'current_ratio': info.get('currentRatio', 0),
            'quick_ratio': info.get('quickRatio', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'payout_ratio': info.get('payoutRatio', 0)
        }
    except Exception as e:
        logger.error(f"Error fetching metrics for {ticker}: {e}")
        return {}


def get_historical_prices(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Get historical price data
    
    Args:
        ticker: Stock ticker
        start: Start date 'YYYY-MM-DD'
        end: End date 'YYYY-MM-DD'
    
    Returns:
        DataFrame with OHLCV data
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start, end=end)
        return hist
    except Exception as e:
        logger.error(f"Error fetching history for {ticker}: {e}")
        return pd.DataFrame()


def get_option_chain(ticker: str) -> Dict:
    """
    Get option chain data
    
    Args:
        ticker: Stock ticker
    
    Returns:
        Dictionary with calls and puts
    """
    try:
        stock = yf.Ticker(ticker)
        return {
            'calls': stock.option_chain().calls if hasattr(stock, 'option_chain') else pd.DataFrame(),
            'puts': stock.option_chain().puts if hasattr(stock, 'option_chain') else pd.DataFrame()
        }
    except Exception as e:
        logger.error(f"Error fetching options for {ticker}: {e}")
        return {'calls': pd.DataFrame(), 'puts': pd.DataFrame()}


def get_financial_ratios(ticker: str) -> Dict:
    """
    Calculate financial ratios from raw data
    
    Args:
        ticker: Stock ticker
    
    Returns:
        Dictionary with financial ratios
    """
    try:
        balance = get_balance_sheet(ticker)
        income = get_income_statement(ticker)
        
        if balance.empty or income.empty:
            return {}
        
        # Get latest values
        total_assets = balance.loc['Total Assets'].iloc[0] if 'Total Assets' in balance.index else 0
        total_equity = balance.loc['Total Stockholder Equity'].iloc[0] if 'Total Stockholder Equity' in balance.index else 0
        total_debt = balance.loc['Total Debt'].iloc[0] if 'Total Debt' in balance.index else 0
        revenue = income.loc['Total Revenue'].iloc[0] if 'Total Revenue' in income.index else 0
        net_income = income.loc['Net Income'].iloc[0] if 'Net Income' in income.index else 0
        
        return {
            'roe': net_income / total_equity if total_equity else 0,
            'roa': net_income / total_assets if total_assets else 0,
            'debt_ratio': total_debt / total_assets if total_assets else 0,
            'debt_equity': total_debt / total_equity if total_equity else 0,
            'net_margin': net_income / revenue if revenue else 0
        }
    except Exception as e:
        logger.error(f"Error calculating ratios for {ticker}: {e}")
        return {}


def get_volatility(ticker: str, period: int = 252) -> float:
    """
    Calculate historical volatility
    
    Args:
        ticker: Stock ticker
        period: Number of trading days
    
    Returns:
        Annualized volatility
    """
    try:
        hist = get_historical_prices(ticker, 
            (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d'))
        
        if hist.empty:
            return 0.0
        
        returns = hist['Close'].pct_change().dropna()
        return returns.std() * np.sqrt(period)
    except Exception as e:
        logger.error(f"Error calculating volatility for {ticker}: {e}")
        return 0.0
