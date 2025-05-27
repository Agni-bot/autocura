import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import json
import os
from src.utils.logs.gerenciador_logs import GerenciadorLogs, Log

@pytest.fixture
def config():
    """Configuração básica para os testes."""
    return {
        "base_dir": "test_logs"
    }

@pytest.fixture
def gerenciador(config):
    """Instância do gerenciador de logs."""
    return GerenciadorLogs(config)

@pytest.fixture
def log_exemplo():
    """Log de exemplo para testes."""
    return {
        "nivel": "INFO",
        "mensagem": "Teste de log",
        "origem": "teste",
        "contexto": {"chave": "valor"},
        "tags": ["teste"],
        "traceback": None
    }

@pytest.mark.asyncio
async def test_inicializacao(gerenciador, config):
    """Testa a inicialização do gerenciador."""
    assert gerenciador.config == config
    assert gerenciador.base_dir == Path(config["base_dir"])
    assert isinstance(gerenciador.logs, dict)
    assert "DEBUG" in gerenciador.niveis
    assert "INFO" in gerenciador.niveis
    assert "WARNING" in gerenciador.niveis
    assert "ERROR" in gerenciador.niveis
    assert "CRITICAL" in gerenciador.niveis
    assert "logs_criados" in gerenciador.metricas
    assert "logs_retidos" in gerenciador.metricas
    assert "logs_limpos" in gerenciador.metricas
    assert "tempo_operacao" in gerenciador.metricas
    assert "arquivo" in gerenciador.handlers
    assert "console" in gerenciador.handlers
    assert "elastic" in gerenciador.handlers
    assert "prometheus" in gerenciador.handlers

@pytest.mark.asyncio
async def test_registrar_log(gerenciador, log_exemplo):
    """Testa o registro de log."""
    log = await gerenciador.registrar_log(**log_exemplo)
    
    assert log is not None
    assert log.nivel == log_exemplo["nivel"]
    assert log.mensagem == log_exemplo["mensagem"]
    assert log.origem == log_exemplo["origem"]
    assert log.contexto == log_exemplo["contexto"]
    assert log.tags == log_exemplo["tags"]
    assert log.traceback == log_exemplo["traceback"]
    
    # Verifica arquivo
    data_dir = gerenciador.base_dir / log.timestamp.strftime("%Y%m%d")
    arquivo = data_dir / f"{log.nivel.lower()}.log"
    assert arquivo.exists()
    
    with open(arquivo, "r") as f:
        linha = f.readline()
        dados = json.loads(linha)
        assert dados["id"] == log.id
        assert dados["nivel"] == log.nivel
        assert dados["mensagem"] == log.mensagem
        assert dados["origem"] == log.origem
        assert dados["contexto"] == log.contexto
        assert dados["tags"] == log.tags
    
    # Verifica cache
    assert log.id in gerenciador.logs
    assert gerenciador.logs[log.id] == log

@pytest.mark.asyncio
async def test_registrar_log_nivel_invalido(gerenciador, log_exemplo):
    """Testa registro de log com nível inválido."""
    log_exemplo["nivel"] = "INVALIDO"
    log = await gerenciador.registrar_log(**log_exemplo)
    assert log is None

@pytest.mark.asyncio
async def test_obter_log(gerenciador, log_exemplo):
    """Testa a obtenção de log."""
    # Registra log
    log = await gerenciador.registrar_log(**log_exemplo)
    assert log is not None
    
    # Obtém log
    log_obtido = await gerenciador.obter_log(log.id)
    assert log_obtido == log
    
    # Testa log inexistente
    log_inexistente = await gerenciador.obter_log("inexistente")
    assert log_inexistente is None

