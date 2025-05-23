"""Sistema de métricas do módulo core."""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .interfaces import MetricsInterface
from .config.config import config
from .logging import logger

class MetricsCollector(MetricsInterface):
    """Coletor de métricas do sistema."""
    
    def __init__(self):
        """Inicializa o coletor de métricas."""
        self._metrics: Dict[str, Dict[str, float]] = {}
        self._histories: Dict[str, List[Tuple[datetime, float]]] = {}
        self._enabled = config.METRICS_ENABLED
        
    async def record_metric(self, name: str, value: float,
                          tags: Optional[Dict[str, str]] = None) -> None:
        """Registra uma métrica."""
        if not self._enabled:
            return
            
        tag_key = str(tags) if tags else "default"
        
        # Atualiza valor atual
        if name not in self._metrics:
            self._metrics[name] = {}
        self._metrics[name][tag_key] = value
        
        # Atualiza histórico
        if name not in self._histories:
            self._histories[name] = []
        self._histories[name].append((datetime.now(), value))
        
        # Limpa histórico antigo
        self._cleanup_history(name)
        
        # Log da métrica
        await logger.log("DEBUG", f"Métrica registrada: {name}={value}",
                        metric_name=name, value=value, tags=tags)
        
    async def get_metric(self, name: str,
                        tags: Optional[Dict[str, str]] = None) -> float:
        """Recupera o valor de uma métrica."""
        if not self._enabled:
            return 0.0
            
        tag_key = str(tags) if tags else "default"
        return self._metrics.get(name, {}).get(tag_key, 0.0)
        
    async def list_metrics(self, pattern: str) -> List[str]:
        """Lista métricas que correspondem a um padrão."""
        if not self._enabled:
            return []
            
        import re
        regex = re.compile(pattern)
        return [k for k in self._metrics.keys() if regex.match(k)]
        
    def _cleanup_history(self, name: str) -> None:
        """Limpa histórico antigo de uma métrica."""
        if name not in self._histories:
            return
            
        # Mantém apenas últimas 1000 entradas
        self._histories[name] = self._histories[name][-1000:]
        
    async def get_metric_history(self, name: str,
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> List[Tuple[datetime, float]]:
        """Recupera histórico de uma métrica."""
        if not self._enabled or name not in self._histories:
            return []
            
        history = self._histories[name]
        
        if start_time:
            history = [h for h in history if h[0] >= start_time]
            
        if end_time:
            history = [h for h in history if h[0] <= end_time]
            
        return history
        
    async def get_metric_stats(self, name: str,
                             start_time: Optional[datetime] = None,
                             end_time: Optional[datetime] = None) -> Dict[str, float]:
        """Recupera estatísticas de uma métrica."""
        history = await self.get_metric_history(name, start_time, end_time)
        
        if not history:
            return {
                "min": 0.0,
                "max": 0.0,
                "avg": 0.0,
                "count": 0
            }
            
        values = [h[1] for h in history]
        
        return {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "count": len(values)
        }

class Timer:
    """Context manager para medição de tempo."""
    
    def __init__(self, metrics: MetricsCollector, name: str,
                tags: Optional[Dict[str, str]] = None):
        """Inicializa o timer."""
        self.metrics = metrics
        self.name = name
        self.tags = tags
        self.start_time = None
        
    async def __aenter__(self) -> 'Timer':
        """Inicia o timer."""
        self.start_time = time.time()
        return self
        
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Finaliza o timer e registra a métrica."""
        if self.start_time is None:
            return
            
        duration = time.time() - self.start_time
        await self.metrics.record_metric(
            f"{self.name}_duration",
            duration,
            self.tags
        )

# Instância global do coletor de métricas
metrics = MetricsCollector() 