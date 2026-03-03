# Financial Valuation Skills - Implementation Plan

**Working Directory:** `/mnt/c/git_repo/valuation_skills/`
**Output Directory:** `~/docgen_output/`
**Created:** 2026-03-04

---

## 1. Project Overview

### 1.1 Purpose

Build a comprehensive financial valuation system for OpenCode that:
- Performs professional valuations according to IAS/IFRS and IVS standards
- Includes advanced cost of capital models (Fama-French 5-Factor, KMV)
- Prices derivatives (options, swaps, convertible bonds, futures)
- Reviews and validates existing valuation reports (Excel, PDF, Word, Image)
- Generates bilingual (English/Chinese) valuation reports

### 1.2 Differentiators from Existing Skills

| Feature | Existing Skills | This Implementation |
|---------|-----------------|---------------------|
| Standards | None | IVS 2025, IFRS 13, IAS 36, HKFRS 9 |
| Cost of Equity | Simple CAPM | Fama-French 5-Factor |
| Cost of Debt | Basic | KMV Structural Model |
| Derivatives | None | Options, Swaps, CB, Futures |
| Excel Review | None | Full formula & assumption validation |
| Report Review | None | PDF, Word, Image OCR |

---

## 2. File Structure

```
/mnt/c/git_repo/valuation_skills/
├── requirements.txt                 # Python dependencies
├── SKILL.md                       # Skill documentation
├── valuation_engine.py            # Main entry point
├── README.md                      # Usage instructions
├── IMPLEMENTATION_PLAN.md         # This file
│
├── src/                          # Source code
│   ├── __init__.py
│   ├── fetch_data.py             # Data fetching (yfinance)
│   ├── constants.py              # Standards references
│   │
│   ├── valuation/                # Valuation modules
│   │   ├── __init__.py
│   │   ├── dcf.py               # DCF valuation
│   │   ├── nav.py               # NAV valuation
│   │   ├── multiples.py          # CCA multiples
│   │   └── sensitivity.py        # Sensitivity analysis
│   │
│   ├── cost_of_capital/          # Cost of capital
│   │   ├── __init__.py
│   │   ├── wacc.py              # WACC calculation
│   │   ├── fama_french.py       # FF5 for cost of equity
│   │   └── kmv.py               # KMV for cost of debt
│   │
│   ├── credit_risk/             # Credit risk
│   │   ├── __init__.py
│   │   ├── ecl.py               # HKFRS 9 ECL
│   │   └── pd_models.py         # PD estimation
│   │
│   ├── derivatives/              # Derivatives (via QuantLib)
│   │   ├── __init__.py
│   │   ├── options.py           # Options pricing
│   │   ├── swaps.py             # Swap valuation
│   │   ├── convertible_bonds.py # Convertible bonds
│   │   ├── futures.py           # Futures pricing
│   │   └── greeks.py           # Greeks calculation
│   │
│   ├── report_review/            # Valuation report review
│   │   ├── __init__.py
│   │   ├── excel_analyzer.py    # Excel model review
│   │   ├── pdf_analyzer.py      # PDF document review
│   │   ├── word_analyzer.py     # Word document review
│   │   └── image_analyzer.py    # Image OCR review
│   │
│   └── output/                   # Output formatting
│       ├── __init__.py
│       ├── report_formatter.py  # Report formatting
│       └── chart_data.py        # Chart data for docgen
│
├── templates/                    # Report templates
│   └── valuation_report/
│       ├── en_template.md
│       └── cn_template.md
│
├── data/                         # Cache directory
│   └── .gitkeep
│
└── output/                       # Generated reports
    └── .gitkeep
```

---

## 3. Dependencies

### 3.1 requirements.txt

```text
# Data fetching
yfinance>=0.2.0
pandas-datareader>=0.10.0

# Core computation
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
statsmodels>=0.14.0
scikit-learn>=1.3.0

# Derivatives pricing
QuantLib-Python>=1.32

# Excel analysis
openpyxl>=3.1.0
xlrd>=2.0.0

# PDF analysis
pypdf2>=3.0.0
pdfplumber>=0.10.0

# Word analysis
python-docx>=1.1.0

# Image/OCR analysis
pytesseract>=0.3.10
Pillow>=10.0.0
easyocr>=1.7.0
```

