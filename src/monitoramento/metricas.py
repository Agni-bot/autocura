"""
Módulo de métricas do sistema de autocura.
Contém as classes e estruturas de dados para métricas do sistema.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class MetricasSistema:
    """Classe que representa as métricas do sistema."""
    
    throughput: float  # Requisições por segundo
    taxa_erro: float   # Porcentagem de erros
    latencia: float    # Tempo de resposta em ms
    uso_recursos: Dict[str, float]  # Uso de recursos em porcentagem
    timestamp: datetime = datetime.now()
    
    def __post_init__(self):
        """Validação dos dados após inicialização."""
        if self.throughput < 0:
            raise ValueError("Throughput não pode ser negativo")
        if not 0 <= self.taxa_erro <= 100:
            raise ValueError("Taxa de erro deve estar entre 0 e 100")
        if self.latencia < 0:
            raise ValueError("Latência não pode ser negativa")
        for recurso, uso in self.uso_recursos.items():
            if not 0 <= uso <= 100:
                raise ValueError(f"Uso de {recurso} deve estar entre 0 e 100")

class MonitoramentoMultidimensional:
    """Classe para monitoramento multidimensional do sistema."""
    
    def __init__(self):
        self._historico: List[MetricasSistema] = []
    
    def coletar_metricas(self) -> MetricasSistema:
        """Coleta métricas atuais do sistema."""
        # TODO: Implementar coleta real de métricas
        # Por enquanto retorna métricas simuladas
        return MetricasSistema(
            throughput=500.0,
            taxa_erro=2.5,
            latencia=50.0,
            uso_recursos={
                "cpu": 45.0,
                "memoria": 60.0,
                "disco": 30.0
            }
        )
    
    def registrar_metricas(self, metricas: MetricasSistema) -> None:
        """Registra métricas no histórico."""
        self._historico.append(metricas)
    
    def obter_historico(self, limite: Optional[int] = None) -> List[MetricasSistema]:
        """Retorna o histórico de métricas."""
        if limite is None:
            return self._historico
        return self._historico[-limite:]
    
    def limpar_historico(self) -> None:
        """Limpa o histórico de métricas."""
        self._historico = [] 