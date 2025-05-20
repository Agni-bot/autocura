"""
Testes para o módulo MT5.
"""

import pytest
from datetime import datetime, timedelta
import pandas as pd
from trading.mt5_manager import MT5Manager
from trading.mt5_handler import MT5Handler

@pytest.fixture
def mt5_manager():
    """Fixture para criar uma instância do MT5Manager."""
    return MT5Manager()

@pytest.fixture
def mt5_handler():
    """Fixture para criar uma instância do MT5Handler."""
    return MT5Handler()

def test_mt5_manager_initialization(mt5_manager):
    """Testa a inicialização do MT5Manager."""
    assert mt5_manager is not None
    assert mt5_manager.handler is None
    assert isinstance(mt5_manager.config, dict)

def test_mt5_handler_initialization(mt5_handler):
    """Testa a inicialização do MT5Handler."""
    assert mt5_handler is not None
    assert mt5_handler.connected is False
    assert mt5_handler.account_info is None
    assert isinstance(mt5_handler.symbols_info, dict)

def test_mt5_connect(mt5_manager):
    """Testa a conexão com o MT5."""
    success, message = mt5_manager.connect()
    assert isinstance(success, bool)
    assert isinstance(message, str)

def test_mt5_disconnect(mt5_manager):
    """Testa a desconexão do MT5."""
    mt5_manager.connect()
    mt5_manager.disconnect()
    assert mt5_manager.handler is None

def test_get_account_info(mt5_manager):
    """Testa a obtenção de informações da conta."""
    mt5_manager.connect()
    account_info = mt5_manager.get_account_info()
    assert isinstance(account_info, dict)
    if "error" not in account_info:
        assert "balance" in account_info
        assert "equity" in account_info
        assert "margin" in account_info

def test_get_symbol_info(mt5_manager):
    """Testa a obtenção de informações de um símbolo."""
    mt5_manager.connect()
    symbol_info = mt5_manager.get_symbol_info("EURUSD")
    assert isinstance(symbol_info, dict)
    if "error" not in symbol_info:
        assert "name" in symbol_info
        assert "bid" in symbol_info
        assert "ask" in symbol_info

def test_get_current_price(mt5_manager):
    """Testa a obtenção do preço atual."""
    mt5_manager.connect()
    price = mt5_manager.get_current_price("EURUSD")
    assert isinstance(price, dict)
    if "error" not in price:
        assert "symbol" in price
        assert "bid" in price
        assert "ask" in price
        assert "time" in price

def test_place_order(mt5_manager):
    """Testa a colocação de uma ordem."""
    mt5_manager.connect()
    order = mt5_manager.place_order(
        symbol="EURUSD",
        order_type="BUY",
        volume=0.01
    )
    assert isinstance(order, dict)
    if "error" not in order:
        assert "order_id" in order
        assert "volume" in order
        assert "price" in order

def test_get_open_positions(mt5_manager):
    """Testa a obtenção de posições abertas."""
    mt5_manager.connect()
    positions = mt5_manager.get_open_positions()
    assert isinstance(positions, list)
    if positions and "error" not in positions[0]:
        assert "ticket" in positions[0]
        assert "symbol" in positions[0]
        assert "type" in positions[0]
        assert "volume" in positions[0]

def test_close_position(mt5_manager):
    """Testa o fechamento de uma posição."""
    mt5_manager.connect()
    # Primeiro abre uma posição
    order = mt5_manager.place_order(
        symbol="EURUSD",
        order_type="BUY",
        volume=0.01
    )
    if "error" not in order:
        # Depois tenta fechar
        result = mt5_manager.close_position(order["order_id"])
        assert isinstance(result, dict)
        if "error" not in result:
            assert "order_id" in result
            assert "volume" in result
            assert "price" in result

def test_get_historical_data(mt5_manager):
    """Testa a obtenção de dados históricos."""
    mt5_manager.connect()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    data = mt5_manager.get_historical_data(
        symbol="EURUSD",
        timeframe="H1",
        start_date=start_date,
        end_date=end_date
    )
    assert isinstance(data, pd.DataFrame)
    if not data.empty:
        assert "time" in data.columns
        assert "open" in data.columns
        assert "high" in data.columns
        assert "low" in data.columns
        assert "close" in data.columns
        assert "volume" in data.columns

def test_get_available_symbols(mt5_manager):
    """Testa a obtenção de símbolos disponíveis."""
    symbols = mt5_manager.get_available_symbols()
    assert isinstance(symbols, dict)
    assert "major" in symbols
    assert "minor" in symbols
    assert isinstance(symbols["major"], list)
    assert isinstance(symbols["minor"], list)

def test_get_available_timeframes(mt5_manager):
    """Testa a obtenção de timeframes disponíveis."""
    timeframes = mt5_manager.get_available_timeframes()
    assert isinstance(timeframes, list)
    assert all(isinstance(tf, str) for tf in timeframes)
    assert all(tf in ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"] for tf in timeframes) 