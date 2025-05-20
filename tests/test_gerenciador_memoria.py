"""
Testes do gerenciador de memória do sistema.
"""
import pytest
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import asyncio
from unittest.mock import Mock, patch
from pathlib import Path

from src.memoria.gerenciador_memoria import GerenciadorMemoria, EntidadeMemoria

@pytest.fixture
def config():
    """Fornece configuração básica para os testes."""
    return {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0
    }

@pytest.fixture
def gerenciador(config):
    """Fornece uma instância do gerenciador de memória para testes."""
    with patch("redis.Redis") as mock_redis:
        gerenciador = GerenciadorMemoria(config)
        gerenciador.redis = mock_redis
        yield gerenciador

@pytest.fixture
def entidade_exemplo():
    """Fornece uma entidade de exemplo para testes."""
    return {
        "tipo": "conhecimento",
        "dados": {
            "titulo": "Teste",
            "conteudo": "Conteúdo de teste"
        },
        "tags": ["teste", "exemplo"]
    }

@pytest.mark.asyncio
async def test_inicializacao(gerenciador):
    """Testa a inicialização do gerenciador de memória."""
    assert gerenciador.config["redis_host"] == "localhost"
    assert gerenciador.config["redis_port"] == 6379
    assert gerenciador.config["redis_db"] == 0
    assert isinstance(gerenciador.cache_local, dict)
    assert len(gerenciador.tipos_entidade) == 4
    assert "conhecimento" in gerenciador.tipos_entidade
    assert "evento" in gerenciador.tipos_entidade
    assert "metricas" in gerenciador.tipos_entidade
    assert "configuracao" in gerenciador.tipos_entidade

@pytest.mark.asyncio
async def test_criar_entidade(gerenciador, entidade_exemplo):
    """Testa a criação de entidades."""
    # Mock do Redis
    gerenciador.redis.set = Mock()
    
    # Cria entidade
    entidade = await gerenciador.criar_entidade(
        tipo=entidade_exemplo["tipo"],
        dados=entidade_exemplo["dados"],
        tags=entidade_exemplo["tags"]
    )
    
    assert entidade is not None
    assert entidade.tipo == entidade_exemplo["tipo"]
    assert entidade.dados == entidade_exemplo["dados"]
    assert entidade.tags == entidade_exemplo["tags"]
    assert entidade.versao == "1.0"
    assert len(entidade.relacionamentos) == 0
    
    # Verifica se foi salvo no Redis
    gerenciador.redis.set.assert_called_once()
    
    # Verifica se foi adicionado ao cache local
    assert entidade.id in gerenciador.cache_local
    assert gerenciador.cache_local[entidade.id] == entidade

@pytest.mark.asyncio
async def test_criar_entidade_tipo_invalido(gerenciador, entidade_exemplo):
    """Testa a criação de entidade com tipo inválido."""
    entidade = await gerenciador.criar_entidade(
        tipo="tipo_invalido",
        dados=entidade_exemplo["dados"],
        tags=entidade_exemplo["tags"]
    )
    
    assert entidade is None

@pytest.mark.asyncio
async def test_criar_entidade_tamanho_excedido(gerenciador):
    """Testa a criação de entidade que excede o tamanho máximo."""
    # Cria dados grandes
    dados_grandes = {
        "conteudo": "x" * (1024 * 1024 + 1)  # 1MB + 1 byte
    }
    
    entidade = await gerenciador.criar_entidade(
        tipo="conhecimento",
        dados=dados_grandes,
        tags=["teste"]
    )
    
    assert entidade is None

