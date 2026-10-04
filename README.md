# Fair Value

[![PyPI](https://img.shields.io/pypi/v/fair-value.svg)](https://pypi.org/project/fair-value/)
[![CI](https://github.com/simonmak-ascent/fair-value/actions/workflows/ci.yml/badge.svg)](https://github.com/simonmak-ascent/fair-value/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![MCP Registry](https://img.shields.io/badge/MCP-Registry-blue.svg)](https://registry.modelcontextprotocol.io/v0/servers?search=fair-value)
[![TDQS](https://glama.ai/mcp/servers/simonmak-ascent/fair-value/badges/score.svg)](https://glama.ai/mcp/servers/simonmak-ascent/fair-value)

Professional financial valuation system for OpenCode with IFRS/IVS compliance.

mcp-name: io.github.simonmak-ascent/fair-value

## Overview

This project provides comprehensive financial valuation capabilities including:
- DCF, NAV, and CCA valuations
- Fama-French 5-Factor cost of equity
- KMV credit risk model
- Derivatives pricing (Options, Swaps, CB)
- Excel model review and validation
- PDF/Word/Image document analysis

## Quick start (≤ 5 minutes)

Fastest path — no install:

- **Hosted MCP (Streamable HTTP):** `https://fair-value.ascent-partners.com/mcp`
- **Run locally, no install:** `uvx --from "fair-value[mcp]" fair-value-mcp`

Then call any of the 16 `calculate_*` tools (DCF, WACC (FF5), multiples, residual income,
options, credit risk, actuarial PV, convertible bonds, …). Client config: [MCP Server](#mcp-server).

## Architecture

```mermaid
flowchart LR
  CLIENT["AI agent / OpenCode"] -->|"stdio (uvx) or Streamable HTTP"| MCP["fair-value-mcp<br/>16 calculate_* tools"]
  HOST["Hosted · fair-value.ascent-partners.com"] --> CLIENT
  MCP --> REG["method-spec registry<br/>(valuation://methods)"]
  REG --> CORE["valuation engine<br/>DCF · NAV · CCA · WACC (FF5) · KMV<br/>derivatives · report review"]
  CORE --> DATA["market data (yfinance)"]
```

## Installation

```bash
pip install -r requirements.txt   # dev workflow (unchanged)
# or, as a package:
pip install .                     # base library
pip install ".[mcp]"              # + MCP server dependencies (A-004)
```

The console command `fair-value-mcp` runs the MCP server (stdio; add `--http` for Streamable HTTP).

Hosted (zero install): `https://fair-value.ascent-partners.com/` (Streamable HTTP).

## MCP Server

```bash
# run locally without installing (stdio)
uvx --from "fair-value[mcp]" fair-value-mcp

# or install and run
pip install "fair-value[mcp]"
fair-value-mcp            # stdio
fair-value-mcp --http     # Streamable HTTP
```

The server exposes 16 native `calculate_*` tools spanning DCF, cost of capital, market multiples, residual income, options, expected value, credit risk, actuarial PV, sector metrics, fair-value adjustments, convertible bonds, structured products, loss-making companies, fixed income, report review, and company profiles — all derived from one method-spec registry.

**Adoption target:** ≥ 100 PyPI downloads and ≥ 1 directory listing within 90 days of the first release (tracked via the PyPI stats API and the directory listing).

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

## MCP tool surface

```mermaid
flowchart LR
    SEED["method_spec_seed.py<br/>method tables (123 methods)"] --> SPEC["method_spec.py<br/>parameter vocabulary"]
    SPEC --> SURF["tool_surface.py<br/>derives the 16 calculate_* tools"]
    SURF --> SRV["server.py (FastMCP)"]
    SRV --> STDIO["stdio · uvx fair-value-mcp"]
    SRV --> HTTP["Streamable HTTP · fair-value-mcp --http"]
    ASGI["asgi.py → api/index.py"] --> HOST["Hosted · fair-value.ascent-partners.com"]
    SRV -.->|resources| RES["valuation://methods · valuation://standards"]
```

## Request lifecycle

```mermaid
sequenceDiagram
    autonumber
    participant C as MCP client / Python caller
    participant E as validation + dispatch
    participant R as method-spec registry
    participant M as computation modules (src/)
    participant O as output envelope
    C->>E: calculate_*(...) / run_valuation(...)
    E->>R: resolve method + validate parameters
    R-->>E: method spec
    E->>M: dispatch to valuation / cost_of_capital / credit_risk / derivatives
    M-->>E: value + steps + assumptions
    E->>O: ok() / error() envelope
    O-->>C: status · method · value · assumptions · formula_ref · disclaimer
```

## Report review pipeline

```mermaid
flowchart LR
    F["Excel / PDF / Word / image"] --> G{"Guards"}
    G -->|macro-enabled or remote formulas| REF["Refused / flagged"]
    G -->|safe| P["Parse<br/>openpyxl · pdfplumber · python-docx · OCR"]
    P --> CH["Checks (report_review/)"]
    CH --> FI["Findings + audit"]
    FI --> ENV["Shared envelope"]
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

See [SKILL.md](./SKILL.md) for the capability spec; the machine-readable method catalog is served by the MCP server at the `valuation://methods` resource, and a docs site is configured via `mkdocs.yml`.

## Standards Compliance

- IVS 2025
- IFRS 13 (Fair Value Measurement)
- IAS 36 (Impairment)
- HKFRS 9 (ECL)

## License

Released under the [MIT License](LICENSE).