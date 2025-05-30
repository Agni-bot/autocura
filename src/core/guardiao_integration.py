"""
Integração do serviço guardião com o core do sistema.
"""

from typing import Dict, Any, List
import logging
from .sandbox import SandboxManager
from .plugins import PluginManager
from .versioning import VersionManager

logger = logging.getLogger(__name__)

class GuardiaoIntegration:
    """Integração do serviço guardião com o core do sistema."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa a integração do guardião.
        
        Args:
            config: Configuração do serviço
        """
        self.config = config
        self.sandbox = SandboxManager(config)
        self.plugins = PluginManager(config)
        self.versioning = VersionManager(config)
        
    async def proteger_sistema(self, acao: Dict[str, Any]) -> Dict[str, Any]:
        """Protege o sistema executando ações em ambiente seguro.
        
        Args:
            acao: Ação a ser executada
            
        Returns:
            Resultado da execução
        """
        try:
            # Verifica versão
            versao_atual = await self.versioning.verificar_versao()
            
            # Carrega plugins necessários
            plugins = await self.plugins.carregar_plugins(acao)
            
            # Executa em sandbox
            resultado = await self.sandbox.executar(acao, plugins)
            
            # Registra versão
            await self.versioning.registrar_execucao(versao_atual)
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao proteger sistema: {e}")
            raise 