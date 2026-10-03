"""QuantLib parity checks for the optional derivatives backend.

Skipped unless QuantLib is installed (it is not a CI dependency; see
requirements-optional.txt). Run locally or on a box with QuantLib to exercise
the optional path.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.derivatives.options import (  # noqa: E402
    QUANTLIB_AVAILABLE,
    black_scholes_price,
    quantlib_option_price,
)

pytestmark = pytest.mark.skipif(not QUANTLIB_AVAILABLE, reason="QuantLib not installed")


@pytest.mark.parametrize("option_type", ["call", "put"])
@pytest.mark.parametrize("strike", [80.0, 100.0, 120.0])
def test_quantlib_matches_black_scholes(option_type, strike):
    bs = black_scholes_price(100.0, strike, 1.0, 0.05, 0.2, option_type)
    ql = quantlib_option_price(100.0, strike, 1.0, 0.05, 0.2, option_type)
    assert abs(ql - bs) / max(bs, 1e-9) < 0.01
