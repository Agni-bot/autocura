"""
MetaTrader 5 Handler Module
Responsible for managing connection and operations with MetaTrader 5.
"""

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    mt5 = None

import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple, Union
import time

logger = logging.getLogger("will_mt5_handler")

class MT5Handler:
    """Classe para gerenciar conexão e operações com MetaTrader 5."""

    def __init__(self, 
                 server: str = "MetaQuotes-Demo",
                 login: int = None,
                 password: str = None,
                 path: str = None):
        """
        Inicializa o handler do MT5.
        
        Args:
            server (str): Nome do servidor MT5
            login (int): Número da conta
            password (str): Senha da conta
            path (str): Caminho para o terminal MT5
        """
        self.server = server
        self.login = login
        self.password = password
        self.path = path
        self.connected = False
        self.account_info = None
        self.symbols_info = {}

    def connect(self) -> Tuple[bool, str]:
        """
        Conecta ao terminal MT5.
        
        Returns:
            tuple[bool, str]: (sucesso, mensagem)
        """
        if not MT5_AVAILABLE:
            return False, "MetaTrader5 não está disponível no ambiente."

        try:
            # Inicializa o MT5
            if not mt5.initialize(path=self.path):
                error = mt5.last_error()
                logger.error(f"Falha ao inicializar MT5: {error}")
                return False, f"Falha ao inicializar MT5: {error}"

            # Tenta conectar à conta
            if self.login and self.password:
                authorized = mt5.login(
                    login=self.login,
                    password=self.password,
                    server=self.server
                )
                if not authorized:
                    error = mt5.last_error()
                    logger.error(f"Falha ao autenticar: {error}")
                    return False, f"Falha ao autenticar: {error}"

            # Obtém informações da conta
            self.account_info = mt5.account_info()
            if self.account_info is None:
                error = mt5.last_error()
                logger.error(f"Falha ao obter informações da conta: {error}")
                return False, f"Falha ao obter informações da conta: {error}"

            # Carrega informações dos símbolos
            self._load_symbols_info()

            self.connected = True
            logger.info("Conectado ao MT5 com sucesso")
            return True, "Conectado com sucesso"

        except Exception as e:
            logger.error(f"Erro ao conectar ao MT5: {str(e)}")
            return False, f"Erro ao conectar: {str(e)}"

    def disconnect(self) -> None:
        """Desconecta do terminal MT5."""
        if not MT5_AVAILABLE:
            return

        if self.connected:
            mt5.shutdown()
            self.connected = False
            self.account_info = None
            self.symbols_info = {}
            logger.info("Desconectado do MT5")

    def _load_symbols_info(self) -> None:
        """Carrega informações de todos os símbolos disponíveis."""
        if not MT5_AVAILABLE:
            return

        symbols = mt5.symbols_get()
        if symbols is None:
            error = mt5.last_error()
            logger.error(f"Falha ao obter símbolos: {error}")
            return

        for symbol in symbols:
            self.symbols_info[symbol.name] = {
                'name': symbol.name,
                'bid': symbol.bid,
                'ask': symbol.ask,
                'point': symbol.point,
                'digits': symbol.digits,
                'volume_min': symbol.volume_min,
                'volume_max': symbol.volume_max,
                'volume_step': symbol.volume_step,
                'spread': symbol.spread,
                'trade_contract_size': symbol.trade_contract_size,
                'trade_mode': symbol.trade_mode,
                'trade_exemode': symbol.trade_exemode,
                'swap_mode': symbol.swap_mode,
                'swap_long': symbol.swap_long,
                'swap_short': symbol.swap_short,
                'margin_initial': symbol.margin_initial,
                'margin_maintenance': symbol.margin_maintenance
            }

    def get_account_info(self) -> Dict:
        """
        Retorna informações da conta.
        
        Returns:
            dict: Informações da conta
        """
        if not MT5_AVAILABLE:
            return {"error": "MetaTrader5 não está disponível no ambiente."}

        if not self.connected:
            return {"error": "Não conectado ao MT5"}

        return {
            'login': self.account_info.login,
            'server': self.account_info.server,
            'balance': self.account_info.balance,
            'equity': self.account_info.equity,
            'margin': self.account_info.margin,
            'free_margin': self.account_info.margin_free,
            'leverage': self.account_info.leverage,
            'currency': self.account_info.currency,
            'profit': self.account_info.profit
        }

    def get_symbol_info(self, symbol: str) -> Dict:
        """
        Retorna informações de um símbolo específico.
        
        Args:
            symbol (str): Nome do símbolo (ex: "EURUSD")
            
        Returns:
            dict: Informações do símbolo
        """
        if not MT5_AVAILABLE:
            return {"error": "MetaTrader5 não está disponível no ambiente."}

        if not self.connected:
            return {"error": "Não conectado ao MT5"}

        if symbol not in self.symbols_info:
            return {"error": f"Símbolo {symbol} não encontrado"}

        return self.symbols_info[symbol]

    def get_current_price(self, symbol: str) -> Dict:
        """
        Retorna preço atual de um símbolo.
        
        Args:
            symbol (str): Nome do símbolo
            
        Returns:
            dict: Preço atual (bid/ask)
        """
        if not MT5_AVAILABLE:
            return {"error": "MetaTrader5 não está disponível no ambiente."}

        if not self.connected:
            return {"error": "Não conectado ao MT5"}

        symbol_info = mt5.symbol_info_tick(symbol)
        if symbol_info is None:
            error = mt5.last_error()
            return {"error": f"Falha ao obter preço: {error}"}

        return {
            'symbol': symbol,
            'bid': symbol_info.bid,
            'ask': symbol_info.ask,
            'last': symbol_info.last,
            'volume': symbol_info.volume,
            'time': datetime.fromtimestamp(symbol_info.time).isoformat()
        }

    def place_order(self, 
                   symbol: str,
                   order_type: str,
                   volume: float,
                   price: float = None,
                   sl: float = None,
                   tp: float = None,
                   comment: str = "") -> Dict:
        """
        Coloca uma ordem no mercado.
        
        Args:
            symbol (str): Nome do símbolo
            order_type (str): Tipo da ordem ("BUY" ou "SELL")
            volume (float): Volume da ordem
            price (float): Preço da ordem (opcional para ordens de mercado)
            sl (float): Stop Loss (opcional)
            tp (float): Take Profit (opcional)
            comment (str): Comentário da ordem
            
        Returns:
            dict: Resultado da ordem
        """
        if not MT5_AVAILABLE:
            return {"error": "MetaTrader5 não está disponível no ambiente."}

        if not self.connected:
            return {"error": "Não conectado ao MT5"}

        # Valida símbolo
        if symbol not in self.symbols_info:
            return {"error": f"Símbolo {symbol} não encontrado"}

        # Valida volume
        symbol_info = self.symbols_info[symbol]
        if volume < symbol_info['volume_min'] or volume > symbol_info['volume_max']:
            return {"error": f"Volume fora dos limites permitidos"}

        # Prepara a ordem
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL,
            "price": price if price else mt5.symbol_info_tick(symbol).ask,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Envia a ordem
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            error = mt5.last_error()
            return {"error": f"Falha ao executar ordem: {error}"}

        return {
            'order_id': result.order,
            'volume': result.volume,
            'price': result.price,
            'bid': result.bid,
            'ask': result.ask,
            'comment': result.comment,
            'retcode': result.retcode,
            'retcode_description': result.retcode_description
        }

    def get_open_positions(self) -> List[Dict]:
        """
        Retorna posições abertas.
        
        Returns:
            list: Lista de posições abertas
        """
        if not MT5_AVAILABLE:
            return [{"error": "MetaTrader5 não está disponível no ambiente."}]

        if not self.connected:
            return [{"error": "Não conectado ao MT5"}]

        positions = mt5.positions_get()
        if positions is None:
            error = mt5.last_error()
            return [{"error": f"Falha ao obter posições: {error}"}]

        return [{
            'ticket': pos.ticket,
            'symbol': pos.symbol,
            'type': "BUY" if pos.type == mt5.POSITION_TYPE_BUY else "SELL",
            'volume': pos.volume,
            'price_open': pos.price_open,
            'price_current': pos.price_current,
            'sl': pos.sl,
            'tp': pos.tp,
            'profit': pos.profit,
            'swap': pos.swap,
            'time': datetime.fromtimestamp(pos.time).isoformat()
        } for pos in positions]

    def close_position(self, ticket: int) -> Dict:
        """
        Fecha uma posição específica.
        
        Args:
            ticket (int): ID da posição
            
        Returns:
            dict: Resultado da operação
        """
        if not MT5_AVAILABLE:
            return {"error": "MetaTrader5 não está disponível no ambiente."}

        if not self.connected:
            return {"error": "Não conectado ao MT5"}

        position = mt5.positions_get(ticket=ticket)
        if position is None:
            error = mt5.last_error()
            return {"error": f"Falha ao obter posição: {error}"}

        if len(position) == 0:
            return {"error": f"Posição {ticket} não encontrada"}

        pos = position[0]
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": ticket,
            "price": mt5.symbol_info_tick(pos.symbol).bid if pos.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(pos.symbol).ask,
            "deviation": 20,
            "magic": 234000,
            "comment": "Close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            error = mt5.last_error()
            return {"error": f"Falha ao fechar posição: {error}"}

        return {
            'order_id': result.order,
            'volume': result.volume,
            'price': result.price,
            'bid': result.bid,
            'ask': result.ask,
            'comment': result.comment,
            'retcode': result.retcode,
            'retcode_description': result.retcode_description
        }

    def get_historical_data(self, 
                          symbol: str,
                          timeframe: str,
                          start_date: datetime,
                          end_date: datetime = None) -> pd.DataFrame:
        """
        Obtém dados históricos de um símbolo.
        
        Args:
            symbol (str): Nome do símbolo
            timeframe (str): Timeframe (ex: "M1", "M5", "H1", "D1")
            start_date (datetime): Data inicial
            end_date (datetime): Data final (opcional)
            
        Returns:
            pd.DataFrame: Dados históricos
        """
        if not MT5_AVAILABLE:
            return pd.DataFrame()

        if not self.connected:
            return pd.DataFrame()

        # Converte timeframe para formato MT5
        tf_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1
        }

        if timeframe not in tf_map:
            return pd.DataFrame()

        # Obtém os dados
        rates = mt5.copy_rates_range(
            symbol,
            tf_map[timeframe],
            start_date,
            end_date if end_date else datetime.now()
        )

        if rates is None:
            return pd.DataFrame()

        # Converte para DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df 