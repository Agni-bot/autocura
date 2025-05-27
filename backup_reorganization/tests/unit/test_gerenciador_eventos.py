import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import json

from src.eventos.gerenciador_eventos import GerenciadorEventos, Evento

@pytest.fixture
def config():
    """Fornece configuração básica para os testes."""
    return {
        "max_eventos": 1000,
        "ttl_padrao": 86400  # 24 horas
    }

@pytest.fixture
def gerenciador(config):
    """Fornece uma instância do gerenciador de eventos para testes."""
    return GerenciadorEventos(config)

@pytest.fixture
def evento_exemplo():
    """Fornece um evento de exemplo para testes."""
    return {
        "tipo": "sistema",
        "dados": {
            "mensagem": "Teste",
            "nivel": "info"
        },
        "origem": "teste",
        "tags": ["teste", "exemplo"]
    }

@pytest.mark.asyncio
async def test_inicializacao(gerenciador):
    """Testa a inicialização do gerenciador de eventos."""
    assert gerenciador.config["max_eventos"] == 1000
    assert gerenciador.config["ttl_padrao"] == 86400
    assert isinstance(gerenciador.eventos, dict)
    assert len(gerenciador.tipos_evento) == 4
    assert "sistema" in gerenciador.tipos_evento
    assert "aplicacao" in gerenciador.tipos_evento
    assert "seguranca" in gerenciador.tipos_evento
    assert "monitoramento" in gerenciador.tipos_evento

@pytest.mark.asyncio
async def test_registrar_evento(gerenciador, evento_exemplo):
    """Testa o registro de eventos."""
    # Registra evento
    evento = await gerenciador.registrar_evento(
        tipo=evento_exemplo["tipo"],
        dados=evento_exemplo["dados"],
        origem=evento_exemplo["origem"],
        tags=evento_exemplo["tags"]
    )
    
    assert evento is not None
    assert evento.tipo == evento_exemplo["tipo"]
    assert evento.dados == evento_exemplo["dados"]
    assert evento.origem == evento_exemplo["origem"]
    assert evento.tags == evento_exemplo["tags"]
    assert evento.status == "pendente"
    assert evento.prioridade == gerenciador.tipos_evento[evento_exemplo["tipo"]]["prioridade"]
    
    # Verifica se foi adicionado ao cache
    assert evento.id in gerenciador.eventos
    assert gerenciador.eventos[evento.id] == evento

@pytest.mark.asyncio
async def test_registrar_evento_tipo_invalido(gerenciador, evento_exemplo):
    """Testa o registro de evento com tipo inválido."""
    evento = await gerenciador.registrar_evento(
        tipo="tipo_invalido",
        dados=evento_exemplo["dados"],
        origem=evento_exemplo["origem"],
        tags=evento_exemplo["tags"]
    )
    
    assert evento is None

@pytest.mark.asyncio
async def test_processar_evento(gerenciador, evento_exemplo):
    """Testa o processamento de eventos."""
    # Mock do handler
    handler_mock = Mock()
    handler_mock.__name__ = "test_handler"
    
    # Registra handler
    gerenciador.registrar_handler(evento_exemplo["tipo"], handler_mock)
    
    # Registra evento
    evento = await gerenciador.registrar_evento(
        tipo=evento_exemplo["tipo"],
        dados=evento_exemplo["dados"],
        origem=evento_exemplo["origem"],
        tags=evento_exemplo["tags"]
    )
    
    # Aguarda processamento
    await asyncio.sleep(0.1)
    
    # Verifica se handler foi chamado
    handler_mock.assert_called_once_with(evento)
    
    # Verifica status
    assert evento.status == "processado"

@pytest.mark.asyncio
async def test_processar_evento_sem_handler(gerenciador, evento_exemplo):
    """Testa o processamento de evento sem handler registrado."""
    # Registra evento
    evento = await gerenciador.registrar_evento(
        tipo=evento_exemplo["tipo"],
        dados=evento_exemplo["dados"],
        origem=evento_exemplo["origem"],
        tags=evento_exemplo["tags"]
    )
    
    # Aguarda processamento
    await asyncio.sleep(0.1)
    
    # Verifica status
    assert evento.status == "pendente"

