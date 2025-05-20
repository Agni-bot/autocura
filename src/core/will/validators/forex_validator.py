"""
Forex Validator Module
Responsible for validating forex currency pairs and trading parameters.
"""

# Lista de moedas principais do Forex
MAJOR_CURRENCIES = {
    'USD': 'US Dollar',
    'EUR': 'Euro',
    'GBP': 'British Pound',
    'JPY': 'Japanese Yen',
    'AUD': 'Australian Dollar',
    'CAD': 'Canadian Dollar',
    'CHF': 'Swiss Franc',
    'NZD': 'New Zealand Dollar'
}

# Pares de moedas mais negociados (Majors)
MAJOR_PAIRS = [
    'EUR/USD',  # Euro / US Dollar
    'GBP/USD',  # British Pound / US Dollar
    'USD/JPY',  # US Dollar / Japanese Yen
    'USD/CHF',  # US Dollar / Swiss Franc
    'AUD/USD',  # Australian Dollar / US Dollar
    'USD/CAD',  # US Dollar / Canadian Dollar
    'NZD/USD',  # New Zealand Dollar / US Dollar
]

# Pares de moedas secundários (Minors)
MINOR_PAIRS = [
    'EUR/GBP',  # Euro / British Pound
    'EUR/JPY',  # Euro / Japanese Yen
    'GBP/JPY',  # British Pound / Japanese Yen
    'EUR/AUD',  # Euro / Australian Dollar
    'EUR/CAD',  # Euro / Canadian Dollar
    'EUR/CHF',  # Euro / Swiss Franc
    'GBP/CHF',  # British Pound / Swiss Franc
]

# Todos os pares válidos
VALID_PAIRS = MAJOR_PAIRS + MINOR_PAIRS

class ForexValidator:
    """Classe para validação de pares de moedas e parâmetros de trading forex."""

    @staticmethod
    def validate_currency_pair(pair: str) -> tuple[bool, str]:
        """
        Valida se um par de moedas é válido para trading.
        
        Args:
            pair (str): Par de moedas no formato 'XXX/YYY'
            
        Returns:
            tuple[bool, str]: (é_válido, mensagem_erro)
        """
        if not isinstance(pair, str):
            return False, "Par de moedas deve ser uma string"
            
        if '/' not in pair:
            return False, "Formato inválido. Use 'XXX/YYY'"
            
        base, quote = pair.split('/')
        
        if len(base) != 3 or len(quote) != 3:
            return False, "Códigos de moeda devem ter 3 caracteres"
            
        if base not in MAJOR_CURRENCIES:
            return False, f"Moeda base '{base}' não é uma moeda principal"
            
        if quote not in MAJOR_CURRENCIES:
            return False, f"Moeda quote '{quote}' não é uma moeda principal"
            
        if base == quote:
            return False, "Moeda base e quote não podem ser iguais"
            
        if pair not in VALID_PAIRS:
            return False, f"Par '{pair}' não é um par de moedas negociado"
            
        return True, ""

    @staticmethod
    def validate_volume(volume: float) -> tuple[bool, str]:
        """
        Valida o volume de trading.
        
        Args:
            volume (float): Volume em unidades da moeda base
            
        Returns:
            tuple[bool, str]: (é_válido, mensagem_erro)
        """
        if not isinstance(volume, (int, float)):
            return False, "Volume deve ser um número"
            
        if volume <= 0:
            return False, "Volume deve ser positivo"
            
        # Volume mínimo de 1000 unidades
        if volume < 1000:
            return False, "Volume mínimo é 1000 unidades"
            
        # Volume máximo de 1000000 unidades
        if volume > 1000000:
            return False, "Volume máximo é 1000000 unidades"
            
        return True, ""

    @staticmethod
    def get_pair_info(pair: str) -> dict:
        """
        Retorna informações sobre um par de moedas.
        
        Args:
            pair (str): Par de moedas no formato 'XXX/YYY'
            
        Returns:
            dict: Informações sobre o par
        """
        if pair not in VALID_PAIRS:
            return {}
            
        base, quote = pair.split('/')
        
        return {
            'pair': pair,
            'base_currency': {
                'code': base,
                'name': MAJOR_CURRENCIES[base]
            },
            'quote_currency': {
                'code': quote,
                'name': MAJOR_CURRENCIES[quote]
            },
            'type': 'MAJOR' if pair in MAJOR_PAIRS else 'MINOR',
            'typical_spread': 0.0002 if pair in MAJOR_PAIRS else 0.0003,
            'min_trade_size': 1000,
            'max_trade_size': 1000000
        }

    @staticmethod
    def get_all_valid_pairs() -> list:
        """
        Retorna lista de todos os pares válidos.
        
        Returns:
            list: Lista de pares válidos
        """
        return VALID_PAIRS

    @staticmethod
    def get_major_pairs() -> list:
        """
        Retorna lista de pares principais.
        
        Returns:
            list: Lista de pares principais
        """
        return MAJOR_PAIRS

    @staticmethod
    def get_minor_pairs() -> list:
        """
        Retorna lista de pares secundários.
        
        Returns:
            list: Lista de pares secundários
        """
        return MINOR_PAIRS 