"""
Prometheus Registry Singleton
============================

Singleton para evitar conflitos de timeseries duplicadas no Prometheus.
"""

import prometheus_client
from typing import Optional, Dict, Any
import threading
import logging

logger = logging.getLogger(__name__)

class PrometheusRegistry:
    """Singleton para gerenciar registry Prometheus global"""
    
    _instance: Optional['PrometheusRegistry'] = None
    _registry: Optional[prometheus_client.CollectorRegistry] = None
    _lock = threading.Lock()
    _metrics_cache: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._registry = prometheus_client.CollectorRegistry()
                    logger.info("Prometheus Registry Singleton criado")
        return cls._instance
    
    @property
    def registry(self):
        """Retorna o registry singleton"""
        return self._registry
    
    def get_or_create_counter(self, name: str, description: str, labelnames=None):
        """Obtém ou cria um Counter, evitando duplicatas"""
        key = f"counter_{name}"
        if key not in self._metrics_cache:
            with self._lock:
                if key not in self._metrics_cache:
                    self._metrics_cache[key] = prometheus_client.Counter(
                        name=name,
                        documentation=description,
                        labelnames=labelnames or [],
                        registry=self._registry
                    )
        return self._metrics_cache[key]
    
    def get_or_create_gauge(self, name: str, description: str, labelnames=None):
        """Obtém ou cria um Gauge, evitando duplicatas"""
        key = f"gauge_{name}"
        if key not in self._metrics_cache:
            with self._lock:
                if key not in self._metrics_cache:
                    self._metrics_cache[key] = prometheus_client.Gauge(
                        name=name,
                        documentation=description,
                        labelnames=labelnames or [],
                        registry=self._registry
                    )
        return self._metrics_cache[key]
    
    def get_or_create_histogram(self, name: str, description: str, labelnames=None, buckets=None):
        """Obtém ou cria um Histogram, evitando duplicatas"""
        key = f"histogram_{name}"
        if key not in self._metrics_cache:
            with self._lock:
                if key not in self._metrics_cache:
                    self._metrics_cache[key] = prometheus_client.Histogram(
                        name=name,
                        documentation=description,
                        labelnames=labelnames or [],
                        buckets=buckets,
                        registry=self._registry
                    )
        return self._metrics_cache[key]
    
    def clear_metrics(self):
        """Limpa todas as métricas (útil para testes)"""
        with self._lock:
            self._metrics_cache.clear()
            if self._registry:
                collectors = list(self._registry._collector_to_names.keys())
                for collector in collectors:
                    try:
                        self._registry.unregister(collector)
                    except KeyError:
                        pass  # Collector já foi removido
            logger.info("Métricas Prometheus limpas")
    
    def get_metrics_count(self) -> int:
        """Retorna número de métricas registradas"""
        return len(self._metrics_cache)

# Instância global
prometheus_registry = PrometheusRegistry()

# Funções utilitárias para uso direto
def get_counter(name: str, description: str, labelnames=None):
    """Função utilitária para obter Counter"""
    return prometheus_registry.get_or_create_counter(name, description, labelnames)

def get_gauge(name: str, description: str, labelnames=None):
    """Função utilitária para obter Gauge"""
    return prometheus_registry.get_or_create_gauge(name, description, labelnames)

def get_histogram(name: str, description: str, labelnames=None, buckets=None):
    """Função utilitária para obter Histogram"""
    return prometheus_registry.get_or_create_histogram(name, description, labelnames, buckets)

def get_registry():
    """Função utilitária para obter registry"""
    return prometheus_registry.registry 