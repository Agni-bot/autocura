"""
Testes de integração do módulo de observabilidade.
"""

import requests
import time
import json
from datetime import datetime
import pytest

# URLs dos serviços
OBSERVABILIDADE_URL = "http://localhost:8080"
MONITORAMENTO_URL = "http://localhost:8081"
DIAGNOSTICO_URL = "http://localhost:5002"
GERADOR_URL = "http://localhost:5003"

def test_health_check():
    """Testa o endpoint de health check."""
    response = requests.get(f"{OBSERVABILIDADE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_obter_metricas():
    """Testa a obtenção de métricas."""
    response = requests.get(f"{OBSERVABILIDADE_URL}/api/v1/metricas")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "nome" in data[0]
        assert "valor" in data[0]
        assert "timestamp" in data[0]

def test_obter_diagnosticos():
    """Testa a obtenção de diagnósticos."""
    response = requests.get(f"{OBSERVABILIDADE_URL}/api/v1/diagnosticos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_obter_acoes():
    """Testa a obtenção de ações."""
    response = requests.get(f"{OBSERVABILIDADE_URL}/api/v1/acoes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_criar_visualizacao_metricas():
    """Testa a criação de visualização de métricas."""
    payload = {
        "titulo": "Teste de Visualização",
        "agrupar_por_dimensao": True,
        "salvar": True
    }
    response = requests.post(
        f"{OBSERVABILIDADE_URL}/api/visualizacoes/metricas-temporais",
        json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert "url" in data

def test_gerar_relatorio_completo():
    """Testa a geração de relatório completo."""
    response = requests.get(f"{OBSERVABILIDADE_URL}/api/v1/relatorio-completo")
    assert response.status_code == 200
    data = response.json()
    assert "metricas" in data
    assert "diagnosticos" in data
    assert "acoes" in data
    assert "eventos" in data

def test_fluxo_completo():
    """Testa o fluxo completo do sistema."""
    # 1. Verifica saúde do sistema
    assert test_health_check()
    
    # 2. Obtém métricas
    metricas = requests.get(f"{OBSERVABILIDADE_URL}/api/v1/metricas").json()
    assert isinstance(metricas, list)
    
    # 3. Obtém diagnósticos
    diagnosticos = requests.get(f"{OBSERVABILIDADE_URL}/api/v1/diagnosticos").json()
    assert isinstance(diagnosticos, list)
    
    # 4. Obtém ações
    acoes = requests.get(f"{OBSERVABILIDADE_URL}/api/v1/acoes").json()
    assert isinstance(acoes, list)
    
    # 5. Cria visualização
    payload = {
        "titulo": "Fluxo Completo Test",
        "agrupar_por_dimensao": True,
        "salvar": True
    }
    visualizacao = requests.post(
        f"{OBSERVABILIDADE_URL}/api/visualizacoes/metricas-temporais",
        json=payload
    ).json()
    assert "url" in visualizacao
    
    # 6. Gera relatório
    relatorio = requests.get(f"{OBSERVABILIDADE_URL}/api/v1/relatorio-completo").json()
    assert "metricas" in relatorio
    assert "diagnosticos" in relatorio
    assert "acoes" in relatorio
    assert "eventos" in relatorio

if __name__ == "__main__":
    # Executa todos os testes
    pytest.main([__file__, "-v"]) 