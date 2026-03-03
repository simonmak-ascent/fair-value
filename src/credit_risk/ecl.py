"""
Expected Credit Loss (ECL) calculation per HKFRS 9 / IFRS 9
"""

import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def calculate_ecL(exposure_at_default: float, 
                 probability_of_default: float,
                 loss_given_default: float) -> float:
    """
    Calculate Expected Credit Loss
    
    ECL = EAD × PD × LGD
    
    Args:
        exposure_at_default: EAD (Amount exposed to default)
        probability_of_default: PD (Probability of default)
        loss_given_default: LGD (Loss given default, 0-1)
    
    Returns:
        Expected Credit Loss
    """
    return exposure_at_default * probability_of_default * loss_given_default


def get_pd_from_rating(credit_rating: str) -> float:
    """
    Map credit rating to probability of default
    
    Args:
        credit_rating: Credit rating (e.g., 'A', 'BBB', 'BB')
    
    Returns:
        Probability of default
    """
    rating_to_pd = {
        'AAA': 0.001,
        'AA+': 0.002,
        'AA': 0.005,
        'AA-': 0.008,
        'A+': 0.01,
        'A': 0.02,
        'A-': 0.03,
        'BBB+': 0.04,
        'BBB': 0.05,
        'BBB-': 0.08,
        'BB+': 0.10,
        'BB': 0.15,
        'BB-': 0.20,
        'B+': 0.25,
        'B': 0.30,
        'B-': 0.40,
        'CCC': 0.50,
        'CC': 0.60,
        'C': 0.80,
        'D': 1.00
    }
    
    return rating_to_pd.get(credit_rating.upper(), 0.30)


def get_lgd_from_recovery(recovery_rate: float) -> float:
    """
    Derive LGD from recovery rate
    
    LGD = 1 - Recovery Rate
    
    Args:
        recovery_rate: Recovery rate (0-1)
    
    Returns:
        Loss given default
    """
    return 1 - recovery_rate


def get_default_lgd_by_seniority(seniority: str) -> float:
    """
    Get typical LGD by debt seniority
    
    Args:
        seniority: 'Senior Secured', 'Senior Unsecured', 'Subordinated', 'Preferred'
    
    Returns:
        LGD
    """
    lgd_by_seniority = {
        'Senior Secured': 0.25,
        'Senior Unsecured': 0.45,
        'Subordinated': 0.75,
        'Preferred': 0.85
    }
    
    return lgd_by_seniority.get(seniority, 0.45)


def calculate_12m_ecL(exposure: float, pd_12m: float, lgd: float) -> float:
    """
    Calculate 12-month ECL (Stage 1)
    
    Args:
        exposure: Exposure at default
        pd_12m: 12-month PD
        lgd: Loss given default
    
    Returns:
        12-month ECL
    """
    return exposure * pd_12m * lgd


def calculate_lifetime_ecL(exposure: float, pd_lifetime: float, lgd: float) -> float:
    """
    Calculate lifetime ECL (Stage 2 & 3)
    
    Args:
        exposure: Exposure at default
        pd_lifetime: Lifetime PD
        lgd: Loss given default
    
    Returns:
        Lifetime ECL
    """
    return exposure * pd_lifetime * lgd


def forward_looking_adjustment(base_ecL: float, 
                              gdp_factor: float = 1.0,
                              inflation_factor: float = 1.0,
                              industry_factor: float = 1.0) -> float:
    """
    Apply forward-looking adjustment to ECL per HKFRS 9
    
    Args:
        base_ecL: Base ECL calculation
        gdp_factor: GDP growth factor (e.g., 1.2 for stress)
        inflation_factor: Inflation factor
        industry_factor: Industry-specific factor
    
    Returns:
        Adjusted ECL
    """
    overall_factor = gdp_factor * inflation_factor * industry_factor
    return base_ecL * overall_factor


def calculate_ecL_portfolio(assets: list, 
                           pd_by_asset: list,
                           lgd_by_asset: list) -> Dict:
    """
    Calculate ECL for a portfolio of assets
    
    Args:
        assets: List of asset exposures
        pd_by_asset: List of PDs for each asset
        lgd_by_asset: List of LGDs for each asset
    
    Returns:
        Portfolio ECL analysis
    """
    if len(assets) != len(pd_by_asset) or len(assets) != len(lgd_by_asset):
        return {'error': 'Mismatched asset arrays'}
    
    total_exposure = sum(assets)
    ecls = [assets[i] * pd_by_asset[i] * lgd_by_asset[i] for i in range(len(assets))]
    total_ecL = sum(ecls)
    
    # Weighted average PD
    weighted_pd = sum([assets[i] * pd_by_asset[i] for i in range(len(assets))]) / total_exposure
    
    return {
        'total_exposure': total_exposure,
        'total_ecl': total_ecL,
        'weighted_average_pd': weighted_pd,
        'ecl_by_asset': ecls,
        'coverage_ratio': total_ecL / total_exposure if total_exposure > 0 else 0
    }


def assess_credit_stage(pd_12m: float, significant_increase: bool = False) -> str:
    """
    Assess credit stage per HKFRS 9
    
    Stage 1: 12-month ECL (performing)
    Stage 2: Lifetime ECL (significant increase in credit risk)
    Stage 3: Lifetime ECL (credit-impaired)
    
    Args:
        pd_12m: 12-month probability of default
        significant_increase: Whether credit risk has increased significantly
    
    Returns:
        Stage ('Stage 1', 'Stage 2', or 'Stage 3')
    """
    # Threshold for significant increase: PD > 0.5% or increase > 0.3%
    if pd_12m > 0.10:
        return 'Stage 3'
    elif significant_increase or pd_12m > 0.005:
        return 'Stage 2'
    else:
        return 'Stage 1'
