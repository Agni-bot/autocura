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

from ..core.logger import Logger
from ..core.cache import Cache

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("coletor_metricas")

class ColetorMetricas:
    """Sistema de coleta de métricas"""
    
    def __init__(self, logger: Logger, cache: Cache, config_path: str = "config/metricas.json"):
        self.logger = logger
        self.cache = cache
        self.config = self._carregar_config(config_path)
        self.lock = threading.Lock()
        self.thread_coleta = None
        self.running = False
        self.logger.registrar_evento("metricas", "INFO", "Sistema de Métricas inicializado")
    
    def _carregar_config(self, config_path: str) -> Dict[str, Any]:
        """Carrega a configuração do coletor"""
        try:
            caminho_config = Path(config_path)
            if caminho_config.exists():
                with open(caminho_config, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.registrar_evento("metricas", "WARNING", "Arquivo de configuração não encontrado. Usando configuração padrão.")
                return self._criar_config_padrao()
        except Exception as e:
            self.logger.registrar_erro("metricas", "Erro ao carregar configuração", e)
            return self._criar_config_padrao()
    
    def _criar_config_padrao(self) -> Dict[str, Any]:
        """Cria configuração padrão do coletor"""
        return {
            "configuracoes": {
                "intervalo_coleta": 60,
                "max_historico": 1000,
                "limites": {
                    "cpu_percent": 80,
                    "memoria_percent": 80,
                    "disco_percent": 80,
                    "tempo_resposta": 1.0
                }
            },
            "metricas": {
                "sistema": {
                    "cpu": ["percent", "count", "freq"],
                    "memoria": ["total", "available", "percent", "used", "free"],
                    "disco": ["total", "used", "free", "percent"],
                    "rede": ["bytes_sent", "bytes_recv", "packets_sent", "packets_recv"]
                },
                "aplicacao": {
                    "threads": ["count", "active"],
                    "memoria": ["rss", "vms", "shared", "text", "lib", "data", "dirty"],
                    "tempo_resposta": ["min", "max", "avg", "p95", "p99"]
                }
            }
        }
    
    def iniciar(self) -> None:
        """Inicia o coletor de métricas"""
        try:
            if self.running:
                self.logger.registrar_evento("metricas", "WARNING", "Coletor já está em execução")
                return
            
            self.running = True
            self.thread_coleta = threading.Thread(target=self._executar_coleta)
            self.thread_coleta.start()
            
            self.logger.registrar_evento("metricas", "INFO", "Coletor iniciado com sucesso")
            
        except Exception as e:
            self.logger.registrar_erro("metricas", "Erro ao iniciar coletor", e)
            self.running = False
    
    def parar(self) -> None:
        """Para o coletor de métricas"""
        try:
            if not self.running:
                self.logger.registrar_evento("metricas", "WARNING", "Coletor não está em execução")
                return
            
            self.running = False
            if self.thread_coleta:
                self.thread_coleta.join()
            
            self.logger.registrar_evento("metricas", "INFO", "Coletor parado com sucesso")
            
        except Exception as e:
            self.logger.registrar_erro("metricas", "Erro ao parar coletor", e)
    
    def _executar_coleta(self) -> None:
        """Executa o processo de coleta de métricas"""
        try:
            while self.running:
                # Coleta métricas do sistema
                metricas_sistema = self.coletar_metricas_sistema()
                
                # Coleta métricas da aplicação
                metricas_aplicacao = self.coletar_metricas_aplicacao()
                
                # Verifica limites
                alertas = self.verificar_limites(metricas_sistema)
                
                # Registra métricas
                self.registrar_metricas(metricas_sistema, metricas_aplicacao, alertas)
                
                # Aguarda próximo ciclo
                time.sleep(self.config["configuracoes"]["intervalo_coleta"])
            
        except Exception as e:
            self.logger.registrar_erro("metricas", "Erro no processo de coleta", e)
            self.running = False
    
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
            self.logger.registrar_erro("metricas", "Erro ao coletar métricas do sistema", e)
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
                    "shared": memoria.shared,
                    "text": memoria.text,
                    "lib": memoria.lib,
                    "data": memoria.data,
                    "dirty": memoria.dirty
                }
            
            # Tempo de resposta
            if "tempo_resposta" in self.config["metricas"]["aplicacao"]:
                metricas["tempo_resposta"] = self._calcular_tempo_resposta()
            
            return metricas
            
        except Exception as e:
            self.logger.registrar_erro("metricas", "Erro ao coletar métricas da aplicação", e)
            return {}
    
    def _calcular_tempo_resposta(self) -> Dict[str, float]:
        """Calcula métricas de tempo de resposta"""
        try:
            # Obtém tempos de resposta do cache
            tempos = self.cache.obter("tempo_resposta", "historico") or []
            
            if not tempos:
                return {
                    "min": 0.0,
                    "max": 0.0,
                    "avg": 0.0,
                    "p95": 0.0,
                    "p99": 0.0
                }
            
            # Calcula métricas
            tempos.sort()
            n = len(tempos)
            
            return {
                "min": tempos[0],
                "max": tempos[-1],
                "avg": sum(tempos) / n,
                "p95": tempos[int(n * 0.95)],
                "p99": tempos[int(n * 0.99)]
            }
            
        except Exception as e:
            self.logger.registrar_erro("metricas", "Erro ao calcular tempo de resposta", e)
            return {}
    
    def verificar_limites(self, metricas: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Verifica limites das métricas"""
        try:
            alertas = []
            limites = self.config["configuracoes"]["limites"]
            
            # CPU
            if "cpu" in metricas and "percent" in metricas["cpu"]:
                if metricas["cpu"]["percent"] > limites["cpu_percent"]:
                    alertas.append({
                        "tipo": "cpu",
                        "metrica": "percent",
                        "valor": metricas["cpu"]["percent"],
                        "limite": limites["cpu_percent"],
                        "mensagem": f"Uso de CPU acima do limite: {metricas['cpu']['percent']}%"
                    })
            
            # Memória
            if "memoria" in metricas and "percent" in metricas["memoria"]:
                if metricas["memoria"]["percent"] > limites["memoria_percent"]:
                    alertas.append({
                        "tipo": "memoria",
                        "metrica": "percent",
                        "valor": metricas["memoria"]["percent"],
                        "limite": limites["memoria_percent"],
                        "mensagem": f"Uso de memória acima do limite: {metricas['memoria']['percent']}%"
                    })
            
            # Disco
            if "disco" in metricas and "percent" in metricas["disco"]:
                if metricas["disco"]["percent"] > limites["disco_percent"]:
                    alertas.append({
                        "tipo": "disco",
                        "metrica": "percent",
                        "valor": metricas["disco"]["percent"],
                        "limite": limites["disco_percent"],
                        "mensagem": f"Uso de disco acima do limite: {metricas['disco']['percent']}%"
                    })
            
            # Tempo de resposta
            if "tempo_resposta" in metricas and "p95" in metricas["tempo_resposta"]:
                if metricas["tempo_resposta"]["p95"] > limites["tempo_resposta"]:
                    alertas.append({
                        "tipo": "tempo_resposta",
                        "metrica": "p95",
                        "valor": metricas["tempo_resposta"]["p95"],
                        "limite": limites["tempo_resposta"],
                        "mensagem": f"Tempo de resposta acima do limite: {metricas['tempo_resposta']['p95']}s"
                    })
            
            return alertas
            
        except Exception as e:
            self.logger.registrar_erro("metricas", "Erro ao verificar limites", e)
            return []
    
    def registrar_metricas(self, metricas_sistema: Dict[str, Any],
                          metricas_aplicacao: Dict[str, Any],
                          alertas: List[Dict[str, Any]]) -> None:
        """Registra métricas coletadas"""
        try:
            # Prepara dados
            dados = {
                "timestamp": datetime.now().isoformat(),
                "sistema": metricas_sistema,
                "aplicacao": metricas_aplicacao,
                "alertas": alertas
            }
            
            # Registra no cache
            self.cache.definir("metricas", "ultimas", dados)
            
            # Registra no log
            self.logger.registrar_metricas("coleta", dados)
            
        except Exception as e:
            self.logger.registrar_erro("metricas", "Erro ao registrar métricas", e)
    
    def obter_metricas(self, tipo: str = "ultimas") -> Dict[str, Any]:
        """Obtém métricas registradas"""
        try:
            return self.cache.obter("metricas", tipo) or {}
            
        except Exception as e:
            self.logger.registrar_erro("metricas", "Erro ao obter métricas", e)
            return {}
    
    def obter_alertas(self) -> List[Dict[str, Any]]:
        """Obtém alertas ativos"""
        try:
            metricas = self.obter_metricas()
            return metricas.get("alertas", [])
            
        except Exception as e:
            self.logger.registrar_erro("metricas", "Erro ao obter alertas", e)
            return [] 