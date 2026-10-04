"""Method-spec registry and alias registry (Phase 1)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server import aliases as al
from mcp_server import method_spec as ms


def test_seed_tools_registered():
    assert "calculate_dcf" in ms.tools()
    assert "calculate_option" in ms.tools()
    assert "dcf" in ms.methods_for("calculate_dcf")
    assert "black_scholes" in ms.methods_for("calculate_option")


def test_all_tools_registered():
    assert len(ms.tools()) == 14
    for name in (
        "calculate_dcf",
        "calculate_discount_rate",
        "calculate_market_multiple",
        "calculate_residual",
        "calculate_option",
        "calculate_expected_value",
        "calculate_credit_loss",
        "calculate_actuarial_pv",
        "calculate_sector_metrics",
        "calculate_fair_value_adjustment",
        "calculate_convertible_bond",
        "calculate_structured_product",
        "calculate_loss_making_company",
    ):
        assert name in ms.tools(), name


def test_registry_is_sound():
    assert ms.validate_registry() == []


def test_catalog_lists_every_method():
    cat = ms.catalog()
    assert cat["tool_count"] == 14
    assert cat["method_count"] == sum(len(ms.methods_for(t)) for t in ms.tools())
    entry = next(e for e in cat["methods"] if e["tool"] == "calculate_dcf" and e["method"] == "dcf")
    assert entry["required"] == ["cash_flows", "discount_rate"]
    assert ms.catalog_json().startswith("{")


def test_every_method_declares_required_inputs():
    for tool in ms.tools():
        for method in ms.methods_for(tool):
            spec = ms.get(tool, method)
            assert spec is not None and spec.required, f"{tool}.{method}"


def test_valid_arguments_pass():
    assert (
        ms.validate_arguments("calculate_dcf", "dcf", {"cash_flows": [1.0], "discount_rate": 0.1})
        == []
    )


def test_missing_required_is_reported():
    problems = ms.validate_arguments("calculate_dcf", "dcf", {"cash_flows": [1.0]})
    assert problems and "discount_rate" in problems[0]


def test_extraneous_argument_is_rejected():
    problems = ms.validate_arguments(
        "calculate_dcf", "dcf", {"cash_flows": [1.0], "discount_rate": 0.1, "bogus": 1}
    )
    assert any("unexpected" in p and "bogus" in p for p in problems)


def test_unknown_method_is_reported():
    problems = ms.validate_arguments("calculate_dcf", "nope", {})
    assert problems and "unknown method" in problems[0]


def test_input_schema_shape():
    schema = ms.input_schema("calculate_dcf")
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["method"]
    assert "dcf" in schema["properties"]["method"]["enum"]
    assert "cash_flows" in schema["properties"]
    assert schema["properties"]["discount_rate"]["description"]


def test_method_matrix_text_nonempty():
    text = ms.method_matrix_text("calculate_option")
    assert "black_scholes" in text and "spot" in text


def test_alias_tool_resolution():
    assert al.resolve_tool("valuation_dcf") == "calculate_dcf"
    assert al.resolve_tool("calculate_ecL") == "calculate_credit_loss"
    assert al.resolve_tool("already_canonical") == "already_canonical"


def test_alias_method_resolution():
    assert al.resolve_method("calculate_credit_loss", "ecl") == "ecl_12m"
    assert al.resolve_method("calculate_option", "binomial") == "binomial_american"
    assert al.resolve("calculate_ecL", "ecl") == ("calculate_credit_loss", "ecl_12m")
