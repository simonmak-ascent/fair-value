"""Method catalog, standards resource, and guided prompts."""

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
    assert cat["tool_count"] == 14
    assert cat["method_count"] == len(cat["methods"])
    assert cat["surface_version"] == "3.0"


def test_catalog_every_method_has_metadata():
    for entry in catalog.build_catalog()["methods"]:
        assert entry["tool"] and entry["method"]
        assert isinstance(entry["required"], list) and entry["required"]
        assert "formula_ref" in entry and "standards" in entry


def test_catalog_json_roundtrips():
    parsed = json.loads(catalog.catalog_json())
    assert parsed["tool_count"] == 14


def test_standards_taxonomy_covers_ivs_and_ifrs():
    std = catalog.standards()["standards"]
    assert "IVS 2025" in std and "IFRS 13" in std and "IFRS 9" in std
    assert json.loads(catalog.standards_json())["standards"] == std


# --- guided prompts --------------------------------------------------------


def test_prompt_set():
    assert set(prompts.GUIDED_PROMPTS) == {
        "value_company_dcf",
        "explain_cost_of_capital",
    }


def test_prompts_render_text_mentioning_tools():
    assert "calculate_dcf" in prompts.value_company_dcf("ACME")
    assert "calculate_discount_rate" in prompts.explain_cost_of_capital("ACME")


# --- registration ----------------------------------------------------------


def test_register_prompts_on_fake_server():
    server = _FakeServer()
    names = register_prompts(server)
    assert len(names) == 2
    assert len(server.prompts) == 2


def test_register_resources_on_fake_server():
    server = _FakeServer()
    uris = register_resources(server)
    assert uris == ["valuation://methods", "fair-value://methods", "valuation://standards"]
    assert "valuation://standards" in server.resources
    assert "fair-value://methods" in server.resources
