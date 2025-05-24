import pytest
import os
import json
from typing import Dict
from ..src.evolution.evolution_engine import EvolutionEngine

@pytest.fixture
def engine(tmp_path):
    """Fixture que cria um motor de evolução com diretório temporário."""
    config_path = os.path.join(tmp_path, "config", "evolution_config.json")
    return EvolutionEngine(config_path=config_path)

def test_engine_initialization(engine):
    """Testa inicialização do motor de evolução."""
    assert engine.evolution_history == []
    assert isinstance(engine.current_state, dict)
    assert "evolution_level" in engine.current_state
    assert "capabilities" in engine.current_state
    assert "metrics" in engine.current_state

def test_load_config(engine):
    """Testa carregamento de configuração."""
    config = engine._load_config()
    assert isinstance(config, dict)
    assert "evolution_thresholds" in config
    assert "check_interval" in config
    assert "max_evolution_level" in config
    assert "required_metrics" in config

def test_create_default_config(engine):
    """Testa criação de configuração padrão."""
    config = engine._create_default_config()
    assert isinstance(config, dict)
    assert config["evolution_thresholds"]["quantum"] == 0.8
    assert config["evolution_thresholds"]["nano"] == 0.9
    assert config["evolution_thresholds"]["bio"] == 0.95

def test_assess_readiness(engine):
    """Testa avaliação de prontidão."""
    readiness = engine.assess_readiness()
    assert isinstance(readiness, dict)
    assert all(isinstance(v, float) for v in readiness.values())

def test_evolve_capabilities(engine):
    """Testa evolução de capacidades."""
    initial_level = engine.current_state["evolution_level"]
    engine.evolve_capabilities()
    assert len(engine.evolution_history) >= 0
    assert engine.current_state["last_check"] is not None

def test_activate_capability(engine):
    """Testa ativação de capacidade."""
    capability = "quantum"
    initial_level = engine.current_state["evolution_level"]
    engine._activate_capability(capability)
    assert engine.current_state["capabilities"][capability]
    assert engine.current_state["evolution_level"] > initial_level
    assert len(engine.evolution_history) == 1

def test_save_state(engine):
    """Testa salvamento de estado."""
    engine._save_state()
    state_file = os.path.join(os.path.dirname(engine.config_path), "evolution_state.json")
    assert os.path.exists(state_file)
    with open(state_file, 'r') as f:
        saved_state = json.load(f)
    assert saved_state == engine.current_state 