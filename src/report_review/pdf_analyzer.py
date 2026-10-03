"""
PDF Report Analyzer Module
Extract and review PDF valuation reports
"""

import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


def extract_full_text(file_path: str) -> str:
    """
    Extract all text from PDF
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        Full text content
    """
    if not PYPDF2_AVAILABLE:
        return ""
    
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return ""


def extract_tables(file_path: str) -> List[List[List[str]]]:
    """
    Extract tables from PDF
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        List of tables (each table is list of rows)
    """
    if not PDFPLUMBER_AVAILABLE:
        return []
    
    try:
        tables = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                tables.extend(page_tables)
        return tables
    except Exception as e:
        logger.error(f"Error extracting tables: {e}")
        return []


def extract_fair_value(text: str) -> Dict:
    """
    Extract fair value from text
    
    Args:
        text: PDF text content
    
    Returns:
        Fair value information
    """
    patterns = [
        r'fair\s+value[:\s]+[\$€£¥]?\s*([\d,]+(?:\.\d+)?)',
        r'valuation[:\s]+[\$€£¥]?\s*([\d,]+(?:\.\d+)?)',
        r'value\s+per\s+share[:\s]+[\$€£¥]?\s*([\d,]+(?:\.\d+)?)',
        r'estimated\s+value[:\s]+[\$€£¥]?\s*([\d,]+(?:\.\d+)?)',
        r'target\s+price[:\s]+[\$€£¥]?\s*([\d,]+(?:\.\d+)?)'
    ]
    
    results = {}
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            results['matches'] = matches
    
    return results


def extract_methodology(text: str) -> Dict:
    """
    Identify valuation methodology
    
    Args:
        text: PDF text
    
    Returns:
        Methodology information
    """
    methodologies = []
    
    if re.search(r'discounted\s+cash\s+flow|dcf', text, re.IGNORECASE):
        methodologies.append('DCF')
    
    if re.search(r'net\s+asset\s+value|nav', text, re.IGNORECASE):
        methodologies.append('NAV')
    
    if re.search(r'comparable|multiples|peer', text, re.IGNORECASE):
        methodologies.append('CCA')
    
    if re.search(r'precedent\s+transaction', text, re.IGNORECASE):
        methodologies.append('PTA')
    
    if re.search(r'residual\s+income|divergence', text, re.IGNORECASE):
        methodologies.append('RI')
    
    return {
        'methodology': methodologies[0] if methodologies else 'Unknown',
        'all_mentioned': methodologies
    }


def extract_assumptions(text: str) -> Dict:
    """
    Extract key assumptions
    
    Args:
        text: PDF text
    
    Returns:
        Assumptions dictionary
    """
    assumptions = {}
    
    # Growth rate
    growth = re.search(r'growth\s+rate[:\s]+(\d+(?:\.\d+)?)\s*%?', text, re.IGNORECASE)
    if growth:
        assumptions['growth_rate'] = growth.group(1)
    
    # WACC
    wacc = re.search(r'wacc[:\s]+(\d+(?:\.\d+)?)\s*%?', text, re.IGNORECASE)
    if wacc:
        assumptions['wacc'] = wacc.group(1)
    
    # Terminal growth
    terminal = re.search(r'terminal\s+growth[:\s]+(\d+(?:\.\d+)?)\s*%?', text, re.IGNORECASE)
    if terminal:
        assumptions['terminal_growth'] = terminal.group(1)
    
    # Discount rate
    discount = re.search(r'discount\s+rate[:\s]+(\d+(?:\.\d+)?)\s*%?', text, re.IGNORECASE)
    if discount:
        assumptions['discount_rate'] = discount.group(1)
    
    return assumptions


def extract_standards_compliance(text: str) -> Dict:
    """
    Check for standards compliance
    
    Args:
        text: PDF text
    
    Returns:
        Standards compliance information
    """
    standards = []
    
    if re.search(r'IVS\s*2025|international\s+valuation\s+standard', text, re.IGNORECASE):
        standards.append('IVS 2025')
    
    if re.search(r'IFRS\s*13|fair\s+value\s+measurement', text, re.IGNORECASE):
        standards.append('IFRS 13')
    
    if re.search(r'IAS\s*36|impairment', text, re.IGNORECASE):
        standards.append('IAS 36')
    
    if re.search(r'HKFRS\s*9|expected\s+credit\s+loss', text, re.IGNORECASE):
        standards.append('HKFRS 9')
    
    return {
        'standards': standards,
        'is_compliant': len(standards) > 0
    }


def verify_valuation_conclusion(text: str) -> Dict:
    """
    Verify that conclusion matches calculations
    
    Args:
        text: PDF text
    
    Returns:
        Verification results
    """
    return {
        'has_conclusion': bool(re.search(r'conclusion|summary|result', text, re.IGNORECASE)),
        'has_disclaimer': bool(re.search(r'disclaimer|important|note', text, re.IGNORECASE))
    }


def analyze_pdf_report(file_path: str) -> Dict:
    """
    Main entry point for PDF analysis
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        Comprehensive analysis
    """
    try:
        text = extract_full_text(file_path)
        
        if not text:
            return {
                'file': file_path,
                'status': 'error',
                'message': 'Could not extract text from PDF'
            }
        
        return {
            'file': file_path,
            'status': 'success',
            'text_length': len(text),
            'methodology': extract_methodology(text),
            'assumptions': extract_assumptions(text),
            'fair_value': extract_fair_value(text),
            'standards': extract_standards_compliance(text),
            'conclusion': verify_valuation_conclusion(text)
        }
    except Exception as e:
        logger.error(f"Error analyzing PDF: {e}")
        return {
            'file': file_path,
            'status': 'error',
            'message': str(e)
        }
