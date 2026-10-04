# MCP Server

## Install and run

```bash
# stdio (default)
uvx --from "fair-value[mcp]" fair-value-mcp

# or install and run
pip install "fair-value[mcp]"
fair-value-mcp            # stdio
fair-value-mcp --http     # Streamable HTTP (default 127.0.0.1:8000)
```

## Surface

- **Tools** — 14 native `calculate_*` tools / **135 methods** derived from the
  method-spec registry (DCF, cost of capital, multiples, residual/asset
  valuation, options, expected value, credit risk, actuarial PV, sector metrics,
  fair-value adjustments, convertible bonds, structured products, loss-making
  companies, and fixed income). Every result carries
  `statistics` and `citations`; add `-help` (or `help=true`) for the generated
  transparency record.
- **Prompts** — guided workflows: `value_company_dcf`, `review_valuation_report`,
  `explain_cost_of_capital`.
- **Resources** — `valuation://methods`: a machine-readable catalogue of methods,
  formula references, and governing standards; `valuation://standards`: the
  IVS/IFRS taxonomy with per-clause text and the methods citing each.

The same core is served as a **REST API** at `/v1` (see [REST API](api.md)).

## Registry

- PyPI: `fair-value`
- MCP Registry: `io.github.simonmak-ascent/fair-value`
- Hosted: `https://fair-value.ascent-partners.com/mcp` (Streamable HTTP; the frontage and docs are at `/`)

Directory sites (Glama, PulseMCP, mcp.so) ingest the official MCP Registry, so
publishing there makes the server discoverable across them automatically; the
social preview asset is at `assets/social-card.svg`.
