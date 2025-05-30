"""
Exemplo de integração entre a visualização 4D, Grafana e InfluxDB.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
from requests.auth import HTTPBasicAuth
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from ..visualizacao_4d import Visualizacao4D, Dimensao4D
from ..config import CONFIG

class GrafanaInfluxDBExporter:
    """Exporta dados da visualização 4D para o Grafana via InfluxDB."""
    
    def __init__(self, visualizador: Visualizacao4D, grafana_url: str, influx_url: str, influx_token: str, influx_org: str, influx_bucket: str, grafana_api_key: str):
        """
        Inicializa o exportador.
        
        Args:
            visualizador: Instância do visualizador 4D
            grafana_url: URL base do Grafana
            influx_url: URL do InfluxDB
            influx_token: Token do InfluxDB
            influx_org: Organização do InfluxDB
            influx_bucket: Bucket do InfluxDB
            grafana_api_key: Chave de API do Grafana
        """
        self.visualizador = visualizador
        self.grafana_url = grafana_url.rstrip("/")
        self.grafana_headers = {
            "Authorization": f"Bearer {grafana_api_key}",
            "Content-Type": "application/json",
            "kbn-xsrf": "true"
        }
        
        # Inicializa cliente InfluxDB
        self.influx_client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
        self.influx_bucket = influx_bucket
        self.influx_write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
        self.influx_query_api = self.influx_client.query_api()
    
    def exportar_dados_influxdb(self):
        """Exporta dados para o InfluxDB."""
        points = []
        
        # Exporta dimensões
        for nome in ["cpu", "memoria", "disco", "latencia", "erros"]:
            dimensoes = self.visualizador.obter_dimensao(nome)
            
            for d in dimensoes:
                point = Point(nome) \
                    .field("valor", d.value) \
                    .time(d.timestamp)
                
                # Adiciona tags do contexto
                for tag, valor in d.context.items():
                    if isinstance(valor, (str, int, float, bool)):
                        point = point.tag(tag, str(valor))
                
                points.append(point)
        
        # Exporta correlações
        matriz = self.visualizador.gerar_matriz_correlacao()
        timestamp = datetime.now()
        
        for dim1 in matriz:
            for dim2, corr in matriz[dim1].items():
                if dim1 != dim2:
                    point = Point("correlacao") \
                        .tag("dimensao1", dim1) \
                        .tag("dimensao2", dim2) \
                        .field("valor", corr) \
                        .time(timestamp)
                    points.append(point)
        
        # Exporta anomalias
        for nome in ["cpu", "memoria", "disco", "latencia", "erros"]:
            anomalias = self.visualizador.detectar_anomalias(nome)
            
            for a in anomalias:
                point = Point("anomalia") \
                    .tag("dimensao", nome) \
                    .field("valor", a["valor"]) \
                    .field("z_score", a["z_score"]) \
                    .time(datetime.now())
                points.append(point)
        
        if points:
            self.influx_write_api.write(bucket=self.influx_bucket, record=points)
    
    def criar_datasource_influxdb(self) -> Dict[str, Any]:
        """
        Cria datasource do InfluxDB no Grafana.
        
        Returns:
            Dicionário com informações do datasource criado
        """
        datasource = {
            "name": "InfluxDB 4D",
            "type": "influxdb",
            "url": self.influx_client.url,
            "access": "proxy",
            "basicAuth": False,
            "isDefault": True,
            "jsonData": {
                "version": "Flux",
                "organization": self.influx_client.org,
                "defaultBucket": self.influx_bucket,
                "tlsSkipVerify": True
            },
            "secureJsonData": {
                "token": self.influx_client.token
            }
        }
        
        # Cria datasource via API
        response = requests.post(
            f"{self.grafana_url}/api/datasources",
            headers=self.grafana_headers,
            json=datasource
        )
        response.raise_for_status()
        
        return response.json()
    
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
                "datasource": "InfluxDB 4D",
                "targets": [
                    {
                        "query": f'''
                        from(bucket: "{self.influx_bucket}")
                            |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
                            |> filter(fn: (r) => r._measurement == "{nome}")
                            |> filter(fn: (r) => r._field == "valor")
                        ''',
                        "refId": "A"
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
            "datasource": "InfluxDB 4D",
            "targets": [
                {
                    "query": f'''
                    from(bucket: "{self.influx_bucket}")
                        |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
                        |> filter(fn: (r) => r._measurement == "correlacao")
                        |> filter(fn: (r) => r._field == "valor")
                    ''',
                    "refId": "A"
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
            "datasource": "InfluxDB 4D",
            "targets": [
                {
                    "query": f'''
                    from(bucket: "{self.influx_bucket}")
                        |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
                        |> filter(fn: (r) => r._measurement == "anomalia")
                        |> filter(fn: (r) => r._field == "valor" or r._field == "z_score")
                    ''',
                    "refId": "A"
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
            headers=self.grafana_headers,
            json=dashboard
        )
        response.raise_for_status()
        
        return response.json()

async def demonstrar_integracao():
    """Demonstra a integração entre Grafana, InfluxDB e visualização 4D."""
    # Inicializa visualizador
    visualizador = Visualizacao4D(CONFIG)
    
    # Inicializa exportador
    exporter = GrafanaInfluxDBExporter(
        visualizador,
        "http://localhost:5601",
        "http://localhost:8086",
        "seu_token_influx_aqui",
        "sua_org_influx_aqui",
        "monitoramento",
        "seu_api_key_grafana_aqui"
    )
    
    try:
        # Cria datasource
        print("Criando datasource no Grafana...")
        datasource = exporter.criar_datasource_influxdb()
        print(f"Datasource criado: {datasource['id']}")
        
        # Cria dashboard
        print("\nCriando dashboard...")
        dashboard = exporter.criar_dashboard("Monitoramento 4D")
        print(f"Dashboard criado: {dashboard['id']}")
        
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
            exporter.exportar_dados_influxdb()
            
            await asyncio.sleep(1)
        
        print("\nDemonstração concluída!")
        print(f"Dashboard disponível em: {exporter.grafana_url}/app/dashboards#{dashboard['id']}")
        
    except Exception as e:
        print(f"Erro durante a demonstração: {e}")
    finally:
        # Fecha conexão
        exporter.influx_client.close()

if __name__ == "__main__":
    asyncio.run(demonstrar_integracao()) 