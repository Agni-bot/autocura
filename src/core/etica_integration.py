"""
Integração do serviço ético com o core do sistema.
"""

from typing import Dict, Any, List
import logging
from .validacao import ValidationManager
from .interpretabilidade import InterpretabilityManager

logger = logging.getLogger(__name__)

class EticaIntegration:
    """Integração do serviço ético com o core do sistema."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa a integração ética.
        
        Args:
            config: Configuração do serviço
        """
        self.config = config
        self.validacao = ValidationManager(config)
        self.interpretabilidade = InterpretabilityManager(config)
        
    async def validar_acao(self, acao: Dict[str, Any]) -> Dict[str, Any]:
        """Valida uma ação sob aspectos éticos.
        
        Args:
            acao: Ação a ser validada
            
        Returns:
            Resultado da validação
        """
        try:
            # Valida a ação
            resultado_validacao = await self.validacao.validar(acao)
            
            # Gera explicação se necessário
            if resultado_validacao.get("necessita_explicacao", False):
                explicacao = await self.interpretabilidade.explicar(acao)
                resultado_validacao["explicacao"] = explicacao
            
            return resultado_validacao
            
        except Exception as e:
            logger.error(f"Erro ao validar ação: {e}")
            raise 