### 3.2 Installation Command

```bash
cd /mnt/c/git_repo/valuation_skills
pip install -r requirements.txt
```

---

## 4. Module Specifications

### 4.1 src/constants.py

**Purpose:** Store IVS/IFRS standards references and constants

**Content:**
```python
IVS_2025 = {
    "IVS_100": "General Concepts",
    "IVS_200": "Assets",
    "IVS_210": "Intangible Assets",
    "IVS_300": "Business and Business Interests",
    "IVS_400": "Financial Instruments"
}

IFRS_STANDARDS = {
    "IFRS_13": "Fair Value Measurement",
    "IAS_36": "Impairment of Assets",
    "IAS_38": "Intangible Assets",
    "HKFRS_9": "Financial Instruments",
    "IFRS_9": "Financial Instruments"
}

FAIR_VALUE_HIERARCHY = {
    "Level_1": "Quoted prices in active markets",
    "Level_2": "Observable inputs other than Level 1",
    "Level_3": "Unobservable inputs"
}

CREDIT_RATINGS = {
    "AAA": 0.001, "AA": 0.005, "A": 0.01,
    "BBB": 0.05, "BB": 0.15, "B": 0.30, "CCC": 0.50
}
```

---

### 4.2 src/fetch_data.py

**Purpose:** Fetch financial data from yfinance

**Functions:**
```python
def get_stock_price(ticker: str, date: str = None) -> float
def get_company_info(ticker: str) -> dict
def get_income_statement(ticker: str, period: str = "annual") -> pd.DataFrame
def get_balance_sheet(ticker: str, period: str = "annual") -> pd.DataFrame
def get_cash_flow(ticker: str, period: str = "annual") -> pd.DataFrame
def get_key_metrics(ticker: str) -> dict
def get_historical_prices(ticker: str, start: str, end: str) -> pd.DataFrame
def get_option_chain(ticker: str) -> dict
def get_financial_ratios(ticker: str) -> dict
```

---

### 4.3 src/cost_of_capital/fama_french.py

**Purpose:** Fama-French 5-Factor Model for cost of equity

**Formula:**
```
R_i - R_f = α + β₁(RMRF) + β₂(SMB) + β₃(HML) + β₄(RMW) + β₅(CMA) + ε
```

**Functions:**
```python
def fetch_ff_factors(start_date: str, end_date: str) -> pd.DataFrame
    # Fetch from Kenneth French data library

def calculate_factor_betas(ticker: str, factors: pd.DataFrame, 
                          start_date: str, end_date: str) -> dict:
    # Regress stock returns against factors
    # Return: {beta_mkt, beta_smb, beta_hml, beta_rmw, beta_cma, alpha}

def cost_of_equity_ff5(risk_free_rate: float, factors: dict, 
                       market_premium: float = None) -> float:
    # Re = Rf + β₁(RMRF) + β₂(SMB) + β₃(HML) + β₄(RMW) + β₅(CMA)
```

**Data Source:** Kenneth French Data Library (free)

---

### 4.4 src/cost_of_capital/kmv.py

**Purpose:** KMV Structural Model for cost of debt and credit risk

**Key Concepts:**
- Distance to Default (DD) = (V_A - D) / (V_A × σ_A)
- Expected Default Frequency (EDF) = N(-DD)
- Cost of Debt = R_f + EDF × Spread

