from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseProcessador(ABC):
    """Interface base para processadores de métricas."""
    
    @abstractmethod
    async def processar(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Processa os dados coletados.
        
        Args:
            dados (Dict[str, Any]): Dados a serem processados
            
        Returns:
            Dict[str, Any]: Dados processados
        """
        pass
    
    @abstractmethod
    async def validar(self) -> bool:
        """Valida se o processador está funcionando corretamente.
        
        Returns:
            bool: True se o processador está funcionando, False caso contrário
        """
        pass
    
    @abstractmethod
    def get_metadados(self) -> Dict[str, Any]:
        """Retorna metadados do processador.
        
        Returns:
            Dict[str, Any]: Metadados do processador
        """
        pass
    
    @abstractmethod
    def get_operacoes_suportadas(self) -> List[str]:
        """Retorna lista de operações suportadas pelo processador.
        
        Returns:
            List[str]: Lista de operações suportadas
        """
        pass 