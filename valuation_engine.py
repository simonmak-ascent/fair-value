"""
Main valuation engine - entry point for all valuation operations
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.fetch_data import (
    get_stock_price, get_company_info, get_key_metrics,
    get_income_statement, get_balance_sheet, get_cash_flow,
    get_historical_prices, get_volatility
)

# Import valuation modules (to be implemented)
# from src.valuation import dcf, nav, multiples
# from src.cost_of_capital import wacc, fama_french, kmv
# from src.derivatives import options, swaps, greeks
# from src.credit_risk import ecl
# from src.report_review import excel_analyzer, pdf_analyzer


def run_valuation(ticker: str, method: str, params: Dict = None) -> Dict:
    """
    Main entry point for running valuations
    
    Args:
        ticker: Stock ticker (e.g., '9988.HK', 'AAPL')
        method: Valuation method ('dcf', 'nav', 'cca')
        params: Additional parameters
    
    Returns:
        Dictionary with valuation results
    """
    params = params or {}
    
    if method.lower() == 'dcf':
        return run_dcf(ticker, params)
    elif method.lower() == 'nav':
        return run_nav(ticker, params)
    elif method.lower() == 'cca':
        return run_cca(ticker, params)
    else:
        return {'error': f'Unknown method: {method}'}


def run_dcf(ticker: str, params: Dict) -> Dict:
    """
    Run DCF valuation
    
    Args:
        ticker: Stock ticker
        params: DCF parameters
    
    Returns:
        DCF valuation results
    """
    # Get company data
    info = get_company_info(ticker)
    metrics = get_key_metrics(ticker)
    price = get_stock_price(ticker)
    
    # Placeholder for full DCF implementation
    result = {
        'ticker': ticker,
        'method': 'DCF',
        'company_name': info.get('name', ''),
        'current_price': price,
        'status': 'pending_implementation',
        'message': 'DCF with FF5 and KMV to be implemented'
    }
    
    return result


def run_nav(ticker: str, params: Dict) -> Dict:
    """
    Run NAV valuation
    
    Args:
        ticker: Stock ticker
        params: NAV parameters
    
    Returns:
        NAV valuation results
    """
    info = get_company_info(ticker)
    price = get_stock_price(ticker)
    
    result = {
        'ticker': ticker,
        'method': 'NAV',
        'company_name': info.get('name', ''),
        'current_price': price,
        'status': 'pending_implementation',
        'message': 'NAV valuation to be implemented'
    }
    
    return result


def run_cca(ticker: str, params: Dict) -> Dict:
    """
    Run Comparable Company Analysis
    
    Args:
        ticker: Stock ticker
        params: CCA parameters
    
    Returns:
        CCA valuation results
    """
    info = get_company_info(ticker)
    price = get_stock_price(ticker)
    
    result = {
        'ticker': ticker,
        'method': 'CCA',
        'company_name': info.get('name', ''),
        'current_price': price,
        'status': 'pending_implementation',
        'message': 'Comparable Company Analysis to be implemented'
    }
    
    return result


def review_report(file_path: str) -> Dict:
    """
    Main entry point for reviewing valuation reports
    
    Args:
        file_path: Path to the report file
    
    Returns:
        Review results
    """
    from src.report_review import excel_analyzer, pdf_analyzer
    
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    if suffix in ['.xlsx', '.xls']:
        return review_excel(file_path)
    elif suffix == '.pdf':
        return review_pdf(file_path)
    elif suffix in ['.docx', '.doc']:
        return review_word(file_path)
    elif suffix in ['.png', '.jpg', '.jpeg']:
        return review_image(file_path)
    else:
        return {'error': f'Unsupported file type: {suffix}'}


def review_excel(file_path: str) -> Dict:
    """
    Review Excel valuation model
    
    Args:
        file_path: Path to Excel file
    
    Returns:
        Review results
    """
    # Import and run analyzer
    try:
        from src.report_review import excel_analyzer
        return excel_analyzer.analyze_excel_model(file_path)
    except ImportError:
        return {
            'file': file_path,
            'status': 'pending_implementation',
            'message': 'Excel analyzer to be implemented'
        }


def review_pdf(file_path: str) -> Dict:
    """
    Review PDF valuation report
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        Review results
    """
    try:
        from src.report_review import pdf_analyzer
        return pdf_analyzer.analyze_pdf_report(file_path)
    except ImportError:
        return {
            'file': file_path,
            'status': 'pending_implementation',
            'message': 'PDF analyzer to be implemented'
        }


def review_word(file_path: str) -> Dict:
    """
    Review Word valuation report
    
    Args:
        file_path: Path to Word file
    
    Returns:
        Review results
    """
    try:
        from src.report_review import word_analyzer
        return word_analyzer.analyze_word_report(file_path)
    except ImportError:
        return {
            'file': file_path,
            'status': 'pending_implementation',
            'message': 'Word analyzer to be implemented'
        }


def review_image(file_path: str) -> Dict:
    """
    Review image (scanned document)
    
    Args:
        file_path: Path to image file
    
    Returns:
        Review results
    """
    try:
        from src.report_review import image_analyzer
        return image_analyzer.extract_valuation_data(file_path)
    except ImportError:
        return {
            'file': file_path,
            'status': 'pending_implementation',
            'message': 'Image analyzer to be implemented'
        }


def scan_directory(directory: str = ".") -> List[Dict]:
    """
    Scan directory for valuation files
    
    Args:
        directory: Directory path to scan
    
    Returns:
        List of found valuation files
    """
    from src.constants import SUPPORTED_FILE_TYPES
    
    path = Path(directory)
    found_files = []
    
    # Patterns to search
    patterns = []
    for extensions in SUPPORTED_FILE_TYPES.values():
        patterns.extend(extensions)
    
    for pattern in patterns:
        found_files.extend(path.glob(f"**/*{pattern}"))
    
    results = []
    for f in found_files:
        results.append({
            'path': str(f),
            'type': f.suffix.lower(),
            'size': f.stat().st_size
        })
    
    return results


def get_valuation_summary(ticker: str) -> Dict:
    """
    Get comprehensive valuation summary for a ticker
    
    Args:
        ticker: Stock ticker
    
    Returns:
        Summary dictionary
    """
    info = get_company_info(ticker)
    metrics = get_key_metrics(ticker)
    price = get_stock_price(ticker)
    volatility = get_volatility(ticker)
    
    return {
        'ticker': ticker,
        'company': info,
        'metrics': metrics,
        'price': price,
        'volatility': volatility,
        'data_sources': 'Yahoo Finance (yfinance)'
    }


# CLI entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Financial Valuation Engine')
    parser.add_argument('--ticker', help='Stock ticker')
    parser.add_argument('--method', default='dcf', help='Valuation method')
    parser.add_argument('--review', help='Review file path')
    parser.add_argument('--scan', help='Scan directory')
    
    args = parser.parse_args()
    
    if args.review:
        result = review_report(args.review)
        print(result)
    elif args.scan:
        files = scan_directory(args.scan)
        for f in files:
            print(f)
    elif args.ticker:
        result = run_valuation(args.ticker, args.method)
        print(result)
    else:
        parser.print_help()