**Functions:**
```python
def estimate_asset_value(equity_value: float, debt_value: float, 
                        risk_free: float, time_to_debt: float) -> float:
    # Use Merton structural model
    # V_A = f(E, D, r, T)

def estimate_asset_volatility(equity_vol: float, equity_value: float,
                              asset_value: float, debt_value: float) -> float:
    # σ_A = σ_E × (E / V_A)

def distance_to_default(asset_value: float, debt_default_point: float,
                       asset_volatility: float) -> float:
    # DD = (V_A - D) / (V_A × σ_A)

def expected_default_frequency(distance_to_default: float) -> float:
    # EDF = N(-DD)
    # Use standard normal CDF

def cost_of_debt_from_kmv(edf: float, risk_free_rate: float,
                          market_spread: float = 0.03) -> float:
    # Rd = Rf + EDF × Spread
```

---

### 4.5 src/cost_of_capital/wacc.py

**Purpose:** Weighted Average Cost of Capital

**Formula:**
```
WACC = (E/V) × Re + (D/V) × Rd × (1 - Tax)
```

**Functions:**
```python
def calculate_wacc(equity_weight: float, debt_weight: float,
                  cost_equity: float, cost_debt: float,
                  tax_rate: float = 0.25) -> float:
    # WACC = (E/V) × Re + (D/V) × Rd × (1-T)

def get_capital_structure(ticker: str) -> dict:
    # Get E/(D+E) and D/(D+E) from balance sheet

def calculate_cost_of_capital_full(ticker: str, tax_rate: float = 0.25) -> dict:
    # Full calculation:
    # 1. Get FF5 cost of equity
    # 2. Get KMV cost of debt
    # 3. Calculate WACC
```

---

### 4.6 src/valuation/dcf.py

**Purpose:** Discounted Cash Flow valuation

**Functions:**
```python
def project_free_cash_flows(revenue_history: list, growth_rate: float,
                            ebitda_margin: float, capex_pct: float,
                            nwc_pct: float, years: int = 5) -> list:
    # Project FCF for n years

def calculate_terminal_value_gordon(final_fcf: float, wacc: float,
                                    perpetual_growth: float) -> float:
    # TV = FCF × (1+g) / (WACC - g)

def calculate_terminal_value_exit(final_fcf: float, exit_multiple: float) -> float:
    # TV = FCF × Exit Multiple

def discount_cash_flows(cash_flows: list, wacc: float) -> float:
    # NPV of projected cash flows

def dcf_valuation(ticker: str, assumptions: dict) -> dict:
    # Full DCF valuation:
    # 1. Get historical financials
    # 2. Calculate WACC (FF5 + KMV)
    # 3. Project FCFs
    # 4. Calculate terminal value
    # 5. Discount to present
    # 6. Derive equity value per share
```

---

### 4.7 src/valuation/nav.py

**Purpose:** Net Asset Value for investment holding companies

**Functions:**
```python
def value_listed_securities(holdings: dict, valuation_date: str) -> float:
    # Market value = Σ(shares × price)

def value_unlisted_assets(assets: dict, valuation_method: str) -> float:
    # Appraisal value or discounted cash flow

def calculate_receivables_ ecl(accounts_receivable: float,
                               aging: dict, pd_by_age: dict) -> float:
    # HKFRS 9 ECL for receivables

def calculate_nav(assets: dict, liabilities: dict, 
                 minority_discount: float = 0.0) -> dict:
    # NAV = (Total Assets - Total Liabilities) × (1 - Discount)
```

---

### 4.8 src/credit_risk/ecl.py

**Purpose:** HKFRS 9 Expected Credit Loss calculation

**Formula:**
```
ECL = EAD × PD × LGD
```

**Functions:**
```python
def calculate_ecL(exposure_at_default: float, 
                 probability_of_default: float,
                 loss_given_default: float) -> float:
    # Simple ECL calculation

def calculate_forward_looking_ecL(base_ecL: float, 
                                 gdp_factor: float,
                                 inflation_factor: float,
                                 industry_factor: float) -> float:
    # Forward-looking adjustment per HKFRS 9

def pd_12m_and_lifetime(exposure: float, credit_rating: str,
                         is_credit_impaired: bool) -> dict:
    # 12-month vs lifetime PD
```

---

### 4.9 src/derivatives/options.py

**Purpose:** Options pricing using QuantLib

