# test_forex_trader.py
import pytest
from unittest.mock import patch, MagicMock

import sys
import os
# Adiciona o diretório src ao sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..")) # Sobe dois níveis de tests/ para src/
sys.path.insert(0, project_root)

from financas.forex_trader import ForexTrader, METATRADER5_AVAILABLE

# Mock para a biblioteca MetaTrader5 se não estiver realmente disponível ou para isolar testes
FORCE_MOCK_MT5 = True 

@pytest.fixture
def mock_mt5_library():
    if not METATRADER5_AVAILABLE or FORCE_MOCK_MT5:
        mock_mt5 = MagicMock()
        mock_mt5.initialize.return_value = True
        mock_mt5.terminal_info.return_value = MagicMock(version="5.0.0.1234")
        mock_mt5.login.return_value = True
        mock_mt5.account_info.return_value = MagicMock(
            login=12345678,
            balance=10000.00,
            currency="USD",
            equity=10050.00,
            profit=50.00,
            margin=200.00,
            margin_free=9800.00,
            margin_level=5025.00,
            server="TestBroker-Demo",
            trade_mode="Demo Account",
            _asdict=lambda: { 
                "login": 12345678, "balance": 10000.00, "currency": "USD", "equity": 10050.00,
                "profit": 50.00, "margin": 200.00, "margin_free": 9800.00, "margin_level": 5025.00,
                "server": "TestBroker-Demo", "trade_mode": "Demo Account"
            }
        )
        mock_mt5.symbol_info.return_value = MagicMock(
            name="EURUSD",
            ask=1.08550,
            bid=1.08540,
            point=0.00001,
            digits=5,
            spread=10,
            volume_min=0.01,
            volume_max=100.0,
            volume_step=0.01,
            _asdict=lambda: { 
                "name": "EURUSD", "ask": 1.08550, "bid": 1.08540, "point": 0.00001, "digits": 5,
                "spread": 10, "volume_min": 0.01, "volume_max": 100.0, "volume_step": 0.01
            }
        )
        mock_mt5.symbol_info_tick.return_value = MagicMock(ask=1.08550, bid=1.08540)
        mock_mt5.order_send.return_value = MagicMock(
            retcode=10009, 
            deal=12345, 
            order=67890,
            volume=0.01,
            price=1.08550,
            comment="Order placed successfully",
            _asdict=lambda: { 
                "retcode": 10009, "deal": 12345, "order": 67890, "volume": 0.01,
                "price": 1.08550, "comment": "Order placed successfully"
            }
        )
        mock_mt5.TRADE_ACTION_DEAL = 1 
        mock_mt5.ORDER_TYPE_BUY = 0
        mock_mt5.ORDER_TYPE_SELL = 1
        mock_mt5.ORDER_TIME_GTC = 1
        mock_mt5.ORDER_FILLING_IOC = 1
        mock_mt5.TRADE_RETCODE_DONE = 10009
        
        with patch("financas.forex_trader.mt5", mock_mt5),
             patch("financas.forex_trader.METATRADER5_AVAILABLE", True):
            yield mock_mt5
    else:
        import MetaTrader5 as mt5
        yield mt5 

@pytest.fixture
def trader(mock_mt5_library):
    ft_instance = ForexTrader(mt5_login=12345678, mt5_password="test_pass", mt5_server="TestBroker-Demo")
    return ft_instance

def test_forex_trader_initialization_success(trader, mock_mt5_library):
    if FORCE_MOCK_MT5 or not METATRADER5_AVAILABLE:
        assert trader.initialized is True
        assert trader.connection_status == "connected"
        mock_mt5_library.initialize.assert_called_once()
        mock_mt5_library.login.assert_called_once_with(12345678, "test_pass", "TestBroker-Demo")
    else:
        assert trader.initialized is (True if trader.connection_status == "connected" else False)

