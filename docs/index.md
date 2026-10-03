# Fair Value

Professional financial valuation for AI agents and analysts: corporate valuation
(DCF / NAV / CCA), cost of capital (WACC, Fama-French 5-factor, KMV), derivatives
pricing (options, swaps, convertible bonds, futures, greeks), IFRS 9 / HKFRS 9
credit risk (ECL, PD models), and valuation-report review — aligned to
**IVS 2025** and **IFRS 13**.

The MCP server exposes 16 native `calculate_*` tools derived from a single
method-spec registry, covering corporate, startup, and intangible valuation,
derivatives, credit risk, and report review.

## Quick start

```bash
# run without installing (stdio)
uvx --from "fair-value[mcp]" fair-value-mcp
```

See [MCP Server](mcp.md) for transports and configuration, and
[Methods](methods.md) for the tool catalogue.

!!! warning "Not investment advice"
    All output is for informational purposes only and is not investment advice.
