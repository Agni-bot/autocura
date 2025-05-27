import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path
import threading
import time
import psutil
import os
import sys
import queue
from dataclasses import dataclass

# Importações corrigidas para nova estrutura
from ...core.models.metricas import Metrica, MetricasSistema
from ...utils.logging.logger import get_logger
from ...utils.cache.redis_cache import CacheDistribuido
from ...monitoring.metrics.prometheus_singleton import get_counter, get_gauge, get_histogram

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("coletor_metricas")

class ColetorMetricas:
    """Sistema de coleta de métricas com nova estrutura"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._config_default()
        self.logger = get_logger("coletor_metricas")
        self.cache = CacheDistribuido() if self.config.get("cache_enabled", True) else None
        self.metricas_queue = queue.Queue()
        self.executando = False
        self.thread_coleta = None
        
        # Prometheus metrics usando singleton
        self.cpu_gauge = get_gauge("sistema_cpu_percent", "Percentual de uso de CPU")
        self.memoria_gauge = get_gauge("sistema_memoria_percent", "Percentual de uso de memória")
        self.disco_gauge = get_gauge("sistema_disco_percent", "Percentual de uso de disco")
        self.metricas_counter = get_counter("metricas_coletadas_total", "Total de métricas coletadas")

    def _config_default(self) -> Dict[str, Any]:
        """Configuração padrão do coletor"""
        return {
            "intervalo_coleta": 30,
            "base_dir": "data/metricas",
            "cache_enabled": True,
            "prometheus_enabled": True,
            "metricas": {
                "sistema": ["cpu", "memoria", "disco", "rede"],
                "aplicacao": ["threads", "memoria", "tempo_resposta"]
            }
        }

    def iniciar_coleta(self):
        """Inicia a coleta de métricas em background"""
        if not self.executando:
            self.executando = True
            self.thread_coleta = threading.Thread(target=self._loop_coleta, daemon=True)
            self.thread_coleta.start()
            self.logger.info("Coleta de métricas iniciada")

    def parar_coleta(self):
        """Para a coleta de métricas"""
        self.executando = False
        if self.thread_coleta and self.thread_coleta.is_alive():
            self.thread_coleta.join(timeout=5)
        self.logger.info("Coleta de métricas parada")

    def _loop_coleta(self):
        """Loop principal de coleta"""
        while self.executando:
            try:
                metricas_sistema = self.coletar_metricas_sistema()
                metricas_app = self.coletar_metricas_aplicacao()
                
                # Atualiza Prometheus
                self._atualizar_prometheus(metricas_sistema)
                
                # Atualiza cache
                if self.cache:
                    self.cache.set("metricas_sistema", metricas_sistema, ttl=300)
                    self.cache.set("metricas_aplicacao", metricas_app, ttl=300)
                
                # Incrementa contador
                self.metricas_counter.inc()
                
                time.sleep(self.config["intervalo_coleta"])
                
            except Exception as e:
                self.logger.error(f"Erro na coleta de métricas: {e}")
                time.sleep(10)  # Espera antes de tentar novamente

    def _atualizar_prometheus(self, metricas: Dict[str, Any]):
        """Atualiza métricas Prometheus"""
        try:
            if "cpu" in metricas:
                self.cpu_gauge.set(metricas["cpu"]["percent"])
            if "memoria" in metricas:
                self.memoria_gauge.set(metricas["memoria"]["percent"])
            if "disco" in metricas:
                self.disco_gauge.set(metricas["disco"]["percent"])
        except Exception as e:
            self.logger.error(f"Erro ao atualizar Prometheus: {e}")

    def coletar_metricas_sistema(self) -> Dict[str, Any]:
        """Coleta métricas do sistema"""
        try:
            metricas = {}
            
            # CPU
            if "cpu" in self.config["metricas"]["sistema"]:
                metricas["cpu"] = {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                }
            
            # Memória
            if "memoria" in self.config["metricas"]["sistema"]:
                memoria = psutil.virtual_memory()
                metricas["memoria"] = {
                    "total": memoria.total,
                    "available": memoria.available,
                    "percent": memoria.percent,
                    "used": memoria.used,
                    "free": memoria.free
                }
            
            # Disco
            if "disco" in self.config["metricas"]["sistema"]:
                disco = psutil.disk_usage('/')
                metricas["disco"] = {
                    "total": disco.total,
                    "used": disco.used,
                    "free": disco.free,
                    "percent": disco.percent
                }
            
            # Rede
            if "rede" in self.config["metricas"]["sistema"]:
                rede = psutil.net_io_counters()
                metricas["rede"] = {
                    "bytes_sent": rede.bytes_sent,
                    "bytes_recv": rede.bytes_recv,
                    "packets_sent": rede.packets_sent,
                    "packets_recv": rede.packets_recv
                }
            
            return metricas
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas do sistema: {e}")
            return {}
    
    def coletar_metricas_aplicacao(self) -> Dict[str, Any]:
        """Coleta métricas da aplicação"""
        try:
            metricas = {}
            processo = psutil.Process(os.getpid())
            
            # Threads
            if "threads" in self.config["metricas"]["aplicacao"]:
                metricas["threads"] = {
                    "count": processo.num_threads(),
                    "active": threading.active_count()
                }
            
            # Memória
            if "memoria" in self.config["metricas"]["aplicacao"]:
                memoria = processo.memory_info()
                metricas["memoria"] = {
                    "rss": memoria.rss,
                    "vms": memoria.vms,
                    "percent": processo.memory_percent()
                }
            
            # Tempo de resposta
            if "tempo_resposta" in self.config["metricas"]["aplicacao"]:
                metricas["tempo_resposta"] = self._calcular_tempo_resposta()
            
            return metricas
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas da aplicação: {e}")
            return {}

    def _calcular_tempo_resposta(self) -> float:
        """Calcula tempo de resposta médio (simulado)"""
        # Implementação simplificada
        return 50.0  # ms

    def obter_metricas_sistema_formato_padrao(self) -> MetricasSistema:
        """Retorna métricas no formato padrão MetricasSistema"""
        try:
            metricas = self.coletar_metricas_sistema()
            
            return MetricasSistema(
                throughput=0.0,  # Seria calculado baseado em requests/sec
                taxa_erro=0.0,   # Seria calculado baseado em logs de erro
                latencia=self._calcular_tempo_resposta(),
                uso_recursos={
                    "cpu": metricas.get("cpu", {}).get("percent", 0.0),
                    "memoria": metricas.get("memoria", {}).get("percent", 0.0),
                    "disco": metricas.get("disco", {}).get("percent", 0.0)
                }
            )
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas formato padrão: {e}")
            return MetricasSistema()  # Retorna métricas vazias

    def __del__(self):
        """Cleanup ao destruir objeto"""
        self.parar_coleta() 