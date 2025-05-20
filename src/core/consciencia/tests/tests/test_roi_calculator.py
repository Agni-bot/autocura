# test_roi_calculator.py
import pytest
import numpy as np
# Ajuste para importação relativa
import sys
import os
# Adiciona o diretório src ao sys.path para permitir importações como se estivesse na raiz
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..")) 
sys.path.insert(0, project_root)

from conscienciaSituacional.planejamento.roi_calculator import ROICalculator

@pytest.fixture
def calculator():
    return ROICalculator(default_discount_rate=0.10)

def test_calculate_simple_roi(calculator):
    assert calculator.calculate_simple_roi(net_profit=20000, cost_of_investment=100000) == pytest.approx(20.00)
    assert calculator.calculate_simple_roi(net_profit=-10000, cost_of_investment=50000) == pytest.approx(-20.00)
    assert calculator.calculate_simple_roi(net_profit=0, cost_of_investment=10000) == pytest.approx(0.00)
    assert calculator.calculate_simple_roi(net_profit=100, cost_of_investment=0) is None
    assert calculator.calculate_simple_roi(net_profit=100, cost_of_investment=-10) is None

def test_calculate_payback_period(calculator):
    assert calculator.calculate_payback_period(initial_investment=50000, annual_cash_flows=[15000, 20000, 25000, 10000]) == pytest.approx(2.60)
    assert calculator.calculate_payback_period(initial_investment=30000, annual_cash_flows=[10000, 20000, 15000]) == pytest.approx(2.00)
    assert calculator.calculate_payback_period(initial_investment=100000, annual_cash_flows=[10000, 10000, 10000]) is None
    assert calculator.calculate_payback_period(initial_investment=0, annual_cash_flows=[10000]) is None
    assert calculator.calculate_payback_period(initial_investment=100, annual_cash_flows=[]) is None
    assert calculator.calculate_payback_period(initial_investment=5000, annual_cash_flows=[10000, 5000]) == pytest.approx(0.50)

def test_calculate_npv(calculator):
    assert calculator.calculate_npv(initial_investment=100000, cash_flows_per_period=[30000, 35000, 40000, 25000, 20000]) == pytest.approx(15744.48, abs=0.01)
    assert calculator.calculate_npv(initial_investment=50000, cash_flows_per_period=[20000, 20000, 15000], discount_rate=0.08) == pytest.approx(-2427.21, abs=0.01)
    assert calculator.calculate_npv(initial_investment=20000, cash_flows_per_period=[5000, -2000, 8000], discount_rate=0.05) == pytest.approx(-8473.17, abs=0.01)

def test_calculate_irr(calculator):
    irr_value = calculator.calculate_irr(initial_investment=100000, cash_flows_per_period=[30000, 35000, 40000, 25000, 20000])
    assert irr_value is not None
    assert irr_value == pytest.approx(0.1986, abs=0.0001)
    assert calculator.calculate_irr(initial_investment=1000, cash_flows_per_period=[100, 100, 100]) is None 
    assert calculator.calculate_irr(initial_investment=100, cash_flows_per_period=[-10, -20]) is None 

def test_analyze_technology_adoption(calculator):
    tech_investment = 200000
    tech_benefits = [60000, 70000, 80000, 80000, 75000]
    tech_op_costs = [10000, 12000, 12000, 13000, 13000]
    lifespan_years = 5
    analysis = calculator.analyze_technology_adoption(
        tech_name="Sistema Teste",
        investment_cost=tech_investment,
        expected_annual_benefits=tech_benefits,
        expected_annual_costs=tech_op_costs,
        lifespan_years=lifespan_years,
        discount_rate=0.12
    )
    assert analysis is not None
    assert analysis["technology_name"] == "Sistema Teste"
    assert analysis["investment_cost_usd"] == pytest.approx(200000)
    assert analysis["total_net_profit_usd"] == pytest.approx(105000.00)
    assert analysis["simple_roi_percentage"] == pytest.approx(52.50)
    assert analysis["payback_period_years"] == pytest.approx(3.36, abs=0.01) # Payback pode ter pequenas variações
    assert analysis["npv_usd"] == pytest.approx(29327.98, abs=0.01)
    assert analysis["irr_percentage"] == pytest.approx(20.63, abs=0.01) # IRR pode ter pequenas variações
    assert analysis["discount_rate_used"] == pytest.approx(0.12)

