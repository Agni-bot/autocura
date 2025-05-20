import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch
from src.integracao.camada_integracao import CamadaIntegracao
from src.monitoramento.coletor_metricas import Metrica
from src.diagnostico.rede_neural import Diagnostico
from src.acoes.gerador_acoes import Acao

@pytest.fixture
def config():
    """Fixture que fornece configuração para os testes."""
    return {
        "prometheus_url": "http://localhost:9090",
        "loki_url": "http://localhost:3100",
        "grafana_url": "http://localhost:3000",
        "kubernetes_url": "http://localhost:8001",
        "redis_url": "redis://localhost:6379",
        "auth_token": "test_token"
    }

@pytest.fixture
def camada(config):
    """Fixture que fornece uma instância da camada de integração para os testes."""
    return CamadaIntegracao(config)

@pytest.fixture
def metricas():
    """Fixture que fornece métricas de exemplo para os testes."""
    return [
        Metrica(
            nome="cpu_usage",
            valor=0.75,
            tipo="gauge",
            labels={"host": "test"},
            timestamp=datetime.now()
        ),
        Metrica(
            nome="memory_usage",
            valor=0.65,
            tipo="gauge",
            labels={"host": "test"},
            timestamp=datetime.now()
        )
    ]

@pytest.fixture
def diagnostico():
    """Fixture que fornece um diagnóstico de exemplo para os testes."""
    return Diagnostico(
        timestamp=datetime.now(),
        anomalia_detectada=True,
        score_anomalia=0.9,
        padrao_detectado="alta_cpu",
        confianca=0.8,
        metricas_relevantes=["cpu_usage"],
        recomendacoes=["Verificar processos com alto consumo de CPU"]
    )

@pytest.fixture
def acao(diagnostico):
    """Fixture que fornece uma ação de exemplo para os testes."""
    return Acao(
        id="acao_1",
        tipo="escalar_horizontal",
        descricao="Escalar horizontalmente",
        prioridade=2,
        timestamp=datetime.now(),
        diagnostico=diagnostico,
        parametros={
            "min_replicas": 2,
            "max_replicas": 5
        },
        status="pendente"
    )

@pytest.mark.asyncio
async def test_inicializacao(camada):
    """Testa a inicialização da camada de integração."""
    assert camada.config is not None
    assert camada.timeout == 30
    assert camada.max_retries == 3
    assert camada.session is None
    assert len(camada.endpoints) == 5
    assert "Authorization" in camada.headers

@pytest.mark.asyncio
async def test_inicializar_finalizar(camada):
    """Testa a inicialização e finalização da sessão HTTP."""
    await camada.inicializar()
    assert camada.session is not None
    
    await camada.finalizar()
    assert camada.session is None

@pytest.mark.asyncio
async def test_enviar_metricas(camada, metricas):
    """Testa o envio de métricas."""
    # Mock da resposta HTTP
    mock_response = Mock()
    mock_response.status = 200
    
    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        await camada.inicializar()
        sucesso = await camada.enviar_metricas(metricas)
        assert sucesso

@pytest.mark.asyncio
async def test_enviar_metricas_falha(camada, metricas):
    """Testa o envio de métricas com falha."""
    # Mock da resposta HTTP com erro
    mock_response = Mock()
    mock_response.status = 500
    
    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        await camada.inicializar()
        sucesso = await camada.enviar_metricas(metricas)
        assert not sucesso

@pytest.mark.asyncio
async def test_enviar_diagnostico(camada, diagnostico):
    """Testa o envio de diagnóstico."""
    # Mock da resposta HTTP
    mock_response = Mock()
    mock_response.status = 200
    
    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        await camada.inicializar()
        sucesso = await camada.enviar_diagnostico(diagnostico)
        assert sucesso

@pytest.mark.asyncio
async def test_enviar_acao(camada, acao):
    """Testa o envio de ação."""
    # Mock da resposta HTTP
    mock_response = Mock()
    mock_response.status = 200
    
    with patch("aiohttp.ClientSession.post", return_value=mock_response):
        await camada.inicializar()
        sucesso = await camada.enviar_acao(acao)
        assert sucesso

@pytest.mark.asyncio
async def test_obter_metricas(camada):
    """Testa a obtenção de métricas."""
    # Mock da resposta HTTP
    mock_response = Mock()
    mock_response.status = 200
    mock_response.json = Mock(return_value={
        "data": {
            "result": [
                {
                    "metric": {"name": "cpu_usage"},
                    "value": [1234567890, "0.75"]
                }
            ]
        }
    })
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        await camada.inicializar()
        metricas = await camada.obter_metricas("cpu_usage")
        assert len(metricas) == 1
        assert metricas[0]["metric"]["name"] == "cpu_usage"

@pytest.mark.asyncio
async def test_obter_logs(camada):
    """Testa a obtenção de logs."""
    # Mock da resposta HTTP
    mock_response = Mock()
    mock_response.status = 200
    mock_response.json = Mock(return_value={
        "data": {
            "result": [
                {
                    "stream": {"level": "info"},
                    "values": [["1234567890", "Test log"]]
                }
            ]
        }
    })
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        await camada.inicializar()
        logs = await camada.obter_logs("level=info")
        assert len(logs) == 1
        assert logs[0]["stream"]["level"] == "info"

@pytest.mark.asyncio
async def test_verificar_saude_endpoint(camada):
    """Testa a verificação de saúde de um endpoint."""
    # Mock da resposta HTTP
    mock_response = Mock()
    mock_response.status = 200
    mock_response.json = Mock(return_value={"status": "ok"})
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        await camada.inicializar()
        resultado = await camada.verificar_saude_endpoint("prometheus")
        assert resultado["status"] == "ok"
        assert resultado["endpoint"] == "prometheus"

@pytest.mark.asyncio
async def test_verificar_saude_endpoint_falha(camada):
    """Testa a verificação de saúde de um endpoint com falha."""
    # Mock da resposta HTTP com erro
    mock_response = Mock()
    mock_response.status = 500
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        await camada.inicializar()
        resultado = await camada.verificar_saude_endpoint("prometheus")
        assert resultado["status"] == "error"
        assert "error" in resultado

@pytest.mark.asyncio
async def test_verificar_saude_todos_endpoints(camada):
    """Testa a verificação de saúde de todos os endpoints."""
    # Mock da resposta HTTP
    mock_response = Mock()
    mock_response.status = 200
    mock_response.json = Mock(return_value={"status": "ok"})
    
    with patch("aiohttp.ClientSession.get", return_value=mock_response):
        await camada.inicializar()
        resultados = await camada.verificar_saude_todos_endpoints()
        assert len(resultados) == 5
        assert all(r["status"] == "ok" for r in resultados.values())

@pytest.mark.asyncio
async def test_retry_mechanism(camada, metricas):
    """Testa o mecanismo de retry."""
    # Mock da resposta HTTP com falhas seguidas de sucesso
    mock_response1 = Mock()
    mock_response1.status = 500
    
    mock_response2 = Mock()
    mock_response2.status = 200
    
    with patch("aiohttp.ClientSession.post", side_effect=[mock_response1, mock_response2]):
        await camada.inicializar()
        sucesso = await camada.enviar_metricas(metricas)
        assert sucesso

@pytest.mark.asyncio
async def test_timeout(camada, metricas):
    """Testa o timeout da requisição."""
    # Mock da resposta HTTP com timeout
    with patch("aiohttp.ClientSession.post", side_effect=asyncio.TimeoutError()):
        await camada.inicializar()
        sucesso = await camada.enviar_metricas(metricas)
        assert not sucesso 