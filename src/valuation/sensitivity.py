"""
Sensitivity Analysis Module
Two-way sensitivity tables and scenario analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def generate_sensitivity_range(
    base_value: float,
    variation: float,
    steps: int = 5
) -> List[float]:
    """
    Generate a range of values for sensitivity analysis
    
    Args:
        base_value: Base case value
        variation: Total variation (e.g., 0.02 = +/-2%)
        steps: Number of steps
    
    Returns:
        List of values
    """
    if steps == 1:
        return [base_value]
    
    half_range = base_value * variation
    step_size = half_range * 2 / (steps - 1)
    
    values = []
    for i in range(steps):
        values.append(base_value - half_range + step_size * i)
    
    return values


def two_way_sensitivity(
    base_value: float,
    var1_name: str,
    var1_range: List[float],
    var2_name: str,
    var2_range: List[float],
    calculate_fn
) -> pd.DataFrame:
    """
    Generate two-way sensitivity table
    
    Args:
        base_value: Base case result
        var1_name: Name of first variable
        var1_range: Range of first variable values
        var2_name: Name of second variable
        var2_range: Range of second variable values
        calculate_fn: Function to calculate result given (var1, var2)
    
    Returns:
        DataFrame with sensitivity results
    """
    results = np.zeros((len(var2_range), len(var1_range)))
    
    for i, v2 in enumerate(var2_range):
        for j, v1 in enumerate(var1_range):
            try:
                results[i, j] = calculate_fn(v1, v2)
            except Exception as e:
                logger.error(f"Error calculating sensitivity: {e}")
                results[i, j] = 0.0
    
    df = pd.DataFrame(
        results,
        index=[f"{var2_name}={v:.4f}" for v in var2_range],
        columns=[f"{var1_name}={v:.4f}" for v in var1_range]
    )
    
    return df


def wacc_sensitivity(
    cost_of_equity: float,
    debt_weight_range: List[float],
    cost_debt_range: List[float],
    tax_rate: float = 0.25
) -> pd.DataFrame:
    """
    Generate WACC sensitivity table
    
    Args:
        cost_of_equity: Cost of equity
        debt_weight_range: Range of debt weights
        cost_debt_range: Range of cost of debt
        tax_rate: Tax rate
    
    Returns:
        WACC sensitivity DataFrame
    """
    def calc_wacc(debt_weight, cost_debt):
        equity_weight = 1 - debt_weight
        return equity_weight * cost_of_equity + debt_weight * cost_debt * (1 - tax_rate)
    
    return two_way_sensitivity(
        0.0,
        "Debt Weight",
        debt_weight_range,
        "Cost of Debt",
        cost_debt_range,
        calc_wacc
    )


def dcf_sensitivity(
    base_fcf: float,
    terminal_growth_range: List[float],
    wacc_range: List[float],
    years: int = 5
) -> pd.DataFrame:
    """
    Generate DCF sensitivity table (Terminal Value impact)
    
    Args:
        base_fcf: Base year FCF
        terminal_growth_range: Range of terminal growth rates
        wacc_range: Range of WACC values
        years: Projection years
    
    Returns:
        DCF sensitivity DataFrame
    """
    def calc_dcf_value(growth, wacc):
        if wacc <= growth:
            return 0.0
        
        # Terminal value
        terminal_value = base_fcf * (1 + growth) / (wacc - growth)
        
        # PV of terminal value
        return terminal_value / (1 + wacc) ** years
    
    return two_way_sensitivity(
        0.0,
        "Terminal Growth",
        terminal_growth_range,
        "WACC",
        wacc_range,
        calc_dcf_value
    )


def scenario_analysis(
    base_case: Dict,
    best_case: Dict,
    worst_case: Dict,
    variables: List[str]
) -> Dict:
    """
    Generate scenario analysis
    
    Args:
        base_case: Base case parameters and result
        best_case: Best case parameters
        worst_case: Worst case parameters
        variables: Variables to include in scenario
    
    Returns:
        Scenario analysis results
    """
    scenarios = {
        'worst': worst_case,
        'base': base_case,
        'best': best_case
    }
    
    results = {}
    for scenario_name, params in scenarios.items():
        results[scenario_name] = {
            'inputs': {v: params.get(v, 0) for v in variables},
            'result': params.get('result', 0)
        }
    
    # Calculate ranges
    results_list = [r['result'] for r in results.values()]
    results['range'] = {
        'min': min(results_list),
        'max': max(results_list),
        'spread': max(results_list) - min(results_list)
    }
    
    return results


def tornado_analysis(
    base_result: float,
    variable_impacts: Dict[str, Tuple[float, float]]
) -> Dict:
    """
    Generate tornado analysis (one-way sensitivity)
    
    Args:
        base_result: Base case result
        variable_impacts: Dict of {variable: (low_impact, high_impact)}
    
    Returns:
        Tornado analysis results sorted by impact
    """
    impacts = []
    
    for var_name, (low_val, high_val) in variable_impacts.items():
        low_impact = abs(low_val - base_result)
        high_impact = abs(high_val - base_result)
        max_impact = max(low_impact, high_impact)
        
        impacts.append({
            'variable': var_name,
            'low_value': low_val,
            'high_value': high_val,
            'low_impact': low_impact,
            'high_impact': high_impact,
            'max_impact': max_impact,
            'swing': high_val - low_val
        })
    
    # Sort by max impact
    impacts.sort(key=lambda x: x['max_impact'], reverse=True)
    
    return {
        'base_result': base_result,
        'variables': impacts,
        'most_sensitive': impacts[0]['variable'] if impacts else None
    }


def monte_carlo_valuation(
    base_params: Dict,
    param_distributions: Dict[str, Tuple[str, float, float]],
    n_simulations: int = 10000,
    calculate_fn=None
) -> Dict:
    """
    Monte Carlo simulation for valuation
    
    Args:
        base_params: Base parameters
        param_distributions: {param: (distribution_type, mean, std)}
        n_simulations: Number of simulations
        calculate_fn: Function to calculate result
    
    Returns:
        Monte Carlo results
    """
    results = []
    
    for _ in range(n_simulations):
        params = base_params.copy()
        
        for param, (dist_type, mean, std) in param_distributions.items():
            if dist_type == 'normal':
                params[param] = np.random.normal(mean, std)
            elif dist_type == 'uniform':
                params[param] = np.random.uniform(mean, std)
            elif dist_type == 'triangular':
                params[param] = np.random.triangular(mean - std, mean, mean + std)
        
        try:
            result = calculate_fn(**params)
            results.append(result)
        except:
            pass
    
    if not results:
        return {'error': 'No valid results from simulation'}
    
    results_array = np.array(results)
    
    return {
        'n_simulations': len(results),
        'mean': np.mean(results_array),
        'median': np.median(results_array),
        'std': np.std(results_array),
        'min': np.min(results_array),
        'max': np.max(results_array),
        'percentile_5': np.percentile(results_array, 5),
        'percentile_25': np.percentile(results_array, 25),
        'percentile_75': np.percentile(results_array, 75),
        'percentile_95': np.percentile(results_array, 95)
    }
