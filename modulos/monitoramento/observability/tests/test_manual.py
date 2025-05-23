"""
Script para testes manuais do módulo de observabilidade.
"""

import requests
import json
from datetime import datetime
import time

# URLs dos serviços
OBSERVABILIDADE_URL = "http://localhost:8080"
MONITORAMENTO_URL = "http://localhost:8081"
DIAGNOSTICO_URL = "http://localhost:5002"
GERADOR_URL = "http://localhost:5003"

def print_separator():
    """Imprime separador para melhor visualização."""
    print("\n" + "="*80 + "\n")

def test_health_check():
    """Testa o endpoint de health check."""
    print("Testando health check...")
    response = requests.get(f"{OBSERVABILIDADE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    print_separator()

def test_obter_metricas():
    """Testa a obtenção de métricas."""
    print("Obtendo métricas...")
    response = requests.get(f"{OBSERVABILIDADE_URL}/api/v1/metricas")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Número de métricas: {len(data)}")
    if len(data) > 0:
        print("Exemplo de métrica:")
        print(json.dumps(data[0], indent=2))
    print_separator()

def test_obter_diagnosticos():
    """Testa a obtenção de diagnósticos."""
    print("Obtendo diagnósticos...")
    response = requests.get(f"{OBSERVABILIDADE_URL}/api/v1/diagnosticos")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Número de diagnósticos: {len(data)}")
    if len(data) > 0:
        print("Exemplo de diagnóstico:")
        print(json.dumps(data[0], indent=2))
    print_separator()

def test_obter_acoes():
    """Testa a obtenção de ações."""
    print("Obtendo ações...")
    response = requests.get(f"{OBSERVABILIDADE_URL}/api/v1/acoes")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Número de ações: {len(data)}")
    if len(data) > 0:
        print("Exemplo de ação:")
        print(json.dumps(data[0], indent=2))
    print_separator()

def test_criar_visualizacao():
    """Testa a criação de visualização."""
    print("Criando visualização...")
    payload = {
        "titulo": f"Teste Manual - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "agrupar_por_dimensao": True,
        "salvar": True
    }
    response = requests.post(
        f"{OBSERVABILIDADE_URL}/api/visualizacoes/metricas-temporais",
        json=payload
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print("Resposta:")
    print(json.dumps(data, indent=2))
    print_separator()

def test_gerar_relatorio():
    """Testa a geração de relatório."""
    print("Gerando relatório completo...")
    response = requests.get(f"{OBSERVABILIDADE_URL}/api/v1/relatorio-completo")
    print(f"Status: {response.status_code}")
    data = response.json()
    print("Resumo do relatório:")
    print(f"- Número de métricas: {len(data.get('metricas', []))}")
    print(f"- Número de diagnósticos: {len(data.get('diagnosticos', []))}")
    print(f"- Número de ações: {len(data.get('acoes', []))}")
    print(f"- Número de eventos: {len(data.get('eventos', []))}")
    print_separator()

def test_fluxo_completo():
    """Testa o fluxo completo do sistema."""
    print("Iniciando teste do fluxo completo...")
    
    # 1. Health Check
    test_health_check()
    time.sleep(1)
    
    # 2. Métricas
    test_obter_metricas()
    time.sleep(1)
    
    # 3. Diagnósticos
    test_obter_diagnosticos()
    time.sleep(1)
    
    # 4. Ações
    test_obter_acoes()
    time.sleep(1)
    
    # 5. Visualização
    test_criar_visualizacao()
    time.sleep(1)
    
    # 6. Relatório
    test_gerar_relatorio()
    
    print("Teste do fluxo completo finalizado!")

if __name__ == "__main__":
    print("Iniciando testes manuais do módulo de observabilidade...")
    print_separator()
    
    try:
        test_fluxo_completo()
    except Exception as e:
        print(f"Erro durante os testes: {str(e)}")
        raise
    
    print("Testes manuais finalizados!") 