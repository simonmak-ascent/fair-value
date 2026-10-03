"""
Chart Data Module
Prepare data for chart generation via docgen
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


def prepare_bar_chart_data(categories: List[str], values: List[float], title: str) -> Dict:
    """
    Prepare data for bar chart

    Args:
        categories: X-axis labels
        values: Bar values
        title: Chart title

    Returns:
        Chart data dictionary
    """
    return {"chart_type": "bar", "title": title, "labels": categories, "values": values}


def prepare_line_chart_data(series: Dict[str, List[float]], title: str) -> Dict:
    """
    Prepare data for line chart

    Args:
        series: Dictionary of {series_name: values}
        title: Chart title

    Returns:
        Chart data dictionary
    """
    return {"chart_type": "line", "title": title, "series": series}


def prepare_pie_chart_data(labels: List[str], values: List[float], title: str) -> Dict:
    """
    Prepare data for pie chart

    Args:
        labels: Segment labels
        values: Segment values
        title: Chart title

    Returns:
        Chart data dictionary
    """
    return {"chart_type": "pie", "title": title, "labels": labels, "values": values}


def prepare_combo_chart_data(
    categories: List[str], bar_values: List[float], line_values: List[float], title: str
) -> Dict:
    """
    Prepare data for combo chart (bar + line)

    Args:
        categories: X-axis labels
        bar_values: Values for bar series
        line_values: Values for line series
        title: Chart title

    Returns:
        Chart data dictionary
    """
    return {
        "chart_type": "combo",
        "title": title,
        "labels": categories,
        "series": {"Bar Series": bar_values, "Line Series": line_values},
    }


def prepare_cash_flow_chart(projections: List[Dict]) -> Dict:
    """
    Prepare cash flow chart data

    Args:
        projections: List of projection dictionaries

    Returns:
        Chart data
    """
    years = [f"Year {p.get('year', i + 1)}" for i, p in enumerate(projections)]
    revenue = [p.get("revenue", 0) / 1e9 for p in projections]
    fcf = [p.get("free_cash_flow", 0) / 1e9 for p in projections]

    return prepare_combo_chart_data(years, revenue, fcf, "Cash Flow Projections")


def prepare_sensitivity_heatmap(sensitivity_df) -> Dict:
    """
    Prepare sensitivity table as heatmap data

    Args:
        sensitivity_df: DataFrame with sensitivity results

    Returns:
        Heatmap data
    """
    return {
        "chart_type": "bar",
        "title": "Sensitivity Analysis",
        "labels": list(sensitivity_df.index),
        "values": [sensitivity_df.iloc[i].mean() for i in range(len(sensitivity_df))],
    }


def prepare_comparison_chart(
    items: List[str], current: List[float], target: List[float], title: str
) -> Dict:
    """
    Prepare comparison bar chart

    Args:
        items: Items to compare
        current: Current values
        target: Target values
        title: Chart title

    Returns:
        Chart data
    """
    return {
        "chart_type": "combo",
        "title": title,
        "labels": items,
        "series": {"Current": current, "Target": target},
    }


def prepare_scatter_data(x_values: List[float], y_values: List[float], title: str) -> Dict:
    """
    Prepare scatter plot data

    Args:
        x_values: X-axis values
        y_values: Y-axis values
        title: Chart title

    Returns:
        Scatter data
    """
    return {"chart_type": "scatter", "title": title, "x": x_values, "y": y_values}
