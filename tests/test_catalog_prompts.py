"""A-013: method catalog + guided prompts (and their MCP registration)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server import catalog, prompts  # noqa: E402
from mcp_server.server import register_prompts, register_resources  # noqa: E402


class _FakeServer:
    """Minimal FastMCP stand-in capturing prompt/resource registrations."""

    def __init__(self):
        self.prompts = []
        self.resources = []

    def prompt(self, *args, **kwargs):
        if args and callable(args[0]):
            self.prompts.append(getattr(args[0], "__name__", None))
            return args[0]

        def deco(fn):
            self.prompts.append(kwargs.get("name") or getattr(fn, "__name__", None))
            return fn

        return deco

    def resource(self, *args, **kwargs):
        uri = args[0] if args else kwargs.get("uri")
        if args and callable(args[0]):
            self.resources.append(uri)
            return args[0]

        def deco(fn):
            self.resources.append(uri)
            return fn

        return deco


# --- catalog ---------------------------------------------------------------


def test_catalog_shape():
    cat = catalog.build_catalog()
    assert cat["server"] == "fair-value"
    assert cat["tool_count"] == 8
    assert len(cat["tools"]) == 8


def test_catalog_every_tool_has_method_metadata():
    for tool in catalog.build_catalog()["tools"]:
        assert tool["method"], f"{tool['name']} has no method"
        assert tool["formula_ref"], f"{tool['name']} has no formula_ref"
        assert isinstance(tool["standards"], list)


def test_catalog_json_roundtrips():
    parsed = json.loads(catalog.catalog_json())
    assert parsed["server"] == "fair-value"


# --- guided prompts --------------------------------------------------------


def test_prompt_set():
    assert set(prompts.GUIDED_PROMPTS) == {
        "value_company_dcf",
        "review_valuation_report",
        "explain_cost_of_capital",
    }


def test_prompts_render_text_mentioning_tools():
    assert "valuation_dcf" in prompts.value_company_dcf("ACME")
    assert "review_report" in prompts.review_valuation_report("r.pdf")
    assert "calculate_wacc" in prompts.explain_cost_of_capital("ACME")


# --- registration ----------------------------------------------------------


def test_register_prompts_on_fake_server():
    server = _FakeServer()
    names = register_prompts(server)
    assert len(names) == 3
    assert len(server.prompts) == 3


def test_register_resources_on_fake_server():
    server = _FakeServer()
    uris = register_resources(server)
    assert uris == ["valuation://methods"]
    assert "valuation://methods" in server.resources
