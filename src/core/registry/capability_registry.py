"""
Registro de Capacidades - Sistema AutoCura
========================================

Este módulo mantém o registro central de capacidades tecnológicas disponíveis
no sistema, permitindo controle granular sobre recursos e evolução.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TechnologyType(Enum):
    """Tipos de tecnologias suportadas"""
    CLASSICAL = "classical"
    QUANTUM = "quantum"
    NANO = "nano"
    BIO = "bio"
    NEUROMORPHIC = "neuromorphic"

@dataclass
class TechnologyCapability:
    """Informações sobre uma capacidade tecnológica"""
    name: str
    type: TechnologyType
    version: str
    enabled: bool = False
    last_updated: datetime = field(default_factory=datetime.now)
    dependencies: Set[str] = field(default_factory=set)
    requirements: Dict[str, str] = field(default_factory=dict)

class CapabilityRegistry:
    """
    Registro central de capacidades tecnológicas do sistema.
    Gerencia disponibilidade e dependências entre tecnologias.
    """
    
    def __init__(self):
        self._capabilities: Dict[str, TechnologyCapability] = {}
        self._initialize_capabilities()
    
    def _initialize_capabilities(self) -> None:
        """Inicializa o registro com capacidades base"""
        # Capacidades clássicas sempre disponíveis
        self._capabilities = {
            "classical_computing": TechnologyCapability(
                name="Computação Clássica",
                type=TechnologyType.CLASSICAL,
                version="1.0",
                enabled=True
            ),
            "quantum_computing": TechnologyCapability(
                name="Computação Quântica",
                type=TechnologyType.QUANTUM,
                version="0.1",
                enabled=False,
                requirements={
                    "quantum_hardware": "required",
                    "quantum_software": "required"
                }
            ),
            "nano_technology": TechnologyCapability(
                name="Nanotecnologia",
                type=TechnologyType.NANO,
                version="0.1",
                enabled=False,
                requirements={
                    "nano_controllers": "required",
                    "nano_sensors": "required"
                }
            ),
            "bio_computing": TechnologyCapability(
                name="Biocomputação",
                type=TechnologyType.BIO,
                version="0.1",
                enabled=False,
                requirements={
                    "bio_interface": "required",
                    "bio_processors": "required"
                }
            ),
            "neuromorphic_computing": TechnologyCapability(
                name="Computação Neuromórfica",
                type=TechnologyType.NEUROMORPHIC,
                version="0.1",
                enabled=False,
                requirements={
                    "neuromorphic_hardware": "required",
                    "neural_models": "required"
                }
            )
        }
    
    def register_capability(self, capability: TechnologyCapability) -> bool:
        """
        Registra uma nova capacidade tecnológica.
        
        Args:
            capability: Capacidade a ser registrada
            
        Returns:
            bool: True se o registro foi bem sucedido
        """
        if capability.name in self._capabilities:
            logger.warning(f"Capacidade {capability.name} já registrada")
            return False
        
        self._capabilities[capability.name] = capability
        logger.info(f"Capacidade {capability.name} registrada com sucesso")
        return True
    
    def enable_capability(self, name: str) -> bool:
        """
        Habilita uma capacidade tecnológica.
        
        Args:
            name: Nome da capacidade
            
        Returns:
            bool: True se a habilitação foi bem sucedida
        """
        if name not in self._capabilities:
            logger.error(f"Capacidade {name} não encontrada")
            return False
        
        capability = self._capabilities[name]
        
        # Verificar dependências
        for dep in capability.dependencies:
            if dep not in self._capabilities or not self._capabilities[dep].enabled:
                logger.error(f"Dependência {dep} não satisfeita para {name}")
                return False
        
        # Verificar requisitos
        for req, status in capability.requirements.items():
            if status == "required" and req not in self._capabilities:
                logger.error(f"Requisito {req} não satisfeito para {name}")
                return False
        
        capability.enabled = True
        capability.last_updated = datetime.now()
        logger.info(f"Capacidade {name} habilitada com sucesso")
        return True
    
    def disable_capability(self, name: str) -> bool:
        """
        Desabilita uma capacidade tecnológica.
        
        Args:
            name: Nome da capacidade
            
        Returns:
            bool: True se a desabilitação foi bem sucedida
        """
        if name not in self._capabilities:
            logger.error(f"Capacidade {name} não encontrada")
            return False
        
        capability = self._capabilities[name]
        capability.enabled = False
        capability.last_updated = datetime.now()
        logger.info(f"Capacidade {name} desabilitada com sucesso")
        return True
    
    def get_capability(self, name: str) -> Optional[TechnologyCapability]:
        """
        Retorna informações sobre uma capacidade.
        
        Args:
            name: Nome da capacidade
            
        Returns:
            Optional[TechnologyCapability]: Informações da capacidade ou None
        """
        return self._capabilities.get(name)
    
    def list_capabilities(self, 
                         enabled_only: bool = False,
                         type_filter: Optional[TechnologyType] = None) -> List[TechnologyCapability]:
        """
        Lista capacidades registradas com filtros opcionais.
        
        Args:
            enabled_only: Se True, retorna apenas capacidades habilitadas
            type_filter: Filtra por tipo de tecnologia
            
        Returns:
            List[TechnologyCapability]: Lista de capacidades
        """
        capabilities = self._capabilities.values()
        
        if enabled_only:
            capabilities = [c for c in capabilities if c.enabled]
        
        if type_filter:
            capabilities = [c for c in capabilities if c.type == type_filter]
        
        return list(capabilities)
    
    def add_dependency(self, capability: str, dependency: str) -> bool:
        """
        Adiciona uma dependência entre capacidades.
        
        Args:
            capability: Nome da capacidade
            dependency: Nome da dependência
            
        Returns:
            bool: True se a dependência foi adicionada
        """
        if capability not in self._capabilities or dependency not in self._capabilities:
            logger.error("Capacidade ou dependência não encontrada")
            return False
        
        self._capabilities[capability].dependencies.add(dependency)
        logger.info(f"Dependência {dependency} adicionada a {capability}")
        return True
    
    def remove_dependency(self, capability: str, dependency: str) -> bool:
        """
        Remove uma dependência entre capacidades.
        
        Args:
            capability: Nome da capacidade
            dependency: Nome da dependência
            
        Returns:
            bool: True se a dependência foi removida
        """
        if capability not in self._capabilities:
            logger.error(f"Capacidade {capability} não encontrada")
            return False
        
        if dependency in self._capabilities[capability].dependencies:
            self._capabilities[capability].dependencies.remove(dependency)
            logger.info(f"Dependência {dependency} removida de {capability}")
            return True
        
        return False 