@pytest.mark.asyncio
async def test_atualizar_entidade(gerenciador, entidade_exemplo):
    """Testa a atualização de entidades."""
    # Mock do Redis
    gerenciador.redis.set = Mock()
    
    # Cria entidade
    entidade = await gerenciador.criar_entidade(
        tipo=entidade_exemplo["tipo"],
        dados=entidade_exemplo["dados"],
        tags=entidade_exemplo["tags"]
    )
    
    # Atualiza dados
    novos_dados = {
        "titulo": "Teste Atualizado",
        "conteudo": "Conteúdo atualizado"
    }
    
    sucesso = await gerenciador.atualizar_entidade(entidade.id, novos_dados)
    
    assert sucesso is True
    
    # Verifica se foi atualizado
    entidade_atualizada = gerenciador.cache_local[entidade.id]
    assert entidade_atualizada.dados == novos_dados
    assert entidade_atualizada.versao == "1.1"
    
    # Verifica se foi salvo no Redis
    assert gerenciador.redis.set.call_count == 2  # Criar + Atualizar

@pytest.mark.asyncio
async def test_atualizar_entidade_inexistente(gerenciador):
    """Testa a atualização de entidade inexistente."""
    sucesso = await gerenciador.atualizar_entidade("id_inexistente", {})
    assert sucesso is False

@pytest.mark.asyncio
async def test_obter_entidade(gerenciador, entidade_exemplo):
    """Testa a obtenção de entidades."""
    # Mock do Redis
    gerenciador.redis.get = Mock(return_value=None)
    
    # Cria entidade
    entidade = await gerenciador.criar_entidade(
        tipo=entidade_exemplo["tipo"],
        dados=entidade_exemplo["dados"],
        tags=entidade_exemplo["tags"]
    )
    
    # Obtém do cache local
    entidade_obtida = await gerenciador.obter_entidade(entidade.id)
    assert entidade_obtida == entidade
    
    # Limpa cache local
    gerenciador.cache_local.clear()
    
    # Mock do Redis para retornar dados
    dados_json = json.dumps(entidade.__dict__, default=str)
    gerenciador.redis.get = Mock(return_value=dados_json)
    
    # Obtém do Redis
    entidade_obtida = await gerenciador.obter_entidade(entidade.id)
    assert entidade_obtida is not None
    assert entidade_obtida.id == entidade.id
    assert entidade_obtida.tipo == entidade.tipo
    assert entidade_obtida.dados == entidade.dados

@pytest.mark.asyncio
async def test_obter_entidade_inexistente(gerenciador):
    """Testa a obtenção de entidade inexistente."""
    # Mock do Redis
    gerenciador.redis.get = Mock(return_value=None)
    
    entidade = await gerenciador.obter_entidade("id_inexistente")
    assert entidade is None

@pytest.mark.asyncio
async def test_buscar_entidades(gerenciador, entidade_exemplo):
    """Testa a busca de entidades."""
    # Mock do Redis
    gerenciador.redis.scan_iter = Mock(return_value=["entidade:1", "entidade:2"])
    gerenciador.redis.get = Mock(return_value=None)
    
    # Cria entidades
    entidade1 = await gerenciador.criar_entidade(
        tipo=entidade_exemplo["tipo"],
        dados=entidade_exemplo["dados"],
        tags=entidade_exemplo["tags"]
    )
    
    entidade2 = await gerenciador.criar_entidade(
        tipo="evento",
        dados={"tipo": "teste"},
        tags=["evento"]
    )
    
    # Busca por tipo
    entidades = await gerenciador.buscar_entidades(tipo="conhecimento")
    assert len(entidades) == 1
    assert entidades[0].id == entidade1.id
    
    # Busca por tags
    entidades = await gerenciador.buscar_entidades(tags=["teste"])
    assert len(entidades) == 1
    assert entidades[0].id == entidade1.id
    
    # Busca por tipo e tags
    entidades = await gerenciador.buscar_entidades(
        tipo="conhecimento",
        tags=["teste"]
    )
    assert len(entidades) == 1
    assert entidades[0].id == entidade1.id

