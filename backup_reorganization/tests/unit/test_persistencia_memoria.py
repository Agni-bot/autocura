import pytest
import json
import os
from datetime import datetime, timedelta
from src.services.memoria.gerenciador_memoria import GerenciadorMemoria

@pytest.fixture
def gerenciador():
    return GerenciadorMemoria()

def test_salvar_carregar_memoria(gerenciador):
    """Testa o salvamento e carregamento da memória."""
    dados = {
        "estado_sistema": {
            "nivel_autonomia": 1,
            "status": "normal"
        },
        "metricas": {
            "cpu_uso": 60,
            "memoria_uso": 65
        }
    }
    gerenciador.salvar_memoria(dados)
    memoria_carregada = gerenciador.carregar_memoria()
    assert memoria_carregada["estado_sistema"]["nivel_autonomia"] == 1
    assert memoria_carregada["estado_sistema"]["status"] == "normal"
    assert memoria_carregada["metricas"]["cpu_uso"] == 60
    assert memoria_carregada["metricas"]["memoria_uso"] == 65

def test_backup_memoria(gerenciador):
    """Testa o backup da memória."""
    dados = {
        "estado_sistema": {
            "nivel_autonomia": 1,
            "status": "normal"
        },
        "metricas": {
            "cpu_uso": 60,
            "memoria_uso": 65
        }
    }
    gerenciador.salvar_memoria(dados)
    backup_path = gerenciador.backup_memoria()
    assert os.path.exists(backup_path)
    with open(backup_path, 'r') as f:
        backup_data = json.load(f)
        assert backup_data["estado_sistema"]["nivel_autonomia"] == 1
        assert backup_data["metricas"]["cpu_uso"] == 60
    os.remove(backup_path)

def test_restaurar_backup(gerenciador):
    """Testa a restauração de backup."""
    dados = {
        "estado_sistema": {
            "nivel_autonomia": 1,
            "status": "normal"
        },
        "metricas": {
            "cpu_uso": 60,
            "memoria_uso": 65
        }
    }
    gerenciador.salvar_memoria(dados)
    backup_path = gerenciador.backup_memoria()
    gerenciador.limpar_memoria()
    gerenciador.restaurar_backup(backup_path)
    memoria = gerenciador.carregar_memoria()
    assert memoria["estado_sistema"]["nivel_autonomia"] == 1
    assert memoria["metricas"]["cpu_uso"] == 60
    os.remove(backup_path)

def test_limpar_memoria(gerenciador):
    """Testa a limpeza da memória."""
    dados = {
        "estado_sistema": {
            "nivel_autonomia": 1,
            "status": "normal"
        },
        "metricas": {
            "cpu_uso": 60,
            "memoria_uso": 65
        }
    }
    gerenciador.salvar_memoria(dados)
    gerenciador.limpar_memoria()
    memoria = gerenciador.carregar_memoria()
    assert memoria == {}

def test_limpar_memoria_antiga(gerenciador):
    """Testa a limpeza de memória antiga."""
    agora = datetime.now()
    antigo = agora - timedelta(days=30)
    registro_antigo = {
        "id": "test_1",
        "tipo": "manutencao",
        "timestamp": antigo.isoformat()
    }
    registro_recente = {
        "id": "test_2",
        "tipo": "hotfix",
        "timestamp": agora.isoformat()
    }
    gerenciador.registrar_decisao(registro_antigo)
    gerenciador.registrar_acao(registro_recente)
    gerenciador.limpar_memoria_antiga(dias=15)
    memoria = gerenciador.carregar_memoria()
    assert len(memoria["decisoes"]) == 0
    assert len(memoria["acoes"]) == 1
    assert memoria["acoes"][0]["id"] == "test_2" 