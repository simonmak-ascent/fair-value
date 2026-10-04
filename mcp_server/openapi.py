"""OpenAPI 3 document for the `/v1` REST API (VDD A-011).

Hand-built from the registry (no FastAPI dependency): discovery paths plus the
`calculate` and `help` operations, with the tool list as an enum. Served at
`/v1/openapi.json` and rendered by a small `/v1/docs` page.
"""

from __future__ import annotations

from typing import Any, Dict

from . import method_spec as ms
from .rest import API_VERSION

OPENAPI_VERSION = "3.0.3"


def _tools_enum() -> list:
    return ms.tools()


def build_openapi() -> Dict[str, Any]:
    """Return the OpenAPI 3.0 document for the `/v1` surface."""
    version = ms.catalog()["surface_version"]
    return {
        "openapi": OPENAPI_VERSION,
        "info": {
            "title": "Fair Value API",
            "version": f"{API_VERSION}-surface-{version}",
            "description": (
                "Dual-standard (IVS 2025 + IFRS/IAS) valuation calculations. Every "
                "result is a centre value plus statistical characteristics "
                "(statistics/solution_type) with the clauses it satisfies (citations)."
            ),
        },
        "servers": [{"url": "/", "description": "Current host"}],
        "paths": {
            "/v1/health": {
                "get": {
                    "summary": "Health and surface version",
                    "responses": {"200": {"description": "Service status"}},
                }
            },
            "/v1/tools": {
                "get": {
                    "summary": "List tools with titles, descriptions and methods",
                    "responses": {"200": {"description": "Tool map"}},
                }
            },
            "/v1/methods": {
                "get": {
                    "summary": "Method catalog (inputs, formula refs, standards)",
                    "responses": {"200": {"description": "Method catalog"}},
                }
            },
            "/v1/standards": {
                "get": {
                    "summary": "Standards, clauses, and the methods citing each",
                    "responses": {"200": {"description": "Standards index"}},
                }
            },
            "/v1/help/{tool}": {
                "get": {
                    "summary": "Transparency record for a tool",
                    "parameters": [
                        {
                            "name": "tool",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string", "enum": _tools_enum()},
                        }
                    ],
                    "responses": {
                        "200": {"description": "Help record"},
                        "404": {"description": "Unknown tool"},
                    },
                }
            },
            "/v1/calculate/{tool}": {
                "post": {
                    "summary": "Run a method and return the shared envelope",
                    "parameters": [
                        {
                            "name": "tool",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string", "enum": _tools_enum()},
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["method"],
                                    "properties": {
                                        "method": {
                                            "type": "string",
                                            "description": (
                                                "Method name for the tool (see /v1/methods "
                                                "for each method's required inputs)."
                                            ),
                                        }
                                    },
                                    "additionalProperties": True,
                                },
                                "example": {
                                    "method": "dcf",
                                    "cash_flows": [100, 110],
                                    "discount_rate": 0.1,
                                },
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "Result envelope"},
                        "400": {"description": "Invalid method, inputs or body"},
                        "404": {"description": "Unknown tool"},
                    },
                }
            },
        },
    }
