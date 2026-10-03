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

- **Tools** — the native valuation / cost-of-capital / derivatives / credit-risk
  / report-review tools, plus delegated tools from the `startup-valuation` and
  `intangible-valuation` MCP servers (strict superset).
- **Prompts** — guided workflows: `value_company_dcf`, `review_valuation_report`,
  `explain_cost_of_capital`.
- **Resources** — `valuation://methods`: a machine-readable catalogue of methods,
  formula references, and governing standards.

## Registry

- PyPI: `fair-value`
- MCP Registry: `io.github.simonmak-ascent/fair-value`
- Hosted: `https://fair-value.ascent-partners.com/` (Streamable HTTP; `/mcp` 308-redirects to `/`)

Directory sites (Glama, PulseMCP, mcp.so) ingest the official MCP Registry, so
publishing there makes the server discoverable across them automatically; the
social preview asset is at `assets/social-card.svg`.
