"""
Integração do serviço de diagnóstico com o core do sistema.
"""

from typing import Dict, Any, List
import logging
from .diagnostico_avancado import DiagnosticoAvancado
from .predicao import PredictionManager
from .sintese import SynthesisManager

logger = logging.getLogger(__name__)

class DiagnosticoIntegration:
    """Integração do serviço de diagnóstico com o core do sistema."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa a integração de diagnóstico.
        
        Args:
            config: Configuração do serviço
        """
        self.config = config
        self.diagnostico = DiagnosticoAvancado(config)
        self.predicao = PredictionManager(config)
        self.sintese = SynthesisManager(config)
        
    async def realizar_diagnostico(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza diagnóstico do sistema.
        
        Args:
            dados: Dados para diagnóstico
            
        Returns:
            Resultado do diagnóstico
        """
        try:
            # Realiza diagnóstico avançado
            resultado_diagnostico = await self.diagnostico.analisar(dados)
            
            # Faz predições baseadas no diagnóstico
            predicoes = await self.predicao.prever(resultado_diagnostico)
            
            # Sintetiza resultados
            resultado_final = await self.sintese.sintetizar({
                "diagnostico": resultado_diagnostico,
                "predicoes": predicoes
            })
            
            return resultado_final
            
        except Exception as e:
            logger.error(f"Erro ao realizar diagnóstico: {e}")
            raise 