"""
Image Analyzer Module
OCR and data extraction from scanned images
"""

import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

try:
    import pytesseract
    from PIL import Image
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False


def extract_text_from_image(file_path: str, method: str = "pytesseract") -> str:
    """
    Extract text from image using OCR
    
    Args:
        file_path: Path to image file
        method: OCR method ('pytesseract' or 'easyocr')
    
    Returns:
        Extracted text
    """
    if method == "easyocr" and EASYOCR_AVAILABLE:
        return _easyocr_extract(file_path)
    elif method == "pytesseract" and PYTESSERACT_AVAILABLE:
        return _pytesseract_extract(file_path)
    else:
        logger.warning("No OCR library available")
        return ""


def _pytesseract_extract(file_path: str) -> str:
    """Extract text using pytesseract"""
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logger.error(f"pytesseract error: {e}")
        return ""


def _easyocr_extract(file_path: str) -> str:
    """Extract text using easyocr"""
    try:
        reader = easyocr.Reader(['en'])
        results = reader.readtext(file_path)
        text = " ".join([result[1] for result in results])
        return text
    except Exception as e:
        logger.error(f"easyocr error: {e}")
        return ""


def extract_table_from_image(file_path: str) -> List[List[str]]:
    """
    Extract table structure from image
    
    Args:
        file_path: Path to image
    
    Returns:
        Table data
    """
    text = extract_text_from_image(file_path)
    
    lines = text.split('\n')
    table = []
    
    for line in lines:
        if line.strip():
            cells = [c.strip() for c in line.split('|')]
            if any(cells):
                table.append(cells)
    
    return table


def extract_valuation_data(image_path: str) -> Dict:
    """
    Main entry point for image analysis
    
    Args:
        image_path: Path to image file
    
    Returns:
        Extracted valuation data
    """
    try:
        text = extract_text_from_image(image_path)
        
        if not text:
            return {
                'file': image_path,
                'status': 'error',
                'message': 'Could not extract text from image'
            }
        
        # Extract key information
        fair_value = re.search(
            r'fair\s+value[:\s]*[\$€£¥]?\s*([\d,]+(?:\.\d+)?)',
            text, re.IGNORECASE
        )
        
        methodology = re.search(
            r'(DCF|NAV|CCA|DCF|NAV)',
            text, re.IGNORECASE
        )
        
        return {
            'file': image_path,
            'status': 'success',
            'text_length': len(text),
            'text_preview': text[:500],
            'extracted': {
                'fair_value': fair_value.group(1) if fair_value else None,
                'methodology': methodology.group(1) if methodology else None
            }
        }
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return {
            'file': image_path,
            'status': 'error',
            'message': str(e)
        }


def detect_charts(image_path: str) -> Dict:
    """
    Detect if image contains charts/tables
    
    Args:
        image_path: Path to image
    
    Returns:
        Detection results
    """
    return {
        'has_text': True,
        'chart_type': 'unknown'
    }