**Functions:**
```python
def black_scholes_price(spot: float, strike: float, 
                        maturity: float, risk_free: float,
                        volatility: float, option_type: str) -> float:
    # Black-Scholes-Merton formula

def binomial_tree_price(spot: float, strike: float,
                       maturity: float, risk_free: float,
                       volatility: float, steps: int,
                       option_type: str) -> float:
    # Cox-Ross-Rubinstein binomial tree

def monte_carlo_option(spot: float, strike: float,
                       maturity: float, risk_free: float,
                       volatility: float, simulations: int,
                       option_type: str) -> float:
    # Monte Carlo simulation

def garman_kohlhagen(spot: float, strike: float,
                     maturity: float, domestic_rf: float,
                     foreign_rf: float, volatility: float,
                     option_type: str) -> float:
    # For FX options
```

---

### 4.10 src/derivatives/swaps.py

**Purpose:** Interest rate and currency swap valuation

**Functions:**
```python
def interest_rate_swap_value(notional: float, fixed_rate: float,
                             floating_curve: list, tenor_years: int,
                             discount_curve: list) -> float:
    # IRS valuation

def currency_swap_value(notional_domestic: float, notional_foreign: float,
                        domestic_rate: float, foreign_rate: float,
                        fx_spot: float, tenor_years: int) -> float:
    # Cross-currency swap

def swap_rate_from_curve(tenor: int, zero_rates: list) -> float:
    # Derive swap rate from zero curve
```

---

### 4.11 src/derivatives/convertible_bonds.py

**Purpose:** Convertible bond valuation

**Functions:**
```python
def straight_bond_value(face: float, coupon_rate: float,
                       maturity: float, yield_to_maturity: float) -> float:
    # Value as plain bond

def conversion_value(stock_price: float, conversion_ratio: float,
                   face_value: float) -> float:
    # Value if converted to equity

def convertible_bond_price(straight_value: float, option_value: float,
                          discount: float = 0.0) -> float:
    # CB = Straight Bond + Call Option - Discount

def binomial_convertible(spot: float, strike: float,
                        maturity: float, coupon: float,
                        volatility: float, risk_free: float,
                        conversion_ratio: float) -> float:
    # Binomial tree for convertible
```

---

### 4.12 src/derivatives/futures.py

**Purpose:** Futures and forward pricing

**Functions:**
```python
def futures_price(spot: float, cost_of_carry: float,
                 time_to_expiry: float) -> float:
    # F = S × e^(c × T)

def forward_price(spot: float, risk_free: float,
                 dividend_yield: float, time: float) -> float:
    # F = S × e^((r-d) × T)
```

---

### 4.13 src/derivatives/greeks.py

**Purpose:** Option Greeks calculation

**Functions:**
```python
def delta(spot: float, strike: float, maturity: float,
          risk_free: float, volatility: float, option_type: str) -> float

def gamma(spot: float, strike: float, maturity: float,
          risk_free: float, volatility: float) -> float

def theta(spot: float, strike: float, maturity: float,
          risk_free: float, volatility: float, option_type: str) -> float

def vega(spot: float, strike: float, maturity: float,
         risk_free: float, volatility: float) -> float

def rho(spot: float, strike: float, maturity: float,
        risk_free: float, volatility: float) -> float
```

---

### 4.14 src/report_review/excel_analyzer.py

**Purpose:** Comprehensive Excel valuation model review

**Review Categories:**

| Category | Checks |
|----------|--------|
| Model Use | Correct methodology selection (DCF/NAV/CCA), appropriate for company type |
| Formula Use | Syntax, cell references, function usage, circular reference detection |
| Calculation Accuracy | Numerical accuracy, rounding, link integrity, precision |
| Data Source | Provenance, refresh capability, external links, API integration |
| Assumption Accuracy | Reasonable ranges, sensitivity impact, market consistency |

