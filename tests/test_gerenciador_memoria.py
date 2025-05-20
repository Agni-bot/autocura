"""
Testes do gerenciador de memória do sistema.
"""
import pytest
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any

from src.memoria.gerenciador_memoria import GerenciadorMemoria

@pytest.fixture
def gerenciador():
    """Fixture que fornece uma instância do gerenciador de memória para os testes."""
    gerenciador = GerenciadorMemoria()
    yield gerenciador
    # Limpar arquivo de memória após os testes
    if os.path.exists(gerenciador.arquivo_memoria):
        os.remove(gerenciador.arquivo_memoria)

def test_salvar_carregar_memoria():
    """Testa o salvamento e carregamento da memória."""
    gerenciador = GerenciadorMemoria()
    
    # Simular dados
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
    
    # Salvar memória
    gerenciador.salvar_memoria(dados)
    
    # Carregar memória
    memoria_carregada = gerenciador.carregar_memoria()
    
    # Verificar resultado
    assert memoria_carregada["estado_sistema"]["nivel_autonomia"] == 1
    assert memoria_carregada["estado_sistema"]["status"] == "normal"
    assert memoria_carregada["metricas"]["cpu_uso"] == 60
    assert memoria_carregada["metricas"]["memoria_uso"] == 65

def test_atualizar_estado_sistema():
    """Testa a atualização do estado do sistema."""
    gerenciador = GerenciadorMemoria()
    
    # Simular estado
    estado = {
        "nivel_autonomia": 2,
        "status": "normal",
        "timestamp": datetime.now().isoformat()
    }
    
    # Atualizar estado
    gerenciador.atualizar_estado_sistema(estado)
    
    # Carregar memória
    memoria = gerenciador.carregar_memoria()
    
    # Verificar resultado
    assert memoria["estado_sistema"]["nivel_autonomia"] == 2
    assert memoria["estado_sistema"]["status"] == "normal"
    assert "timestamp" in memoria["estado_sistema"]

def test_atualizar_metricas():
    """Testa a atualização de métricas."""
    gerenciador = GerenciadorMemoria()
    
    # Simular métricas
    metricas = {
        "cpu_uso": 75,
        "memoria_uso": 80,
        "disco_uso": 60,
        "rede_uso": 50,
        "timestamp": datetime.now().isoformat()
    }
    
    # Atualizar métricas
    gerenciador.atualizar_metricas(metricas)
    
    # Carregar memória
    memoria = gerenciador.carregar_memoria()
    
    # Verificar resultado
    assert memoria["metricas"]["cpu_uso"] == 75
    assert memoria["metricas"]["memoria_uso"] == 80
    assert memoria["metricas"]["disco_uso"] == 60
    assert memoria["metricas"]["rede_uso"] == 50
    assert "timestamp" in memoria["metricas"]

def test_registrar_decisao():
    """Testa o registro de uma decisão."""
    gerenciador = GerenciadorMemoria()
    
    # Simular decisão
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "descricao": "Corrigir bug crítico",
        "componente": "api",
        "impacto": "alto",
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar decisão
    gerenciador.registrar_decisao(decisao)
    
    # Carregar memória
    memoria = gerenciador.carregar_memoria()
    
    # Verificar resultado
    assert len(memoria["decisoes"]) == 1
    assert memoria["decisoes"][0]["id"] == "test_1"
    assert memoria["decisoes"][0]["tipo"] == "manutencao"
    assert memoria["decisoes"][0]["componente"] == "api"

