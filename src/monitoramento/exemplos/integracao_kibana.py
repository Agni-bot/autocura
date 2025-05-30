"""
Exemplo de integração entre a visualização 4D e o Kibana.
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

class KibanaExporter:
    """Exporta visualizações 4D para o Kibana."""
    
    def __init__(self, visualizador: Visualizacao4D, kibana_url: str, es_url: str, api_key: str):
        """
        Inicializa o exportador.
        
        Args:
            visualizador: Instância do visualizador 4D
            kibana_url: URL base do Kibana
            es_url: URL do Elasticsearch
            api_key: Chave de API do Kibana
        """
        self.visualizador = visualizador
        self.kibana_url = kibana_url.rstrip("/")
        self.es_url = es_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "kbn-xsrf": "true"
        }
    
    def criar_dashboard(self, titulo: str) -> Dict[str, Any]:
        """
        Cria um novo dashboard no Kibana.
        
        Args:
            titulo: Título do dashboard
            
        Returns:
            Dicionário com informações do dashboard criado
        """
        # Template do dashboard
        dashboard = {
            "attributes": {
                "title": titulo,
                "hits": 0,
                "description": "Dashboard de monitoramento 4D",
                "panelsJSON": json.dumps([
                    # Painel de séries temporais
                    {
                        "type": "visualization",
                        "id": "series_temporais",
                        "panelIndex": "1",
                        "gridData": {
                            "x": 0,
                            "y": 0,
                            "w": 24,
                            "h": 15,
                            "i": "1"
                        },
                        "version": "7.9.0",
                        "embeddableConfig": {
                            "title": "Séries Temporais"
                        }
                    },
                    # Painel de correlação
                    {
                        "type": "visualization",
                        "id": "correlacao",
                        "panelIndex": "2",
                        "gridData": {
                            "x": 0,
                            "y": 15,
                            "w": 12,
                            "h": 15,
                            "i": "2"
                        },
                        "version": "7.9.0",
                        "embeddableConfig": {
                            "title": "Matriz de Correlação"
                        }
                    },
                    # Painel de anomalias
                    {
                        "type": "visualization",
                        "id": "anomalias",
                        "panelIndex": "3",
                        "gridData": {
                            "x": 12,
                            "y": 15,
                            "w": 12,
                            "h": 15,
                            "i": "3"
                        },
                        "version": "7.9.0",
                        "embeddableConfig": {
                            "title": "Anomalias Detectadas"
                        }
                    }
                ]),
                "optionsJSON": json.dumps({
                    "hidePanelTitles": False,
                    "useMargins": True
                }),
                "version": 1,
                "timeRestore": False,
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": json.dumps({
                        "query": {"query": "", "language": "kuery"},
                        "filter": []
                    })
                }
            }
        }
        
        # Cria dashboard via API
        response = requests.post(
            f"{self.kibana_url}/api/saved_objects/dashboard",
            headers=self.headers,
            json=dashboard
        )
        response.raise_for_status()
        
        return response.json()
    
    def criar_visualizacao_series_temporais(self) -> Dict[str, Any]:
        """
        Cria visualização de séries temporais no Kibana.
        
        Returns:
            Dicionário com informações da visualização criada
        """
        # Template da visualização
        vis = {
            "attributes": {
                "title": "Séries Temporais",
                "visState": json.dumps({
                    "title": "Séries Temporais",
                    "type": "line",
                    "params": {
                        "type": "line",
                        "grid": {"categoryLines": False},
                        "categoryAxes": [
                            {
                                "id": "CategoryAxis-1",
                                "type": "category",
                                "position": "bottom",
                                "show": True,
                                "style": {},
                                "scale": {"type": "linear"},
                                "labels": {"show": True, "filter": True, "truncate": 100},
                                "title": {}
                            }
                        ],
                        "valueAxes": [
                            {
                                "id": "ValueAxis-1",
                                "type": "value",
                                "position": "left",
                                "show": True,
                                "style": {},
                                "scale": {"type": "linear", "mode": "normal"},
                                "labels": {"show": True, "rotate": 0, "filter": False, "truncate": 100},
                                "title": {"text": "Valor"}
                            }
                        ],
                        "seriesParams": [
                            {
                                "show": True,
                                "type": "line",
                                "mode": "normal",
                                "data": {"label": "Valor", "id": "1"},
                                "valueAxis": "ValueAxis-1",
                                "drawLinesBetweenPoints": True,
                                "lineWidth": 2,
                                "interpolate": "linear",
                                "showCircles": True
                            }
                        ],
                        "addTooltip": True,
                        "addLegend": True,
                        "legendPosition": "right",
                        "times": [],
                        "addTimeMarker": False
                    },
                    "aggs": [
                        {
                            "id": "1",
                            "enabled": True,
                            "type": "avg",
                            "schema": "metric",
                            "params": {"field": "valor"}
                        },
                        {
                            "id": "2",
                            "enabled": True,
                            "type": "date_histogram",
                            "schema": "segment",
                            "params": {
                                "field": "timestamp",
                                "timeRange": {"from": "now-15m", "to": "now"},
                                "useNormalizedEsInterval": True,
                                "scaleMetricValues": False,
                                "interval": "auto",
                                "drop_partials": False,
                                "min_doc_count": 1,
                                "extended_bounds": {}
                            }
                        }
                    ]
                }),
                "uiStateJSON": "{}",
                "description": "",
                "savedSearchRefName": "search_0",
                "version": 1,
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": json.dumps({
                        "query": {"query": "", "language": "kuery"},
                        "filter": []
                    })
                }
            }
        }
        
        # Cria visualização via API
        response = requests.post(
            f"{self.kibana_url}/api/saved_objects/visualization",
            headers=self.headers,
            json=vis
        )
        response.raise_for_status()
        
        return response.json()
    
    def criar_visualizacao_correlacao(self) -> Dict[str, Any]:
        """
        Cria visualização de correlação no Kibana.
        
        Returns:
            Dicionário com informações da visualização criada
        """
        # Template da visualização
        vis = {
            "attributes": {
                "title": "Matriz de Correlação",
                "visState": json.dumps({
                    "title": "Matriz de Correlação",
                    "type": "heatmap",
                    "params": {
                        "type": "heatmap",
                        "addTooltip": True,
                        "addLegend": True,
                        "enableHover": False,
                        "legendPosition": "right",
                        "times": [],
                        "addTimeMarker": False,
                        "dimensions": {
                            "x": {
                                "accessor": 0,
                                "format": {"id": "string"},
                                "params": {"date": True, "interval": "PT30S", "intervalESValue": 30, "intervalESUnit": "s", "format": "HH:mm:ss", "bounds": {"min": "2020-01-01T00:00:00.000Z", "max": "2020-12-31T23:59:59.999Z"}},
                                "aggType": "date_histogram"
                            },
                            "y": {
                                "accessor": 1,
                                "format": {"id": "string"},
                                "params": {"date": False, "interval": 30, "intervalESValue": 30, "intervalESUnit": "s", "format": "HH:mm:ss", "bounds": {"min": 0, "max": 100}},
                                "aggType": "histogram"
                            },
                            "z": {
                                "accessor": 2,
                                "format": {"id": "number"},
                                "params": {},
                                "aggType": "avg"
                            }
                        },
                        "gridConfig": {
                            "type": "heatmap",
                            "title": "Valor",
                            "xAxis": {"title": "Tempo"},
                            "yAxis": {"title": "Dimensão"}
                        }
                    },
                    "aggs": [
                        {
                            "id": "1",
                            "enabled": True,
                            "type": "date_histogram",
                            "schema": "segment",
                            "params": {
                                "field": "timestamp",
                                "timeRange": {"from": "now-15m", "to": "now"},
                                "useNormalizedEsInterval": True,
                                "scaleMetricValues": False,
                                "interval": "auto",
                                "drop_partials": False,
                                "min_doc_count": 1,
                                "extended_bounds": {}
                            }
                        },
                        {
                            "id": "2",
                            "enabled": True,
                            "type": "terms",
                            "schema": "group",
                            "params": {
                                "field": "dimensao",
                                "size": 5,
                                "order": "desc",
                                "orderBy": "_term",
                                "otherBucket": False,
                                "otherBucketLabel": "Other",
                                "missingBucket": False,
                                "missingBucketLabel": "Missing"
                            }
                        },
                        {
                            "id": "3",
                            "enabled": True,
                            "type": "avg",
                            "schema": "metric",
                            "params": {"field": "correlacao"}
                        }
                    ]
                }),
                "uiStateJSON": "{}",
                "description": "",
                "savedSearchRefName": "search_0",
                "version": 1,
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": json.dumps({
                        "query": {"query": "", "language": "kuery"},
                        "filter": []
                    })
                }
            }
        }
        
        # Cria visualização via API
        response = requests.post(
            f"{self.kibana_url}/api/saved_objects/visualization",
            headers=self.headers,
            json=vis
        )
        response.raise_for_status()
        
        return response.json()
    
    def criar_visualizacao_anomalias(self) -> Dict[str, Any]:
        """
        Cria visualização de anomalias no Kibana.
        
        Returns:
            Dicionário com informações da visualização criada
        """
        # Template da visualização
        vis = {
            "attributes": {
                "title": "Anomalias Detectadas",
                "visState": json.dumps({
                    "title": "Anomalias Detectadas",
                    "type": "table",
                    "params": {
                        "perPage": 10,
                        "showPartialRows": False,
                        "showMetricsAtAllLevels": False,
                        "sort": {"columnIndex": None, "direction": None},
                        "showTotal": False,
                        "totalFunc": "sum",
                        "percentageCol": ""
                    },
                    "aggs": [
                        {
                            "id": "1",
                            "enabled": True,
                            "type": "count",
                            "schema": "metric",
                            "params": {}
                        },
                        {
                            "id": "2",
                            "enabled": True,
                            "type": "terms",
                            "schema": "bucket",
                            "params": {
                                "field": "dimensao",
                                "size": 5,
                                "order": "desc",
                                "orderBy": "_term",
                                "otherBucket": False,
                                "otherBucketLabel": "Other",
                                "missingBucket": False,
                                "missingBucketLabel": "Missing"
                            }
                        },
                        {
                            "id": "3",
                            "enabled": True,
                            "type": "avg",
                            "schema": "metric",
                            "params": {"field": "z_score"}
                        }
                    ]
                }),
                "uiStateJSON": "{}",
                "description": "",
                "savedSearchRefName": "search_0",
                "version": 1,
                "kibanaSavedObjectMeta": {
                    "searchSourceJSON": json.dumps({
                        "query": {"query": "", "language": "kuery"},
                        "filter": []
                    })
                }
            }
        }
        
        # Cria visualização via API
        response = requests.post(
            f"{self.kibana_url}/api/saved_objects/visualization",
            headers=self.headers,
            json=vis
        )
        response.raise_for_status()
        
        return response.json()

async def demonstrar_integracao():
    """Demonstra a integração entre Kibana e visualização 4D."""
    # Inicializa visualizador
    visualizador = Visualizacao4D(CONFIG)
    
    # Inicializa exportador
    exporter = KibanaExporter(
        visualizador,
        "http://localhost:5601",
        "http://localhost:9200",
        "seu_api_key_aqui"
    )
    
    try:
        # Cria visualizações
        print("Criando visualizações no Kibana...")
        
        series = exporter.criar_visualizacao_series_temporais()
        print(f"Visualização de séries temporais criada: {series['id']}")
        
        correlacao = exporter.criar_visualizacao_correlacao()
        print(f"Visualização de correlação criada: {correlacao['id']}")
        
        anomalias = exporter.criar_visualizacao_anomalias()
        print(f"Visualização de anomalias criada: {anomalias['id']}")
        
        # Cria dashboard
        print("\nCriando dashboard...")
        dashboard = exporter.criar_dashboard("Monitoramento 4D")
        print(f"Dashboard criado: {dashboard['id']}")
        
        print("\nDemonstração concluída!")
        print(f"Dashboard disponível em: {exporter.kibana_url}/app/dashboards#{dashboard['id']}")
        
    except Exception as e:
        print(f"Erro durante a demonstração: {e}")

if __name__ == "__main__":
    asyncio.run(demonstrar_integracao()) 