**Functions:**
```python
def analyze_excel_model(file_path: str) -> dict:
    # Main entry point - returns comprehensive review

def identify_valuation_method(sheet_names: list, cells: dict) -> str:
    # Detect DCF, NAV, CCA, etc.

def validate_dcf_formulas(workbook) -> list:
    # Check: NPV, IRR, discount factors, terminal value
    # Return: list of issues

def validate_wacc_calculation(sheet) -> dict:
    # Check: Cost of equity, cost of debt, weights
    # Return: {is_valid, issues, calculated_wacc}

def validate_terminal_value(sheet) -> dict:
    # Check: Gordon growth vs exit multiple formula
    # Return: {method, formula_correct, issues}

def validate_cash_flow_projections(sheet) -> dict:
    # Check: Revenue growth, EBITDA, capex, working capital
    # Return: {assumptions, issues}

def validate_sensitivity_table(sheet) -> dict:
    # Check: Proper data table structure, formulas linked
    # Return: {is_valid, issues}

def check_data_sources(workbook) -> dict:
    # Check: External links, data provenance
    # Return: {sources, issues, refreshable}

def verify_assumptions(sheet, ticker: str = None) -> dict:
    # Check: Assumption reasonableness vs market
    # Return: {assumptions, comparison, issues}

def compare_with_market_data(assumptions: dict, ticker: str) -> dict:
    # Compare key assumptions with yfinance data
    # Return: {deviations, recommendations}

def generate_review_report(analysis: dict) -> str:
    # Generate human-readable review report

def export_findings_to_excel(analysis: dict, output_path: str) -> str:
    # Export review findings to Excel
```

**Specific Formula Checks:**

| Check | Description | Detection |
|-------|-------------|-----------|
| NPV Formula | `=NPV(rate, values)` | Cell formula analysis |
| Discount Factor | `=1/(1+rate)^period` | Formula validation |
| Terminal Value (Gordon) | `=FCF*(1+g)/(WACC-g)` | Pattern matching |
| Terminal Value (Exit) | `=FCF*Multiple` | Pattern matching |
| WACC | Weighted average formula | Calculation verification |
| Beta Calculation | Regression vs manual | Value range check |

---

### 4.15 src/report_review/pdf_analyzer.py

**Purpose:** Extract and review PDF valuation reports

**Functions:**
```python
def extract_full_text(file_path: str) -> str:
    # Extract all text using pypdf2

def extract_tables(file_path: str) -> list:
    # Extract tables using pdfplumber

def extract_fair_value(text: str) -> dict:
    # Extract: Fair Value, Value per Share, Currency
    # Return: {fair_value, currency, context}

def extract_methodology(text: str) -> dict:
    # Detect: DCF, NAV, CCA, Asset-based
    # Return: {methodology, details}

def extract_assumptions(text: str) -> dict:
    # Extract: Growth rate, WACC, Terminal growth, etc.
    # Return: {assumptions}

def extract_standards_compliance(text: str) -> dict:
    # Check: IVS, IFRS 13, IAS 36 mention
    # Return: {standards, compliance_level}

def verify_valuation_conclusion(text: str) -> dict:
    # Verify: Conclusion matches calculations
    # Return: {is_consistent, deviations}

def generate_review_report(analysis: dict) -> str:
    # Generate review report
```

---

### 4.16 src/report_review/word_analyzer.py

**Purpose:** Review Word-format valuation reports

**Functions:**
```python
def extract_text(file_path: str) -> str:
    # Extract using python-docx

def extract_tables(file_path: str) -> list:
    # Extract tables

def extract_valuation_conclusion(text: str) -> dict:
    # Extract fair value and methodology

def check_ivs_compliance(text: str) -> dict:
    # Check standards mentions
```

---

### 4.17 src/report_review/image_analyzer.py

**Purpose:** OCR and review scanned documents

**Functions:**
```python
def extract_text_from_image(file_path: str) -> str:
    # Use easyocr or pytesseract

def extract_table_from_image(file_path: str) -> list:
    # Detect and extract table structures

def extract_valuation_data(image_path: str) -> dict:
    # Main entry for image review
```

---

### 4.18 src/output/report_formatter.py

**Purpose:** Format valuation results for docgen output