def test_registrar_acao():
    """Testa o registro de uma ação."""
    gerenciador = GerenciadorMemoria()
    
    # Simular ação
    acao = {
        "id": "test_1",
        "tipo": "manutencao",
        "status": "pendente",
        "componente": "api",
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar ação
    gerenciador.registrar_acao(acao)
    
    # Carregar memória
    memoria = gerenciador.carregar_memoria()
    
    # Verificar resultado
    assert len(memoria["acoes"]) == 1
    assert memoria["acoes"][0]["id"] == "test_1"
    assert memoria["acoes"][0]["tipo"] == "manutencao"
    assert memoria["acoes"][0]["status"] == "pendente"

def test_registrar_incidente():
    """Testa o registro de um incidente."""
    gerenciador = GerenciadorMemoria()
    
    # Simular incidente
    incidente = {
        "id": "test_1",
        "tipo": "critico",
        "componente": "api",
        "mensagem": "Falha crítica detectada",
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar incidente
    gerenciador.registrar_incidente(incidente)
    
    # Carregar memória
    memoria = gerenciador.carregar_memoria()
    
    # Verificar resultado
    assert len(memoria["incidentes"]) == 1
    assert memoria["incidentes"][0]["id"] == "test_1"
    assert memoria["incidentes"][0]["tipo"] == "critico"
    assert memoria["incidentes"][0]["componente"] == "api"

def test_registrar_aprendizado():
    """Testa o registro de um aprendizado."""
    gerenciador = GerenciadorMemoria()
    
    # Simular aprendizado
    aprendizado = {
        "id": "test_1",
        "tipo": "otimizacao",
        "descricao": "Melhorar performance da API",
        "componente": "api",
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar aprendizado
    gerenciador.registrar_aprendizado(aprendizado)
    
    # Carregar memória
    memoria = gerenciador.carregar_memoria()
    
    # Verificar resultado
    assert len(memoria["aprendizados"]) == 1
    assert memoria["aprendizados"][0]["id"] == "test_1"
    assert memoria["aprendizados"][0]["tipo"] == "otimizacao"
    assert memoria["aprendizados"][0]["componente"] == "api"

def test_obter_historico():
    """Testa a obtenção do histórico."""
    gerenciador = GerenciadorMemoria()
    
    # Simular registros
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "timestamp": datetime.now().isoformat()
    }
    acao = {
        "id": "test_2",
        "tipo": "hotfix",
        "timestamp": datetime.now().isoformat()
    }
    incidente = {
        "id": "test_3",
        "tipo": "critico",
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar dados
    gerenciador.registrar_decisao(decisao)
    gerenciador.registrar_acao(acao)
    gerenciador.registrar_incidente(incidente)
    
    # Obter histórico
    historico = gerenciador.obter_historico()
    
    # Verificar resultado
    assert len(historico) == 3
    assert historico[0]["id"] == "test_1"
    assert historico[1]["id"] == "test_2"
    assert historico[2]["id"] == "test_3"

def test_obter_historico_por_tipo():
    """Testa a obtenção do histórico por tipo."""
    gerenciador = GerenciadorMemoria()
    
    # Simular registros
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "timestamp": datetime.now().isoformat()
    }
    acao = {
        "id": "test_2",
        "tipo": "hotfix",
        "timestamp": datetime.now().isoformat()
    }
    incidente = {
        "id": "test_3",
        "tipo": "critico",
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar dados
    gerenciador.registrar_decisao(decisao)
    gerenciador.registrar_acao(acao)
    gerenciador.registrar_incidente(incidente)
    
    # Obter histórico por tipo
    historico_decisoes = gerenciador.obter_historico_por_tipo("decisao")
    historico_acoes = gerenciador.obter_historico_por_tipo("acao")
    historico_incidentes = gerenciador.obter_historico_por_tipo("incidente")
    
    # Verificar resultado
    assert len(historico_decisoes) == 1
    assert len(historico_acoes) == 1
    assert len(historico_incidentes) == 1
    assert historico_decisoes[0]["id"] == "test_1"
    assert historico_acoes[0]["id"] == "test_2"
    assert historico_incidentes[0]["id"] == "test_3"

def test_obter_historico_por_periodo():
    """Testa a obtenção do histórico por período."""
    gerenciador = GerenciadorMemoria()
    
    # Simular registros
    agora = datetime.now()
    ontem = agora - timedelta(days=1)
    
    registro_antigo = {
        "id": "test_1",
        "tipo": "manutencao",
        "timestamp": ontem.isoformat()
    }
    registro_recente = {
        "id": "test_2",
        "tipo": "hotfix",
        "timestamp": agora.isoformat()
    }
    
    # Registrar dados
    gerenciador.registrar_decisao(registro_antigo)
    gerenciador.registrar_acao(registro_recente)
    
    # Obter histórico por período
    historico_recente = gerenciador.obter_historico_por_periodo(agora - timedelta(hours=1))
    
    # Verificar resultado
    assert len(historico_recente) == 1
    assert historico_recente[0]["id"] == "test_2"

def test_limpar_memoria_antiga():
    """Testa a limpeza de memória antiga."""
    gerenciador = GerenciadorMemoria()
    
    # Simular registros
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
    
    # Registrar dados
    gerenciador.registrar_decisao(registro_antigo)
    gerenciador.registrar_acao(registro_recente)
    
    # Limpar memória antiga
    gerenciador.limpar_memoria_antiga(dias=15)
    
    # Carregar memória
    memoria = gerenciador.carregar_memoria()
    
    # Verificar resultado
    assert len(memoria["decisoes"]) == 0
    assert len(memoria["acoes"]) == 1
    assert memoria["acoes"][0]["id"] == "test_2"

def test_backup_memoria():
    """Testa o backup da memória."""
    gerenciador = GerenciadorMemoria()
    
    # Simular dados
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
    
    # Salvar memória
    gerenciador.salvar_memoria(dados)
    
    # Fazer backup
    backup_path = gerenciador.backup_memoria()
    
    # Verificar resultado
    assert os.path.exists(backup_path)
    with open(backup_path, 'r') as f:
        backup_data = json.load(f)
        assert backup_data["estado_sistema"]["nivel_autonomia"] == 1
        assert backup_data["metricas"]["cpu_uso"] == 60
    
    # Limpar arquivo de backup
    os.remove(backup_path)

def test_restaurar_backup():
    """Testa a restauração de backup."""
    gerenciador = GerenciadorMemoria()
    
    # Simular dados
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
    
    # Salvar memória
    gerenciador.salvar_memoria(dados)
    
    # Fazer backup
    backup_path = gerenciador.backup_memoria()
    
    # Limpar memória atual
    gerenciador.limpar_memoria()
    
    # Restaurar backup
    gerenciador.restaurar_backup(backup_path)
    
    # Carregar memória
    memoria = gerenciador.carregar_memoria()
    
    # Verificar resultado
    assert memoria["estado_sistema"]["nivel_autonomia"] == 1
    assert memoria["metricas"]["cpu_uso"] == 60
    
    # Limpar arquivo de backup
    os.remove(backup_path)

def test_limpar_memoria():
    """Testa a limpeza da memória."""
    gerenciador = GerenciadorMemoria()
    
    # Simular dados
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
    
    # Salvar memória
    gerenciador.salvar_memoria(dados)
    
    # Limpar memória
    gerenciador.limpar_memoria()
    
    # Carregar memória
    memoria = gerenciador.carregar_memoria()
    
    # Verificar resultado
    assert memoria == {} 