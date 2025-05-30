"""
Integração do serviço de memória com o core do sistema.
"""

from typing import Dict, Any, List
import logging
from .memoria import MemoryManager
from .cache import CacheManager
from .serialization import SerializationManager

logger = logging.getLogger(__name__)

class MemoriaIntegration:
    """Integração do serviço de memória com o core do sistema."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa a integração de memória.
        
        Args:
            config: Configuração do serviço
        """
        self.config = config
        self.memoria = MemoryManager(config)
        self.cache = CacheManager(config)
        self.serializacao = SerializationManager(config)
        
    async def armazenar_dados(self, dados: Dict[str, Any]) -> bool:
        """Armazena dados na memória.
        
        Args:
            dados: Dados a serem armazenados
            
        Returns:
            True se os dados foram armazenados com sucesso
        """
        try:
            # Serializa os dados
            dados_serializados = await self.serializacao.serializar(dados)
            
            # Armazena em cache se necessário
            if self.config.get("usar_cache", True):
                await self.cache.armazenar(dados_serializados)
            
            # Armazena na memória principal
            await self.memoria.armazenar(dados_serializados)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao armazenar dados: {e}")
            return False
            
    async def recuperar_dados(self, chave: str) -> Dict[str, Any]:
        """Recupera dados da memória.
        
        Args:
            chave: Chave dos dados
            
        Returns:
            Dados recuperados
        """
        try:
            # Tenta recuperar do cache
            if self.config.get("usar_cache", True):
                dados = await self.cache.recuperar(chave)
                if dados:
                    return await self.serializacao.desserializar(dados)
            
            # Recupera da memória principal
            dados = await self.memoria.recuperar(chave)
            return await self.serializacao.desserializar(dados)
            
        except Exception as e:
            logger.error(f"Erro ao recuperar dados: {e}")
            raise 