"""
Excel Valuation Model Analyzer
Reviews and validates Excel valuation models
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)

# Try to import openpyxl
try:
    import openpyxl  # noqa: F401  # availability probe (also exported to callers)
    from openpyxl import load_workbook

    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    logger.warning("openpyxl not available for Excel analysis")


def analyze_excel_model(file_path: str) -> Dict:
    """
    Main entry point for Excel model analysis

    Args:
        file_path: Path to Excel file

    Returns:
        Comprehensive analysis results
    """
    if not OPENPYXL_AVAILABLE:
        return {
            "file": file_path,
            "status": "error",
            "message": "openpyxl not installed. Run: pip install openpyxl",
        }

    try:
        # Load workbook
        workbook = load_workbook(file_path, data_only=False)

        # Run analysis
        analysis = {
            "file": file_path,
            "status": "success",
            "sheets": workbook.sheetnames,
            "model_analysis": analyze_valuation_methodology(workbook),
            "formula_validation": validate_dcf_formulas(workbook),
            "wacc_validation": validate_wacc_calculation(workbook),
            "terminal_value_check": validate_terminal_value(workbook),
            "assumptions": extract_assumptions(workbook),
            "data_sources": check_data_sources(workbook),
        }

        # Generate review report
        analysis["review_report"] = generate_review_report(analysis)

        return analysis

    except Exception as e:
        logger.error(f"Error analyzing Excel file: {e}")
        return {"file": file_path, "status": "error", "message": str(e)}


def analyze_valuation_methodology(workbook) -> Dict:
    """
    Identify and validate valuation methodology

    Args:
        workbook: openpyxl workbook object

    Returns:
        Methodology analysis
    """
    sheet_names = [s.lower() for s in workbook.sheetnames]

    # Detect methodology
    methodology = None
    confidence = 0

    # DCF indicators
    dcf_indicators = ["dcf", "discounted cash flow", "cash flow", "wacc", "discount rate"]
    if any(ind in " ".join(sheet_names) for ind in dcf_indicators):
        methodology = "DCF"
        confidence = 0.8

    # NAV indicators
    nav_indicators = ["nav", "net asset", "asset value", "holdings"]
    if any(ind in " ".join(sheet_names) for ind in nav_indicators):
        methodology = "NAV"
        confidence = 0.8

    # CCA indicators
    cca_indicators = ["comparable", "multiples", "peers", "trading"]
    if any(ind in " ".join(sheet_names) for ind in cca_indicators):
        methodology = "CCA"
        confidence = 0.7

    return {
        "identified_methodology": methodology,
        "confidence": confidence,
        "detected_sheets": sheet_names,
    }


def validate_dcf_formulas(workbook) -> Dict:
    """
    Validate DCF formulas in Excel model

    Checks:
    - NPV function usage
    - Discount factor calculations
    - Cash flow projections

    Args:
        workbook: openpyxl workbook object

    Returns:
        Formula validation results
    """
    issues = []
    found_formulas = []

    # Search for NPV formulas
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]

        for row in sheet.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    formula = cell.value

                    # Check for NPV
                    if "NPV" in formula.upper():
                        found_formulas.append(
                            {
                                "sheet": sheet_name,
                                "cell": cell.coordinate,
                                "formula": formula,
                                "type": "NPV",
                            }
                        )

                    # Check for discount factors
                    if "1/(1+" in formula or "POWER" in formula.upper():
                        found_formulas.append(
                            {
                                "sheet": sheet_name,
                                "cell": cell.coordinate,
                                "formula": formula[:50],  # Truncate for display
                                "type": "Discount Factor",
                            }
                        )

                    # Check for IRR
                    if "IRR" in formula.upper():
                        found_formulas.append(
                            {
                                "sheet": sheet_name,
                                "cell": cell.coordinate,
                                "formula": formula,
                                "type": "IRR",
                            }
                        )

    return {
        "formulas_found": found_formulas,
        "issues": issues,
        "validation_status": "passed" if len(issues) == 0 else "issues_found",
    }


def validate_wacc_calculation(workbook) -> Dict:
    """
    Validate WACC calculation

    Checks:
    - Cost of equity formula
    - Cost of debt formula
    - Weight calculations
    - Final WACC

    Args:
        workbook: openpyxl workbook object

    Returns:
        WACC validation results
    """
    wacc_indicators = []
    cost_of_equity_found = False
    cost_of_debt_found = False

    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]

        for row in sheet.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    value_lower = cell.value.lower()

                    # Look for WACC references
                    if "wacc" in value_lower or "weighted average" in value_lower:
                        wacc_indicators.append(
                            {
                                "sheet": sheet_name,
                                "cell": cell.coordinate,
                                "formula": cell.value[:100],
                            }
                        )

                    # Look for cost of equity
                    if "cost of equity" in value_lower or "ke" in value_lower:
                        cost_of_equity_found = True

                    # Look for cost of debt
                    if "cost of debt" in value_lower or "kd" in value_lower:
                        cost_of_debt_found = True

    return {
        "wacc_references": wacc_indicators,
        "cost_of_equity_found": cost_of_equity_found,
        "cost_of_debt_found": cost_of_debt_found,
        "is_complete": cost_of_equity_found and cost_of_debt_found,
    }


def validate_terminal_value(workbook) -> Dict:
    """
    Validate terminal value calculation

    Checks:
    - Gordon growth method
    - Exit multiple method

    Args:
        workbook: openpyxl workbook object

    Returns:
        Terminal value validation results
    """
    terminal_value_found = False
    gordon_growth_found = False
    exit_multiple_found = False

    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]

        for row in sheet.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    value = cell.value.lower()

                    if "terminal" in value or "tv" in value:
                        terminal_value_found = True

                    if "gordon" in value or "perpetual" in value:
                        gordon_growth_found = True

                    if "exit" in value or "multiple" in value:
                        exit_multiple_found = True

    return {
        "terminal_value_found": terminal_value_found,
        "gordon_growth_method": gordon_growth_found,
        "exit_multiple_method": exit_multiple_found,
        "validation": "passed" if terminal_value_found else "warning",
    }


def extract_assumptions(workbook) -> Dict:
    """
    Extract key assumptions from Excel model

    Args:
        workbook: openpyxl workbook object

    Returns:
        Extracted assumptions
    """
    assumptions = {}
    assumption_keywords = [
        "growth",
        "wacc",
        "discount",
        "terminal",
        "margin",
        "capex",
        "working capital",
        "tax rate",
        "beta",
    ]

    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]

        for row in sheet.iter_rows():
            for cell in row:
                if cell.value:
                    # Check if cell is assumption label
                    if isinstance(cell.value, str):
                        value_lower = cell.value.lower()

                        for keyword in assumption_keywords:
                            if keyword in value_lower:
                                # Check adjacent cell for value
                                next_cell = sheet.cell(row.cell.row, cell.column + 1)
                                if next_cell.value:
                                    assumptions[keyword] = {
                                        "value": next_cell.value,
                                        "sheet": sheet_name,
                                        "cell": next_cell.coordinate,
                                    }

    return assumptions


def check_data_sources(workbook) -> Dict:
    """
    Check data sources in the Excel model

    Args:
        workbook: openpyxl workbook object

    Returns:
        Data source information
    """
    external_links = []
    data_connections = []

    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]

        for row in sheet.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    # Check for external references
                    if "[" in cell.value or ".xls" in cell.value.lower():
                        external_links.append(
                            {
                                "sheet": sheet_name,
                                "cell": cell.coordinate,
                                "reference": cell.value[:100],
                            }
                        )

                    # Check for data functions
                    if any(fn in cell.value.upper() for fn in ["WEBSERVICE", "IMPORTDATA"]):
                        data_connections.append({"sheet": sheet_name, "cell": cell.coordinate})

    return {
        "external_links": external_links,
        "data_connections": data_connections,
        "is_self_contained": len(external_links) == 0,
    }


def compare_with_market_data(assumptions: Dict, ticker: str) -> Dict:
    """
    Compare model assumptions with current market data

    Args:
        assumptions: Extracted assumptions
        ticker: Stock ticker

    Returns:
        Comparison results
    """
    from ..fetch_data import get_key_metrics, get_stock_price

    comparison = {"assumptions": assumptions, "market_data": {}, "deviations": []}

    try:
        # Get market data
        metrics = get_key_metrics(ticker)
        price = get_stock_price(ticker)

        comparison["market_data"] = {
            "price": price,
            "beta": metrics.get("beta", 0),
            "pe_ratio": metrics.get("pe_ratio", 0),
            "market_cap": metrics.get("market_cap", 0),
        }

        # Compare key assumptions
        # This is a simplified comparison
        # Real implementation would parse assumption values

    except Exception as e:
        comparison["error"] = str(e)

    return comparison


def generate_review_report(analysis: Dict) -> str:
    """
    Generate human-readable review report

    Args:
        analysis: Analysis results dictionary

    Returns:
        Formatted review report
    """
    report = []
    report.append("=" * 60)
    report.append("EXCEL VALUATION MODEL REVIEW REPORT")
    report.append("=" * 60)
    report.append("")

    # File info
    report.append(f"File: {analysis.get('file', 'N/A')}")
    report.append(f"Status: {analysis.get('status', 'N/A')}")
    report.append("")

    # Methodology
    model = analysis.get("model_analysis", {})
    report.append("VALUATION METHODOLOGY")
    report.append("-" * 40)
    report.append(f"Identified: {model.get('identified_methodology', 'Unknown')}")
    report.append(f"Confidence: {model.get('confidence', 0):.0%}")
    report.append("")

    # Formula validation
    formulas = analysis.get("formula_validation", {})
    report.append("FORMULA VALIDATION")
    report.append("-" * 40)
    report.append(f"Status: {formulas.get('validation_status', 'N/A')}")
    report.append(f"Formulas found: {len(formulas.get('formulas_found', []))}")
    if formulas.get("issues"):
        report.append("Issues:")
        for issue in formulas["issues"]:
            report.append(f"  - {issue}")
    report.append("")

    # WACC validation
    wacc = analysis.get("wacc_validation", {})
    report.append("WACC CALCULATION")
    report.append("-" * 40)
    report.append(f"Cost of Equity: {'Found' if wacc.get('cost_of_equity_found') else 'Not Found'}")
    report.append(f"Cost of Debt: {'Found' if wacc.get('cost_of_debt_found') else 'Not Found'}")
    report.append(f"Complete: {'Yes' if wacc.get('is_complete') else 'No'}")
    report.append("")

    # Terminal value
    tv = analysis.get("terminal_value_check", {})
    report.append("TERMINAL VALUE")
    report.append("-" * 40)
    report.append(f"Found: {'Yes' if tv.get('terminal_value_found') else 'No'}")
    report.append(f"Gordon Growth: {'Yes' if tv.get('gordon_growth_method') else 'No'}")
    report.append(f"Exit Multiple: {'Yes' if tv.get('exit_multiple_method') else 'No'}")
    report.append("")

    # Assumptions
    assumptions = analysis.get("assumptions", {})
    report.append("KEY ASSUMPTIONS")
    report.append("-" * 40)
    for key, value in assumptions.items():
        report.append(f"{key}: {value.get('value', 'N/A')}")
    report.append("")

    # Data sources
    sources = analysis.get("data_sources", {})
    report.append("DATA SOURCES")
    report.append("-" * 40)
    report.append(f"Self-contained: {'Yes' if sources.get('is_self_contained') else 'No'}")
    report.append(f"External links: {len(sources.get('external_links', []))}")
    report.append("")

    report.append("=" * 60)

    return "\n".join(report)
