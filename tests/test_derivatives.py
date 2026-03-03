"""
Test Options pricing
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.derivatives.options import (
    black_scholes_price,
    black_scholes_delta,
    black_scholes_gamma,
    black_scholes_vega,
    black_scholes_theta,
    black_scholes_rho,
    implied_volatility
)
from src.derivatives.futures import (
    futures_price,
    forward_price,
    currency_forward,
    basis,
    implied_rate_from_futures
)
from src.derivatives.futures import (
    futures_price,
    forward_price,
    currency_forward,
    basis,
    implied_rate_from_futures
)
from src.derivatives.greeks import (
    delta,
    gamma,
    theta,
    vega,
    rho,
    all_greeks
)


class TestBlackScholes:
    """Test Black-Scholes pricing"""
    
    def test_call_price_atm(self):
        """Test ATM call option"""
        price = black_scholes_price(100, 100, 1, 0.05, 0.2, "call")
        assert 8 < price < 12  # Approximate range
    
    def test_call_price_itm(self):
        """Test ITM call option"""
        price = black_scholes_price(120, 100, 1, 0.05, 0.2, "call")
        assert price > 20
    
    def test_call_price_otm(self):
        """Test OTM call option"""
        price = black_scholes_price(80, 100, 1, 0.05, 0.2, "call")
        assert 0 < price < 5
    
    def test_put_price_atm(self):
        """Test ATM put option"""
        price = black_scholes_price(100, 100, 1, 0.05, 0.2, "put")
        assert 5 < price < 10
    
    def test_call_price_zero_maturity(self):
        """Test option at maturity"""
        price = black_scholes_price(110, 100, 0, 0.05, 0.2, "call")
        assert price == 10
    
    def test_put_price_zero_maturity(self):
        """Test put at maturity"""
        price = black_scholes_price(90, 100, 0, 0.05, 0.2, "put")
        assert price == 10


class TestGreeks:
    """Test option Greeks"""
    
    def test_call_delta_positive(self):
        """Call delta should be positive"""
        d = black_scholes_delta(100, 100, 1, 0.05, 0.2, "call")
        assert 0 < d < 1
    
    def test_put_delta_negative(self):
        """Put delta should be negative"""
        d = black_scholes_delta(100, 100, 1, 0.05, 0.2, "put")
        assert -1 < d < 0
    
    def test_gamma_positive(self):
        """Gamma should be positive"""
        g = black_scholes_gamma(100, 100, 1, 0.05, 0.2)
        assert g > 0
    
    def test_vega_positive(self):
        """Vega should be positive"""
        v = black_scholes_vega(100, 100, 1, 0.05, 0.2)
        assert v > 0
    
    def test_call_theta_negative(self):
        """Theta should be negative for long option"""
        t = black_scholes_theta(100, 100, 1, 0.05, 0.2, "call")
        assert t < 0


class TestFutures:
    """Test futures pricing"""
    
    def test_futures_price_basic(self):
        """Test basic futures pricing"""
        f = futures_price(100, 0.05, 1)
        expected = 100 * 1.05127
        assert abs(f - expected) < 0.1
    
    def test_forward_price(self):
        """Test forward pricing"""
        f = forward_price(100, 0.05, 0.02, 1)
        expected = 100 * 1.03
        assert abs(f - expected) < 0.1
    
    def test_currency_forward(self):
        """Test currency forward"""
        f = currency_forward(7.8, 0.04, 0.02, 1)
        assert f > 7.8  # Higher domestic rate
    
    def test_basis(self):
        """Test basis calculation"""
        b = basis(105, 100)
        assert b == -5
    
    def test_implied_rate(self):
        """Test implied rate calculation"""
        r = implied_rate_from_futures(100, 105, 1)
        assert abs(r - 0.0488) < 0.01


class TestGreeksModule:
    """Test Greeks from greeks module"""
    
    def test_delta_call(self):
        """Test call delta"""
        d = delta(100, 100, 1, 0.05, 0.2, "call")
        assert 0 < d < 1
    
    def test_delta_put(self):
        """Test put delta"""
        d = delta(100, 100, 1, 0.05, 0.2, "put")
        assert -1 < d < 0
    
    def test_all_greeks(self):
        """Test all greeks calculation"""
        g = all_greeks(100, 100, 1, 0.05, 0.2, "call")
        assert 'delta' in g
        assert 'gamma' in g
        assert 'theta' in g
        assert 'vega' in g
        assert 'rho' in g
