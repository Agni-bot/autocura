from typing import Dict, List, Optional
import logging
import time
from dataclasses import dataclass
import statistics
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class MetricasScaling:
    cpu_usage: float
    memoria_usage: float
    latencia: float
    requests_por_segundo: float
    timestamp: datetime

class AutoScaling:
    def __init__(self,
                 min_instancias: int = 1,
                 max_instancias: int = 10,
                 cpu_threshold: float = 70.0,
                 memoria_threshold: float = 80.0,
                 latencia_threshold: float = 200.0,
                 cooldown_period: int = 300):
        """
        Inicializa o gerenciador de auto-scaling.
        
        Args:
            min_instancias: Número mínimo de instâncias
            max_instancias: Número máximo de instâncias
            cpu_threshold: Limite de uso de CPU para scaling (percentual)
            memoria_threshold: Limite de uso de memória para scaling (percentual)
            latencia_threshold: Limite de latência para scaling (ms)
            cooldown_period: Período de cooldown entre operações de scaling (segundos)
        """
        self.min_instancias = min_instancias
        self.max_instancias = max_instancias
        self.cpu_threshold = cpu_threshold
        self.memoria_threshold = memoria_threshold
        self.latencia_threshold = latencia_threshold
        self.cooldown_period = cooldown_period
        
        self.instancias_atuais = min_instancias
        self.ultimo_scaling = datetime.now()
        self.metricas_historico: List[MetricasScaling] = []
        
        logger.info("Auto-scaling inicializado com sucesso")

    def registrar_metricas(self, metricas: MetricasScaling) -> None:
        """
        Registra novas métricas para análise.
        
        Args:
            metricas: Objeto contendo as métricas atuais
        """
        self.metricas_historico.append(metricas)
        # Mantém apenas as últimas 100 métricas
        if len(self.metricas_historico) > 100:
            self.metricas_historico.pop(0)

    def _calcular_tendencia(self, metricas: List[float]) -> float:
        """
        Calcula a tendência das métricas usando regressão linear simples.
        
        Args:
            metricas: Lista de valores das métricas
            
        Returns:
            float: Coeficiente angular da reta de tendência
        """
        if len(metricas) < 2:
            return 0.0
            
        x = list(range(len(metricas)))
        y = metricas
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(i * j for i, j in zip(x, y))
        sum_xx = sum(i * i for i in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
        return slope

    def _analisar_necessidade_scaling(self) -> Optional[int]:
        """
        Analisa as métricas e determina se é necessário fazer scaling.
        
        Returns:
            Optional[int]: Número de instâncias desejado ou None se não houver necessidade
        """
        if not self.metricas_historico:
            return None
            
        # Verifica período de cooldown
        if (datetime.now() - self.ultimo_scaling).total_seconds() < self.cooldown_period:
            return None
            
        # Obtém métricas mais recentes
        metricas_recentes = self.metricas_historico[-10:]
        
        # Calcula médias
        cpu_media = statistics.mean([m.cpu_usage for m in metricas_recentes])
        memoria_media = statistics.mean([m.memoria_usage for m in metricas_recentes])
        latencia_media = statistics.mean([m.latencia for m in metricas_recentes])
        
        # Calcula tendências
        cpu_tendencia = self._calcular_tendencia([m.cpu_usage for m in metricas_recentes])
        memoria_tendencia = self._calcular_tendencia([m.memoria_usage for m in metricas_recentes])
        latencia_tendencia = self._calcular_tendencia([m.latencia for m in metricas_recentes])
        
        # Determina necessidade de scaling
        scaling_up = False
        scaling_down = False
        
        # Condições para scaling up
        if (cpu_media > self.cpu_threshold or 
            memoria_media > self.memoria_threshold or 
            latencia_media > self.latencia_threshold or
            cpu_tendencia > 5 or 
            memoria_tendencia > 5 or 
            latencia_tendencia > 5):
            scaling_up = True
            
        # Condições para scaling down
        elif (cpu_media < self.cpu_threshold * 0.5 and 
              memoria_media < self.memoria_threshold * 0.5 and 
              latencia_media < self.latencia_threshold * 0.5 and
              cpu_tendencia < -5 and 
              memoria_tendencia < -5 and 
              latencia_tendencia < -5):
            scaling_down = True
            
        # Calcula número de instâncias desejado
        if scaling_up and self.instancias_atuais < self.max_instancias:
            return min(self.instancias_atuais + 1, self.max_instancias)
        elif scaling_down and self.instancias_atuais > self.min_instancias:
            return max(self.instancias_atuais - 1, self.min_instancias)
            
        return None

    def executar_scaling(self) -> Optional[int]:
        """
        Executa o processo de auto-scaling se necessário.
        
        Returns:
            Optional[int]: Número de instâncias após o scaling ou None se não houve alteração
        """
        novas_instancias = self._analisar_necessidade_scaling()
        
        if novas_instancias is not None and novas_instancias != self.instancias_atuais:
            self.instancias_atuais = novas_instancias
            self.ultimo_scaling = datetime.now()
            logger.info(f"Auto-scaling executado: {self.instancias_atuais} instâncias")
            return novas_instancias
            
        return None

    def obter_metricas_atual(self) -> Dict:
        """
        Retorna as métricas atuais do sistema.
        
        Returns:
            Dict: Dicionário com as métricas atuais
        """
        if not self.metricas_historico:
            return {
                "instancias": self.instancias_atuais,
                "cpu_usage": 0.0,
                "memoria_usage": 0.0,
                "latencia": 0.0,
                "requests_por_segundo": 0.0
            }
            
        ultima_metrica = self.metricas_historico[-1]
        return {
            "instancias": self.instancias_atuais,
            "cpu_usage": ultima_metrica.cpu_usage,
            "memoria_usage": ultima_metrica.memoria_usage,
            "latencia": ultima_metrica.latencia,
            "requests_por_segundo": ultima_metrica.requests_por_segundo
        } 