@pytest.mark.asyncio
async def test_adicionar_relacionamento(gerenciador, entidade_exemplo):
    """Testa a adição de relacionamentos entre entidades."""
    # Mock do Redis
    gerenciador.redis.set = Mock()
    
    # Cria entidades
    entidade1 = await gerenciador.criar_entidade(
        tipo=entidade_exemplo["tipo"],
        dados=entidade_exemplo["dados"],
        tags=entidade_exemplo["tags"]
    )
    
    entidade2 = await gerenciador.criar_entidade(
        tipo="evento",
        dados={"tipo": "teste"},
        tags=["evento"]
    )
    
    # Adiciona relacionamento
    sucesso = await gerenciador.adicionar_relacionamento(entidade1.id, entidade2.id)
    assert sucesso is True
    
    # Verifica relacionamentos
    assert entidade2.id in entidade1.relacionamentos
    assert entidade1.id in entidade2.relacionamentos
    
    # Verifica se foi salvo no Redis
    assert gerenciador.redis.set.call_count == 4  # Criar + Criar + Relacionar + Relacionar

@pytest.mark.asyncio
async def test_adicionar_relacionamento_inexistente(gerenciador, entidade_exemplo):
    """Testa a adição de relacionamento com entidade inexistente."""
    # Cria entidade
    entidade = await gerenciador.criar_entidade(
        tipo=entidade_exemplo["tipo"],
        dados=entidade_exemplo["dados"],
        tags=entidade_exemplo["tags"]
    )
    
    # Tenta adicionar relacionamento com entidade inexistente
    sucesso = await gerenciador.adicionar_relacionamento(entidade.id, "id_inexistente")
    assert sucesso is False

@pytest.mark.asyncio
async def test_obter_relacionamentos(gerenciador, entidade_exemplo):
    """Testa a obtenção de relacionamentos."""
    # Mock do Redis
    gerenciador.redis.set = Mock()
    
    # Cria entidades
    entidade1 = await gerenciador.criar_entidade(
        tipo=entidade_exemplo["tipo"],
        dados=entidade_exemplo["dados"],
        tags=entidade_exemplo["tags"]
    )
    
    entidade2 = await gerenciador.criar_entidade(
        tipo="evento",
        dados={"tipo": "teste"},
        tags=["evento"]
    )
    
    # Adiciona relacionamento
    await gerenciador.adicionar_relacionamento(entidade1.id, entidade2.id)
    
    # Obtém relacionamentos
    relacionamentos = await gerenciador.obter_relacionamentos(entidade1.id)
    assert len(relacionamentos) == 1
    assert relacionamentos[0].id == entidade2.id

@pytest.mark.asyncio
async def test_obter_relacionamentos_inexistente(gerenciador):
    """Testa a obtenção de relacionamentos de entidade inexistente."""
    relacionamentos = await gerenciador.obter_relacionamentos("id_inexistente")
    assert len(relacionamentos) == 0

@pytest.mark.asyncio
async def test_limpar_cache(gerenciador, entidade_exemplo):
    """Testa a limpeza do cache local."""
    # Cria entidade
    entidade = await gerenciador.criar_entidade(
        tipo=entidade_exemplo["tipo"],
        dados=entidade_exemplo["dados"],
        tags=entidade_exemplo["tags"]
    )
    
    assert len(gerenciador.cache_local) > 0
    
    # Limpa cache
    await gerenciador.limpar_cache()
    assert len(gerenciador.cache_local) == 0

@pytest.mark.asyncio
async def test_obter_estatisticas(gerenciador, entidade_exemplo):
    """Testa a obtenção de estatísticas."""
    # Cria entidades
    entidade1 = await gerenciador.criar_entidade(
        tipo=entidade_exemplo["tipo"],
        dados=entidade_exemplo["dados"],
        tags=entidade_exemplo["tags"]
    )
    
    entidade2 = await gerenciador.criar_entidade(
        tipo="evento",
        dados={"tipo": "teste"},
        tags=["evento"]
    )
    
    # Obtém estatísticas
    stats = await gerenciador.obter_estatisticas()
    
    assert "timestamp" in stats
    assert stats["total_entidades"] == 2
    assert stats["por_tipo"]["conhecimento"] == 1
    assert stats["por_tipo"]["evento"] == 1
    assert stats["por_tag"]["teste"] == 1
    assert stats["por_tag"]["evento"] == 1
    assert stats["tamanho_total"] > 0

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