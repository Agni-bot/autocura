"""
MetaTrader 5 Manager Module
Responsible for managing MT5 connection and integrating it with the API.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd

from .mt5_handler import MT5Handler

logger = logging.getLogger("will_mt5_manager")

class MT5Manager:
    """Classe para gerenciar conexão com MT5 e integrar com a API."""

    def __init__(self, config_path: str = None):
        """
        Inicializa o gerenciador MT5.
        
        Args:
            config_path (str): Caminho para o arquivo de configuração
        """
        self.config = self._load_config(config_path)
        self.handler = None
        self._setup_logging()

    def _load_config(self, config_path: str = None) -> Dict:
        """
        Carrega configurações do arquivo YAML.
        
        Args:
            config_path (str): Caminho para o arquivo de configuração
            
        Returns:
            dict: Configurações carregadas
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "mt5_config.yaml"

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config.get('mt5', {})
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {str(e)}")
            return {}

    def _setup_logging(self) -> None:
        """Configura o logging para o MT5."""
        log_config = self.config.get('logging', {})
        if not log_config:
            return

        log_file = log_config.get('file')
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            handler = logging.FileHandler(log_file)
            handler.setFormatter(logging.Formatter(log_config.get('format')))
            logger.addHandler(handler)
            logger.setLevel(log_config.get('level', 'INFO'))

    def connect(self) -> Tuple[bool, str]:
        """
        Conecta ao terminal MT5.
        
        Returns:
            tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            self.handler = MT5Handler(
                server=self.config.get('server'),
                login=self.config.get('login'),
                password=self.config.get('password'),
                path=self.config.get('path')
            )
            return self.handler.connect()
        except Exception as e:
            logger.error(f"Erro ao conectar ao MT5: {str(e)}")
            return False, f"Erro ao conectar: {str(e)}"

    def disconnect(self) -> None:
        """Desconecta do terminal MT5."""
        if self.handler:
            self.handler.disconnect()
            self.handler = None

    def get_account_info(self) -> Dict:
        """
        Retorna informações da conta.
        
        Returns:
            dict: Informações da conta
        """
        if not self.handler:
            return {"error": "MT5 não conectado"}

        return self.handler.get_account_info()

    def get_symbol_info(self, symbol: str) -> Dict:
        """
        Retorna informações de um símbolo.
        
        Args:
            symbol (str): Nome do símbolo
            
        Returns:
            dict: Informações do símbolo
        """
        if not self.handler:
            return {"error": "MT5 não conectado"}

        return self.handler.get_symbol_info(symbol)

    def get_current_price(self, symbol: str) -> Dict:
        """
        Retorna preço atual de um símbolo.
        
        Args:
            symbol (str): Nome do símbolo
            
        Returns:
            dict: Preço atual
        """
        if not self.handler:
            return {"error": "MT5 não conectado"}

        return self.handler.get_current_price(symbol)

    def place_order(self, 
                   symbol: str,
                   order_type: str,
                   volume: float = None,
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
            price (float): Preço da ordem
            sl (float): Stop Loss
            tp (float): Take Profit
            comment (str): Comentário da ordem
            
        Returns:
            dict: Resultado da ordem
        """
        if not self.handler:
            return {"error": "MT5 não conectado"}

        # Usa volume padrão se não especificado
        if volume is None:
            volume = self.config.get('trading', {}).get('default_volume', 0.1)

        return self.handler.place_order(
            symbol=symbol,
            order_type=order_type,
            volume=volume,
            price=price,
            sl=sl,
            tp=tp,
            comment=comment
        )

    def get_open_positions(self) -> List[Dict]:
        """
        Retorna posições abertas.
        
        Returns:
            list: Lista de posições abertas
        """
        if not self.handler:
            return [{"error": "MT5 não conectado"}]

        return self.handler.get_open_positions()

    def close_position(self, ticket: int) -> Dict:
        """
        Fecha uma posição.
        
        Args:
            ticket (int): ID da posição
            
        Returns:
            dict: Resultado da operação
        """
        if not self.handler:
            return {"error": "MT5 não conectado"}

        return self.handler.close_position(ticket)

    def get_historical_data(self, 
                          symbol: str,
                          timeframe: str,
                          start_date: datetime,
                          end_date: datetime = None) -> pd.DataFrame:
        """
        Obtém dados históricos.
        
        Args:
            symbol (str): Nome do símbolo
            timeframe (str): Timeframe
            start_date (datetime): Data inicial
            end_date (datetime): Data final
            
        Returns:
            pd.DataFrame: Dados históricos
        """
        if not self.handler:
            return pd.DataFrame()

        return self.handler.get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date
        )

    def get_available_symbols(self) -> Dict[str, List[str]]:
        """
        Retorna lista de símbolos disponíveis.
        
        Returns:
            dict: Dicionário com símbolos major e minor
        """
        return self.config.get('symbols', {'major': [], 'minor': []})

    def get_available_timeframes(self) -> List[str]:
        """
        Retorna lista de timeframes disponíveis.
        
        Returns:
            list: Lista de timeframes
        """
        return self.config.get('timeframes', []) 