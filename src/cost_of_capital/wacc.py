"""
Weighted Average Cost of Capital (WACC) calculation
Combines Fama-French 5-Factor cost of equity with KMV cost of debt
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)


def calculate_wacc(
    equity_weight: float,
    debt_weight: float,
    cost_equity: float,
    cost_debt: float,
    tax_rate: float = 0.25,
) -> float:
    """
    Calculate Weighted Average Cost of Capital

    WACC = (E/V) × Re + (D/V) × Rd × (1-T)

    Args:
        equity_weight: Weight of equity (e.g., 0.7)
        debt_weight: Weight of debt (e.g., 0.3)
        cost_equity: Cost of equity (e.g., 0.10 for 10%)
        cost_debt: Cost of debt (e.g., 0.05 for 5%)
        tax_rate: Corporate tax rate (default: 25%)

    Returns:
        WACC as decimal
    """
    # Normalize weights
    total = equity_weight + debt_weight
    if total == 0:
        return 0.0

    equity_weight = equity_weight / total
    debt_weight = debt_weight / total

    wacc = equity_weight * cost_equity + debt_weight * cost_debt * (1 - tax_rate)

    return wacc


def get_capital_structure_from_balance_sheet(equity: float, debt: float) -> Dict:
    """
    Calculate capital structure weights from balance sheet values

    Args:
        equity: Total equity (book or market value)
        debt: Total debt

    Returns:
        Dictionary with weights
    """
    total = equity + debt
    if total == 0:
        return {"equity_weight": 0, "debt_weight": 0, "debt_to_equity": 0}

    return {
        "equity_weight": equity / total,
        "debt_weight": debt / total,
        "debt_to_equity": debt / equity if equity > 0 else 0,
    }


def calculate_wacc_sensitivity(
    wacc_base: float, variables: Dict[str, tuple], steps: int = 5
) -> Dict:
    """
    Generate WACC sensitivity analysis

    Args:
        wacc_base: Base WACC value
        variables: Dictionary of variables with (low, high) ranges
                  e.g., {'cost_of_equity': (0.08, 0.12), 'debt_weight': (0.2, 0.4)}
        steps: Number of steps for sensitivity

    Returns:
        Sensitivity matrix
    """
    results = {}

    for var_name, (low, high) in variables.items():
        values = []
        step = (high - low) / (steps - 1)

        for i in range(steps):
            value = low + step * i
            values.append(value)

        results[var_name] = values

    return results
