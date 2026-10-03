"""A-003: the MCP tool surface contract."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server import tool_surface as ts


def test_surface_has_at_least_six_tools():
    assert len(ts.TOOL_SURFACE) >= 6


def test_unknown_tool_raises_keyerror():
    with pytest.raises(KeyError):
        ts.get_tool("no_such_tool")


def test_every_tool_has_required_fields():
    for tool in ts.list_tools():
        assert tool.name
        assert tool.title
        assert tool.description
        assert isinstance(tool.input_schema, dict)
        assert isinstance(tool.output_schema, dict)
        assert tool.handler


def test_names_unique_and_snake_case():
    assert ts.validate_surface() == []
    names = ts.tool_names()
    assert len(names) == len(set(names))


def test_validate_surface_detects_duplicates():
    dup = ts.TOOL_SURFACE + (ts.TOOL_SURFACE[0],)
    problems = ts.validate_surface(dup)
    assert any("duplicate" in p for p in problems)


def test_handlers_resolve_to_callables():
    for tool in ts.list_tools():
        assert callable(ts.resolve_handler(tool)), tool.name


def test_unresolvable_handler_raises():
    bad = ts.ToolSpec(
        name="bad",
        title="bad",
        description="bad",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        handler="no.such.module_xyz.func",
    )
    with pytest.raises(Exception):
        ts.resolve_handler(bad)


def test_schemas_are_objects_and_annotations_present():
    for tool in ts.list_tools():
        assert tool.input_schema.get("type") == "object"
        assert "properties" in tool.input_schema
        assert tool.annotations.get("readOnlyHint") is True
        assert tool.annotations.get("idempotentHint") is True
        assert tool.annotations.get("destructiveHint") is False


def test_tool_surface_module_does_not_import_fastmcp():
    source = Path(ts.__file__).read_text()
    assert "import fastmcp" not in source
    assert "from fastmcp" not in source


def test_core_families_present():
    names = set(ts.tool_names())
    assert {"calculate_dcf", "calculate_discount_rate", "calculate_market_multiple"} <= names
    assert "calculate_convertible_bond" in names
    assert "calculate_structured_product" in names
    assert "calculate_report_review" in names
    assert "calculate_company_summary" in names
    assert len(names) == 16


def test_versioned_identity():
    assert ts.SERVER_NAME == "fair-value"
    assert ts.SURFACE_VERSION
