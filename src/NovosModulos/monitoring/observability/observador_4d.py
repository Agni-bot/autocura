import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import numpy as np
from prometheus_client import start_http_server, Gauge, Counter, Histogram

@dataclass
class Dimensao4D:
    """Representa uma dimensão 4D do sistema."""
    nome: str
    valor: float
    timestamp: datetime
    contexto: Dict[str, Any]

class Observador4D:
    """Módulo de observabilidade 4D para visualização e controle do sistema."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o observador 4D.
        
        Args:
            config: Configuração do observador
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Métricas Prometheus
        self.metricas = {
            "cpu_usage": Gauge("cpu_usage", "Uso de CPU", ["host"]),
            "memory_usage": Gauge("memory_usage", "Uso de memória", ["host"]),
            "disk_usage": Gauge("disk_usage", "Uso de disco", ["host"]),
            "network_io": Gauge("network_io", "I/O de rede", ["host", "direction"]),
            "request_latency": Histogram("request_latency", "Latência de requisições", ["endpoint"]),
            "error_rate": Counter("error_rate", "Taxa de erros", ["type"]),
            "active_connections": Gauge("active_connections", "Conexões ativas", ["service"])
        }
        
        # Dimensões 4D
        self.dimensoes = {
            "performance": [],
            "saude": [],
            "seguranca": [],
            "custo": []
        }
        
        # Cache de métricas
        self.cache_metricas = {}
        self.cache_timeout = timedelta(minutes=5)
        
        # Inicializa servidor Prometheus
        start_http_server(self.config.get("prometheus_port", 9090))
        
        self.logger.info("Observador 4D inicializado")
    
    async def atualizar_dimensao(self, nome: str, valor: float, contexto: Dict[str, Any]) -> None:
        """Atualiza uma dimensão 4D.
        
        Args:
            nome: Nome da dimensão
            valor: Valor da dimensão
            contexto: Contexto adicional
        """
        dimensao = Dimensao4D(
            nome=nome,
            valor=valor,
            timestamp=datetime.now(),
            contexto=contexto
        )
        
        if nome in self.dimensoes:
            self.dimensoes[nome].append(dimensao)
            # Mantém apenas as últimas 1000 dimensões
            if len(self.dimensoes[nome]) > 1000:
                self.dimensoes[nome] = self.dimensoes[nome][-1000:]
        
        self.logger.debug(f"Dimensão {nome} atualizada: {valor}")
    
    async def obter_dimensao(self, nome: str, periodo: Optional[timedelta] = None) -> List[Dimensao4D]:
        """Obtém as dimensões 4D de um período.
        
        Args:
            nome: Nome da dimensão
            periodo: Período de tempo (opcional)
            
        Returns:
            Lista de dimensões
        """
        if nome not in self.dimensoes:
            return []
        
        dimensoes = self.dimensoes[nome]
        
        if periodo:
            inicio = datetime.now() - periodo
            dimensoes = [d for d in dimensoes if d.timestamp >= inicio]
        
        return dimensoes
    
    async def calcular_estatisticas(self, nome: str, periodo: Optional[timedelta] = None) -> Dict[str, float]:
        """Calcula estatísticas de uma dimensão.
        
        Args:
            nome: Nome da dimensão
            periodo: Período de tempo (opcional)
            
        Returns:
            Dicionário com estatísticas
        """
        dimensoes = await self.obter_dimensao(nome, periodo)
        
        if not dimensoes:
            return {}
        
        valores = [d.valor for d in dimensoes]
        
        return {
            "media": np.mean(valores),
            "mediana": np.median(valores),
            "desvio_padrao": np.std(valores),
            "min": np.min(valores),
            "max": np.max(valores)
        }
    
    async def detectar_anomalias(self, nome: str, periodo: Optional[timedelta] = None) -> List[Dict[str, Any]]:
        """Detecta anomalias em uma dimensão.
        
        Args:
            nome: Nome da dimensão
            periodo: Período de tempo (opcional)
            
        Returns:
            Lista de anomalias detectadas
        """
        dimensoes = await self.obter_dimensao(nome, periodo)
        
        if not dimensoes:
            return []
        
        valores = np.array([d.valor for d in dimensoes])
        media = np.mean(valores)
        desvio = np.std(valores)
        
        anomalias = []
        for i, dimensao in enumerate(dimensoes):
            z_score = abs(dimensao.valor - media) / desvio
            if z_score > 3:  # Mais de 3 desvios padrão
                anomalias.append({
                    "timestamp": dimensao.timestamp,
                    "valor": dimensao.valor,
                    "z_score": z_score,
                    "contexto": dimensao.contexto
                })
        
        return anomalias
    
    async def atualizar_metricas(self, metricas: Dict[str, Any]) -> None:
        """Atualiza as métricas do sistema.
        
        Args:
            metricas: Dicionário com métricas
        """
        for nome, valor in metricas.items():
            if nome in self.metricas:
                if isinstance(self.metricas[nome], Gauge):
                    self.metricas[nome].set(value=valor)
                elif isinstance(self.metricas[nome], Counter):
                    self.metricas[nome].inc(value=valor)
                elif isinstance(self.metricas[nome], Histogram):
                    self.metricas[nome].observe(value=valor)
        
        self.cache_metricas = metricas
        self.cache_metricas["timestamp"] = datetime.now()
    
    async def obter_metricas(self, nome: Optional[str] = None) -> Dict[str, Any]:
        """Obtém as métricas do sistema.
        
        Args:
            nome: Nome da métrica (opcional)
            
        Returns:
            Dicionário com métricas
        """
        if nome:
            return {nome: self.cache_metricas.get(nome)}
        
        return self.cache_metricas
    
    async def gerar_relatorio(self, periodo: Optional[timedelta] = None) -> Dict[str, Any]:
        """Gera um relatório do sistema.
        
        Args:
            periodo: Período de tempo (opcional)
            
        Returns:
            Dicionário com relatório
        """
        relatorio = {
            "timestamp": datetime.now(),
            "dimensoes": {},
            "metricas": self.cache_metricas,
            "anomalias": {}
        }
        
        for nome in self.dimensoes:
            relatorio["dimensoes"][nome] = await self.calcular_estatisticas(nome, periodo)
            relatorio["anomalias"][nome] = await self.detectar_anomalias(nome, periodo)
        
        return relatorio
    
    async def limpar_dados_antigos(self, periodo: timedelta) -> None:
        """Limpa dados antigos do sistema.
        
        Args:
            periodo: Período de tempo para manter
        """
        inicio = datetime.now() - periodo
        
        for nome in self.dimensoes:
            self.dimensoes[nome] = [
                d for d in self.dimensoes[nome]
                if d.timestamp >= inicio
            ]
        
        self.logger.info(f"Dados antigos removidos (período: {periodo})") 