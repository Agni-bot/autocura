"""
Testes do Sistema AutoCura
=========================

Testes unitários e de integração para os componentes principais
do sistema de autocura.
"""

import pytest
from datetime import datetime
from typing import Dict

from src.core.interfaces.universal_interface import UniversalModuleInterface
from src.core.plugins.plugin_manager import PluginManager
from src.core.registry.capability_registry import CapabilityRegistry, TechnologyType
from src.versioning.version_manager import VersionManager, VersionType
from src.main import AutoCura

# Fixtures
@pytest.fixture
def autocura():
    """Fixture que fornece uma instância do sistema AutoCura."""
    return AutoCura()

@pytest.fixture
def config():
    """Fixture que fornece configurações de teste."""
    return {
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "capabilities": {
            "classical_computing": True,
            "quantum_computing": False,
            "nano_technology": False,
            "bio_computing": False
        }
    }

# Testes de Inicialização
def test_autocura_initialization(autocura):
    """Testa a inicialização básica do sistema."""
    assert autocura._initialized == False
    assert autocura._running == False
    assert isinstance(autocura.interface, UniversalModuleInterface)
    assert isinstance(autocura.plugin_manager, PluginManager)
    assert isinstance(autocura.capability_registry, CapabilityRegistry)
    assert isinstance(autocura.version_manager, VersionManager)

def test_autocura_initialize_with_config(autocura, config):
    """Testa a inicialização do sistema com configurações."""
    assert autocura.initialize(config) == True
    assert autocura._initialized == True
    assert autocura._config == config

def test_autocura_initialize_without_config(autocura):
    """Testa a inicialização do sistema sem configurações."""
    assert autocura.initialize() == True
    assert autocura._initialized == True
    assert autocura._config == {}

# Testes de Capacidades
def test_register_base_capabilities(autocura):
    """Testa o registro de capacidades base."""
    autocura.initialize()
    capabilities = autocura.capability_registry.list_capabilities()
    
    # Verifica capacidades clássicas
    classical = next(c for c in capabilities if c.name == "classical_computing")
    assert classical.enabled == True
    
    # Verifica capacidades em desenvolvimento
    quantum = next(c for c in capabilities if c.name == "quantum_computing")
    assert quantum.enabled == False
    assert quantum.type == TechnologyType.QUANTUM

def test_upgrade_capability(autocura):
    """Testa o upgrade de uma capacidade."""
    autocura.initialize()
    
    # Tenta fazer upgrade de uma capacidade inexistente
    assert autocura.upgrade_capability("inexistente") == False
    
    # Tenta fazer upgrade de uma capacidade existente
    assert autocura.upgrade_capability("classical_computing") == True
    capability = autocura.capability_registry.get_capability("classical_computing")
    assert capability.enabled == True

# Testes de Versionamento
def test_version_compatibility(autocura):
    """Testa a compatibilidade entre versões."""
    autocura.initialize()
    versions = autocura.version_manager.list_versions()
    
    # Verifica versão do core
    core_version = next(v for v in versions if v.component == "core")
    assert core_version.is_stable == True
    assert core_version.type == VersionType.MAJOR
    
    # Verifica versões em desenvolvimento
    quantum_version = next(v for v in versions if v.component == "quantum")
    assert quantum_version.is_stable == False
    assert quantum_version.type == VersionType.ALPHA

# Testes de Estado
def test_system_status(autocura):
    """Testa o retorno do status do sistema."""
    autocura.initialize()
    status = autocura.get_status()
    
    assert isinstance(status, dict)
    assert "initialized" in status
    assert "running" in status
    assert "capabilities" in status
    assert "versions" in status
    
    assert status["initialized"] == True
    assert status["running"] == False

def test_start_stop_system(autocura):
    """Testa o início e parada do sistema."""
    autocura.initialize()
    
    # Testa início
    assert autocura.start() == True
    assert autocura._running == True
    
    # Testa parada
    assert autocura.stop() == True
    assert autocura._running == False

# Testes de Integração
def test_full_system_cycle(autocura, config):
    """Testa um ciclo completo do sistema."""
    # Inicialização
    assert autocura.initialize(config) == True
    
    # Início
    assert autocura.start() == True
    
    # Verifica status
    status = autocura.get_status()
    assert status["initialized"] == True
    assert status["running"] == True
    
    # Tenta upgrade de capacidade
    assert autocura.upgrade_capability("classical_computing") == True
    
    # Parada
    assert autocura.stop() == True
    
    # Verifica status final
    status = autocura.get_status()
    assert status["running"] == False

# Testes de Erro
def test_error_handling(autocura):
    """Testa o tratamento de erros do sistema."""
    # Tenta iniciar sem inicializar
    assert autocura.start() == False
    
    # Tenta parar sem iniciar
    assert autocura.stop() == True  # Deve retornar True pois já está parado
    
    # Tenta upgrade de capacidade inexistente
    assert autocura.upgrade_capability("inexistente") == False

if __name__ == "__main__":
    pytest.main([__file__]) 