# Financial Valuation Skill

## Overview

Professional financial valuation system for OpenCode that performs valuations according to IAS/IFRS and IVS standards.

## Trigger Conditions

Use this skill when user requests:

- "Value [company] using DCF/NAV/CCA"
- "Review valuation report at [file]"
- "Validate Excel model at [path]"
- "Calculate fair value per IFRS 13"
- "Extract fair value from [PDF]"
- "Check if assumptions are reasonable"
- "Price options/swaps for [instrument]"
- "Calculate WACC using FF5"
- "Run KMV credit analysis"
- Any valuation, derivatives, or credit risk calculation

## Standards Compliance

### IVS 2025
- IVS 100: General Concepts
- IVS 200: Assets
- IVS 210: Intangible Assets
- IVS 300: Business and Business Interests
- IVS 400: Financial Instruments

### IFRS Standards
- IFRS 13: Fair Value Measurement
- IAS 36: Impairment of Assets
- IAS 38: Intangible Assets
- HKFRS 9: Financial Instruments
- IFRS 9: Financial Instruments

## Capabilities

### 1. Valuation Methods

#### DCF (Discounted Cash Flow)
- Fama-French 5-Factor cost of equity
- KMV cost of debt
- Multi-stage projections
- Gordon growth & exit multiple terminal value

#### NAV (Net Asset Value)
- Listed securities at fair value
- Unlisted assets at appraised value
- Receivables with ECL adjustment
- Minority discount application

#### CCA (Comparable Company Analysis)
- P/E, EV/EBITDA, P/B multiples
- Peer selection criteria
- Median multiple application

#### Sensitivity Analysis
- Two-way sensitivity tables
- Tornado analysis
- Scenario modeling

### 2. Cost of Capital

#### Fama-French 5-Factor Model
- Market factor (RMRF)
- Size factor (SMB)
- Value factor (HML)
- Profitability factor (RMW)
- Investment factor (CMA)

#### KMV Structural Model
- Asset value estimation
- Asset volatility calculation
- Distance to default
- Expected default frequency (EDF)
- Cost of debt derivation

#### WACC Calculation
- Capital structure from balance sheet
- Tax effect on debt
- Sector-specific weights

### 3. Derivatives Pricing (via QuantLib)

#### Options
- Black-Scholes-Merton (European)
- Binomial tree (American)
- Monte Carlo simulation
- Garman-Kohlhagen (FX options)
- Greeks calculation (Delta, Gamma, Theta, Vega, Rho)

#### Swaps
- Interest rate swaps
- Currency swaps
- Basis swaps

#### Convertible Bonds
- Straight bond value
- Conversion value
- Option-adjusted spread

#### Futures
- Forward/futures pricing
- Cost of carry model

### 4. Credit Risk

#### HKFRS 9 ECL
- 12-month and lifetime PD
- Exposure at Default (EAD)
- Loss Given Default (LGD)
- Forward-looking adjustments

#### PD Estimation
- Rating-based PD mapping
- KMV EDF conversion
- Statistical default models

### 5. Report Review

#### Excel Model Review
- Model methodology validation
- Formula correctness (NPV, WACC, Terminal Value)
- Calculation accuracy
- Data source verification
- Assumption reasonableness
- Comparison with market data

#### Document Review
- PDF text/table extraction
- Fair value extraction
- Methodology identification
- Standards compliance check

#### Image Review
- OCR extraction
- Table detection
- Valuation data parsing

## Supported Markets

| Market | Code Format | Example |
|--------|-------------|---------|
| US | SYMBOL | AAPL, MSFT, GOOGL |
| HK | CODE.HK | 0700.HK, 9988.HK |
| CN | CODE.SH/SZ | 600519.SH, 000001.SZ |
| JP | CODE.T | 7203.T, 9432.T |

## Usage Examples

### Valuation

```
User: "Value Alibaba (9988.HK) using DCF with 5-year projection"
System: Run DCF with FF5 cost of equity, KMV cost of debt

User: "Calculate NAV for investment holding company"
System: Value listed securities at market, apply ECL to receivables

User: "Perform CCA for Tencent vs peers"
System: Calculate median multiples from peer group
```

### Report Review

```
User: "Review valuation report at /path/to/model.xlsx"
System: Analyze Excel model, validate formulas, check assumptions

User: "Extract fair value from /path/to/report.pdf"
System: Parse PDF, extract fair value, verify methodology

User: "Validate DCF formulas in valuation.xlsx"
System: Check NPV, WACC, terminal value formulas
```

### Derivatives

```
User: "Price call option on AAPL with strike $150, 1 year maturity"
System: Use Black-Scholes via QuantLib

User: "Value interest rate swap, 10M notional, 5 years"
System: Calculate fixed vs floating leg values
```

## Output

### Generated Files
- PDF valuation report → `~/docgen_output/`
- Excel model → `~/docgen_output/`
- Review findings → `~/docgen_output/`

### Report Sections (IVS Compliant)
1. Scope of engagement
2. Valuation basis and definition of fair value
3. Valuation premise
4. Methodology selection and justification
5. Data quality and sources
6. Valuation calculations
7. Assumptions and limitations
8. Sensitivity analysis
9. Certification and compliance statement

## Data Sources

| Data Type | Source |
|-----------|--------|
| Stock prices | Provided as cited inputs by apdb-etl |
| Financial statements | Yahoo Finance |
| FF factors | Kenneth French Data Library |
| Market data | Provided as cited inputs by apdb-etl |
| Economic data | pandas-datareader |

## Error Handling

- Input validation for all parameters
- Graceful degradation when data unavailable
- Clear error messages
- Fallback to conservative assumptions

## Limitations

- KMV requires equity volatility
- Convertible bond pricing simplified
- Forward-looking ECL requires macro data

## Notes

- All valuations are estimates for reference only
- Not investment advice
- Professional valuations require expert judgment
- Check local regulatory requirements