@pytest.mark.asyncio
async def test_processar_evento_erro_handler(gerenciador, evento_exemplo):
    """Testa o processamento de evento com erro no handler."""
    # Mock do handler com erro
    def handler_com_erro(evento):
        raise Exception("Erro no handler")
    
    handler_com_erro.__name__ = "handler_com_erro"
    
    # Registra handler
    gerenciador.registrar_handler(evento_exemplo["tipo"], handler_com_erro)
    
    # Registra evento
    evento = await gerenciador.registrar_evento(
        tipo=evento_exemplo["tipo"],
        dados=evento_exemplo["dados"],
        origem=evento_exemplo["origem"],
        tags=evento_exemplo["tags"]
    )
    
    # Aguarda processamento
    await asyncio.sleep(0.1)
    
    # Verifica status
    assert evento.status == "erro"

@pytest.mark.asyncio
async def test_obter_evento(gerenciador, evento_exemplo):
    """Testa a obtenção de eventos."""
    # Registra evento
    evento = await gerenciador.registrar_evento(
        tipo=evento_exemplo["tipo"],
        dados=evento_exemplo["dados"],
        origem=evento_exemplo["origem"],
        tags=evento_exemplo["tags"]
    )
    
    # Obtém evento
    evento_obtido = await gerenciador.obter_evento(evento.id)
    assert evento_obtido == evento
    
    # Tenta obter evento inexistente
    evento_inexistente = await gerenciador.obter_evento("id_inexistente")
    assert evento_inexistente is None

@pytest.mark.asyncio
async def test_buscar_eventos(gerenciador, evento_exemplo):
    """Testa a busca de eventos."""
    # Registra eventos
    evento1 = await gerenciador.registrar_evento(
        tipo=evento_exemplo["tipo"],
        dados=evento_exemplo["dados"],
        origem=evento_exemplo["origem"],
        tags=evento_exemplo["tags"]
    )
    
    evento2 = await gerenciador.registrar_evento(
        tipo="aplicacao",
        dados={"acao": "teste"},
        origem="teste2",
        tags=["teste"]
    )
    
    # Busca por tipo
    eventos = await gerenciador.buscar_eventos(tipo="sistema")
    assert len(eventos) == 1
    assert eventos[0].id == evento1.id
    
    # Busca por status
    eventos = await gerenciador.buscar_eventos(status="pendente")
    assert len(eventos) == 2
    
    # Busca por origem
    eventos = await gerenciador.buscar_eventos(origem="teste2")
    assert len(eventos) == 1
    assert eventos[0].id == evento2.id
    
    # Busca por tags
    eventos = await gerenciador.buscar_eventos(tags=["exemplo"])
    assert len(eventos) == 1
    assert eventos[0].id == evento1.id
    
    # Busca por período
    agora = datetime.now()
    eventos = await gerenciador.buscar_eventos(
        inicio=agora - timedelta(minutes=1),
        fim=agora + timedelta(minutes=1)
    )
    assert len(eventos) == 2

@pytest.mark.asyncio
async def test_limpar_eventos_antigos(gerenciador, evento_exemplo):
    """Testa a limpeza de eventos antigos."""
    # Registra evento
    evento = await gerenciador.registrar_evento(
        tipo=evento_exemplo["tipo"],
        dados=evento_exemplo["dados"],
        origem=evento_exemplo["origem"],
        tags=evento_exemplo["tags"]
    )
    
    # Modifica timestamp para evento antigo
    evento.timestamp = datetime.now() - timedelta(days=8)
    
    # Limpa eventos antigos
    await gerenciador.limpar_eventos_antigos()
    
    # Verifica se evento foi removido
    assert evento.id not in gerenciador.eventos

@pytest.mark.asyncio
async def test_obter_estatisticas(gerenciador, evento_exemplo):
    """Testa a obtenção de estatísticas."""
    # Registra eventos
    evento1 = await gerenciador.registrar_evento(
        tipo=evento_exemplo["tipo"],
        dados=evento_exemplo["dados"],
        origem=evento_exemplo["origem"],
        tags=evento_exemplo["tags"]
    )
    
    evento2 = await gerenciador.registrar_evento(
        tipo="aplicacao",
        dados={"acao": "teste"},
        origem="teste2",
        tags=["teste"]
    )
    
    # Obtém estatísticas
    stats = await gerenciador.obter_estatisticas()
    
    assert "timestamp" in stats
    assert stats["total_eventos"] == 2
    assert stats["por_tipo"]["sistema"] == 1
    assert stats["por_tipo"]["aplicacao"] == 1
    assert stats["por_status"]["pendente"] == 2
    assert stats["por_origem"]["teste"] == 1
    assert stats["por_origem"]["teste2"] == 1
    assert stats["por_tag"]["teste"] == 2
    assert stats["por_tag"]["exemplo"] == 1 