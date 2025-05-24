from typing import Dict, Any
import psutil
import time
from datetime import datetime

class MultiDimensionalCollector:
    def __init__(self):
        self.last_collection = None
        self.metrics_history = []
    
    def collect_classical_metrics(self) -> Dict[str, Any]:
        """Coleta métricas tradicionais do sistema"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "per_cpu": psutil.cpu_percent(interval=1, percpu=True),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "used": psutil.virtual_memory().used,
                "free": psutil.virtual_memory().free
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            }
        }
        
        self.last_collection = metrics
        self.metrics_history.append(metrics)
        
        # Mantém histórico limitado
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)
            
        return metrics
    
    def prepare_quantum_metrics(self) -> None:
        """Prepara estrutura para métricas quânticas futuras"""
        # Placeholder para métricas quânticas
        self.quantum_metrics = {
            "coherence_time": None,
            "entanglement_degree": None,
            "quantum_volume": None,
            "error_rate": None
        }
    
    def get_metrics_history(self, limit: int = 100) -> list:
        """Retorna histórico de métricas"""
        return self.metrics_history[-limit:]
    
    def calculate_equity(self) -> float:
        """Calcula índice de equidade na distribuição de recursos"""
        if not self.last_collection:
            return 0.0
            
        cpu_equity = 1.0 - (max(self.last_collection["cpu"]["per_cpu"]) - 
                           min(self.last_collection["cpu"]["per_cpu"])) / 100.0
        
        memory_equity = 1.0 - (self.last_collection["memory"]["percent"] / 100.0)
        
        disk_equity = 1.0 - (self.last_collection["disk"]["percent"] / 100.0)
        
        return (cpu_equity + memory_equity + disk_equity) / 3.0 