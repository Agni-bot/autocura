"""
Integração do serviço de IA com o core do sistema.
"""

from typing import Dict, Any, List
import logging
from .consciencia import ConscienciaManager
from .self_modify import SelfModificationManager
from .adaptacao import AdaptationManager

logger = logging.getLogger(__name__)

class IAIntegration:
    """Integração do serviço de IA com o core do sistema."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa a integração de IA.
        
        Args:
            config: Configuração do serviço
        """
        self.config = config
        self.consciencia = ConscienciaManager(config)
        self.self_modify = SelfModificationManager(config)
        self.adaptacao = AdaptationManager(config)
        
    async def processar_entrada(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Processa entrada usando capacidades cognitivas.
        
        Args:
            dados: Dados de entrada
            
        Returns:
            Resultado do processamento
        """
        try:
            # Processa usando consciência
            resultado_consciencia = await self.consciencia.processar(dados)
            
            # Aplica auto-modificação se necessário
            if resultado_consciencia.get("necessita_modificacao", False):
                await self.self_modify.aplicar_modificacao(resultado_consciencia)
            
            # Adapta baseado no resultado
            resultado_adaptado = await self.adaptacao.adaptar(resultado_consciencia)
            
            return resultado_adaptado
            
        except Exception as e:
            logger.error(f"Erro ao processar entrada: {e}")
            raise 