**Functions:**
```python
def format_for_pdf(valuation_result: dict) -> dict:
    # Prepare sections for create_pdf

def format_for_excel(valuation_result: dict) -> dict:
    # Prepare sheets for create_excel

def create_kpi_cards(valuation_result: dict) -> dict:
    # Create KPI metrics for charts
```

---

## 5. Main Entry Point

### 5.1 valuation_engine.py

```python
def run_valuation(ticker: str, method: str, params: dict) -> dict:
    """
    Main entry point for valuation
    """
    if method == "dcf":
        return dcf.dcf_valuation(ticker, params)
    elif method == "nav":
        return nav.calculate_nav(ticker, params)
    # ...

def review_report(file_path: str) -> dict:
    """
    Main entry point for report review
    """
    if file_path.endswith(('.xlsx', '.xls')):
        return excel_analyzer.analyze_excel_model(file_path)
    elif file_path.endswith('.pdf'):
        return pdf_analyzer.analyze_pdf_report(file_path)
    # ...

def scan_directory(directory: str = ".") -> list:
    """
    Auto-scan directory for valuation files
    """
    patterns = ['*.xlsx', '*.xls', '*.pdf', '*.docx', '*.png', '*.jpg']
    # ...
```

---

## 6. SKILL.md Structure

```yaml
---
name: financial-valuation
version: "1.0.0"
description: Professional financial valuation according to IFRS/IVS standards with comprehensive report review
---

# Financial Valuation Skill

## Trigger Conditions

Use when user requests:
- "Value [company] using DCF/NAV/CCA"
- "Review valuation report at [file]"
- "Validate Excel model at [path]"
- "Calculate fair value per IFRS 13"
- "Extract fair value from [PDF]"
- "Check if assumptions are reasonable"
- "Price options/swaps for [instrument]"

## Capabilities

### 1. Valuation
- DCF with Fama-French 5-Factor cost of equity
- KMV cost of debt
- NAV for holding companies
- CCA with market multiples
- Sensitivity analysis

### 2. Derivatives (QuantLib)
- Options (European, American, FX)
- Interest rate swaps
- Currency swaps
- Convertible bonds
- Futures/forwards

### 3. Credit Risk
- HKFRS 9 ECL calculation
- PD/LGD estimation
- Forward-looking adjustments

### 4. Report Review

#### Excel Review:
- Model methodology validation
- Formula correctness
- Calculation accuracy
- Data source verification
- Assumption reasonableness

#### Document Review:
- PDF text/table extraction
- Fair value extraction
- Standards compliance check

## Supported Markets

| Market | Code Format | Example |
|--------|-------------|---------|
| US | SYMBOL | AAPL, MSFT |
| HK | CODE.HK | 0700.HK, 9988.HK |
| CN | CODE.SH/SZ | 600519.SH |
| JP | CODE.T | 7203.T |

## Usage Examples

```bash
# Run DCF valuation
python valuation_engine.py --ticker 9988.HK --method dcf

# Review Excel model
python valuation_engine.py --review /path/to/model.xlsx

# Scan directory
python valuation_engine.py --scan /path/to/valuation_reports/
```

## Output

- PDF report → ~/docgen_output/
- Excel model → ~/docgen_output/
- Review findings → ~/docgen_output/
```

---

## 7. Implementation Phases

### Phase 1: Foundation (Priority 0)
| File | Lines | Purpose |
|------|-------|---------|
| requirements.txt | 10 | Dependencies |
| src/constants.py | 60 | Standards references |
| src/fetch_data.py | 80 | Data fetching |

**Deliverable:** Basic data retrieval working

### Phase 2: Cost of Capital (Priority 1)
| File | Lines | Purpose |
|------|-------|---------|
| src/cost_of_capital/wacc.py | 60 | WACC calculation |
| src/cost_of_capital/fama_french.py | 120 | FF5 model |
| src/cost_of_capital/kmv.py | 150 | KMV model |

**Deliverable:** FF5 and KMV calculations working

