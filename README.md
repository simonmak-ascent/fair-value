# Financial Valuation Skills

Professional financial valuation system for OpenCode with IFRS/IVS compliance.

## Overview

This project provides comprehensive financial valuation capabilities including:
- DCF, NAV, and CCA valuations
- Fama-French 5-Factor cost of equity
- KMV credit risk model
- Derivatives pricing (Options, Swaps, CB)
- Excel model review and validation
- PDF/Word/Image document analysis

## Installation

```bash
cd /mnt/c/git_repo/valuation_skills
pip install -r requirements.txt
```

## Quick Start

```python
from valuation_engine import run_valuation, review_report, scan_directory

# Run DCF valuation
result = run_valuation('9988.HK', 'dcf')

# Review Excel model
review = review_report('/path/to/model.xlsx')

# Scan for valuation files
files = scan_directory('/path/to/reports/')
```

## Module Structure

```
src/
├── constants.py           # Standards references
├── fetch_data.py          # Data fetching (yfinance)
├── valuation/             # DCF, NAV, CCA
├── cost_of_capital/       # WACC, FF5, KMV
├── credit_risk/           # ECL calculations
├── derivatives/            # Options, Swaps, CB
├── report_review/          # Excel, PDF, Word, Image analysis
└── output/                # Report formatting
```

## Requirements

- Python 3.8+
- yfinance
- pandas, numpy, scipy
- QuantLib-Python
- openpyxl
- pdfplumber
- python-docx

## Documentation

See IMPLEMENTATION_PLAN.md for detailed specifications.

## Standards Compliance

- IVS 2025
- IFRS 13 (Fair Value Measurement)
- IAS 36 (Impairment)
- HKFRS 9 (ECL)

## License

Proprietary & Confidential