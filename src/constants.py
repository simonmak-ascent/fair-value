"""
Constants and standards references for financial valuation
"""

# IVS 2025 Framework
IVS_2025 = {
    "IVS_100": "General Concepts",
    "IVS_105": "Valuation Approaches and Methods",
    "IVS_200": "Assets",
    "IVS_210": "Intangible Assets",
    "IVS_220": "Real Property",
    "IVS_230": "Machinery and Equipment",
    "IVS_300": "Business and Business Interests",
    "IVS_400": "Financial Instruments",
    "IVS_410": "Financial Instruments Other Than Derivatives",
    "IVS_420": "Derivatives"
}

# IFRS Standards
IFRS_STANDARDS = {
    "IFRS_13": "Fair Value Measurement",
    "IAS_36": "Impairment of Assets",
    "IAS_38": "Intangible Assets",
    "HKFRS_9": "Financial Instruments",
    "IFRS_9": "Financial Instruments",
    "IFRS_16": "Leases"
}

# Fair Value Hierarchy (IFRS 13)
FAIR_VALUE_HIERARCHY = {
    "Level_1": "Quoted prices in active markets for identical assets/liabilities",
    "Level_2": "Observable inputs other than Level 1 (e.g., quoted prices for similar assets)",
    "Level_3": "Unobservable inputs (e.g., entity's own assumptions)"
}

# Credit Rating to PD Mapping (Basel Approach)
CREDIT_RATINGS = {
    "AAA": 0.001,
    "AA+": 0.002,
    "AA": 0.005,
    "AA-": 0.008,
    "A+": 0.01,
    "A": 0.02,
    "A-": 0.03,
    "BBB+": 0.04,
    "BBB": 0.05,
    "BBB-": 0.08,
    "BB+": 0.10,
    "BB": 0.15,
    "BB-": 0.20,
    "B+": 0.25,
    "B": 0.30,
    "B-": 0.40,
    "CCC": 0.50,
    "CC": 0.60,
    "C": 0.80,
    "D": 1.00
}

# LGD by Seniority
LGD_BY_SENIORITY = {
    "Senior Secured": 0.25,
    "Senior Unsecured": 0.45,
    "Subordinated": 0.75,
    "Preferred": 0.85
}

# Fama-French Factors
FF_FACTORS = {
    "RMRF": "Market excess return",
    "SMB": "Small Minus Big (size)",
    "HML": "High Minus Low (value)",
    "RMW": "Robust Minus Weak (profitability)",
    "CMA": "Conservative Minus Aggressive (investment)"
}

# Valuation Methods
VALUATION_METHODS = {
    "DCF": "Discounted Cash Flow",
    "NAV": "Net Asset Value",
    "CCA": "Comparable Company Analysis",
    "PTA": "Precedent Transaction Analysis",
    "Income": "Income Approach",
    "Market": "Market Approach",
    "Asset": "Asset-Based Approach"
}

# Default Assumptions
DEFAULT_ASSUMPTIONS = {
    "risk_free_rate": 0.04,  # 4% risk-free rate
    "market_risk_premium": 0.055,  # 5.5% market risk premium
    "terminal_growth_rate": 0.025,  # 2.5% perpetual growth
    "tax_rate": 0.25,  # 25% corporate tax
    "projection_years": 5
}

# Market Suffix Mapping
MARKET_SUFFIXES = {
    "US": "",
    "HK": ".HK",
    "CN_SH": ".SS",
    "CN_SZ": ".SZ",
    "JP": ".T"
}

# File Extensions
SUPPORTED_FILE_TYPES = {
    "excel": [".xlsx", ".xls"],
    "pdf": [".pdf"],
    "word": [".docx", ".doc"],
    "image": [".png", ".jpg", ".jpeg"]
}
