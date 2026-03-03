"""
Comparable Company Analysis (CCA) / Multiples Valuation Module
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def get_peer_data(ticker: str, sector: str = None) -> List[Dict]:
    """
    Get peer company data for comparison
    
    Args:
        ticker: Target ticker
        sector: Optional sector filter
    
    Returns:
        List of peer company metrics
    """
    from ..fetch_data import get_key_metrics, get_company_info
    
    # This is a simplified implementation
    # In production, use a database of comparable companies
    return []


def calculate_equity_value_from_ebitda(
    ebitda: float,
    ev_ebitda_multiple: float
) -> float:
    """
    Calculate equity value from EBITDA multiple
    
    Equity Value = EV - Net Debt
    EV = EBITDA × Multiple
    
    Args:
        ebitda: Company EBITDA
        ev_ebitda_multiple: EV/EBITDA multiple
    
    Returns:
        Enterprise value
    """
    return ebitda * ev_ebitda_multiple


def calculate_pe_multiple(
    price_per_share: float,
    earnings_per_share: float
) -> float:
    """
    Calculate P/E ratio
    
    Args:
        price_per_share: Stock price
        earnings_per_share: EPS
    
    Returns:
        P/E ratio
    """
    if earnings_per_share == 0:
        return 0.0
    return price_per_share / earnings_per_share


def calculate_pb_multiple(
    price_per_share: float,
    book_value_per_share: float
) -> float:
    """
    Calculate P/B ratio
    
    Args:
        price_per_share: Stock price
        book_value_per_share: Book value per share
    
    Returns:
        P/B ratio
    """
    if book_value_per_share == 0:
        return 0.0
    return price_per_share / book_value_per_share


def calculate_ps_multiple(
    price_per_share: float,
    sales_per_share: float
) -> float:
    """
    Calculate P/S ratio
    
    Args:
        price_per_share: Stock price
        sales_per_share: Sales per share
    
    Returns:
        P/S ratio
    """
    if sales_per_share == 0:
        return 0.0
    return price_per_share / sales_per_share


def calculate_ev_ebitda(
    enterprise_value: float,
    ebitda: float
) -> float:
    """
    Calculate EV/EBITDA multiple
    
    Args:
        enterprise_value: Enterprise value
        ebitda: EBITDA
    
    Returns:
        EV/EBITDA multiple
    """
    if ebitda == 0:
        return 0.0
    return enterprise_value / ebitda


def calculate_median_multiples(
    peer_metrics: List[Dict]
) -> Dict:
    """
    Calculate median multiples from peer group
    
    Args:
        peer_metrics: List of peer company metrics
    
    Returns:
        Dictionary of median multiples
    """
    if not peer_metrics:
        return {
            'pe_median': 0.0,
            'pb_median': 0.0,
            'ps_median': 0.0,
            'ev_ebitda_median': 0.0
        }
    
    pe_values = [p.get('pe_ratio', 0) for p in peer_metrics if p.get('pe_ratio', 0) > 0]
    pb_values = [p.get('pb_ratio', 0) for p in peer_metrics if p.get('pb_ratio', 0) > 0]
    ps_values = [p.get('ps_ratio', 0) for p in peer_metrics if p.get('ps_ratio', 0) > 0]
    ev_ebitda_values = [p.get('ev_ebitda', 0) for p in peer_metrics if p.get('ev_ebitda', 0) > 0]
    
    return {
        'pe_median': np.median(pe_values) if pe_values else 0.0,
        'pb_median': np.median(pb_values) if pb_values else 0.0,
        'ps_median': np.median(ps_values) if ps_values else 0.0,
        'ev_ebitda_median': np.median(ev_ebitda_values) if ev_ebitda_values else 0.0,
        'n_peers': len(peer_metrics)
    }


def apply_multiples_valuation(
    target_metrics: Dict,
    median_multiples: Dict
) -> Dict:
    """
    Apply median multiples to target company
    
    Args:
        target_metrics: Target company metrics
        median_multiples: Median multiples from peers
    
    Returns:
        Valuation results from each multiple
    """
    results = {}
    
    # P/E valuation
    eps = target_metrics.get('eps', 0)
    if eps > 0 and median_multiples.get('pe_median', 0) > 0:
        results['pe_valuation'] = eps * median_multiples['pe_median']
    
    # P/B valuation
    book_value_per_share = target_metrics.get('book_value_per_share', 0)
    if book_value_per_share > 0 and median_multiples.get('pb_median', 0) > 0:
        results['pb_valuation'] = book_value_per_share * median_multiples['pb_median']
    
    # P/S valuation
    sales_per_share = target_metrics.get('sales_per_share', 0)
    if sales_per_share > 0 and median_multiples.get('ps_median', 0) > 0:
        results['ps_valuation'] = sales_per_share * median_multiples['ps_median']
    
    # EV/EBITDA valuation
    ebitda = target_metrics.get('ebitda', 0)
    if ebitda > 0 and median_multiples.get('ev_ebitda_median', 0) > 0:
        ev = ebitda * median_multiples['ev_ebitda_median']
        # Convert to equity value
        net_debt = target_metrics.get('net_debt', 0)
        results['ev_ebitda_valuation'] = ev - net_debt
    
    # Calculate average
    valuations = [v for v in results.values() if v > 0]
    results['average_valuation'] = np.mean(valuations) if valuations else 0.0
    
    return results


def cca_valuation(
    ticker: str,
    target_metrics: Dict,
    peer_metrics: List[Dict] = None
) -> Dict:
    """
    Complete Comparable Company Analysis
    
    Args:
        ticker: Target ticker
        target_metrics: Target company metrics
        peer_metrics: Optional peer metrics (will fetch if not provided)
    
    Returns:
        Complete CCA results
    """
    # Get peer data if not provided
    if peer_metrics is None:
        peer_metrics = get_peer_data(ticker, target_metrics.get('sector'))
    
    # Calculate median multiples
    medians = calculate_median_multiples(peer_metrics)
    
    # Apply multiples to target
    valuations = apply_multiples_valuation(target_metrics, medians)
    
    return {
        'ticker': ticker,
        'method': 'CCA',
        'target_metrics': target_metrics,
        'n_peers': len(peer_metrics),
        'median_multiples': medians,
        'valuations': valuations
    }


def get_default_multiples_by_sector() -> Dict:
    """
    Get default multiples by sector (for when peer data unavailable)
    
    Returns:
        Dictionary of sector-specific multiples
    """
    return {
        'Technology': {'pe': 25.0, 'pb': 5.0, 'ps': 6.0, 'ev_ebitda': 18.0},
        'Financials': {'pe': 12.0, 'pb': 1.2, 'ps': 2.5, 'ev_ebitda': 10.0},
        'Consumer': {'pe': 20.0, 'pb': 3.0, 'ps': 2.0, 'ev_ebitda': 14.0},
        'Healthcare': {'pe': 22.0, 'pb': 4.0, 'ps': 5.0, 'ev_ebitda': 16.0},
        'Energy': {'pe': 10.0, 'pb': 1.5, 'ps': 1.2, 'ev_ebitda': 8.0},
        'Industrial': {'pe': 18.0, 'pb': 2.5, 'ps': 1.8, 'ev_ebitda': 12.0},
        'Utilities': {'pe': 15.0, 'pb': 1.8, 'ps': 3.0, 'ev_ebitda': 10.0},
        'Real Estate': {'pe': 14.0, 'pb': 1.0, 'ps': 8.0, 'ev_ebitda': 15.0}
    }
