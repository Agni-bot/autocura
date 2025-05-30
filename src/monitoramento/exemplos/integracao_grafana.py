"""
Exemplo de integração entre a visualização 4D e o Grafana.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
from requests.auth import HTTPBasicAuth

from ..visualizacao_4d import Visualizacao4D, Dimensao4D
from ..config import CONFIG

class GrafanaExporter:
    """Exporta dados da visualização 4D para o Grafana."""
    
    def __init__(self, visualizador: Visualizacao4D, grafana_url: str, api_key: str):
        """
        Inicializa o exportador.
        
        Args:
            visualizador: Instância do visualizador 4D
            grafana_url: URL base do Grafana
            api_key: Chave de API do Grafana
        """
        self.visualizador = visualizador
        self.grafana_url = grafana_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def criar_dashboard(self, titulo: str) -> Dict[str, Any]:
        """
        Cria um novo dashboard no Grafana.
        
        Args:
            titulo: Título do dashboard
            
        Returns:
            Dicionário com informações do dashboard criado
        """
        # Template do dashboard
        dashboard = {
            "dashboard": {
                "title": titulo,
                "panels": [],
                "time": {
                    "from": "now-6h",
                    "to": "now"
                },
                "timezone": "browser"
            },
            "overwrite": True
        }
        
        # Adiciona painéis para cada dimensão
        for nome in ["cpu", "memoria", "disco", "latencia", "erros"]:
            panel = {
                "title": f"{nome.title()} - Série Temporal",
                "type": "graph",
                "datasource": "Prometheus",
                "targets": [
                    {
                        "expr": f"{nome}_usage_percent",
                        "legendFormat": "{{host}}"
                    }
                ],
                "gridPos": {
                    "x": 0,
                    "y": len(dashboard["dashboard"]["panels"]),
                    "w": 12,
                    "h": 8
                }
            }
            dashboard["dashboard"]["panels"].append(panel)
        
        # Adiciona painel de correlação
        correlation_panel = {
            "title": "Matriz de Correlação",
            "type": "heatmap",
            "datasource": "Prometheus",
            "targets": [
                {
                    "expr": "correlation_matrix",
                    "legendFormat": "{{dimension}}"
                }
            ],
            "gridPos": {
                "x": 0,
                "y": len(dashboard["dashboard"]["panels"]),
                "w": 24,
                "h": 8
            }
        }
        dashboard["dashboard"]["panels"].append(correlation_panel)
        
        # Adiciona painel de anomalias
        anomaly_panel = {
            "title": "Anomalias Detectadas",
            "type": "table",
            "datasource": "Prometheus",
            "targets": [
                {
                    "expr": "anomalies",
                    "legendFormat": "{{dimension}}"
                }
            ],
            "gridPos": {
                "x": 0,
                "y": len(dashboard["dashboard"]["panels"]),
                "w": 24,
                "h": 8
            }
        }
        dashboard["dashboard"]["panels"].append(anomaly_panel)
        
        # Cria dashboard via API
        response = requests.post(
            f"{self.grafana_url}/api/dashboards/db",
            headers=self.headers,
            json=dashboard
        )
        response.raise_for_status()
        
        return response.json()
    
    def atualizar_dashboard(self, dashboard_uid: str, dados: Dict[str, Any]):
        """
        Atualiza dados do dashboard no Grafana.
        
        Args:
            dashboard_uid: UID do dashboard
            dados: Dados para atualização
        """
        # Obtém dashboard atual
        response = requests.get(
            f"{self.grafana_url}/api/dashboards/uid/{dashboard_uid}",
            headers=self.headers
        )
        response.raise_for_status()
        dashboard = response.json()["dashboard"]
        
        # Atualiza painéis com novos dados
        for panel in dashboard["panels"]:
            if panel["title"].endswith("Série Temporal"):
                dimensao = panel["title"].split(" - ")[0].lower()
                panel["targets"][0]["expr"] = f"{dimensao}_usage_percent"
            elif panel["title"] == "Matriz de Correlação":
                panel["targets"][0]["expr"] = "correlation_matrix"
            elif panel["title"] == "Anomalias Detectadas":
                panel["targets"][0]["expr"] = "anomalies"
        
        # Atualiza dashboard via API
        response = requests.post(
            f"{self.grafana_url}/api/dashboards/db",
            headers=self.headers,
            json={
                "dashboard": dashboard,
                "overwrite": True
            }
        )
        response.raise_for_status()
    
    def exportar_dados(self, dashboard_uid: str):
        """
        Exporta dados da visualização 4D para o Grafana.
        
        Args:
            dashboard_uid: UID do dashboard
        """
        # Obtém dados da visualização 4D
        dados = {
            "dimensoes": {},
            "correlacoes": {},
            "anomalias": {}
        }
        
        # Exporta dimensões
        for nome in ["cpu", "memoria", "disco", "latencia", "erros"]:
            dimensoes = self.visualizador.obter_dimensao(nome)
            dados["dimensoes"][nome] = [
                {
                    "timestamp": d.timestamp.timestamp() * 1000,
                    "value": d.value,
                    "context": d.context
                }
                for d in dimensoes
            ]
        
        # Exporta correlações
        matriz = self.visualizador.gerar_matriz_correlacao()
        dados["correlacoes"] = matriz
        
        # Exporta anomalias
        for nome in ["cpu", "memoria", "disco", "latencia", "erros"]:
            anomalias = self.visualizador.detectar_anomalias(nome)
            if anomalias:
                dados["anomalias"][nome] = anomalias
        
        # Atualiza dashboard
        self.atualizar_dashboard(dashboard_uid, dados)

async def demonstrar_integracao():
    """Demonstra a integração entre Grafana e visualização 4D."""
    # Inicializa visualizador
    visualizador = Visualizacao4D(CONFIG)
    
    # Inicializa exportador
    exporter = GrafanaExporter(
        visualizador,
        "http://localhost:3000",
        "seu_api_key_aqui"
    )
    
    try:
        # Cria dashboard
        print("Criando dashboard no Grafana...")
        dashboard = exporter.criar_dashboard("Monitoramento 4D")
        print(f"Dashboard criado: {dashboard['url']}")
        
        # Simula dados
        print("\nSimulando dados...")
        for _ in range(10):
            # Atualiza dimensões
            for nome in ["cpu", "memoria", "disco", "latencia", "erros"]:
                valor = random.uniform(0, 100)
                visualizador.atualizar_dimensao(
                    nome,
                    valor,
                    {
                        "host": "server1",
                        "timestamp": datetime.now()
                    }
                )
            
            # Exporta dados
            exporter.exportar_dados(dashboard["uid"])
            
            await asyncio.sleep(1)
        
        print("\nDemonstração concluída!")
        print(f"Dashboard disponível em: {dashboard['url']}")
        
    except Exception as e:
        print(f"Erro durante a demonstração: {e}")

if __name__ == "__main__":
    asyncio.run(demonstrar_integracao()) 