### Phase 3: Core Valuation (Priority 1)
| File | Lines | Purpose |
|------|-------|---------|
| src/valuation/dcf.py | 100 | DCF valuation |
| src/valuation/nav.py | 80 | NAV valuation |
| src/credit_risk/ecl.py | 70 | ECL calculation |

**Deliverable:** DCF and NAV valuations working

### Phase 4: Derivatives (Priority 2)
| File | Lines | Purpose |
|------|-------|---------|
| src/derivatives/options.py | 150 | Options pricing |
| src/derivatives/swaps.py | 100 | Swap valuation |
| src/derivatives/convertible_bonds.py | 120 | CB valuation |
| src/derivatives/futures.py | 60 | Futures pricing |
| src/derivatives/greeks.py | 80 | Greeks |

**Deliverable:** Derivatives pricing working

### Phase 5: Report Review - Excel (Priority 2)
| File | Lines | Purpose |
|------|-------|---------|
| src/report_review/excel_analyzer.py | 250 | Excel review |

**Deliverable:** Excel model validation working

### Phase 6: Report Review - Documents (Priority 3)
| File | Lines | Purpose |
|------|-------|---------|
| src/report_review/pdf_analyzer.py | 120 | PDF review |
| src/report_review/word_analyzer.py | 80 | Word review |
| src/report_review/image_analyzer.py | 80 | Image OCR |

**Deliverable:** Document extraction working

### Phase 7: Output & Integration (Priority 3)
| File | Lines | Purpose |
|------|-------|---------|
| src/output/report_formatter.py | 60 | Output formatting |
| valuation_engine.py | 80 | Main entry |
| SKILL.md | 150 | Documentation |

**Deliverable:** Full system integrated

---

## 8. Total Lines Summary

| Phase | Lines |
|-------|-------|
| Phase 1: Foundation | 150 |
| Phase 2: Cost of Capital | 330 |
| Phase 3: Core Valuation | 250 |
| Phase 4: Derivatives | 510 |
| Phase 5: Excel Review | 250 |
| Phase 6: Document Review | 280 |
| Phase 7: Output | 290 |
| **Total** | **~2,060 lines** |

---

## 9. OpenCode Integration

### 9.1 opencode.json Update

Add Yahoo Finance MCP:
```json
"yfinance": {
  "type": "local",
  "command": ["npx", "-y", "yahoo-finance-mcp-server"],
  "enabled": true
}
```

### 9.2 AGENTS.md Addition

```markdown
## Financial Valuation Skills

- Location: /mnt/c/git_repo/valuation_skills/
- Entry: valuation_engine.py
- Auto-detect: .xlsx, .pdf, .docx, .png, .jpg
- Output: ~/docgen_output/

### Commands
- `run_valuation(ticker, method, params)` - Execute valuation
- `review_report(file_path)` - Review valuation document
- `scan_directory(path)` - Auto-scan for valuation files
```

---

## 10. Testing Checklist

### 10.1 Data Fetching
- [ ] yfinance retrieves US stock data
- [ ] yfinance retrieves HK stock data
- [ ] yfinance retrieves China A-share data

### 10.2 Cost of Capital
- [ ] FF5 factor calculation works
- [ ] KMV model calculates PD
- [ ] WACC combines both correctly

### 10.3 Valuation
- [ ] DCF produces reasonable value
- [ ] NAV calculation matches manual
- [ ] Sensitivity table generates

### 10.4 Derivatives
- [ ] Black-Scholes matches QuantLib
- [ ] Swap valuation works
- [ ] Greeks calculate correctly

### 10.5 Report Review
- [ ] Excel formulas detected correctly
- [ ] WACC calculation validated
- [ ] PDF text extraction works
- [ ] Fair value extracted

---

## 11. Error Handling

All functions should include:
- Try-except blocks for data fetching
- Validation of required inputs
- Clear error messages
- Graceful degradation

---

## 12. Performance Considerations

- Cache yfinance data for 24 hours
- Use vectorized numpy operations
- Lazy load QuantLib when needed
- Parallel processing for Monte Carlo

---

## End of Implementation Plan
