# Methods

The canonical, machine-readable version of this catalogue is served by the MCP
server at the resource `valuation://methods` (see `mcp_server/catalog.py`).

| Tool | Method | Formula reference | Standards |
|------|--------|-------------------|-----------|
| `valuation_dcf` | DCF | IVS 105 income approach; PV of projected FCFF | IVS 2025, IFRS 13 |
| `valuation_nav` | NAV | IVS 105 asset-based; assets − liabilities | IVS 2025 |
| `valuation_cca` | CCA | IVS 105 market approach; median peer multiples | IVS 2025, IFRS 13 |
| `review_report` | Review | IVS 2025 review; methodology + assumption checks | IVS 2025, IFRS 13 |
| `get_valuation_summary` | Profile | Market data (price, beta, volatility) | — |
| `calculate_wacc` | WACC | `WACC = we·ke + wd·kd·(1 − tax)` | IVS 2025 |
| `calculate_ecl` | ECL | `ECL = EAD × PD × LGD` | IFRS 9, HKFRS 9 |
| `black_scholes_price` | Black-Scholes | Black-Scholes-Merton European option price | IFRS 13 |
