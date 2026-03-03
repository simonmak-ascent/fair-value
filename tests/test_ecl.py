"""
Test ECL and Credit Risk
"""

import pytest
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.credit_risk.ecl import (
    calculate_ecL,
    get_pd_from_rating,
    get_lgd_from_recovery,
    get_default_lgd_by_seniority,
    calculate_12m_ecL,
    calculate_lifetime_ecL,
    forward_looking_adjustment,
    calculate_ecL_portfolio,
    assess_credit_stage
)
from src.credit_risk.pd_models import (
    hazard_rate_to_pd,
    pd_to_hazard_rate,
    calculate_cumulative_pd,
    calculate_survival_probability,
    credit_spread_to_pd,
    z_score_to_pd
)


class TestECL:
    """Test ECL calculations"""
    
    def test_ecl_basic(self):
        """Test basic ECL calculation"""
        ecl = calculate_ecL(1000, 0.05, 0.45)
        assert ecl == 22.5
    
    def test_ecl_zero(self):
        """Test ECL with zero values"""
        ecl = calculate_ecL(1000, 0, 0.45)
        assert ecl == 0
    
    def test_pd_from_rating(self):
        """Test PD from credit rating"""
        pd = get_pd_from_rating("AAA")
        assert pd == 0.001
        
        pd = get_pd_from_rating("BBB")
        assert pd == 0.05
    
    def test_lgd_from_recovery(self):
        """Test LGD from recovery rate"""
        lgd = get_lgd_from_recovery(0.55)
        assert lgd == pytest.approx(0.45)
    
    def test_default_lgd(self):
        """Test default LGD by seniority"""
        lgd = get_default_lgd_by_seniority("Senior Secured")
        assert lgd == 0.25
        
        lgd = get_default_lgd_by_seniority("Senior Unsecured")
        assert lgd == 0.45
    
    def test_12m_ecl(self):
        """Test 12-month ECL"""
        ecl = calculate_12m_ecL(1000, 0.02, 0.45)
        assert ecl == 9
    
    def test_lifetime_ecl(self):
        """Test lifetime ECL"""
        ecl = calculate_lifetime_ecL(1000, 0.10, 0.45)
        assert ecl == 45
    
    def test_forward_looking(self):
        """Test forward-looking adjustment"""
        ecl = forward_looking_adjustment(100, 1.2, 1.1, 1.0)
        assert ecl == 132
    
    def test_portfolio_ecl(self):
        """Test portfolio ECL"""
        result = calculate_ecL_portfolio(
            [1000, 2000, 3000],
            [0.01, 0.02, 0.05],
            [0.45, 0.45, 0.45]
        )
        assert result['total_exposure'] == 6000
        assert result['total_ecl'] > 0
    
    def test_credit_stage(self):
        """Test credit stage assessment"""
        stage = assess_credit_stage(0.001, False)
        assert stage == 'Stage 1'
        
        stage = assess_credit_stage(0.02, True)
        assert stage == 'Stage 2'


class TestPDModels:
    """Test PD models"""
    
    def test_hazard_rate_to_pd(self):
        """Test hazard rate to PD"""
        pd = hazard_rate_to_pd(0.05, 1)
        expected = 1 - np.exp(-0.05)
        assert abs(pd - expected) < 0.001
    
    def test_pd_to_hazard_rate(self):
        """Test PD to hazard rate"""
        hr = pd_to_hazard_rate(0.05, 1)
        assert hr > 0
    
    def test_cumulative_pd(self):
        """Test cumulative PD"""
        pd = calculate_cumulative_pd(0.02, 5)
        expected = 1 - (1-0.02)**5
        assert abs(pd - expected) < 0.001
    
    def test_survival_probability(self):
        """Test survival probability"""
        sp = calculate_survival_probability(0.02, 5)
        expected = (1-0.02)**5
        assert abs(sp - expected) < 0.001
    
    def test_credit_spread_to_pd(self):
        """Test credit spread to PD"""
        pd = credit_spread_to_pd(0.03)
        expected = 0.03 / 0.45
        assert abs(pd - expected) < 0.001
    
    def test_z_score_to_pd(self):
        """Test Z-score to PD"""
        pd = z_score_to_pd(3.5)
        assert pd == 0.001
        
        pd = z_score_to_pd(1.5)
        assert pd == 0.15
