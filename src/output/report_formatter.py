"""
Report Formatter Module
Format valuation results for docgen output
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)


def format_for_pdf(valuation_result: Dict) -> Dict:
    """
    Format valuation result for PDF output
    
    Args:
        valuation_result: Valuation results dictionary
    
    Returns:
        Sections for PDF creation
    """
    sections = []
    
    sections.append({
        'type': 'cover',
        'title': valuation_result.get('method', 'Valuation') + ' Report',
        'subtitle': f"Ticker: {valuation_result.get('ticker', 'N/A')}"
    })
    
    if 'value_per_share' in valuation_result:
        sections.append({
            'type': 'kpi_row',
            'metrics': {
                'Fair Value': f"${valuation_result.get('value_per_share', 0):.2f}",
                'Method': valuation_result.get('method', 'DCF'),
                'WACC': f"{valuation_result.get('wacc', 0)*100:.1f}%"
            }
        })
    
    if 'projections' in valuation_result:
        sections.append({
            'type': 'section',
            'heading': 'Financial Projections',
            'body': 'Cash flow projections and assumptions'
        })
        
        table_data = []
        for proj in valuation_result.get('projections', [])[:5]:
            table_data.append([
                f"Year {proj.get('year', '')}",
                f"${proj.get('revenue', 0)/1e9:.1f}B",
                f"${proj.get('free_cash_flow', 0)/1e6:.1f}M"
            ])
        
        sections.append({
            'type': 'table',
            'caption': 'Projections Summary',
            'headers': ['Year', 'Revenue', 'FCF'],
            'rows': table_data
        })
    
    if 'terminal_value' in valuation_result:
        sections.append({
            'type': 'section',
            'heading': 'Terminal Value',
            'body': f"${valuation_result.get('terminal_value', 0)/1e9:.2f}B"
        })
    
    return {'sections': sections}


def format_for_excel(valuation_result: Dict) -> Dict:
    """
    Format valuation result for Excel output
    
    Args:
        valuation_result: Valuation results dictionary
    
    Returns:
        Sheets for Excel creation
    """
    sheets = []
    
    summary_data = [
        ['Metric', 'Value'],
        ['Ticker', valuation_result.get('ticker', '')],
        ['Method', valuation_result.get('method', '')],
    ]
    
    if 'value_per_share' in valuation_result:
        summary_data.append(['Fair Value', valuation_result.get('value_per_share', 0)])
        summary_data.append(['WACC', valuation_result.get('wacc', 0)])
    
    sheets.append({
        'name': 'Summary',
        'headers': ['Metric', 'Value'],
        'rows': summary_data
    })
    
    if 'projections' in valuation_result:
        proj_rows = []
        for proj in valuation_result.get('projections', []):
            proj_rows.append([
                proj.get('year', ''),
                proj.get('revenue', 0),
                proj.get('ebitda', 0),
                proj.get('free_cash_flow', 0)
            ])
        
        sheets.append({
            'name': 'Projections',
            'headers': ['Year', 'Revenue', 'EBITDA', 'FCF'],
            'rows': proj_rows
        })
    
    return {'sheets': sheets}


def create_kpi_cards(valuation_result: Dict) -> Dict:
    """
    Create KPI cards for charts
    
    Args:
        valuation_result: Valuation results
    
    Returns:
        KPI metrics dictionary
    """
    kpis = {}
    
    if 'value_per_share' in valuation_result:
        kpis['Fair Value'] = {
            'value': f"${valuation_result.get('value_per_share', 0):.2f}",
            'unit': '$',
            'change': '+12%'
        }
    
    if 'wacc' in valuation_result:
        kpis['WACC'] = {
            'value': f"{valuation_result.get('wacc', 0)*100:.1f}",
            'unit': '%',
            'change': '-0.5%'
        }
    
    if 'terminal_growth' in valuation_result:
        kpis['Terminal Growth'] = {
            'value': f"{valuation_result.get('terminal_growth', 0)*100:.1f}",
            'unit': '%',
            'change': '0%'
        }
    
    return kpis


def generate_valuation_report(valuation_result: Dict) -> str:
    """
    Generate human-readable report
    
    Args:
        valuation_result: Valuation results
    
    Returns:
        Report text
    """
    lines = []
    lines.append("=" * 60)
    lines.append(f"{valuation_result.get('method', 'Valuation')} Report")
    lines.append(f"Ticker: {valuation_result.get('ticker', 'N/A')}")
    lines.append("=" * 60)
    lines.append("")
    
    if 'value_per_share' in valuation_result:
        lines.append(f"Fair Value per Share: ${valuation_result.get('value_per_share', 0):.2f}")
        lines.append(f"Enterprise Value: ${valuation_result.get('enterprise_value', 0)/1e9:.2f}B")
        lines.append(f"WACC: {valuation_result.get('wacc', 0)*100:.2f}%")
        lines.append("")
    
    if 'assumptions' in valuation_result:
        lines.append("Key Assumptions:")
        for key, value in valuation_result.get('assumptions', {}).items():
            lines.append(f"  {key}: {value}")
        lines.append("")
    
    lines.append("Disclaimer:")
    lines.append("This valuation is for informational purposes only.")
    lines.append("Not investment advice.")
    
    return "\n".join(lines)