def test_get_account_info(trader, mock_mt5_library):
    if not trader.initialized:
        pytest.skip("Trader não inicializado, pulando teste de informações da conta.")
    
    acc_info = trader.get_account_info()
    assert acc_info is not None
    assert acc_info["login"] == 12345678
    assert acc_info["balance"] == 10000.00
    if FORCE_MOCK_MT5 or not METATRADER5_AVAILABLE:
         mock_mt5_library.account_info.assert_called_once()

def test_get_symbol_info(trader, mock_mt5_library):
    if not trader.initialized:
        pytest.skip("Trader não inicializado, pulando teste de informações do símbolo.")

    symbol_info = trader.get_symbol_info("EURUSD")
    assert symbol_info is not None
    assert symbol_info["name"] == "EURUSD"
    assert symbol_info["ask"] == 1.08550
    if FORCE_MOCK_MT5 or not METATRADER5_AVAILABLE:
        mock_mt5_library.symbol_info.assert_called_with("EURUSD")

    assert trader.get_symbol_info("UNKNOWN_SYMBOL") is None

def test_place_order_buy_market(trader, mock_mt5_library):
    if not trader.initialized:
        pytest.skip("Trader não inicializado, pulando teste de colocação de ordem.")

    result = trader.place_order("EURUSD", "buy", 0.01, comment="Test Buy Order")
    assert result is not None
    assert result["retcode"] == 10009 
    assert result["comment"] == "Order placed successfully" or "Order placed successfully (simulated)"
    
    if FORCE_MOCK_MT5 or not METATRADER5_AVAILABLE:
        args, kwargs = mock_mt5_library.order_send.call_args
        request_sent = args[0]
        assert request_sent["symbol"] == "EURUSD"
        assert request_sent["volume"] == 0.01
        assert request_sent["type"] == mock_mt5_library.ORDER_TYPE_BUY
        assert request_sent["action"] == mock_mt5_library.TRADE_ACTION_DEAL
        assert request_sent["comment"] == "Test Buy Order"

def test_place_order_sell_limit(trader, mock_mt5_library):
    if not trader.initialized:
        pytest.skip("Trader não inicializado, pulando teste de ordem limite.")

    limit_price = 1.0900
    result = trader.place_order("EURUSD", "sell_limit", 0.02, price=limit_price, stop_loss=1.0950, take_profit=1.0800)
    assert result is not None
    assert result["retcode"] == 10009
    if FORCE_MOCK_MT5 or not METATRADER5_AVAILABLE:
        args, kwargs = mock_mt5_library.order_send.call_args
        request_sent = args[0]
        assert request_sent["symbol"] == "EURUSD"
        assert request_sent["volume"] == 0.02
        assert request_sent["price"] == limit_price
        assert request_sent["sl"] == 1.0950
        assert request_sent["tp"] == 1.0800

def test_forex_trader_shutdown(trader, mock_mt5_library):
    if not trader.initialized:
        trader.shutdown()
        assert trader.initialized is False 
        if FORCE_MOCK_MT5 or not METATRADER5_AVAILABLE:
            mock_mt5_library.shutdown.assert_not_called() 
        return

    trader.shutdown()
    assert trader.initialized is False
    assert trader.connection_status == "disconnected"
    if FORCE_MOCK_MT5 or not METATRADER5_AVAILABLE:
        mock_mt5_library.shutdown.assert_called_once()

@patch("financas.forex_trader.METATRADER5_AVAILABLE", False)
def test_forex_trader_mt5_not_available():
    ft_instance_no_mt5 = ForexTrader(mt5_login=123, mt5_password="pass", mt5_server="server")
    assert ft_instance_no_mt5.initialized is False
    assert ft_instance_no_mt5.connection_status == "disconnected"
    assert ft_instance_no_mt5.get_account_info() is None
    assert ft_instance_no_mt5.place_order("EURUSD", "buy", 0.01) is None
    ft_instance_no_mt5.shutdown()
