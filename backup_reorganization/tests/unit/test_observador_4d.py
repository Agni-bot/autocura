import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.monitoring.observability.observador_4d import Observador4D, Dimensao4D

@pytest.fixture
def config():
    """Fixture que fornece configuração para os testes."""
    return {
        "prometheus_port": 9090
    }

@pytest.fixture
def observador(config):
    """Fixture que fornece uma instância do observador 4D para os testes."""
    return Observador4D(config)

@pytest.mark.asyncio
async def test_inicializacao(observador):
    """Testa a inicialização do observador 4D."""
    assert observador.config is not None
    assert len(observador.metricas) == 7
    assert len(observador.dimensoes) == 4
    assert observador.cache_metricas == {}
    assert observador.cache_timeout == timedelta(minutes=5)

@pytest.mark.asyncio
async def test_atualizar_dimensao(observador):
    """Testa a atualização de uma dimensão."""
    nome = "performance"
    valor = 0.85
    contexto = {"host": "test"}
    
    await observador.atualizar_dimensao(nome, valor, contexto)
    
    dimensoes = observador.dimensoes[nome]
    assert len(dimensoes) == 1
    assert dimensoes[0].nome == nome
    assert dimensoes[0].valor == valor
    assert dimensoes[0].contexto == contexto

@pytest.mark.asyncio
async def test_atualizar_dimensao_limite(observador):
    """Testa o limite de dimensões armazenadas."""
    nome = "performance"
    for i in range(1100):
        await observador.atualizar_dimensao(nome, float(i), {"index": i})
    
    assert len(observador.dimensoes[nome]) == 1000
    assert observador.dimensoes[nome][-1].valor == 1099

@pytest.mark.asyncio
async def test_obter_dimensao(observador):
    """Testa a obtenção de dimensões."""
    nome = "performance"
    valor = 0.85
    contexto = {"host": "test"}
    
    await observador.atualizar_dimensao(nome, valor, contexto)
    
    dimensoes = await observador.obter_dimensao(nome)
    assert len(dimensoes) == 1
    assert dimensoes[0].valor == valor

@pytest.mark.asyncio
async def test_obter_dimensao_periodo(observador):
    """Testa a obtenção de dimensões em um período."""
    nome = "performance"
    
    # Dimensão antiga
    await observador.atualizar_dimensao(nome, 0.5, {"timestamp": "old"})
    
    # Aguarda 1 segundo
    await asyncio.sleep(1)
    
    # Dimensão recente
    await observador.atualizar_dimensao(nome, 0.85, {"timestamp": "new"})
    
    # Obtém dimensões dos últimos 2 segundos
    dimensoes = await observador.obter_dimensao(nome, timedelta(seconds=2))
    assert len(dimensoes) == 2
    
    # Obtém dimensões dos últimos 0.5 segundos
    dimensoes = await observador.obter_dimensao(nome, timedelta(seconds=0.5))
    assert len(dimensoes) == 1
    assert dimensoes[0].contexto["timestamp"] == "new"

@pytest.mark.asyncio
async def test_calcular_estatisticas(observador):
    """Testa o cálculo de estatísticas."""
    nome = "performance"
    valores = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    for valor in valores:
        await observador.atualizar_dimensao(nome, valor, {})
    
    estatisticas = await observador.calcular_estatisticas(nome)
    assert estatisticas["media"] == 0.3
    assert estatisticas["mediana"] == 0.3
    assert estatisticas["min"] == 0.1
    assert estatisticas["max"] == 0.5
    assert "desvio_padrao" in estatisticas

@pytest.mark.asyncio
async def test_detectar_anomalias(observador):
    """Testa a detecção de anomalias."""
    nome = "performance"
    valores = [0.1, 0.2, 0.3, 0.4, 0.5, 2.0]  # 2.0 é uma anomalia
    
    for valor in valores:
        await observador.atualizar_dimensao(nome, valor, {})
    
    anomalias = await observador.detectar_anomalias(nome)
    assert len(anomalias) == 1
    assert anomalias[0]["valor"] == 2.0
    assert anomalias[0]["z_score"] > 3

@pytest.mark.asyncio
async def test_atualizar_metricas(observador):
    """Testa a atualização de métricas."""
    metricas = {
        "cpu_usage": 0.75,
        "memory_usage": 0.65,
        "disk_usage": 0.55,
        "network_io": 1000,
        "request_latency": 0.1,
        "error_rate": 0.01,
        "active_connections": 100
    }
    
    await observador.atualizar_metricas(metricas)
    
    for nome, valor in metricas.items():
        assert observador.cache_metricas[nome] == valor
    
    assert "timestamp" in observador.cache_metricas

@pytest.mark.asyncio
async def test_obter_metricas(observador):
    """Testa a obtenção de métricas."""
    metricas = {
        "cpu_usage": 0.75,
        "memory_usage": 0.65
    }
    
    await observador.atualizar_metricas(metricas)
    
    # Obtém todas as métricas
    todas_metricas = await observador.obter_metricas()
    assert todas_metricas["cpu_usage"] == 0.75
    assert todas_metricas["memory_usage"] == 0.65
    
    # Obtém uma métrica específica
    cpu_metricas = await observador.obter_metricas("cpu_usage")
    assert cpu_metricas["cpu_usage"] == 0.75

@pytest.mark.asyncio
async def test_gerar_relatorio(observador):
    """Testa a geração de relatório."""
    # Adiciona dados de exemplo
    for nome in observador.dimensoes:
        await observador.atualizar_dimensao(nome, 0.5, {})
    
    metricas = {
        "cpu_usage": 0.75,
        "memory_usage": 0.65
    }
    await observador.atualizar_metricas(metricas)
    
    relatorio = await observador.gerar_relatorio()
    
    assert "timestamp" in relatorio
    assert "dimensoes" in relatorio
    assert "metricas" in relatorio
    assert "anomalias" in relatorio
    
    for nome in observador.dimensoes:
        assert nome in relatorio["dimensoes"]
        assert nome in relatorio["anomalias"]

@pytest.mark.asyncio
async def test_limpar_dados_antigos(observador):
    """Testa a limpeza de dados antigos."""
    nome = "performance"
    
    # Dados antigos
    await observador.atualizar_dimensao(nome, 0.5, {"timestamp": "old"})
    
    # Aguarda 1 segundo
    await asyncio.sleep(1)
    
    # Dados recentes
    await observador.atualizar_dimensao(nome, 0.85, {"timestamp": "new"})
    
    # Limpa dados mais antigos que 0.5 segundos
    await observador.limpar_dados_antigos(timedelta(seconds=0.5))
    
    dimensoes = observador.dimensoes[nome]
    assert len(dimensoes) == 1
    assert dimensoes[0].contexto["timestamp"] == "new" 