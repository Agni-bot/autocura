"""
Modelos de Métricas Centralizados
================================

Definições centralizadas para MetricasSistema e Metrica usadas em todo o sistema.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class TipoMetrica(Enum):
    """Tipos de métricas suportadas"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Metrica:
    """Representa uma métrica individual do sistema"""
    nome: str
    valor: float
    tipo: str
    labels: Dict[str, str]
    timestamp: datetime
    unidade: Optional[str] = None
    descricao: Optional[str] = None

@dataclass
class MetricasSistema:
    """Classe que representa as métricas consolidadas do sistema"""
    throughput: float = 0.0  # Requisições por segundo
    taxa_erro: float = 0.0   # Porcentagem de erros (0-100)
    latencia: float = 0.0    # Tempo de resposta em ms
    uso_recursos: Dict[str, float] = None  # Uso de recursos em porcentagem
    timestamp: datetime = None
    
    def __post_init__(self):
        """Validação e inicialização pós-criação"""
        if self.timestamp is None:
            self.timestamp = datetime.now()
            
        if self.uso_recursos is None:
            self.uso_recursos = {"cpu": 0.0, "memoria": 0.0, "disco": 0.0}
        
        # Validações
        if self.throughput < 0:
            raise ValueError("Throughput não pode ser negativo")
        if not 0 <= self.taxa_erro <= 100:
            raise ValueError("Taxa de erro deve estar entre 0 e 100")
        if self.latencia < 0:
            raise ValueError("Latência não pode ser negativa")
        for recurso, uso in self.uso_recursos.items():
            if not 0 <= uso <= 100:
                raise ValueError(f"Uso de {recurso} deve estar entre 0 e 100")

@dataclass
class MetricasAplicacao:
    """Métricas específicas da aplicação"""
    threads_ativas: int = 0
    memoria_heap: float = 0.0
    memoria_stack: float = 0.0
    conexoes_ativas: int = 0
    cache_hit_rate: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

# Constantes úteis
METRICAS_DEFAULT = MetricasSistema()

# Funções utilitárias
def criar_metrica(nome: str, valor: float, tipo: str = "gauge", **kwargs) -> Metrica:
    """Factory function para criar métricas"""
    return Metrica(
        nome=nome,
        valor=valor,
        tipo=tipo,
        labels=kwargs.get("labels", {}),
        timestamp=kwargs.get("timestamp", datetime.now()),
        unidade=kwargs.get("unidade"),
        descricao=kwargs.get("descricao")
    )

def validar_metricas_sistema(metricas: MetricasSistema) -> bool:
    """Valida se as métricas estão dentro de limites aceitáveis"""
    try:
        # Validação já é feita no __post_init__, só precisamos chamar
        MetricasSistema(
            throughput=metricas.throughput,
            taxa_erro=metricas.taxa_erro,
            latencia=metricas.latencia,
            uso_recursos=metricas.uso_recursos,
            timestamp=metricas.timestamp
        )
        return True
    except ValueError:
        return False 