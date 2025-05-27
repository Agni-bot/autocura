"""
Sistema de Versionamento - Sistema AutoCura
=========================================

Este módulo gerencia o versionamento de componentes do sistema,
permitindo controle granular sobre evolução e compatibilidade.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import semver

logger = logging.getLogger(__name__)

class VersionType(Enum):
    """Tipos de versionamento suportados"""
    MAJOR = "major"  # Mudanças incompatíveis
    MINOR = "minor"  # Novas funcionalidades compatíveis
    PATCH = "patch"  # Correções de bugs
    ALPHA = "alpha"  # Versões de desenvolvimento
    BETA = "beta"    # Versões de teste
    RC = "rc"        # Versões candidatas

@dataclass
class VersionInfo:
    """Informações de versão de um componente"""
    component: str
    version: str
    type: VersionType
    release_date: datetime = field(default_factory=datetime.now)
    dependencies: Dict[str, str] = field(default_factory=dict)
    changelog: List[str] = field(default_factory=list)
    is_stable: bool = False

class VersionManager:
    """
    Gerenciador de versões do sistema.
    Controla evolução e compatibilidade entre componentes.
    """
    
    def __init__(self):
        self._versions: Dict[str, VersionInfo] = {}
        self._initialize_versions()
    
    def _initialize_versions(self) -> None:
        """Inicializa o sistema com versões base"""
        self._versions = {
            "core": VersionInfo(
                component="core",
                version="1.0.0",
                type=VersionType.MAJOR,
                is_stable=True,
                changelog=["Versão inicial do sistema"]
            ),
            "quantum": VersionInfo(
                component="quantum",
                version="0.1.0-alpha",
                type=VersionType.ALPHA,
                dependencies={"core": ">=1.0.0"},
                changelog=["Implementação inicial do módulo quântico"]
            ),
            "nano": VersionInfo(
                component="nano",
                version="0.1.0-alpha",
                type=VersionType.ALPHA,
                dependencies={"core": ">=1.0.0"},
                changelog=["Implementação inicial do módulo nano"]
            ),
            "bio": VersionInfo(
                component="bio",
                version="0.1.0-alpha",
                type=VersionType.ALPHA,
                dependencies={"core": ">=1.0.0"},
                changelog=["Implementação inicial do módulo bio"]
            )
        }
    
    def register_version(self, version_info: VersionInfo) -> bool:
        """
        Registra uma nova versão de componente.
        
        Args:
            version_info: Informações da versão
            
        Returns:
            bool: True se o registro foi bem sucedido
        """
        if version_info.component in self._versions:
            current = self._versions[version_info.component]
            if not self._is_version_compatible(current.version, version_info.version):
                logger.error(f"Versão {version_info.version} incompatível com {current.version}")
                return False
        
        self._versions[version_info.component] = version_info
        logger.info(f"Versão {version_info.version} do componente {version_info.component} registrada")
        return True
    
    def _is_version_compatible(self, current: str, new: str) -> bool:
        """
        Verifica compatibilidade entre versões.
        
        Args:
            current: Versão atual
            new: Nova versão
            
        Returns:
            bool: True se as versões são compatíveis
        """
        try:
            current_ver = semver.VersionInfo.parse(current)
            new_ver = semver.VersionInfo.parse(new)
            
            # Versões alpha/beta/rc são sempre compatíveis entre si
            if "-" in current or "-" in new:
                return True
            
            # Major version deve ser igual para compatibilidade
            if current_ver.major != new_ver.major:
                return False
            
            # Minor version deve ser maior ou igual
            if new_ver.minor < current_ver.minor:
                return False
            
            return True
            
        except ValueError as e:
            logger.error(f"Erro ao comparar versões: {e}")
            return False
    
    def get_version(self, component: str) -> Optional[VersionInfo]:
        """
        Retorna informações sobre a versão de um componente.
        
        Args:
            component: Nome do componente
            
        Returns:
            Optional[VersionInfo]: Informações da versão ou None
        """
        return self._versions.get(component)
    
    def list_versions(self, 
                     stable_only: bool = False,
                     type_filter: Optional[VersionType] = None) -> List[VersionInfo]:
        """
        Lista versões registradas com filtros opcionais.
        
        Args:
            stable_only: Se True, retorna apenas versões estáveis
            type_filter: Filtra por tipo de versão
            
        Returns:
            List[VersionInfo]: Lista de versões
        """
        versions = self._versions.values()
        
        if stable_only:
            versions = [v for v in versions if v.is_stable]
        
        if type_filter:
            versions = [v for v in versions if v.type == type_filter]
        
        return list(versions)
    
    def add_dependency(self, component: str, dependency: str, version_constraint: str) -> bool:
        """
        Adiciona uma dependência entre componentes.
        
        Args:
            component: Nome do componente
            dependency: Nome da dependência
            version_constraint: Restrição de versão (ex: ">=1.0.0")
            
        Returns:
            bool: True se a dependência foi adicionada
        """
        if component not in self._versions:
            logger.error(f"Componente {component} não encontrado")
            return False
        
        self._versions[component].dependencies[dependency] = version_constraint
        logger.info(f"Dependência {dependency} {version_constraint} adicionada a {component}")
        return True
    
    def remove_dependency(self, component: str, dependency: str) -> bool:
        """
        Remove uma dependência entre componentes.
        
        Args:
            component: Nome do componente
            dependency: Nome da dependência
            
        Returns:
            bool: True se a dependência foi removida
        """
        if component not in self._versions:
            logger.error(f"Componente {component} não encontrado")
            return False
        
        if dependency in self._versions[component].dependencies:
            del self._versions[component].dependencies[dependency]
            logger.info(f"Dependência {dependency} removida de {component}")
            return True
        
        return False
    
    def add_changelog_entry(self, component: str, entry: str) -> bool:
        """
        Adiciona uma entrada no changelog de um componente.
        
        Args:
            component: Nome do componente
            entry: Entrada do changelog
            
        Returns:
            bool: True se a entrada foi adicionada
        """
        if component not in self._versions:
            logger.error(f"Componente {component} não encontrado")
            return False
        
        self._versions[component].changelog.append(entry)
        logger.info(f"Entrada adicionada ao changelog de {component}")
        return True
    
    def get_changelog(self, component: str) -> Optional[List[str]]:
        """
        Retorna o changelog de um componente.
        
        Args:
            component: Nome do componente
            
        Returns:
            Optional[List[str]]: Lista de entradas do changelog ou None
        """
        if component not in self._versions:
            return None
        
        return self._versions[component].changelog 