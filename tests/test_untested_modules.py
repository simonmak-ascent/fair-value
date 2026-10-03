"""A-009: coverage for previously untested modules (pure/offline paths).

Covers: valuation.nav, valuation.multiples, valuation.sensitivity,
cost_of_capital.fama_french, cost_of_capital.kmv, credit_risk.pd_models,
output.report_formatter, output.chart_data, constants, and the text-extraction
helpers of report_review.pdf_analyzer / word_analyzer / image_analyzer.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# valuation.nav
# ---------------------------------------------------------------------------
def test_nav_per_share_basic():
    from src.valuation.nav import calculate_nav_per_share

    res = calculate_nav_per_share({"net_assets": 1000.0}, 100)
    assert res["nav_per_share"] == 10.0


def test_nav_per_share_zero_shares():
    from src.valuation.nav import calculate_nav_per_share

    assert calculate_nav_per_share({"net_assets": 1000.0}, 0)["nav_per_share"] == 0


# ---------------------------------------------------------------------------
# valuation.multiples
# ---------------------------------------------------------------------------
def test_multiple_ratios():
    from src.valuation import multiples as m

    assert m.calculate_pe_multiple(20, 2) == 10
    assert m.calculate_pb_multiple(20, 4) == 5
    assert m.calculate_ps_multiple(20, 5) == 4
    assert m.calculate_ev_ebitda(100, 10) == 10


def test_multiple_ratios_zero_denominator():
    from src.valuation import multiples as m

    assert m.calculate_pe_multiple(20, 0) == 0.0
    assert m.calculate_ev_ebitda(100, 0) == 0.0


def test_median_multiples_and_apply():
    from src.valuation import multiples as m

    peers = [
        {"pe_ratio": 10, "pb_ratio": 1, "ps_ratio": 2, "ev_ebitda": 8},
        {"pe_ratio": 20, "pb_ratio": 3, "ps_ratio": 4, "ev_ebitda": 12},
    ]
    med = m.calculate_median_multiples(peers)
    assert med["pe_median"] == 15
    assert med["n_peers"] == 2

    applied = m.apply_multiples_valuation(
        {"eps": 2, "book_value_per_share": 10, "sales_per_share": 5, "ebitda": 100, "net_debt": 50},
        med,
    )
    assert applied["pe_valuation"] == 30  # 2 * 15
    assert applied["average_valuation"] > 0


def test_median_multiples_empty():
    from src.valuation import multiples as m

    med = m.calculate_median_multiples([])
    assert med["pe_median"] == 0.0


# ---------------------------------------------------------------------------
# valuation.sensitivity
# ---------------------------------------------------------------------------
def test_generate_sensitivity_range_symmetric():
    from src.valuation.sensitivity import generate_sensitivity_range

    vals = generate_sensitivity_range(100.0, 0.10, 5)
    assert len(vals) == 5
    assert vals[0] == pytest.approx(90.0)
    assert vals[-1] == pytest.approx(110.0)
    assert vals[2] == pytest.approx(100.0)


def test_generate_sensitivity_single_step():
    from src.valuation.sensitivity import generate_sensitivity_range

    assert generate_sensitivity_range(100.0, 0.10, 1) == [100.0]


def test_two_way_sensitivity_shape():
    from src.valuation.sensitivity import two_way_sensitivity

    df = two_way_sensitivity(
        0.0,
        "wacc",
        [0.08, 0.10],
        "growth",
        [0.01, 0.02, 0.03],
        lambda w, g: w - g,
    )
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (3, 2)


# ---------------------------------------------------------------------------
# credit_risk.pd_models
# ---------------------------------------------------------------------------
def test_mortality_pd_identity():
    from src.credit_risk.pd_models import mortality_rate_to_pd, pd_to_mortality_rate

    assert mortality_rate_to_pd(0.02) == 0.02
    assert pd_to_mortality_rate(0.02) == 0.02


def test_hazard_pd_roundtrip():
    from src.credit_risk.pd_models import hazard_rate_to_pd, pd_to_hazard_rate

    pd_val = hazard_rate_to_pd(0.05, 1.0)
    assert pd_to_hazard_rate(pd_val, 1.0) == pytest.approx(0.05, rel=1e-6)


def test_cumulative_and_survival_complement():
    from src.credit_risk.pd_models import (
        calculate_cumulative_pd,
        calculate_survival_probability,
    )

    c = calculate_cumulative_pd(0.02, 5)
    s = calculate_survival_probability(0.02, 5)
    assert c + s == pytest.approx(1.0)


def test_term_structure_keys():
    from src.credit_risk.pd_models import term_structure_pd

    ts = term_structure_pd(0.02)
    assert set(ts) == set(range(1, 11))


def test_altman_z_score_uses_retained_earnings():
    from src.credit_risk.pd_models import Altman_Z_score

    base = Altman_Z_score(1000, 100, 500, 400, 1000, 900)
    with_re = Altman_Z_score(1000, 100, 500, 400, 1000, 900, retained_earnings=200)
    assert isinstance(base, float)
    assert with_re > base  # adding retained earnings raises X2


def test_z_score_to_pd_monotonic():
    from src.credit_risk.pd_models import z_score_to_pd

    low = z_score_to_pd(3.0)
    high = z_score_to_pd(-1.0)
    assert 0.0 <= low <= high <= 1.0


def test_kmv_edf_to_pd_range():
    from src.credit_risk.pd_models import kmv_edf_to_pd

    for edf in (0.0, 0.05, 0.5):
        assert 0.0 <= kmv_edf_to_pd(edf) <= 1.0


# ---------------------------------------------------------------------------
# cost_of_capital.kmv
# ---------------------------------------------------------------------------
def test_distance_to_default():
    from src.cost_of_capital.kmv import distance_to_default

    assert distance_to_default(1000, 400, 0.2) == pytest.approx(3.0)
    assert distance_to_default(0, 400, 0.2) == 0.0


def test_edf_and_rating():
    from src.cost_of_capital.kmv import _edf_to_rating, expected_default_frequency

    assert expected_default_frequency(0.0) == pytest.approx(0.5)
    assert _edf_to_rating(0.001) == "AAA"
    assert _edf_to_rating(0.2) == "CCC or below"


def test_cost_of_debt_helpers():
    from src.cost_of_capital.kmv import (
        calculate_after_tax_cost_of_debt,
        cost_of_debt_from_kmv,
    )

    assert cost_of_debt_from_kmv(0.01, 0.04) == pytest.approx(0.14)  # 0.04 + min(0.1,0.3)
    assert calculate_after_tax_cost_of_debt(0.10, 0.25) == pytest.approx(0.075)


# ---------------------------------------------------------------------------
# cost_of_capital.fama_french (constants; no network)
# ---------------------------------------------------------------------------
def test_ff5_static_rates():
    from src.cost_of_capital.fama_french import get_market_premium, get_risk_free_rate

    assert get_market_premium() == pytest.approx(0.055)
    assert get_risk_free_rate() == pytest.approx(0.04)


# ---------------------------------------------------------------------------
# output.report_formatter + chart_data
# ---------------------------------------------------------------------------
def test_kpi_cards_and_report_text():
    from src.output.report_formatter import create_kpi_cards, generate_valuation_report

    result = {
        "method": "DCF",
        "ticker": "ACME",
        "value_per_share": 12.5,
        "wacc": 0.09,
        "assumptions": {"growth": 0.03},
    }
    kpis = create_kpi_cards(result)
    assert "Fair Value" in kpis and kpis["WACC"]["unit"] == "%"
    text = generate_valuation_report(result)
    assert "ACME" in text and "Disclaimer" in text


def test_chart_data_preparers():
    from src.output import chart_data as cd

    assert cd.prepare_bar_chart_data(["A"], [1], "t")["chart_type"] == "bar"
    assert cd.prepare_line_chart_data({"s": [1, 2]}, "t")["chart_type"] == "line"
    assert cd.prepare_pie_chart_data(["A"], [1], "t")["chart_type"] == "pie"
    combo = cd.prepare_combo_chart_data(["Y1"], [1], [2], "t")
    assert combo["chart_type"] == "combo"


def test_cash_flow_chart_from_projections():
    from src.output.chart_data import prepare_cash_flow_chart

    out = prepare_cash_flow_chart([{"year": 1, "revenue": 1e9, "free_cash_flow": 1e8}])
    assert out["chart_type"] == "combo"


# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------
def test_constants_tables():
    from src import constants as c

    assert set(c.FAIR_VALUE_HIERARCHY) == {"Level_1", "Level_2", "Level_3"}
    assert isinstance(c.CREDIT_RATINGS, dict) and c.CREDIT_RATINGS
    assert c.LGD_BY_SENIORITY
    assert c.SUPPORTED_FILE_TYPES


# ---------------------------------------------------------------------------
# report_review text extractors (pure; no optional deps)
# ---------------------------------------------------------------------------
def test_pdf_text_extractors():
    from src.report_review import pdf_analyzer as pa

    assert pa.extract_fair_value("Fair Value: $12.50")["matches"] == ["12.50"]
    assert pa.extract_methodology("We use a DCF model")["methodology"] == "DCF"
    assert pa.extract_assumptions("WACC: 8.5% growth rate: 3%")["wacc"] == "8.5"
    assert pa.extract_standards_compliance("Prepared per IFRS 13")["is_compliant"] is True
    assert pa.verify_valuation_conclusion("Conclusion and disclaimer")["has_conclusion"]


def test_word_text_extractors():
    from src.report_review import word_analyzer as wa

    concl = wa.extract_valuation_conclusion("Fair value: $9.99 using DCF")
    assert concl["fair_value"] == "9.99"
    assert wa.check_ivs_compliance("In accordance with IVS and IFRS")["has_standards"]


def test_image_analyzer_graceful_without_ocr(tmp_path):
    from src.report_review import image_analyzer as ia

    # Missing file and/or missing OCR backend must not raise; returns "".
    out = ia.extract_text_from_image(str(tmp_path / "nope.png"))
    assert isinstance(out, str)


# ---------------------------------------------------------------------------
# import smoke for every source module
# ---------------------------------------------------------------------------
def test_all_src_modules_import():
    import importlib

    modules = [
        "src.constants",
        "src.fetch_data",
        "src.valuation.dcf",
        "src.valuation.nav",
        "src.valuation.multiples",
        "src.valuation.sensitivity",
        "src.cost_of_capital.wacc",
        "src.cost_of_capital.fama_french",
        "src.cost_of_capital.kmv",
        "src.derivatives.options",
        "src.derivatives.swaps",
        "src.derivatives.convertible_bonds",
        "src.derivatives.futures",
        "src.derivatives.greeks",
        "src.credit_risk.ecl",
        "src.credit_risk.pd_models",
        "src.report_review.excel_analyzer",
        "src.report_review.pdf_analyzer",
        "src.report_review.word_analyzer",
        "src.report_review.image_analyzer",
        "src.report_review.guards",
        "src.output.report_formatter",
        "src.output.chart_data",
        "src.output.result",
    ]
    for name in modules:
        importlib.import_module(name)
