from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseColetor(ABC):
    """Interface base para coletores de métricas."""
    
    @abstractmethod
    async def coletar(self) -> Dict[str, Any]:
        """Coleta métricas do sistema.
        
        Returns:
            Dict[str, Any]: Dicionário com as métricas coletadas
        """
        pass
    
    @abstractmethod
    async def validar(self) -> bool:
        """Valida se o coletor está funcionando corretamente.
        
        Returns:
            bool: True se o coletor está funcionando, False caso contrário
        """
        pass
    
    @abstractmethod
    def get_metadados(self) -> Dict[str, Any]:
        """Retorna metadados do coletor.
        
        Returns:
            Dict[str, Any]: Metadados do coletor
        """
        pass
    
    @abstractmethod
    def get_metricas_suportadas(self) -> List[str]:
        """Retorna lista de métricas suportadas pelo coletor.
        
        Returns:
            List[str]: Lista de métricas suportadas
        """
        pass 