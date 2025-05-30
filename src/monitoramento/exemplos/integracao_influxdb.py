"""
Exemplo de integração entre a visualização 4D e o InfluxDB.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from ..visualizacao_4d import Visualizacao4D, Dimensao4D
from ..config import CONFIG

class InfluxDBExporter:
    """Exporta dados da visualização 4D para o InfluxDB."""
    
    def __init__(self, visualizador: Visualizacao4D, url: str, token: str, org: str, bucket: str):
        """
        Inicializa o exportador.
        
        Args:
            visualizador: Instância do visualizador 4D
            url: URL do InfluxDB
            token: Token de autenticação
            org: Organização
            bucket: Bucket para armazenamento
        """
        self.visualizador = visualizador
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.bucket = bucket
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
    
    def exportar_dimensoes(self):
        """Exporta dimensões para o InfluxDB."""
        points = []
        
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
        
        if points:
            self.write_api.write(bucket=self.bucket, record=points)
    
    def exportar_correlacoes(self):
        """Exporta correlações para o InfluxDB."""
        points = []
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
        
        if points:
            self.write_api.write(bucket=self.bucket, record=points)
    
    def exportar_anomalias(self):
        """Exporta anomalias para o InfluxDB."""
        points = []
        
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
            self.write_api.write(bucket=self.bucket, record=points)
    
    def exportar_dados(self):
        """Exporta todos os dados para o InfluxDB."""
        self.exportar_dimensoes()
        self.exportar_correlacoes()
        self.exportar_anomalias()
    
    def buscar_dimensoes(self, nome: str, inicio: datetime, fim: datetime) -> List[Dict]:
        """
        Busca dimensões no InfluxDB.
        
        Args:
            nome: Nome da dimensão
            inicio: Data/hora inicial
            fim: Data/hora final
            
        Returns:
            Lista de dimensões encontradas
        """
        query = f'''
        from(bucket: "{self.bucket}")
            |> range(start: {inicio.isoformat()}, stop: {fim.isoformat()})
            |> filter(fn: (r) => r._measurement == "{nome}")
            |> filter(fn: (r) => r._field == "valor")
        '''
        
        result = self.query_api.query(query)
        
        dimensoes = []
        for table in result:
            for record in table.records:
                dimensao = {
                    "nome": nome,
                    "valor": record.get_value(),
                    "timestamp": record.get_time(),
                    "context": {
                        k: v for k, v in record.values.items()
                        if k not in ["_measurement", "_field", "_value", "_time"]
                    }
                }
                dimensoes.append(dimensao)
        
        return dimensoes
    
    def buscar_correlacoes(self, dimensao: str) -> List[Dict]:
        """
        Busca correlações no InfluxDB.
        
        Args:
            dimensao: Nome da dimensão
            
        Returns:
            Lista de correlações encontradas
        """
        query = f'''
        from(bucket: "{self.bucket}")
            |> range(start: -1h)
            |> filter(fn: (r) => r._measurement == "correlacao")
            |> filter(fn: (r) => r.dimensao1 == "{dimensao}" or r.dimensao2 == "{dimensao}")
            |> filter(fn: (r) => r._field == "valor")
        '''
        
        result = self.query_api.query(query)
        
        correlacoes = []
        for table in result:
            for record in table.records:
                correlacao = {
                    "dimensao1": record.values.get("dimensao1"),
                    "dimensao2": record.values.get("dimensao2"),
                    "correlacao": record.get_value(),
                    "timestamp": record.get_time()
                }
                correlacoes.append(correlacao)
        
        return correlacoes
    
    def buscar_anomalias(self, dimensao: str, inicio: datetime, fim: datetime) -> List[Dict]:
        """
        Busca anomalias no InfluxDB.
        
        Args:
            dimensao: Nome da dimensão
            inicio: Data/hora inicial
            fim: Data/hora final
            
        Returns:
            Lista de anomalias encontradas
        """
        query = f'''
        from(bucket: "{self.bucket}")
            |> range(start: {inicio.isoformat()}, stop: {fim.isoformat()})
            |> filter(fn: (r) => r._measurement == "anomalia")
            |> filter(fn: (r) => r.dimensao == "{dimensao}")
            |> filter(fn: (r) => r._field == "valor" or r._field == "z_score")
        '''
        
        result = self.query_api.query(query)
        
        anomalias = []
        for table in result:
            for record in table.records:
                anomalia = {
                    "dimensao": dimensao,
                    "valor": record.get_value() if record.get_field() == "valor" else None,
                    "z_score": record.get_value() if record.get_field() == "z_score" else None,
                    "timestamp": record.get_time()
                }
                anomalias.append(anomalia)
        
        return anomalias

async def demonstrar_integracao():
    """Demonstra a integração entre InfluxDB e visualização 4D."""
    # Inicializa visualizador
    visualizador = Visualizacao4D(CONFIG)
    
    # Inicializa exportador
    exporter = InfluxDBExporter(
        visualizador,
        "http://localhost:8086",
        "seu_token_aqui",
        "sua_org_aqui",
        "monitoramento"
    )
    
    try:
        # Simula dados
        print("Simulando dados...")
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
            exporter.exportar_dados()
            
            await asyncio.sleep(1)
        
        # Demonstra buscas
        print("\nDemonstrando buscas...")
        
        # Busca dimensões
        inicio = datetime.now() - timedelta(minutes=5)
        fim = datetime.now()
        
        print("\nDimensões de CPU:")
        dimensoes = exporter.buscar_dimensoes("cpu", inicio, fim)
        for d in dimensoes:
            print(f"- Valor: {d['valor']:.2f}, Timestamp: {d['timestamp']}")
        
        # Busca correlações
        print("\nCorrelações de CPU:")
        correlacoes = exporter.buscar_correlacoes("cpu")
        for c in correlacoes:
            print(f"- {c['dimensao1']} x {c['dimensao2']}: {c['correlacao']:.2f}")
        
        # Busca anomalias
        print("\nAnomalias de CPU:")
        anomalias = exporter.buscar_anomalias("cpu", inicio, fim)
        for a in anomalias:
            print(f"- Valor: {a['valor']:.2f}, Z-score: {a['z_score']:.2f}")
        
        print("\nDemonstração concluída!")
        
    except Exception as e:
        print(f"Erro durante a demonstração: {e}")
    finally:
        # Fecha conexão
        exporter.client.close()

if __name__ == "__main__":
    asyncio.run(demonstrar_integracao()) 