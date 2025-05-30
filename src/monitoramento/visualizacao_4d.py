"""
Módulo de visualização 4D do sistema AutoCura.

Este módulo implementa visualização multidimensional de métricas, incluindo:
- Visualização temporal
- Análise de correlações
- Detecção de anomalias
- Geração de relatórios
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import numpy as np
from prometheus_client import Gauge, Counter, Histogram, Summary

logger = logging.getLogger(__name__)

@dataclass
class Dimensao4D:
    """Representa uma dimensão 4D do sistema."""
    nome: str
    valor: float
    timestamp: datetime
    contexto: Dict[str, Any]

class Visualizacao4D:
    """Módulo de visualização 4D para análise multidimensional do sistema."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o visualizador 4D.
        
        Args:
            config: Configuração do visualizador
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Métricas Prometheus
        self.metricas = {
            "cpu_uso": Gauge("cpu_uso", "Uso de CPU", ["host"]),
            "memoria_uso": Gauge("memoria_uso", "Uso de memória", ["host"]),
            "disco_uso": Gauge("disco_uso", "Uso de disco", ["host"]),
            "rede_io": Gauge("rede_io", "I/O de rede", ["host", "direcao"]),
            "latencia": Histogram("latencia", "Latência de requisições", ["endpoint"]),
            "taxa_erro": Counter("taxa_erro", "Taxa de erros", ["tipo"]),
            "conexoes_ativas": Gauge("conexoes_ativas", "Conexões ativas", ["servico"])
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
        
        self.logger.info("Visualizador 4D inicializado")
    
    def atualizar_dimensao(self, nome: str, valor: float, contexto: Dict[str, Any]) -> None:
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
    
    def obter_dimensao(self, nome: str, periodo: Optional[timedelta] = None) -> List[Dimensao4D]:
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
    
    def calcular_estatisticas(self, nome: str, periodo: Optional[timedelta] = None) -> Dict[str, float]:
        """Calcula estatísticas de uma dimensão.
        
        Args:
            nome: Nome da dimensão
            periodo: Período de tempo (opcional)
            
        Returns:
            Dicionário com estatísticas
        """
        dimensoes = self.obter_dimensao(nome, periodo)
        
        if not dimensoes:
            return {}
        
        valores = [d.valor for d in dimensoes]
        
        return {
            "media": float(np.mean(valores)),
            "mediana": float(np.median(valores)),
            "desvio_padrao": float(np.std(valores)),
            "min": float(np.min(valores)),
            "max": float(np.max(valores))
        }
    
    def detectar_anomalias(self, nome: str, periodo: Optional[timedelta] = None) -> List[Dict[str, Any]]:
        """Detecta anomalias em uma dimensão.
        
        Args:
            nome: Nome da dimensão
            periodo: Período de tempo (opcional)
            
        Returns:
            Lista de anomalias detectadas
        """
        dimensoes = self.obter_dimensao(nome, periodo)
        
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
                    "timestamp": dimensao.timestamp.isoformat(),
                    "valor": float(dimensao.valor),
                    "z_score": float(z_score),
                    "contexto": dimensao.contexto
                })
        
        return anomalias
    
    def atualizar_metricas(self, metricas: Dict[str, Any]) -> None:
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
    
    def obter_metricas(self, nome: Optional[str] = None) -> Dict[str, Any]:
        """Obtém as métricas do sistema.
        
        Args:
            nome: Nome da métrica (opcional)
            
        Returns:
            Dicionário com métricas
        """
        if nome:
            return {nome: self.cache_metricas.get(nome)}
        
        return self.cache_metricas
    
    def gerar_relatorio(self, periodo: Optional[timedelta] = None) -> Dict[str, Any]:
        """Gera um relatório do sistema.
        
        Args:
            periodo: Período de tempo (opcional)
            
        Returns:
            Dicionário com relatório
        """
        relatorio = {
            "timestamp": datetime.now().isoformat(),
            "dimensoes": {},
            "metricas": self.cache_metricas,
            "anomalias": {}
        }
        
        for nome in self.dimensoes:
            relatorio["dimensoes"][nome] = self.calcular_estatisticas(nome, periodo)
            relatorio["anomalias"][nome] = self.detectar_anomalias(nome, periodo)
        
        return relatorio
    
    def limpar_dados_antigos(self, periodo: timedelta) -> None:
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
    
    def calcular_correlacoes(self, dimensao1: str, dimensao2: str, periodo: Optional[timedelta] = None) -> float:
        """Calcula correlação entre duas dimensões.
        
        Args:
            dimensao1: Nome da primeira dimensão
            dimensao2: Nome da segunda dimensão
            periodo: Período de tempo (opcional)
            
        Returns:
            Coeficiente de correlação
        """
        dim1 = self.obter_dimensao(dimensao1, periodo)
        dim2 = self.obter_dimensao(dimensao2, periodo)
        
        if not dim1 or not dim2:
            return 0.0
        
        # Alinha os timestamps
        timestamps = set(d.timestamp for d in dim1) & set(d.timestamp for d in dim2)
        
        valores1 = [d.valor for d in dim1 if d.timestamp in timestamps]
        valores2 = [d.valor for d in dim2 if d.timestamp in timestamps]
        
        if not valores1 or not valores2:
            return 0.0
        
        return float(np.corrcoef(valores1, valores2)[0, 1])
    
    def gerar_matriz_correlacao(self, periodo: Optional[timedelta] = None) -> Dict[str, Dict[str, float]]:
        """Gera matriz de correlação entre todas as dimensões.
        
        Args:
            periodo: Período de tempo (opcional)
            
        Returns:
            Matriz de correlação
        """
        dimensoes = list(self.dimensoes.keys())
        matriz = {d1: {d2: 0.0 for d2 in dimensoes} for d1 in dimensoes}
        
        for d1 in dimensoes:
            for d2 in dimensoes:
                matriz[d1][d2] = self.calcular_correlacoes(d1, d2, periodo)
        
        return matriz
    
    def detectar_tendencias(self, nome: str, periodo: Optional[timedelta] = None) -> Dict[str, Any]:
        """Detecta tendências em uma dimensão.
        
        Args:
            nome: Nome da dimensão
            periodo: Período de tempo (opcional)
            
        Returns:
            Dicionário com informações sobre tendências
        """
        dimensoes = self.obter_dimensao(nome, periodo)
        
        if not dimensoes:
            return {}
        
        valores = np.array([d.valor for d in dimensoes])
        timestamps = np.array([d.timestamp.timestamp() for d in dimensoes])
        
        # Regressão linear
        z = np.polyfit(timestamps, valores, 1)
        p = np.poly1d(z)
        
        # Calcula R²
        y_pred = p(timestamps)
        r2 = 1 - (np.sum((valores - y_pred) ** 2) / np.sum((valores - np.mean(valores)) ** 2))
        
        return {
            "inclinacao": float(z[0]),
            "intercepto": float(z[1]),
            "r2": float(r2),
            "tendencia": "crescente" if z[0] > 0 else "decrescente" if z[0] < 0 else "estavel"
        } 