@pytest.mark.asyncio
async def test_buscar_logs(gerenciador, log_exemplo):
    """Testa a busca de logs."""
    # Registra logs
    log1 = await gerenciador.registrar_log(**log_exemplo)
    assert log1 is not None
    
    log2 = await gerenciador.registrar_log(
        nivel="ERROR",
        mensagem="Erro de teste",
        origem="teste",
        contexto={"erro": "teste"},
        tags=["teste", "erro"],
        traceback="Traceback de teste"
    )
    assert log2 is not None
    
    # Busca por nível
    logs_nivel = await gerenciador.buscar_logs(nivel="INFO")
    assert len(logs_nivel) == 1
    assert logs_nivel[0] == log1
    
    # Busca por origem
    logs_origem = await gerenciador.buscar_logs(origem="teste")
    assert len(logs_origem) == 2
    
    # Busca por tags
    logs_tags = await gerenciador.buscar_logs(tags=["erro"])
    assert len(logs_tags) == 1
    assert logs_tags[0] == log2
    
    # Busca por período
    agora = datetime.now()
    inicio = agora - timedelta(minutes=5)
    fim = agora + timedelta(minutes=5)
    
    logs_periodo = await gerenciador.buscar_logs(inicio=inicio, fim=fim)
    assert len(logs_periodo) == 2
    
    # Busca combinada
    logs_combinada = await gerenciador.buscar_logs(
        nivel="ERROR",
        origem="teste",
        tags=["erro"],
        inicio=inicio,
        fim=fim
    )
    assert len(logs_combinada) == 1
    assert logs_combinada[0] == log2

@pytest.mark.asyncio
async def test_limpar_logs_antigos(gerenciador, log_exemplo):
    """Testa a limpeza de logs antigos."""
    # Registra logs antigos
    log_antigo = await gerenciador.registrar_log(**log_exemplo)
    assert log_antigo is not None
    
    # Força timestamp antigo
    log_antigo.timestamp = datetime.now() - timedelta(days=8)  # DEBUG retenção é 7 dias
    gerenciador.logs[log_antigo.id] = log_antigo
    
    # Registra log recente
    log_recente = await gerenciador.registrar_log(
        nivel="ERROR",
        mensagem="Erro recente",
        origem="teste",
        contexto={"erro": "recente"},
        tags=["teste", "erro"]
    )
    assert log_recente is not None
    
    # Limpa logs antigos
    await gerenciador.limpar_logs_antigos()
    
    # Verifica cache
    assert log_antigo.id not in gerenciador.logs
    assert log_recente.id in gerenciador.logs

@pytest.mark.asyncio
async def test_obter_estatisticas(gerenciador, log_exemplo):
    """Testa a obtenção de estatísticas."""
    # Registra logs
    log1 = await gerenciador.registrar_log(**log_exemplo)
    assert log1 is not None
    
    log2 = await gerenciador.registrar_log(
        nivel="ERROR",
        mensagem="Erro de teste",
        origem="teste",
        contexto={"erro": "teste"},
        tags=["teste", "erro"],
        traceback="Traceback de teste"
    )
    assert log2 is not None
    
    # Força log antigo
    log_antigo = await gerenciador.registrar_log(**log_exemplo)
    assert log_antigo is not None
    log_antigo.timestamp = datetime.now() - timedelta(days=8)
    gerenciador.logs[log_antigo.id] = log_antigo
    
    # Obtém estatísticas
    stats = await gerenciador.obter_estatisticas()
    
    assert stats["total_logs"] == 3
    assert stats["por_nivel"]["INFO"] == 2
    assert stats["por_nivel"]["ERROR"] == 1
    assert stats["por_origem"]["teste"] == 3
    assert stats["por_tag"]["teste"] == 3
    assert stats["por_tag"]["erro"] == 1
    assert stats["logs_antigos"] == 1

@pytest.mark.asyncio
async def test_limpeza(gerenciador):
    """Testa a limpeza dos arquivos de teste."""
    # Remove diretório de teste
    if gerenciador.base_dir.exists():
        for arquivo in gerenciador.base_dir.glob("**/*"):
            if arquivo.is_file():
                arquivo.unlink()
        gerenciador.base_dir.rmdir() 