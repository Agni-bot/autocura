"""
Sistema de monitoramento para autocura
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path
import psutil
import time

from prometheus_client import start_http_server, Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

class AutocuraMonitor:
    """Sistema de monitoramento para autocura"""
    
    def __init__(
        self,
        metrics_path: Optional[Path] = None,
        prometheus_port: int = 9090
    ):
        self.metrics_path = metrics_path or Path("metrics_history.json")
        self.metrics_history = self._load_metrics_history()
        
        # Inicializa métricas Prometheus
        self._init_prometheus_metrics()
        start_http_server(prometheus_port)
        
        logger.info("AutocuraMonitor inicializado com sucesso")
    
    def _init_prometheus_metrics(self) -> None:
        """Inicializa métricas Prometheus"""
        # Contadores
        self.feedback_counter = Counter(
            'autocura_feedback_total',
            'Total de feedbacks recebidos',
            ['tipo']
        )
        self.evolution_counter = Counter(
            'autocura_evolution_total',
            'Total de ciclos de evolução',
            ['status']
        )
        
        # Gauges
        self.system_health = Gauge(
            'autocura_system_health',
            'Saúde geral do sistema',
            ['componente']
        )
        self.memory_usage = Gauge(
            'autocura_memory_usage',
            'Uso de memória do sistema',
            ['tipo']
        )
        
        # Histogramas
        self.evolution_duration = Histogram(
            'autocura_evolution_duration_seconds',
            'Duração dos ciclos de evolução',
            buckets=[1, 5, 10, 30, 60, 300]
        )
        self.feedback_processing = Histogram(
            'autocura_feedback_processing_seconds',
            'Tempo de processamento de feedback',
            buckets=[0.1, 0.5, 1, 5, 10]
        )
    
    def _load_metrics_history(self) -> List[Dict]:
        """Carrega histórico de métricas"""
        try:
            if self.metrics_path.exists():
                with open(self.metrics_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Erro ao carregar histórico de métricas: {e}")
            return []
    
    def save(self) -> None:
        """Salva histórico de métricas"""
        try:
            with open(self.metrics_path, 'w', encoding='utf-8') as f:
                json.dump(self.metrics_history, f, indent=4, ensure_ascii=False)
            logger.info("Histórico de métricas salvo")
        except Exception as e:
            logger.error(f"Erro ao salvar histórico de métricas: {e}")
    
    def record_feedback(self, feedback_data: Dict) -> None:
        """Registra métricas de feedback"""
        try:
            start_time = time.time()
            
            # Registra feedback no Prometheus
            feedback_type = feedback_data.get("tipo", "geral")
            self.feedback_counter.labels(tipo=feedback_type).inc()
            
            # Registra no histórico
            metrics_entry = {
                "timestamp": datetime.now().isoformat(),
                "tipo": "feedback",
                "data": feedback_data,
                "processing_time": time.time() - start_time
            }
            self.metrics_history.append(metrics_entry)
            
            # Atualiza histograma de processamento
            self.feedback_processing.observe(time.time() - start_time)
            
            self.save()
            logger.info("Métricas de feedback registradas")
        except Exception as e:
            logger.error(f"Erro ao registrar métricas de feedback: {e}")
    
    def record_evolution(self, evolution_data: Dict) -> None:
        """Registra métricas de evolução"""
        try:
            start_time = time.time()
            
            # Registra evolução no Prometheus
            status = evolution_data.get("status", "unknown")
            self.evolution_counter.labels(status=status).inc()
            
            # Registra no histórico
            metrics_entry = {
                "timestamp": datetime.now().isoformat(),
                "tipo": "evolucao",
                "data": evolution_data,
                "processing_time": time.time() - start_time
            }
            self.metrics_history.append(metrics_entry)
            
            # Atualiza histograma de duração
            self.evolution_duration.observe(time.time() - start_time)
            
            self.save()
            logger.info("Métricas de evolução registradas")
        except Exception as e:
            logger.error(f"Erro ao registrar métricas de evolução: {e}")
    
    def update_system_metrics(self) -> None:
        """Atualiza métricas do sistema"""
        try:
            # Métricas de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_health.labels(componente='cpu').set(cpu_percent)
            
            # Métricas de memória
            memory = psutil.virtual_memory()
            self.memory_usage.labels(tipo='total').set(memory.total)
            self.memory_usage.labels(tipo='used').set(memory.used)
            self.memory_usage.labels(tipo='free').set(memory.free)
            
            # Registra no histórico
            metrics_entry = {
                "timestamp": datetime.now().isoformat(),
                "tipo": "sistema",
                "data": {
                    "cpu_percent": cpu_percent,
                    "memory_total": memory.total,
                    "memory_used": memory.used,
                    "memory_free": memory.free
                }
            }
            self.metrics_history.append(metrics_entry)
            
            self.save()
            logger.info("Métricas do sistema atualizadas")
        except Exception as e:
            logger.error(f"Erro ao atualizar métricas do sistema: {e}")
    
    def get_current_metrics(self) -> Dict:
        """Retorna métricas atuais do sistema"""
        try:
            # Coleta métricas do sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Calcula métricas de feedback
            feedback_metrics = self._calculate_feedback_metrics()
            
            # Calcula métricas de evolução
            evolution_metrics = self._calculate_evolution_metrics()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "sistema": {
                    "cpu_percent": cpu_percent,
                    "memory_total": memory.total,
                    "memory_used": memory.used,
                    "memory_free": memory.free
                },
                "feedback": feedback_metrics,
                "evolucao": evolution_metrics
            }
        except Exception as e:
            logger.error(f"Erro ao obter métricas atuais: {e}")
            return {}
    
    def _calculate_feedback_metrics(self) -> Dict:
        """Calcula métricas relacionadas a feedback"""
        try:
            feedback_entries = [
                entry for entry in self.metrics_history
                if entry["tipo"] == "feedback"
            ]
            
            return {
                "total": len(feedback_entries),
                "por_tipo": self._group_by_type(feedback_entries),
                "tempo_medio_processamento": self._calculate_average_processing_time(
                    feedback_entries
                )
            }
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de feedback: {e}")
            return {}
    
    def _calculate_evolution_metrics(self) -> Dict:
        """Calcula métricas relacionadas a evolução"""
        try:
            evolution_entries = [
                entry for entry in self.metrics_history
                if entry["tipo"] == "evolucao"
            ]
            
            return {
                "total": len(evolution_entries),
                "por_status": self._group_by_status(evolution_entries),
                "tempo_medio_processamento": self._calculate_average_processing_time(
                    evolution_entries
                )
            }
        except Exception as e:
            logger.error(f"Erro ao calcular métricas de evolução: {e}")
            return {}
    
    def _group_by_type(self, entries: List[Dict]) -> Dict:
        """Agrupa entradas por tipo"""
        grouped = {}
        for entry in entries:
            entry_type = entry["data"].get("tipo", "geral")
            if entry_type not in grouped:
                grouped[entry_type] = 0
            grouped[entry_type] += 1
        return grouped
    
    def _group_by_status(self, entries: List[Dict]) -> Dict:
        """Agrupa entradas por status"""
        grouped = {}
        for entry in entries:
            status = entry["data"].get("status", "unknown")
            if status not in grouped:
                grouped[status] = 0
            grouped[status] += 1
        return grouped
    
    def _calculate_average_processing_time(self, entries: List[Dict]) -> float:
        """Calcula tempo médio de processamento"""
        if not entries:
            return 0.0
        return sum(entry["processing_time"] for entry in entries) / len(entries)
    
    def get_timestamp(self) -> str:
        """Retorna timestamp atual"""
        return datetime.now().isoformat() 