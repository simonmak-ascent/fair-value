"""
Interest Rate and Currency Swap Valuation Module
"""

import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def discount_factor(rate: float, time: float) -> float:
    """
    Calculate discount factor
    
    DF = 1 / (1 + r)^t
    
    Args:
        rate: Interest rate
        time: Time in years
    
    Returns:
        Discount factor
    """
    return 1 / (1 + rate) ** time


def present_value(payments: List[float], times: List[float], discount_rate: float) -> float:
    """
    Calculate present value of cash flows
    
    Args:
        payments: List of cash payments
        times: List of payment times
        discount_rate: Discount rate
    
    Returns:
        Present value
    """
    pv = 0.0
    for payment, time in zip(payments, times):
        pv += payment * discount_factor(discount_rate, time)
    return pv


def interest_rate_swap_value(
    notional: float,
    fixed_rate: float,
    floating_rates: List[float],
    payment_times: List[float],
    discount_rate: float
) -> Dict:
    """
    Value interest rate swap
    
    Args:
        notional: Notional amount
        fixed_rate: Fixed interest rate
        floating_rates: List of floating rates (for each period)
        payment_times: Payment times
        discount_rate: Discount rate for valuation
    
    Returns:
        Swap valuation results
    """
    # Fixed leg PV
    fixed_payments = [notional * fixed_rate * (payment_times[i+1] - payment_times[i]) 
                     for i in range(len(floating_rates))]
    fixed_pv = present_value(fixed_payments[1:], payment_times[1:], discount_rate)
    
    # Floating leg PV
    floating_payments = [notional * floating_rates[i] * (payment_times[i+1] - payment_times[i])
                       for i in range(len(floating_rates))]
    floating_pv = present_value(floating_payments, payment_times, discount_rate)
    
    return {
        'fixed_leg_pv': fixed_pv,
        'floating_leg_pv': floating_pv,
        'swap_value': floating_pv - fixed_pv,
        'notional': notional
    }


def swap_rate_from_curve(tenor: int, zero_rates: List[float], times: List[float]) -> float:
    """
    Derive swap rate from zero curve
    
    Args:
        tenor: Swap tenor in years
        zero_rates: Zero rates
        times: Corresponding times
    
    Returns:
        Swap rate
    """
    # Simplified: use average of zero rates
    return np.mean(zero_rates[:tenor]) if tenor <= len(zero_rates) else np.mean(zero_rates)


def par_swap_rate(
    notional: float,
    tenor: int,
    forward_rates: List[float],
    discount_rates: List[float]
) -> float:
    """
    Calculate par swap rate
    
    Args:
        notional: Notional amount
        tenor: Tenor in years
        forward_rates: Forward rates
        discount_rates: Discount rates
    
    Returns:
        Par swap rate
    """
    # Numerator: sum of discounted forward rates
    num = sum(forward_rates[i] * discount_factor(discount_rates[i], i+1) 
              for i in range(tenor))
    
    # Denominator: sum of discount factors
    den = sum(discount_factor(discount_rates[i], i+1) for i in range(tenor))
    
    return num / den if den > 0 else 0.0


def currency_swap_value(
    notional_domestic: float,
    notional_foreign: float,
    spot_rate: float,
    domestic_rates: List[float],
    foreign_rates: List[float],
    times: List[float]
) -> Dict:
    """
    Value cross-currency swap
    
    Args:
        notional_domestic: Domestic notional
        notional_foreign: Foreign notional (in foreign currency)
        spot_rate: Spot exchange rate (domestic per foreign)
        domestic_rates: Domestic interest rates
        foreign_rates: Foreign interest rates
        times: Payment times
    
    Returns:
        Currency swap valuation
    """
    domestic_pv = present_value(
        [notional_domestic * domestic_rates[i] for i in range(len(domestic_rates))],
        times,
        np.mean(domestic_rates)
    )
    
    foreign_pv = present_value(
        [notional_foreign * foreign_rates[i] for i in range(len(foreign_rates))],
        times,
        np.mean(foreign_rates)
    )
    
    # Convert foreign PV to domestic
    foreign_pv_domestic = foreign_pv * spot_rate
    
    # Principal exchange
    principal_domestic = notional_domestic
    principal_foreign = notional_foreign * spot_rate
    
    return {
        'domestic_leg_pv': domestic_pv + principal_domestic,
        'foreign_leg_pv': foreign_pv_domestic + principal_foreign,
        'swap_value': domestic_pv + principal_domestic - foreign_pv_domestic - principal_foreign,
        'notional_domestic': notional_domestic,
        'notional_foreign': notional_foreign
    }


def basis_swap_value(
    notional: float,
    rate1_type: str,
    rate2_type: str,
    basis_spread: float,
    times: List[float],
    discount_rate: float
) -> float:
    """
    Value basis swap
    
    Args:
        notional: Notional amount
        rate1_type: First rate type (e.g., 'LIBOR', 'SOFR')
        rate2_type: Second rate type
        basis_spread: Basis spread
        times: Payment times
        discount_rate: Discount rate
    
    Returns:
        Basis swap value
    """
    # Simplified: basis spread value
    pv = 0.0
    for time in times:
        pv += notional * basis_spread * discount_factor(discount_rate, time)
    
    return pv


def amortizing_swap_value(
    notional_initial: float,
    amortization_schedule: List[float],
    fixed_rate: float,
    floating_rates: List[float],
    times: List[float],
    discount_rate: float
) -> Dict:
    """
    Value amortizing interest rate swap
    
    Args:
        notional_initial: Initial notional
        amortization_schedule: Remaining notional at each period
        fixed_rate: Fixed rate
        floating_rates: Floating rates
        times: Payment times
        discount_rate: Discount rate
    
    Returns:
        Amortizing swap valuation
    """
    fixed_pv = 0.0
    floating_pv = 0.0
    
    for i in range(len(times) - 1):
        notional = amortization_schedule[i] if i < len(amortization_schedule) else amortization_schedule[-1]
        dt = times[i+1] - times[i]
        
        fixed_pv += notional * fixed_rate * dt * discount_factor(discount_rate, times[i+1])
        floating_pv += notional * floating_rates[i] * dt * discount_factor(discount_rate, times[i+1])
    
    return {
        'fixed_leg_pv': fixed_pv,
        'floating_leg_pv': floating_pv,
        'swap_value': floating_pv - fixed_pv
    }
