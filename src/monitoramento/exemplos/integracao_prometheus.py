"""
Exemplo de integração entre a visualização 4D e o Prometheus.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List
import prometheus_client as prom
from prometheus_client import start_http_server

from ..visualizacao_4d import Visualizacao4D, Dimensao4D
from ..config import CONFIG

# Métricas Prometheus
CPU_USAGE = prom.Gauge(
    "cpu_usage_percent",
    "Uso de CPU em porcentagem",
    ["host"]
)

MEMORY_USAGE = prom.Gauge(
    "memory_usage_percent",
    "Uso de memória em porcentagem",
    ["host"]
)

DISK_USAGE = prom.Gauge(
    "disk_usage_percent",
    "Uso de disco em porcentagem",
    ["host"]
)

LATENCY = prom.Gauge(
    "request_latency_ms",
    "Latência de requisições em milissegundos",
    ["endpoint"]
)

ERROR_RATE = prom.Gauge(
    "error_rate_percent",
    "Taxa de erros em porcentagem",
    ["service"]
)

class PrometheusExporter:
    """Exporta métricas do Prometheus para a visualização 4D."""
    
    def __init__(self, visualizador: Visualizacao4D):
        """
        Inicializa o exportador.
        
        Args:
            visualizador: Instância do visualizador 4D
        """
        self.visualizador = visualizador
        self.metricas = {
            "cpu": CPU_USAGE,
            "memoria": MEMORY_USAGE,
            "disco": DISK_USAGE,
            "latencia": LATENCY,
            "erros": ERROR_RATE
        }
    
    def atualizar_metricas(self, metricas: Dict[str, float], labels: Dict[str, str]):
        """
        Atualiza métricas do Prometheus e visualização 4D.
        
        Args:
            metricas: Dicionário com valores das métricas
            labels: Dicionário com labels para as métricas
        """
        # Atualiza métricas do Prometheus
        for nome, valor in metricas.items():
            if nome in self.metricas:
                self.metricas[nome].labels(**labels).set(valor)
        
        # Atualiza visualização 4D
        for nome, valor in metricas.items():
            self.visualizador.atualizar_dimensao(
                nome,
                valor,
                {
                    "host": labels.get("host", "desconhecido"),
                    "timestamp": datetime.now()
                }
            )

async def simular_metricas(exporter: PrometheusExporter, duracao: int = 3600):
    """
    Simula métricas do sistema para demonstração.
    
    Args:
        exporter: Instância do exportador
        duracao: Duração da simulação em segundos
    """
    print("Iniciando simulação de métricas...")
    
    # Métricas iniciais
    metricas = {
        "cpu": 50.0,
        "memoria": 60.0,
        "disco": 70.0,
        "latencia": 100.0,
        "erros": 1.0
    }
    
    # Labels para as métricas
    labels = {
        "host": "server1",
        "endpoint": "/api/metrics",
        "service": "monitoramento"
    }
    
    # Simula métricas por duracao segundos
    for _ in range(duracao):
        # Simula variações nas métricas
        for nome in metricas:
            # Adiciona ruído
            metricas[nome] += random.uniform(-5, 5)
            
            # Mantém dentro dos limites
            if nome in ["cpu", "memoria", "disco", "erros"]:
                metricas[nome] = max(0, min(100, metricas[nome]))
            else:  # latencia
                metricas[nome] = max(0, min(1000, metricas[nome]))
        
        # Atualiza métricas
        exporter.atualizar_metricas(metricas, labels)
        
        await asyncio.sleep(1)

async def demonstrar_integracao():
    """Demonstra a integração entre Prometheus e visualização 4D."""
    # Inicializa visualizador
    visualizador = Visualizacao4D(CONFIG)
    
    # Inicializa exportador
    exporter = PrometheusExporter(visualizador)
    
    # Inicia servidor Prometheus
    start_http_server(8000)
    print("Servidor Prometheus iniciado na porta 8000")
    
    # Inicia simulação em background
    simulador = asyncio.create_task(simular_metricas(exporter))
    
    try:
        # Aguarda alguns dados serem gerados
        await asyncio.sleep(10)
        
        # Demonstra métricas do Prometheus
        print("\nMétricas do Prometheus:")
        for nome, metrica in exporter.metricas.items():
            print(f"- {nome}: {metrica._value.get()}")
        
        # Demonstra dimensões da visualização 4D
        print("\nDimensões da visualização 4D:")
        for nome in ["cpu", "memoria", "disco", "latencia", "erros"]:
            dimensoes = visualizador.obter_dimensao(nome)
            print(f"- {nome}: {len(dimensoes)} pontos")
        
        # Demonstra estatísticas
        print("\nEstatísticas de CPU:")
        estatisticas = visualizador.calcular_estatisticas("cpu")
        for nome, valor in estatisticas.items():
            print(f"- {nome}: {valor:.2f}")
        
        # Demonstra anomalias
        print("\nAnomalias detectadas:")
        for nome in ["cpu", "memoria", "disco", "latencia", "erros"]:
            anomalias = visualizador.detectar_anomalias(nome)
            if anomalias:
                print(f"\n{nome}:")
                for anomalia in anomalias:
                    print(f"- Valor: {anomalia['valor']:.2f}, Z-score: {anomalia['z_score']:.2f}")
        
        # Demonstra correlações
        print("\nCorrelações entre métricas:")
        matriz = visualizador.gerar_matriz_correlacao()
        for dim1 in matriz:
            for dim2, corr in matriz[dim1].items():
                if dim1 != dim2:
                    print(f"- {dim1} x {dim2}: {corr:.2f}")
        
        # Demonstra tendências
        print("\nTendências detectadas:")
        for nome in ["cpu", "memoria", "disco", "latencia", "erros"]:
            tendencias = visualizador.detectar_tendencias(nome)
            print(f"- {nome}: {tendencias['tendencia']} (inclinação: {tendencias['inclinacao']:.2f})")
        
        # Demonstra geração de relatório
        print("\nGerando relatório completo...")
        relatorio = visualizador.gerar_relatorio()
        print(f"Relatório gerado com {len(relatorio['dimensoes'])} dimensões")
        
    finally:
        # Cancela simulação
        simulador.cancel()
        try:
            await simulador
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(demonstrar_integracao()) 