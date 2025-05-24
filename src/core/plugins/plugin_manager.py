"""
Gerenciador de Plugins - Sistema AutoCura
=======================================

Este módulo gerencia o carregamento dinâmico de plugins e módulos do sistema,
permitindo evolução contínua e substituição de componentes.
"""

from typing import Dict, List, Optional, Type, Any
import importlib
import inspect
from pathlib import Path
import logging
from ..interfaces.universal_interface import UniversalModuleInterface, ModuleCapabilities

logger = logging.getLogger(__name__)

class PluginManager:
    """
    Gerenciador de plugins que permite carregamento dinâmico de módulos
    e controle de versões e capacidades.
    """
    
    def __init__(self):
        self.loaded_modules: Dict[str, UniversalModuleInterface] = {}
        self.module_capabilities: Dict[str, ModuleCapabilities] = {}
        self.module_versions: Dict[str, str] = {}
        self._initialize_registry()
    
    def _initialize_registry(self) -> None:
        """Inicializa o registro de módulos"""
        self.loaded_modules = {}
        self.module_capabilities = {}
        self.module_versions = {}
    
    def load_module(self, module_type: str, version: str) -> bool:
        """
        Carrega um módulo específico com sua versão.
        
        Args:
            module_type: Tipo do módulo a ser carregado
            version: Versão do módulo
            
        Returns:
            bool: True se o módulo foi carregado com sucesso
        """
        try:
            # Construir o caminho do módulo
            module_path = f"autocura.modules.{module_type}.v{version}"
            
            # Importar o módulo
            module = importlib.import_module(module_path)
            
            # Encontrar a classe que implementa UniversalModuleInterface
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, UniversalModuleInterface) and 
                    obj != UniversalModuleInterface):
                    
                    # Instanciar o módulo
                    instance = obj()
                    
                    # Registrar no gerenciador
                    self.loaded_modules[module_type] = instance
                    self.module_capabilities[module_type] = instance.get_capabilities()
                    self.module_versions[module_type] = version
                    
                    logger.info(f"Módulo {module_type} v{version} carregado com sucesso")
                    return True
            
            logger.error(f"Nenhuma implementação válida encontrada em {module_path}")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao carregar módulo {module_type} v{version}: {str(e)}")
            return False
    
    def unload_module(self, module_type: str) -> bool:
        """
        Remove um módulo carregado.
        
        Args:
            module_type: Tipo do módulo a ser removido
            
        Returns:
            bool: True se o módulo foi removido com sucesso
        """
        if module_type in self.loaded_modules:
            del self.loaded_modules[module_type]
            del self.module_capabilities[module_type]
            del self.module_versions[module_type]
            logger.info(f"Módulo {module_type} removido com sucesso")
            return True
        return False
    
    def get_module(self, module_type: str) -> Optional[UniversalModuleInterface]:
        """
        Retorna uma instância de um módulo carregado.
        
        Args:
            module_type: Tipo do módulo desejado
            
        Returns:
            Optional[UniversalModuleInterface]: Instância do módulo ou None
        """
        return self.loaded_modules.get(module_type)
    
    def get_module_capabilities(self, module_type: str) -> Optional[ModuleCapabilities]:
        """
        Retorna as capacidades de um módulo.
        
        Args:
            module_type: Tipo do módulo
            
        Returns:
            Optional[ModuleCapabilities]: Capacidades do módulo ou None
        """
        return self.module_capabilities.get(module_type)
    
    def get_module_version(self, module_type: str) -> Optional[str]:
        """
        Retorna a versão de um módulo.
        
        Args:
            module_type: Tipo do módulo
            
        Returns:
            Optional[str]: Versão do módulo ou None
        """
        return self.module_versions.get(module_type)
    
    def list_loaded_modules(self) -> List[Dict[str, Any]]:
        """
        Lista todos os módulos carregados com suas informações.
        
        Returns:
            List[Dict[str, Any]]: Lista de informações dos módulos
        """
        return [
            {
                "type": module_type,
                "version": self.module_versions[module_type],
                "capabilities": self.module_capabilities[module_type]
            }
            for module_type in self.loaded_modules
        ]
    
    def upgrade_module(self, module_type: str, new_version: str) -> bool:
        """
        Atualiza um módulo para uma nova versão.
        
        Args:
            module_type: Tipo do módulo a ser atualizado
            new_version: Nova versão do módulo
            
        Returns:
            bool: True se a atualização foi bem sucedida
        """
        if module_type not in self.loaded_modules:
            logger.error(f"Módulo {module_type} não encontrado para atualização")
            return False
        
        # Fazer backup do módulo atual
        old_module = self.loaded_modules[module_type]
        
        # Tentar carregar a nova versão
        if self.load_module(module_type, new_version):
            logger.info(f"Módulo {module_type} atualizado para v{new_version}")
            return True
        
        # Se falhar, restaurar a versão anterior
        self.loaded_modules[module_type] = old_module
        logger.error(f"Falha ao atualizar módulo {module_type} para v{new_version}")
        return False 