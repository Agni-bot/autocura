"""
Testes do sistema de autocura
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from src.core.sistema_autocura import SistemaAutocura
from src.autocura.memory import MemoryManager
from src.autocura.feedback import FeedbackSystem
from src.autocura.monitoring import AutocuraMonitor

# Fixtures
@pytest.fixture
def config():
    return {
        "geral": {
            "versao": "0.1.0",
            "modo_diagnostico": True,
            "limite_agentes": 10,
            "intervalo_evolucao": 3600
        },
        "memoria": {
            "caminho_arquivo": "test_memory.json",
            "max_historico": 1000
        },
        "feedback": {
            "caminho_arquivo": "test_feedback.json",
            "max_historico": 5000
        },
        "monitoramento": {
            "metricas": {
                "caminho_arquivo": "test_metrics.json"
            },
            "prometheus": {
                "porta": 9090
            }
        }
    }

@pytest.fixture
def memory_manager(tmp_path):
    memory_path = tmp_path / "test_memory.json"
    return MemoryManager(memory_path=memory_path)

@pytest.fixture
def feedback_system(tmp_path):
    feedback_path = tmp_path / "test_feedback.json"
    return FeedbackSystem(feedback_path=feedback_path)

@pytest.fixture
def monitor(tmp_path):
    metrics_path = tmp_path / "test_metrics.json"
    return AutocuraMonitor(metrics_path=metrics_path)

@pytest.fixture
def engine(config, memory_manager, feedback_system, monitor):
    return AutocuraEngine(
        config_path=Path("config/autocura.yaml"),
        memory_manager=memory_manager,
        feedback_system=feedback_system,
        monitor=monitor
    )

# Testes do MemoryManager
def test_memory_manager_initialization(memory_manager):
    """Testa inicialização do MemoryManager"""
    assert memory_manager.memory_path.exists()
    assert isinstance(memory_manager.memory, dict)
    assert "estado_sistema" in memory_manager.memory

def test_memory_manager_save(memory_manager):
    """Testa salvamento de memória"""
    test_data = {"test": "data"}
    memory_manager.memory["test"] = test_data
    memory_manager.save()
    
    # Verifica se dados foram salvos
    with open(memory_manager.memory_path, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
    assert saved_data["test"] == test_data

def test_memory_manager_update_from_feedback(memory_manager):
    """Testa atualização de memória com feedback"""
    feedback_data = {
        "tipo": "desempenho",
        "metricas": {"latencia": 100},
        "aprendizado": "teste"
    }
    memory_manager.update_from_feedback(feedback_data)
    
    # Verifica se feedback foi registrado
    assert len(memory_manager.memory["log_eventos"]) > 0
    assert memory_manager.memory["memoria_cognitiva"]["aprendizados"]

# Testes do FeedbackSystem
def test_feedback_system_initialization(feedback_system):
    """Testa inicialização do FeedbackSystem"""
    assert feedback_system.feedback_path.exists()
    assert isinstance(feedback_system.feedback_history, list)

def test_feedback_system_register(feedback_system):
    """Testa registro de feedback"""
    feedback_data = {
        "tipo": "desempenho",
        "detalhes": "teste"
    }
    feedback_system.register(feedback_data)
    
    # Verifica se feedback foi registrado
    assert len(feedback_system.feedback_history) > 0
    assert feedback_system.feedback_history[-1]["data"] == feedback_data

def test_feedback_system_analyze(feedback_system):
    """Testa análise de feedback"""
    # Adiciona alguns feedbacks
    for i in range(3):
        feedback_system.register({
            "tipo": "desempenho",
            "sentimento": "positive" if i % 2 == 0 else "negative"
        })
    
    analysis = feedback_system.analyze()
    assert "total_feedback" in analysis
    assert "tendencias" in analysis
    assert "acoes_recomendadas" in analysis

# Testes do AutocuraMonitor
def test_monitor_initialization(monitor):
    """Testa inicialização do AutocuraMonitor"""
    assert monitor.metrics_path.exists()
    assert isinstance(monitor.metrics_history, list)

def test_monitor_record_feedback(monitor):
    """Testa registro de métricas de feedback"""
    feedback_data = {
        "tipo": "desempenho",
        "detalhes": "teste"
    }
    monitor.record_feedback(feedback_data)
    
    # Verifica se métricas foram registradas
    assert len(monitor.metrics_history) > 0
    assert monitor.metrics_history[-1]["tipo"] == "feedback"

def test_monitor_update_system_metrics(monitor):
    """Testa atualização de métricas do sistema"""
    monitor.update_system_metrics()
    
    # Verifica se métricas foram atualizadas
    assert len(monitor.metrics_history) > 0
    assert monitor.metrics_history[-1]["tipo"] == "sistema"
    assert "cpu_percent" in monitor.metrics_history[-1]["data"]

# Testes do AutocuraEngine
def test_engine_initialization(engine):
    """Testa inicialização do AutocuraEngine"""
    assert engine.config is not None
    assert engine.memory is not None
    assert engine.feedback is not None
    assert engine.monitor is not None

def test_engine_process_feedback(engine):
    """Testa processamento de feedback"""
    feedback_data = {
        "tipo": "desempenho",
        "detalhes": "teste"
    }
    engine.process_feedback(feedback_data)
    
    # Verifica se feedback foi processado
    assert len(engine.memory.memory["log_eventos"]) > 0
    assert len(engine.feedback.feedback_history) > 0
    assert len(engine.monitor.metrics_history) > 0

def test_engine_evolve(engine):
    """Testa ciclo de evolução"""
    evolution_record = engine.evolve()
    
    # Verifica se evolução foi registrada
    assert evolution_record is not None
    assert "timestamp" in evolution_record
    assert "metrics" in evolution_record
    assert "improvements" in evolution_record

# Testes de integração
def test_integration_flow(engine):
    """Testa fluxo completo de integração"""
    # Simula feedback
    feedback_data = {
        "tipo": "desempenho",
        "metricas": {"latencia": 100},
        "aprendizado": "teste"
    }
    engine.process_feedback(feedback_data)
    
    # Executa ciclo de evolução
    evolution_record = engine.evolve()
    
    # Verifica resultados
    assert evolution_record is not None
    assert len(engine.memory.memory["log_eventos"]) > 0
    assert len(engine.feedback.feedback_history) > 0
    assert len(engine.monitor.metrics_history) > 0

# Testes de erro
def test_error_handling(engine):
    """Testa tratamento de erros"""
    # Testa feedback inválido
    with pytest.raises(Exception):
        engine.process_feedback(None)
    
    # Testa evolução com dados inválidos
    with patch.object(engine.monitor, 'get_current_metrics', return_value=None):
        evolution_record = engine.evolve()
        assert evolution_record == {} 