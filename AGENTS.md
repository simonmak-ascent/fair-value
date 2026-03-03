# Financial Valuation Skills - Agent Guidelines

## Project Overview

**Location:** `/mnt/c/git_repo/valuation_skills/`
**Entry Point:** `valuation_engine.py`
**Output Directory:** `~/docgen_output/`

Professional financial valuation system for OpenCode with IVS 2025, IFRS 13, IAS 36, and HKFRS 9 compliance. Includes DCF/NAV/CCA valuations, Fama-French 5-Factor cost of equity, KMV credit risk model, derivatives pricing (via QuantLib), and Excel/PDF/Word report review.

---

## Installation

```bash
cd /mnt/c/git_repo/valuation_skills
pip install -r requirements.txt
```

---

## Commands

### Running the Engine

```bash
# Run DCF valuation
python valuation_engine.py --ticker 9988.HK --method dcf

# Review Excel model
python valuation_engine.py --review /path/to/model.xlsx

# Scan directory for valuation files
python valuation_engine.py --scan /path/to/reports/
```

### Testing

This project uses **pytest** for testing. No test configuration exists yet—create tests in a `tests/` directory following these patterns:

```bash
# Install pytest
pip install pytest pytest-cov

# Run all tests
pytest

# Run specific test file
pytest tests/test_wacc.py

# Run single test
pytest tests/test_wacc.py::test_calculate_wacc -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### Linting & Type Checking

```bash
# Install development dependencies
pip install ruff mypy black

# Run ruff linter (fast)
ruff check src/

# Auto-fix linting issues
ruff check src/ --fix

# Run type checker
mypy src/

# Format code with black
black src/
```

---

## Code Style Guidelines

### General Principles

- **Python 3.8+** - Use type hints throughout
- **Follow existing patterns** - Mimic the code in `valuation_engine.py`, `src/fetch_data.py`, and `src/cost_of_capital/wacc.py`
- **Small, focused functions** - Single responsibility principle
- **No magic strings** - Use constants from `src/constants.py`

### Imports

```python
# Standard library first
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

# Third-party (alphabetical)
import numpy as np
import pandas as pd
import yfinance as yf

# Local imports (absolute from src)
from src.fetch_data import get_stock_price, get_company_info
from src.cost_of_capital.wacc import calculate_wacc
from src.constants import IVS_2025, IFRS_STANDARDS
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Functions | snake_case | `calculate_wacc()`, `get_stock_price()` |
| Classes | PascalCase | `ExcelAnalyzer`, `DCFValuation` |
| Constants | SCREAMING_SNAKE_CASE | `IVS_2025`, `FAIR_VALUE_HIERARCHY` |
| Module files | snake_case | `fetch_data.py`, `excel_analyzer.py` |
| Type aliases | PascalCase | `ValuationResult = Dict[str, Any]` |

### Type Hints

Always use type hints for function signatures:

```python
def calculate_wacc(
    equity_weight: float,
    debt_weight: float,
    cost_equity: float,
    cost_debt: float,
    tax_rate: float = 0.25
) -> float:
    """Calculate Weighted Average Cost of Capital.
    
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
    ...
```

### Docstrings

Use Google-style docstrings (as seen in existing code):

```python
def function_name(param: Type) -> ReturnType:
    """Short one-line description.
    
    Longer description if needed.
    
    Args:
        param_name: Description
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When condition X occurs
    """
```

### Error Handling

```python
def get_stock_price(ticker: str) -> float:
    """Get current stock price."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return float(info.get('currentPrice', 0))
    except Exception as e:
        logger.error(f"Error fetching price for {ticker}: {e}")
        return 0.0
```

- Use try-except for external calls (yfinance, file I/O)
- Log errors with `logger.error()`
- Return sensible defaults (empty dict, 0.0, empty DataFrame)
- Include context in error messages

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# At module level
logging.basicConfig(level=logging.INFO)
```

### Financial Calculations

- Use **decimal for percentages** (0.10 = 10%, not 10)
- Include formulas in docstrings
- Validate inputs (e.g., weights sum to 1)
- Handle edge cases (zero division, negative values)

### File Organization

```
src/
├── __init__.py
├── fetch_data.py          # Data fetching functions
├── constants.py          # Standards, ratings, thresholds
├── valuation/
│   ├── __init__.py
│   ├── dcf.py
│   ├── nav.py
│   └── multiples.py
├── cost_of_capital/
│   ├── __init__.py
│   ├── wacc.py
│   ├── fama_french.py
│   └── kmv.py
├── derivatives/
├── credit_risk/
├── report_review/
│   ├── excel_analyzer.py
│   ├── pdf_analyzer.py
│   └── ...
└── output/
```

### Testing Guidelines

- Create `tests/` directory at project root
- Name test files `test_<module>.py`
- Name test functions `test_<function>_<case>()`
- Use pytest fixtures for shared setup
- Test edge cases and error paths

```python
# tests/test_wacc.py
import pytest
from src.cost_of_capital.wacc import calculate_wacc

def test_calculate_wacc_equal_weights():
    result = calculate_wacc(0.5, 0.5, 0.10, 0.05, 0.25)
    assert abs(result - 0.0875) < 0.0001

def test_calculate_wacc_zero_weights():
    result = calculate_wacc(0, 0, 0.10, 0.05, 0.25)
    assert result == 0.0

def test_calculate_wacc_normalizes_weights():
    # 2:1 ratio should normalize to 0.667:0.333
    result = calculate_wacc(2, 1, 0.10, 0.05, 0.25)
    assert abs(result - 0.0875) < 0.0001
```

---

## Standards Compliance

When implementing valuation logic, reference:

| Standard | Purpose |
|----------|---------|
| IVS 2025 | International Valuation Standards |
| IFRS 13 | Fair Value Measurement |
| IAS 36 | Impairment of Assets |
| HKFRS 9 | Expected Credit Loss |

Constants are defined in `src/constants.py`.

---

## Output

Generated reports go to `~/docgen_output/`:
- PDF valuation reports
- Excel models with charts
- Review findings

---

## Key Entry Points

```python
from valuation_engine import (
    run_valuation,      # Run DCF/NAV/CCA
    review_report,      # Review Excel/PDF/Word/Image
    scan_directory,    # Find valuation files
    get_valuation_summary
)
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| yfinance | Stock data |
| pandas, numpy | Data processing |
| scipy, statsmodels | Statistical calculations |
| QuantLib-Python | Derivatives pricing |
| openpyxl | Excel analysis |
| pdfplumber, pypdf2 | PDF extraction |
| python-docx | Word document parsing |
| easyocr, pytesseract | Image OCR |

---

## Notes

- yfinance data may have delays—verify against official sources
- KMV model requires equity volatility
- All valuations are estimates for reference only
- Not investment advice—include disclaimers in outputs
