"""TDQS invariants for the native tool surface (regression guard).

These assert the deterministic inputs TDQS lints — parameter descriptions,
annotations, a documented output schema, a meaningful title — so the metadata
cannot silently regress (which previously scored the server Tier D).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server import tool_surface as ts  # noqa: E402


def test_surface_validation_clean():
    # validate_surface() flags duplicate names and undocumented parameters.
    assert ts.validate_surface() == []


def test_every_native_param_documented():
    for spec in ts.list_tools():
        for name, prop in (spec.input_schema.get("properties") or {}).items():
            assert prop.get("description"), f"{spec.name}.{name} lacks a description"


def test_every_native_tool_has_annotations():
    for spec in ts.list_tools():
        for hint in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"):
            assert hint in spec.annotations, f"{spec.name} missing {hint}"


def test_every_native_tool_has_documented_output_schema():
    for spec in ts.list_tools():
        assert spec.output_schema.get("properties"), f"{spec.name} output schema empty"


def test_titles_are_meaningful():
    # TDQS titleIsMeaningful: differs from the name and is longer than it.
    for spec in ts.list_tools():
        assert spec.title != spec.name
        assert len(spec.title) > len(spec.name), f"{spec.name} title too short"


def test_all_tools_are_engine_backed():
    # Every surface tool is registry-backed; no sibling-delegation remains.
    for spec in ts.list_tools():
        assert spec.handler.startswith("engine:"), spec.name
