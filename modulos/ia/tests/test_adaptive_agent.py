import pytest
from typing import Dict, Any
from ..src.agents.adaptive_agent import AdaptiveAgent

@pytest.fixture
def agent():
    return AdaptiveAgent()

def test_agent_initialization(agent):
    """Testa inicialização do agente."""
    assert agent.evolution_level == 1
    assert isinstance(agent.capabilities, dict)
    assert "quantum" in agent.capabilities
    assert "nano" in agent.capabilities
    assert "bio" in agent.capabilities

def test_detect_capabilities(agent):
    """Testa detecção de capacidades."""
    capabilities = agent._detect_capabilities()
    assert isinstance(capabilities, dict)
    assert all(isinstance(v, bool) for v in capabilities.values())

def test_process_with_best_available(agent):
    """Testa processamento com melhor tecnologia disponível."""
    input_data = {"test": "data"}
    result = agent.process_with_best_available(input_data)
    assert isinstance(result, dict)
    assert "status" in result
    assert "method" in result

def test_evolve_capabilities(agent):
    """Testa evolução de capacidades."""
    initial_level = agent.evolution_level
    agent.evolve_capabilities()
    assert agent.evolution_level > initial_level

def test_quantum_process_not_available(agent):
    """Testa processamento quântico quando não disponível."""
    agent.capabilities["quantum"] = False
    with pytest.raises(NotImplementedError):
        agent.quantum_process({"test": "data"})

def test_classical_process(agent):
    """Testa processamento clássico."""
    result = agent.classical_process({"test": "data"})
    assert result["method"] == "classical"
    assert result["status"] == "processed" 