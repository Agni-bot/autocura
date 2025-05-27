"""
Interface Universal de Módulos - Sistema AutoCura
===============================================

Esta interface define o contrato base para todos os módulos do sistema,
preparando-o para evolução futura com tecnologias quânticas e nanotecnológicas.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol
from dataclasses import dataclass
from enum import Enum

class TechnologyReadiness(Enum):
    """Níveis de prontidão tecnológica dos módulos"""
    CLASSICAL = 1
    QUANTUM_READY = 2
    QUANTUM_ENABLED = 3
    NANO_READY = 4
    NANO_ENABLED = 5
    BIO_READY = 6
    BIO_ENABLED = 7

@dataclass
class ModuleCapabilities:
    """Capacidades disponíveis em um módulo"""
    quantum_ready: bool = False
    nano_ready: bool = False
    bio_ready: bool = False
    neuromorphic_ready: bool = False

class QuantumReadyInterface(Protocol):
    """Interface preparada para computação quântica"""
    def quantum_process(self, qubits: Any) -> Any: ...
    def quantum_validate(self, data: Any) -> bool: ...
    def quantum_optimize(self, parameters: Dict) -> Dict: ...

class NanoInterface(Protocol):
    """Interface para sistemas nanotecnológicos"""
    def nano_interact(self, particles: Any) -> Any: ...
    def nano_validate(self, data: Any) -> bool: ...
    def nano_optimize(self, parameters: Dict) -> Dict: ...

class BioInterface(Protocol):
    """Interface para biocomputação"""
    def bio_process(self, data: Any) -> Any: ...
    def bio_validate(self, data: Any) -> bool: ...
    def bio_optimize(self, parameters: Dict) -> Dict: ...

class UniversalModuleInterface(ABC):
    """
    Interface base para todos os módulos do sistema.
    Implementa capacidades clássicas e prepara para futuras tecnologias.
    """
    
    def __init__(self):
        self.capabilities = ModuleCapabilities()
        self.technology_readiness = TechnologyReadiness.CLASSICAL
        self._initialize_capabilities()
    
    def _initialize_capabilities(self) -> None:
        """Inicializa as capacidades do módulo"""
        # Por padrão, todos os módulos começam apenas com capacidades clássicas
        self.capabilities = ModuleCapabilities()
    
    @abstractmethod
    def process_classical(self, data: Dict) -> Dict:
        """
        Processamento clássico padrão.
        
        Args:
            data: Dados a serem processados
            
        Returns:
            Dict: Resultado do processamento
        """
        pass
    
    @abstractmethod
    def process_quantum(self, data: Any) -> Any:
        """
        Preparação para processamento quântico.
        
        Args:
            data: Dados a serem processados
            
        Returns:
            Any: Resultado do processamento
            
        Raises:
            NotImplementedError: Se processamento quântico não estiver disponível
        """
        raise NotImplementedError("Quantum processing not yet available")
    
    @abstractmethod
    def process_nano(self, data: Any) -> Any:
        """
        Preparação para interação nano.
        
        Args:
            data: Dados a serem processados
            
        Returns:
            Any: Resultado do processamento
            
        Raises:
            NotImplementedError: Se processamento nano não estiver disponível
        """
        raise NotImplementedError("Nano processing not yet available")
    
    @abstractmethod
    def process_bio(self, data: Any) -> Any:
        """
        Preparação para processamento bio.
        
        Args:
            data: Dados a serem processados
            
        Returns:
            Any: Resultado do processamento
            
        Raises:
            NotImplementedError: Se processamento bio não estiver disponível
        """
        raise NotImplementedError("Bio processing not yet available")
    
    def upgrade_capability(self, capability: str) -> bool:
        """
        Atualiza uma capacidade específica do módulo.
        
        Args:
            capability: Nome da capacidade a ser atualizada
            
        Returns:
            bool: True se a atualização foi bem sucedida
        """
        if capability == "quantum":
            self.capabilities.quantum_ready = True
            self.technology_readiness = TechnologyReadiness.QUANTUM_READY
        elif capability == "nano":
            self.capabilities.nano_ready = True
            self.technology_readiness = TechnologyReadiness.NANO_READY
        elif capability == "bio":
            self.capabilities.bio_ready = True
            self.technology_readiness = TechnologyReadiness.BIO_READY
        else:
            return False
        return True
    
    def get_capabilities(self) -> ModuleCapabilities:
        """
        Retorna as capacidades atuais do módulo.
        
        Returns:
            ModuleCapabilities: Objeto contendo as capacidades
        """
        return self.capabilities
    
    def get_technology_readiness(self) -> TechnologyReadiness:
        """
        Retorna o nível de prontidão tecnológica do módulo.
        
        Returns:
            TechnologyReadiness: Nível atual de prontidão
        """
        return self.technology_readiness 