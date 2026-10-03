"""Baseline tool lists of the sibling MCPs (A-005).

Captured from the sibling repositories so the strict-superset promise can be
checked mechanically. Update this file when a sibling releases new tools.
"""

from __future__ import annotations

# intangible-valuation 2.1.2 — mcp_server/tool_surface.py
INTANGIBLE_TOOLS = (
    "valuation_time_value",
    "valuation_discount_rate",
    "valuation_cost_approach",
    "valuation_market_approach",
    "valuation_income_methods",
    "valuation_ip",
    "valuation_technology",
    "valuation_customer",
    "valuation_human_capital",
    "valuation_goodwill_ppa",
    "valuation_impairment",
    "valuation_royalty_analysis",
    "valuation_simulation",
    "valuation_compliance",
)

# startup-valuation 2.1.2 — src/startup_valuation/mcp/server.py
STARTUP_TOOLS = (
    "valuation_probability",
    "valuation_time_value",
    "valuation_capm",
    "valuation_core",
    "valuation_advanced",
    "valuation_comparables",
    "valuation_saas",
    "valuation_marketplace",
    "valuation_fintech",
    "valuation_biotech",
    "valuation_hardware",
    "valuation_international",
    "valuation_stakeholder",
    "valuation_emerging",
)

SIBLING_SOURCES = (
    {
        "package": "intangible-valuation",
        "version": "2.1.2",
        "tools": INTANGIBLE_TOOLS,
        "provenance": (
            "github.com/simonmak-ascent/intangible-valuation "
            "@ mcp_server/tool_surface.py"
        ),
    },
    {
        "package": "startup-valuation",
        "version": "2.1.2",
        "tools": STARTUP_TOOLS,
        "provenance": (
            "github.com/simonmak-ascent/startup-valuation "
            "@ src/startup_valuation/mcp/server.py"
        ),
    },
)

# Union of sibling tool names (deduplicated).
UNION_TOOLS = tuple(sorted(set(INTANGIBLE_TOOLS) | set(STARTUP_TOOLS)))
