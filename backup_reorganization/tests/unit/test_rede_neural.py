import pytest
import torch
import numpy as np
from datetime import datetime
from src.services.diagnostico.rede_neural import RedeNeuralAltaOrdem, Diagnostico
from src.monitoramento.coletor_metricas import Metrica

@pytest.fixture
def rede():
    """Fixture que fornece uma instância da rede neural para os testes."""
    return RedeNeuralAltaOrdem(
        input_size=4,
        hidden_sizes=[8, 4],
        dropout_rate=0.1,
        learning_rate=0.001
    )

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
        ),
        Metrica(
            nome="request_latency",
            valor=0.5,
            tipo="gauge",
            labels={"host": "test"},
            timestamp=datetime.now()
        ),
        Metrica(
            nome="error_rate",
            valor=0.02,
            tipo="gauge",
            labels={"host": "test"},
            timestamp=datetime.now()
        )
    ]

def test_inicializacao(rede):
    """Testa a inicialização da rede neural."""
    assert rede.input_size == 4
    assert rede.hidden_sizes == [8, 4]
    assert rede.dropout_rate == 0.1
    assert isinstance(rede.network, torch.nn.Sequential)
    assert isinstance(rede.optimizer, torch.optim.Adam)
    assert isinstance(rede.criterion, torch.nn.MSELoss)

def test_forward_pass(rede, metricas):
    """Testa o forward pass da rede neural."""
    x = rede.preparar_dados(metricas)
    anomalia, padroes = rede(x)
    
    assert isinstance(anomalia, torch.Tensor)
    assert isinstance(padroes, torch.Tensor)
    assert anomalia.shape == (1,)
    assert padroes.shape == (32,)  # Tamanho da camada de padrões

def test_preparar_dados(rede, metricas):
    """Testa a preparação dos dados de entrada."""
    x = rede.preparar_dados(metricas)
    
    assert isinstance(x, torch.Tensor)
    assert x.shape == (4,)  # Tamanho do input
    assert torch.all(torch.isfinite(x))  # Verifica se não há NaN ou Inf

def test_detectar_anomalia(rede, metricas):
    """Testa a detecção de anomalias."""
    diagnostico = rede.detectar_anomalia(metricas)
    
    assert isinstance(diagnostico, Diagnostico)
    assert isinstance(diagnostico.timestamp, datetime)
    assert isinstance(diagnostico.anomalia_detectada, bool)
    assert isinstance(diagnostico.score_anomalia, float)
    assert isinstance(diagnostico.padrao_detectado, str)
    assert isinstance(diagnostico.confianca, float)
    assert isinstance(diagnostico.metricas_relevantes, list)
    assert isinstance(diagnostico.recomendacoes, list)

def test_identificar_padrao(rede):
    """Testa a identificação de padrões."""
    # Cria tensor de padrões de exemplo
    padroes = torch.randn(32)  # Tamanho da camada de padrões
    
    padrao = rede._identificar_padrao(padroes)
    
    assert isinstance(padrao, str)
    assert padrao in rede.padroes_conhecidos

def test_identificar_metricas_relevantes(rede, metricas):
    """Testa a identificação de métricas relevantes."""
    padrao = "alta_cpu"
    metricas_relevantes = rede._identificar_metricas_relevantes(
        metricas,
        padrao
    )
    
    assert isinstance(metricas_relevantes, list)
    assert all(isinstance(m, str) for m in metricas_relevantes)
    assert metricas_relevantes == rede.padroes_conhecidos[padrao]["metricas"]

def test_gerar_recomendacoes(rede):
    """Testa a geração de recomendações."""
    padrao = "alta_cpu"
    metricas_relevantes = ["cpu_usage"]
    
    recomendacoes = rede._gerar_recomendacoes(
        padrao,
        metricas_relevantes
    )
    
    assert isinstance(recomendacoes, list)
    assert all(isinstance(r, str) for r in recomendacoes)
    assert len(recomendacoes) > 0

def test_treinar(rede, metricas):
    """Testa o treinamento da rede neural."""
    # Cria dados de treino
    dados_treino = [metricas] * 10  # 10 amostras
    
    # Treina rede
    rede.treinar(
        dados_treino,
        epocas=2,  # Poucas épocas para teste
        batch_size=4
    )
    
    # Verifica se os parâmetros foram atualizados
    for param in rede.parameters():
        assert param.grad is not None

def test_salvar_carregar_modelo(rede, tmp_path):
    """Testa o salvamento e carregamento do modelo."""
    # Salva modelo
    caminho = tmp_path / "modelo.pt"
    rede.salvar_modelo(str(caminho))
    
    # Carrega modelo
    nova_rede = RedeNeuralAltaOrdem(
        input_size=4,
        hidden_sizes=[8, 4]
    )
    nova_rede.carregar_modelo(str(caminho))
    
    # Verifica se os parâmetros são iguais
    for p1, p2 in zip(rede.parameters(), nova_rede.parameters()):
        assert torch.allclose(p1, p2)

def test_deteccao_anomalia_cpu(rede):
    """Testa a detecção de anomalia de CPU."""
    metricas = [
        Metrica(
            nome="cpu_usage",
            valor=0.9,  # Valor alto
            tipo="gauge",
            labels={"host": "test"},
            timestamp=datetime.now()
        ),
        Metrica(
            nome="memory_usage",
            valor=0.5,
            tipo="gauge",
            labels={"host": "test"},
            timestamp=datetime.now()
        ),
        Metrica(
            nome="request_latency",
            valor=0.3,
            type="gauge",
            labels={"host": "test"},
            timestamp=datetime.now()
        ),
        Metrica(
            nome="error_rate",
            valor=0.01,
            type="gauge",
            labels={"host": "test"},
            timestamp=datetime.now()
        )
    ]
    
    diagnostico = rede.detectar_anomalia(metricas)
    
    assert diagnostico.anomalia_detectada
    assert diagnostico.padrao_detectado == "alta_cpu"
    assert "cpu_usage" in diagnostico.metricas_relevantes
    assert any("CPU" in r for r in diagnostico.recomendacoes)

def test_deteccao_anomalia_memoria(rede):
    """Testa a detecção de anomalia de memória."""
    metricas = [
        Metrica(
            nome="cpu_usage",
            valor=0.5,
            type="gauge",
            labels={"host": "test"},
            timestamp=datetime.now()
        ),
        Metrica(
            nome="memory_usage",
            valor=0.9,  # Valor alto
            type="gauge",
            labels={"host": "test"},
            timestamp=datetime.now()
        ),
        Metrica(
            nome="request_latency",
            valor=0.3,
            type="gauge",
            labels={"host": "test"},
            timestamp=datetime.now()
        ),
        Metrica(
            nome="error_rate",
            valor=0.01,
            type="gauge",
            labels={"host": "test"},
            timestamp=datetime.now()
        )
    ]
    
    diagnostico = rede.detectar_anomalia(metricas)
    
    assert diagnostico.anomalia_detectada
    assert diagnostico.padrao_detectado == "alta_memoria"
    assert "memory_usage" in diagnostico.metricas_relevantes
    assert any("memória" in r.lower() for r in diagnostico.recomendacoes) 