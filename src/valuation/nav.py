"""
Net Asset Value (NAV) Valuation Module
For investment holding companies and asset-rich businesses
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


def value_listed_securities(
    holdings: Dict[str, float],
    valuation_date: str = None
) -> float:
    """
    Value listed securities at fair value (market price)
    
    Args:
        holdings: Dictionary of {ticker: shares}
        valuation_date: Optional date for pricing
    
    Returns:
        Total market value
    """
    from ..fetch_data import get_stock_price
    
    total_value = 0.0
    
    for ticker, shares in holdings.items():
        price = get_stock_price(ticker, valuation_date)
        total_value += price * shares
    
    return total_value


def value_unlisted_assets(
    assets: List[Dict],
    valuation_method: str = "dcf"
) -> float:
    """
    Value unlisted assets using appropriate method
    
    Args:
        assets: List of asset dictionaries with details
        valuation_method: 'dcf', 'appraisal', 'book_value'
    
    Returns:
        Total value of unlisted assets
    """
    total_value = 0.0
    
    for asset in assets:
        if valuation_method == "book_value":
            value = asset.get('book_value', 0)
        elif valuation_method == "appraisal":
            value = asset.get('appraised_value', asset.get('book_value', 0))
        else:  # dcf
            # Simplified DCF for individual assets
            cash_flow = asset.get('annual_cash_flow', 0)
            discount_rate = asset.get('discount_rate', 0.10)
            growth = asset.get('growth_rate', 0.02)
            years = asset.get('projection_years', 5)
            
            # Simplified terminal value
            terminal_value = cash_flow * (1 + growth) / (discount_rate - growth)
            
            # PV of cash flows
            pv = 0
            for i in range(years):
                pv += cash_flow * (1 + growth) ** i / (1 + discount_rate) ** (i + 1)
            
            # PV of terminal value
            pv += terminal_value / (1 + discount_rate) ** years
            value = pv
        
        total_value += value
    
    return total_value


def calculate_receivables_ecl(
    accounts_receivable: float,
    aging: Dict[str, float],
    pd_by_age: Dict[str, float],
    lgd: float = 0.45
) -> float:
    """
    Calculate Expected Credit Loss for receivables per HKFRS 9
    
    ECL = EAD × PD × LGD
    
    Args:
        accounts_receivable: Total accounts receivable
        aging: Aging buckets {'current': amt, '30d': amt, '60d': amt, '90d+': amt}
        pd_by_age: PD by aging bucket
        lgd: Loss given default
    
    Returns:
        Expected credit loss
    """
    ecl = 0.0
    
    for age_bucket, amount in aging.items():
        pd = pd_by_age.get(age_bucket, 0.01)
        ead = amount
        ecl += ead * pd * lgd
    
    return ecl


def calculate_nav(
    listed_securities: Dict[str, float],
    unlisted_assets: List[Dict],
    receivables: float,
    aging: Dict[str, float],
    pd_by_age: Dict[str, float],
    total_liabilities: float,
    minority_interest: float = 0,
    minority_discount: float = 0.0,
    tax_rate: float = 0.25
) -> Dict:
    """
    Calculate Net Asset Value
    
    NAV = (Total Assets - Total Liabilities - Minority Interest) × (1 - Discount)
    
    Args:
        listed_securities: {ticker: shares}
        unlisted_assets: List of asset dictionaries
        receivables: Total receivables
        aging: Receivables aging buckets
        pd_by_age: PD by aging bucket
        total_liabilities: Total liabilities
        minority_interest: Minority interest
        minority_discount: Discount for minority interest
        tax_rate: Tax rate for deferred tax liabilities
    
    Returns:
        NAV calculation results
    """
    # Value listed securities
    listed_value = value_listed_securities(listed_securities)
    
    # Value unlisted assets
    unlisted_value = value_unlisted_assets(unlisted_assets)
    
    # Calculate ECL for receivables
    ecl = calculate_receivables_ecl(receivables, aging, pd_by_age)
    
    # Net receivables after ECL
    net_receivables = receivables - ecl
    
    # Total assets
    total_assets = listed_value + unlisted_value + net_receivables
    
    # Apply minority discount
    adjusted_assets = total_assets - minority_interest * minority_discount
    
    # Net assets (after liabilities)
    net_assets = adjusted_assets - total_liabilities
    
    return {
        'method': 'NAV',
        'listed_securities_value': listed_value,
        'unlisted_assets_value': unlisted_value,
        'receivables_gross': receivables,
        'ecl': ecl,
        'receivables_net': net_receivables,
        'total_assets': total_assets,
        'minority_interest': minority_interest,
        'minority_discount': minority_discount,
        'total_liabilities': total_liabilities,
        'net_assets': net_assets,
        'tax_rate': tax_rate
    }


def calculate_nav_per_share(
    nav_result: Dict,
    shares_outstanding: float
) -> Dict:
    """
    Calculate NAV per share
    
    Args:
        nav_result: Result from calculate_nav
        shares_outstanding: Number of shares
    
    Returns:
        NAV per share analysis
    """
    net_assets = nav_result.get('net_assets', 0)
    nav_per_share = net_assets / shares_outstanding if shares_outstanding > 0 else 0
    
    return {
        'net_assets': net_assets,
        'shares_outstanding': shares_outstanding,
        'nav_per_share': nav_per_share
    }


def nav_from_holdings(
    ticker: str,
    holdings: List[Dict],
    liabilities: float,
    shares_outstanding: float
) -> Dict:
    """
    Calculate NAV from holdings data
    
    Args:
        ticker: Holding company ticker
        holdings: List of holdings [{ticker, shares, type}]
        liabilities: Total liabilities
        shares_outstanding: Shares outstanding
    
    Returns:
        NAV results
    """
    
    listed = {}
    unlisted = []
    
    for holding in holdings:
        ticker_sym = holding.get('ticker', '')
        shares = holding.get('shares', 0)
        asset_type = holding.get('type', 'listed')
        
        if asset_type == 'listed':
            listed[ticker_sym] = shares
        else:
            unlisted.append(holding)
    
    # Default aging and PD
    aging = {'current': 0.7, '30d': 0.2, '60d': 0.07, '90d+': 0.03}
    pd_by_age = {'current': 0.005, '30d': 0.02, '60d': 0.05, '90d+': 0.15}
    
    # Assume no receivables for simplicity
    receivables = 0
    
    nav = calculate_nav(
        listed_securities=listed,
        unlisted_assets=unlisted,
        receivables=receivables,
        aging=aging,
        pd_by_age=pd_by_age,
        total_liabilities=liabilities,
        minority_interest=0,
        minority_discount=0.0
    )
    
    # Add per share calculation
    per_share = calculate_nav_per_share(nav, shares_outstanding)
    nav.update(per_share)
    nav['ticker'] = ticker
    
    return nav
