"""
Módulo de métricas do sistema de autocura.
Contém as classes e estruturas de dados para métricas do sistema.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import time
from prometheus_client import Counter, Gauge, Histogram, Summary
from .config import CONFIG

@dataclass
class MetricasSistema:
    """Classe que representa as métricas do sistema."""
    
    throughput: float  # Requisições por segundo
    taxa_erro: float   # Porcentagem de erros
    latencia: float    # Tempo de resposta em ms
    uso_recursos: Dict[str, float]  # Uso de recursos em porcentagem
    
    def __post_init__(self):
        """Validação das métricas após inicialização."""
        if not 0 <= self.taxa_erro <= 100:
            raise ValueError("Taxa de erro deve estar entre 0 e 100")
        if self.latencia < 0:
            raise ValueError("Latência não pode ser negativa")
        if not all(0 <= v <= 100 for v in self.uso_recursos.values()):
            raise ValueError("Uso de recursos deve estar entre 0 e 100")

class MonitoramentoMultidimensional:
    """Classe para monitoramento multidimensional do sistema."""
    
    def __init__(self):
        """Inicializa o monitoramento com métricas Prometheus."""
        # Métricas de throughput
        self.throughput = Counter(
            'autocura_throughput_total',
            'Total de requisições processadas',
            ['endpoint']
        )
        
        # Métricas de taxa de erro
        self.taxa_erro = Gauge(
            'autocura_taxa_erro',
            'Taxa de erro em porcentagem',
            ['endpoint', 'tipo_erro']
        )
        
        # Métricas de latência
        self.latencia = Histogram(
            'autocura_latencia_segundos',
            'Latência das requisições em segundos',
            ['endpoint'],
            buckets=CONFIG.METRICS['latencia']['buckets']
        )
        
        # Métricas de uso de recursos
        self.uso_recursos = Gauge(
            'autocura_uso_recursos',
            'Uso de recursos do sistema em porcentagem',
            ['recurso']
        )
        
        # Histórico de métricas
        self.historico: List[MetricasSistema] = []
    
    def coletar_metricas(self) -> MetricasSistema:
        """Coleta métricas atuais do sistema."""
        # Simulação de coleta de métricas
        metricas = MetricasSistema(
            throughput=100.0,  # req/s
            taxa_erro=2.5,     # %
            latencia=150.0,    # ms
            uso_recursos={
                'cpu': 45.0,
                'memoria': 60.0,
                'disco': 75.0
            }
        )
        
        # Atualiza métricas Prometheus
        self.atualizar_prometheus(metricas)
        
        # Adiciona ao histórico
        self.historico.append(metricas)
        
        # Mantém histórico limitado
        if len(self.historico) > CONFIG.VIZUALIZACAO['dashboard']['max_points']:
            self.historico.pop(0)
            
        return metricas
    
    def atualizar_prometheus(self, metricas: MetricasSistema):
        """Atualiza métricas Prometheus com valores atuais."""
        # Atualiza throughput
        self.throughput.labels(endpoint='/api/metricas').inc(metricas.throughput)
        
        # Atualiza taxa de erro
        self.taxa_erro.labels(
            endpoint='/api/metricas',
            tipo_erro='geral'
        ).set(metricas.taxa_erro)
        
        # Atualiza latência
        self.latencia.labels(
            endpoint='/api/metricas'
        ).observe(metricas.latencia / 1000)  # converte para segundos
        
        # Atualiza uso de recursos
        for recurso, valor in metricas.uso_recursos.items():
            self.uso_recursos.labels(recurso=recurso).set(valor)
    
    def verificar_alertas(self, metricas: MetricasSistema) -> List[Dict]:
        """Verifica se há alertas baseados nas métricas atuais."""
        alertas = []
        
        # Verifica thresholds
        thresholds = CONFIG.ALERTAS['threshold']
        
        if metricas.throughput > thresholds['throughput']['max']:
            alertas.append({
                'tipo': 'threshold',
                'metrica': 'throughput',
                'valor': metricas.throughput,
                'limite': thresholds['throughput']['max'],
                'mensagem': f'Throughput acima do limite: {metricas.throughput:.2f} req/s'
            })
            
        if metricas.taxa_erro > thresholds['taxa_erro']['max']:
            alertas.append({
                'tipo': 'threshold',
                'metrica': 'taxa_erro',
                'valor': metricas.taxa_erro,
                'limite': thresholds['taxa_erro']['max'],
                'mensagem': f'Taxa de erro acima do limite: {metricas.taxa_erro:.2f}%'
            })
            
        if metricas.latencia > thresholds['latencia']['max']:
            alertas.append({
                'tipo': 'threshold',
                'metrica': 'latencia',
                'valor': metricas.latencia,
                'limite': thresholds['latencia']['max'],
                'mensagem': f'Latência acima do limite: {metricas.latencia:.2f}ms'
            })
            
        for recurso, valor in metricas.uso_recursos.items():
            if valor > thresholds['uso_recursos'][recurso]['max']:
                alertas.append({
                    'tipo': 'threshold',
                    'metrica': f'uso_recursos_{recurso}',
                    'valor': valor,
                    'limite': thresholds['uso_recursos'][recurso]['max'],
                    'mensagem': f'Uso de {recurso} acima do limite: {valor:.2f}%'
                })
                
        return alertas
    
    def analisar_metricas(self) -> Dict:
        """Analisa métricas históricas para identificar tendências e anomalias."""
        if not self.historico:
            return {
                'tendencias': {},
                'anomalias': []
            }
            
        # Análise de tendências
        tendencias = {}
        for metrica in ['throughput', 'taxa_erro', 'latencia']:
            valores = [getattr(m, metrica) for m in self.historico]
            if len(valores) > 1:
                tendencia = (valores[-1] - valores[0]) / len(valores)
                tendencias[metrica] = tendencia
                
        # Análise de anomalias
        anomalias = []
        for metrica in ['throughput', 'taxa_erro', 'latencia']:
            valores = [getattr(m, metrica) for m in self.historico]
            if len(valores) > 1:
                media = sum(valores) / len(valores)
                desvio = (sum((x - media) ** 2 for x in valores) / len(valores)) ** 0.5
                
                ultimo_valor = valores[-1]
                if abs(ultimo_valor - media) > CONFIG.ALERTAS['anomalia']['threshold'] * desvio:
                    anomalias.append({
                        'metrica': metrica,
                        'valor': ultimo_valor,
                        'media': media,
                        'desvio': desvio,
                        'mensagem': f'Anomalia detectada em {metrica}: {ultimo_valor:.2f}'
                    })
                    
        return {
            'tendencias': tendencias,
            'anomalias': anomalias
        }
    
    def obter_historico(self, metrica: str, limite: int = 100) -> List[float]:
        """Obtém histórico de uma métrica específica."""
        if not self.historico:
            return []
            
        valores = [getattr(m, metrica) for m in self.historico[-limite:]]
        return valores 