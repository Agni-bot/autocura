# test_risk_manager.py
import pytest
import json

import sys
import os
# Adiciona o diretório src ao sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..")) # Sobe dois níveis de tests/ para src/
sys.path.insert(0, project_root)

from financas.risk_manager import RiskManager

@pytest.fixture
def risk_manager_default_config():
    return RiskManager() # Uses default config

@pytest.fixture
def risk_manager_custom_config():
    custom_config = {
        "max_total_drawdown_percentage": 10,
        "max_daily_loss_usd": 100,
        "max_exposure_per_asset_usd": 2000,
        "forex_trading": {"default_stop_loss_pips": 30, "max_leverage": "1:10", "max_concurrent_trades": 2},
        "crowdfunding": {"max_investment_per_project_usd": 200, "max_total_crowdfunding_exposure_usd": 500}
    }
    return RiskManager(global_risk_config=custom_config)

def test_risk_manager_initialization(risk_manager_default_config, risk_manager_custom_config):
    assert risk_manager_default_config.global_risk_config["max_daily_loss_usd"] == 300
    assert risk_manager_custom_config.global_risk_config["max_daily_loss_usd"] == 100
    assert risk_manager_custom_config.global_risk_config["forex_trading"]["max_concurrent_trades"] == 2

def test_check_trade_viability_approve(risk_manager_default_config):
    rm = risk_manager_default_config
    viable, msg = rm.check_trade_viability(symbol="EURUSD", volume=0.01, order_type="buy", entry_price=1.1000)
    assert viable is True
    assert "Aprovado" in msg

def test_check_trade_viability_reject_max_concurrent_trades(risk_manager_custom_config):
    rm = risk_manager_custom_config # max_concurrent_trades = 2
    # Simulate 2 open trades
    rm.open_positions["forex_trade1"] = {"symbol": "EURUSD", "volume": 0.01, "entry_price": 1.1}
    rm.open_positions["forex_trade2"] = {"symbol": "GBPUSD", "volume": 0.01, "entry_price": 1.2}
    
    viable, msg = rm.check_trade_viability(symbol="AUDUSD", volume=0.01, order_type="sell", entry_price=0.7000)
    assert viable is False
    assert "Limite de trades concorrentes (2) atingido" in msg

def test_check_trade_viability_reject_max_exposure(risk_manager_custom_config):
    rm = risk_manager_custom_config # max_exposure_per_asset_usd = 2000
    viable, msg = rm.check_trade_viability(symbol="USDJPY", volume=0.3, order_type="buy", entry_price=110.00)
    assert viable is False
    assert "Exposição máxima em Forex (2000 USD) seria excedida" in msg

def test_check_trade_viability_warn_daily_loss(risk_manager_custom_config):
    rm = risk_manager_custom_config # max_daily_loss_usd = 100
    rm.daily_profit_loss["forex"] = -60 
    
    viable, msg = rm.check_trade_viability(symbol="EURCAD", volume=0.01, order_type="buy", entry_price=1.4500)
    assert viable is True 
    assert "Aviso: Perda diária em Forex (-60) está se aproximando do limite (100)" in msg

def test_check_crowdfunding_investment_viability_approve(risk_manager_default_config):
    rm = risk_manager_default_config
    viable, msg = rm.check_crowdfunding_investment_viability(project_id="proj_test_001", investment_amount_usd=300)
    assert viable is True
    assert "Aprovado" in msg

def test_check_crowdfunding_investment_reject_max_per_project(risk_manager_custom_config):
    rm = risk_manager_custom_config # max_investment_per_project_usd = 200
    viable, msg = rm.check_crowdfunding_investment_viability(project_id="proj_test_002", investment_amount_usd=250)
    assert viable is False
    assert "Investimento (250 USD) excede o máximo por projeto (200 USD)" in msg

def test_check_crowdfunding_investment_reject_max_total_exposure(risk_manager_custom_config):
    rm = risk_manager_custom_config # max_total_crowdfunding_exposure_usd = 500
    rm.current_exposure["crowdfunding"] = 400 
    
    viable, msg = rm.check_crowdfunding_investment_viability(project_id="proj_test_003", investment_amount_usd=150)
    assert viable is False
    assert "Exposição total em crowdfunding (500 USD) seria excedida" in msg

def test_update_and_close_forex_position(risk_manager_default_config):
    rm = risk_manager_default_config
    ticket = "forex_BUY_EURUSD_123"
    symbol = "EURUSD"
    volume = 0.02
    entry_price = 1.0800
    current_price_profit = 1.0850 
    current_price_loss = 1.0750   

    rm_seq = RiskManager() 
    rm_seq.update_forex_position(ticket, symbol, volume, entry_price, entry_price) 
    assert rm_seq.daily_profit_loss["forex"] == 0
    initial_exposure = volume * 10000 
    assert rm_seq.current_exposure["forex"] == initial_exposure

    rm_seq.update_forex_position(ticket, symbol, volume, entry_price, current_price_profit)
    assert rm_seq.daily_profit_loss["forex"] == 100.00
    assert rm_seq.open_positions[ticket]["last_pl_usd"] == 100.00

    rm_seq.close_forex_position(ticket, current_price_profit)
    assert ticket not in rm_seq.open_positions
    assert rm_seq.current_exposure["forex"] == 0 
    assert rm_seq.daily_profit_loss["forex"] == 100.00

def test_record_crowdfunding_investment(risk_manager_default_config):
    rm = risk_manager_default_config
    initial_cf_exposure = rm.current_exposure["crowdfunding"]
    amount = 250
    rm.record_crowdfunding_investment("proj_cf_007", amount_usd=amount)
    assert rm.current_exposure["crowdfunding"] == initial_cf_exposure + amount
    assert rm.current_exposure["total"] == rm.current_exposure["forex"] + rm.current_exposure["crowdfunding"]

def test_get_current_risk_summary(risk_manager_default_config):
    rm = risk_manager_default_config
    rm.update_forex_position("fx_1", "GBPUSD", 0.03, 1.2500, 1.2520) 
    rm.record_crowdfunding_investment("cf_1", 150)

    summary = rm.get_current_risk_summary()
    assert summary["current_total_exposure_usd"] == (0.03 * 10000) + 150
    assert summary["current_forex_exposure_usd"] == 0.03 * 10000
    assert summary["current_crowdfunding_exposure_usd"] == 150
    assert summary["daily_forex_profit_loss_usd"] == 60.00
    assert summary["open_forex_positions_count"] == 1
    assert summary["global_risk_config"] == rm.global_risk_config
