"""
Módulo de Monitoramento

Este módulo é responsável por coletar e analisar métricas do sistema.
Ele integra:
1. Coleta de métricas
2. Análise estatística
3. Geração de alertas
4. Armazenamento de dados

O módulo utiliza:
- Flask para API REST
- Pandas para análise
- Threading para coleta assíncrona
- Logging para rastreamento
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional, Union, Callable, Set
from dataclasses import dataclass, field
import logging
import json
import time
import threading
from collections import deque, defaultdict
import random
import math
from datetime import datetime
import copy
import uuid
from enum import Enum, auto
import requests
import os
import psutil
import subprocess
from functools import wraps

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("Monitoramento")

class Config:
    """
    Configurações do sistema carregadas do ConfigMap.
    
    Atributos:
        intervalo_coleta: Intervalo entre coletas em segundos
        timeout_api: Timeout para chamadas de API
        api_token: Token de autenticação
        retencao_dados: Tempo de retenção dos dados em segundos
        limite_alertas: Limite de alertas por minuto
    """
    def __init__(self):
        self.intervalo_coleta = int(os.getenv('INTERVALO_COLETA', '60'))
        self.timeout_api = int(os.getenv('TIMEOUT_API', '5'))
        self.api_token = os.getenv('API_TOKEN', '')
        self.retencao_dados = int(os.getenv('RETENCAO_DADOS', '86400'))  # 24h
        self.limite_alertas = int(os.getenv('LIMITE_ALERTAS', '10'))

config = Config()

def log_operacao_critica(func):
    """
    Decorator para logging de operações críticas.
    
    Registra início, sucesso e falha de operações importantes.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Iniciando operação crítica: {func.__name__}")
        try:
            resultado = func(*args, **kwargs)
            logger.info(f"Operação {func.__name__} concluída com sucesso")
            return resultado
        except Exception as e:
            logger.error(f"Erro na operação {func.__name__}: {str(e)}")
            raise
    return wrapper

@dataclass
class MetricaDimensional:
    """
    Representa uma métrica dimensional do sistema.
    
    Atributos:
        id: Identificador único
        nome: Nome da métrica
        valor: Valor atual
        timestamp: Momento da medição
        dimensao: Dimensão da métrica
        unidade: Unidade de medida
        tags: Tags adicionais
        metadados: Metadados extras
    """
    id: str
    nome: str
    valor: float
    timestamp: float
    dimensao: str
    unidade: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadados: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a métrica para formato de dicionário.
        
        Returns:
            dict: Representação em dicionário
        """
        return {
            "id": self.id,
            "nome": self.nome,
            "valor": self.valor,
            "timestamp": self.timestamp,
            "dimensao": self.dimensao,
            "unidade": self.unidade,
            "tags": self.tags,
            "metadados": self.metadados
        }

class ColetorMetricas:
    """
    Responsável por coletar métricas do sistema.
    
    Atributos:
        metricas: Armazena as métricas coletadas
        lock: Lock para thread safety
        thread_coleta: Thread de coleta
        rodando: Flag de controle
    """
    def __init__(self):
        self.metricas = defaultdict(list)
        self.lock = threading.Lock()
        self.thread_coleta = None
        self.rodando = False
    
    def iniciar(self):
        """Inicia a coleta de métricas em background."""
        if self.thread_coleta is None:
            self.rodando = True
            self.thread_coleta = threading.Thread(target=self._loop_coleta)
            self.thread_coleta.daemon = True
            self.thread_coleta.start()
    
    def parar(self):
        """Para a coleta de métricas."""
        self.rodando = False
        if self.thread_coleta:
            self.thread_coleta.join()
            self.thread_coleta = None
    
    def _loop_coleta(self):
        """Loop principal de coleta."""
        while self.rodando:
            try:
                self._coletar_metricas()
                time.sleep(config.intervalo_coleta)
            except Exception as e:
                logger.error(f"Erro no loop de coleta: {e}")
    
    @log_operacao_critica
    def _coletar_metricas(self):
        """Coleta métricas do sistema."""
        # Coleta métricas de performance
        self._coletar_metricas_performance()
        
        # Coleta métricas de disponibilidade
        self._coletar_metricas_disponibilidade()
        
        # Coleta métricas de segurança
        self._coletar_metricas_seguranca()
        
        # Coleta métricas de custo
        self._coletar_metricas_custo()
        
        # Coleta métricas de qualidade
        self._coletar_metricas_qualidade()
    
    def _coletar_metricas_performance(self):
        """Coleta métricas de performance."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self._adicionar_metrica(
                "cpu_usage",
                cpu_percent,
                "PERFORMANCE",
                "%",
                {"tipo": "sistema"}
            )
            
            # Memória
            mem = psutil.virtual_memory()
            self._adicionar_metrica(
                "memoria_usage",
                mem.percent,
                "PERFORMANCE",
                "%",
                {"tipo": "sistema"}
            )
            
            # Disco
            disco = psutil.disk_usage('/')
            self._adicionar_metrica(
                "disco_usage",
                disco.percent,
                "PERFORMANCE",
                "%",
                {"tipo": "sistema"}
            )
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de performance: {e}")
    
    def _coletar_metricas_disponibilidade(self):
        """Coleta métricas de disponibilidade."""
        try:
            # Uptime
            uptime = psutil.boot_time()
            self._adicionar_metrica(
                "uptime",
                time.time() - uptime,
                "DISPONIBILIDADE",
                "segundos",
                {"tipo": "sistema"}
            )
            
            # Serviços
            for servico in ["nginx", "postgres", "redis"]:
                try:
                    status = subprocess.run(
                        ["systemctl", "is-active", servico],
                        capture_output=True,
                        text=True
                    ).stdout.strip()
                    
                    self._adicionar_metrica(
                        f"servico_{servico}",
                        1 if status == "active" else 0,
                        "DISPONIBILIDADE",
                        "boolean",
                        {"tipo": "servico", "nome": servico}
                    )
                except Exception as e:
                    logger.error(f"Erro ao verificar serviço {servico}: {e}")
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de disponibilidade: {e}")
    
    def _coletar_metricas_seguranca(self):
        """Coleta métricas de segurança."""
        try:
            # Tentativas de login
            auth_log = "/var/log/auth.log"
            if os.path.exists(auth_log):
                with open(auth_log, "r") as f:
                    tentativas = sum(1 for line in f if "Failed password" in line)
                
                self._adicionar_metrica(
                    "tentativas_login",
                    tentativas,
                    "SEGURANCA",
                    "contagem",
                    {"tipo": "autenticacao"}
                )
            
            # Portas abertas
            portas = psutil.net_connections()
            self._adicionar_metrica(
                "portas_abertas",
                len(portas),
                "SEGURANCA",
                "contagem",
                {"tipo": "rede"}
            )
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de segurança: {e}")
    
    def _coletar_metricas_custo(self):
        """Coleta métricas de custo."""
        try:
            # Uso de recursos
            cpu_percent = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disco = psutil.disk_usage('/')
            
            # Calcula custo estimado
            custo_cpu = cpu_percent * 0.1  # $0.1 por % de CPU
            custo_mem = mem.percent * 0.05  # $0.05 por % de memória
            custo_disco = disco.percent * 0.02  # $0.02 por % de disco
            
            custo_total = custo_cpu + custo_mem + custo_disco
            
            self._adicionar_metrica(
                "custo_recursos",
                custo_total,
                "CUSTO",
                "USD",
                {"tipo": "recursos"}
            )
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de custo: {e}")
    
    def _coletar_metricas_qualidade(self):
        """Coleta métricas de qualidade."""
        try:
            # Latência
            latencia = self._medir_latencia()
            self._adicionar_metrica(
                "latencia",
                latencia,
                "QUALIDADE",
                "ms",
                {"tipo": "rede"}
            )
            
            # Taxa de erro
            erros = self._contar_erros()
            self._adicionar_metrica(
                "taxa_erro",
                erros,
                "QUALIDADE",
                "%",
                {"tipo": "aplicacao"}
            )
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas de qualidade: {e}")
    
    def _medir_latencia(self) -> float:
        """Mede a latência do sistema."""
        try:
            inicio = time.time()
            requests.get("http://localhost:8080/health", timeout=1)
            return (time.time() - inicio) * 1000  # ms
        except:
            return 999.9
    
    def _contar_erros(self) -> float:
        """Conta a taxa de erros."""
        try:
            logs = self._ler_logs_erro()
            total = len(logs)
            erros = sum(1 for log in logs if "ERROR" in log)
            return (erros / total * 100) if total > 0 else 0
        except:
            return 0
    
    def _ler_logs_erro(self) -> List[str]:
        """Lê logs de erro."""
        try:
            with open("/var/log/nginx/error.log", "r") as f:
                return f.readlines()[-100:]  # Últimas 100 linhas
        except:
            return []
    
    def _adicionar_metrica(self, nome: str, valor: float, dimensao: str, unidade: str, tags: Dict[str, str]):
        """
        Adiciona uma nova métrica.
        
        Args:
            nome: Nome da métrica
            valor: Valor da métrica
            dimensao: Dimensão da métrica
            unidade: Unidade de medida
            tags: Tags adicionais
        """
        metrica = MetricaDimensional(
            id=str(uuid.uuid4()),
            nome=nome,
            valor=valor,
            timestamp=time.time(),
            dimensao=dimensao,
            unidade=unidade,
            tags=tags
        )
        
        with self.lock:
            self.metricas[dimensao].append(metrica)
            self._limpar_metricas_antigas()
    
    def _limpar_metricas_antigas(self):
        """Remove métricas mais antigas que o tempo de retenção."""
        agora = time.time()
        with self.lock:
            for dimensao in self.metricas:
                self.metricas[dimensao] = [
                    m for m in self.metricas[dimensao]
                    if agora - m.timestamp < config.retencao_dados
                ]
    
    def coletar_metricas(self) -> List[MetricaDimensional]:
        """
        Retorna todas as métricas coletadas.
        
        Returns:
            List[MetricaDimensional]: Lista de métricas
        """
        with self.lock:
            todas_metricas = []
            for metricas in self.metricas.values():
                todas_metricas.extend(metricas)
            return todas_metricas

class AnalisadorMetricas:
    """
    Responsável por analisar métricas e detectar padrões.
    
    Atributos:
        coletor: Referência ao coletor de métricas
        lock: Lock para thread safety
    """
    def __init__(self, coletor: ColetorMetricas):
        self.coletor = coletor
        self.lock = threading.Lock()
    
    @log_operacao_critica
    def analisar_metricas(self) -> List[Dict[str, Any]]:
        """
        Analisa métricas coletadas.
        
        Returns:
            List[Dict[str, Any]]: Resultados da análise
        """
        metricas = self.coletor.coletar_metricas()
        resultados = []
        
        # Agrupa por dimensão
        metricas_por_dimensao = defaultdict(list)
        for metrica in metricas:
            metricas_por_dimensao[metrica.dimensao].append(metrica)
        
        # Analisa cada dimensão
        for dimensao, metricas_dimensao in metricas_por_dimensao.items():
            try:
                # Calcula estatísticas
                stats = self._calcular_estatisticas(metricas_dimensao)
                
                # Detecta anomalias
                anomalias = self._detectar_anomalias([m.valor for m in metricas_dimensao])
                
                # Analisa tendências
                tendencias = self._calcular_tendencias([m.valor for m in metricas_dimensao])
                
                resultados.append({
                    "dimensao": dimensao,
                    "estatisticas": stats,
                    "anomalias": anomalias,
                    "tendencias": tendencias,
                    "timestamp": time.time()
                })
                
            except Exception as e:
                logger.error(f"Erro ao analisar dimensão {dimensao}: {e}")
        
        return resultados
    
    def _calcular_estatisticas(self, metricas: List[MetricaDimensional]) -> Dict[str, float]:
        """
        Calcula estatísticas das métricas.
        
        Args:
            metricas: Lista de métricas
            
        Returns:
            Dict[str, float]: Estatísticas calculadas
        """
        valores = [m.valor for m in metricas]
        return {
            "media": np.mean(valores),
            "mediana": np.median(valores),
            "desvio": np.std(valores),
            "min": np.min(valores),
            "max": np.max(valores)
        }
    
    def _detectar_anomalias(self, valores: List[float]) -> List[Dict[str, Any]]:
        """
        Detecta anomalias nos valores.
        
        Args:
            valores: Lista de valores
            
        Returns:
            List[Dict[str, Any]]: Anomalias detectadas
        """
        if len(valores) < 2:
            return []
        
        media = np.mean(valores)
        desvio = np.std(valores)
        limite = 2 * desvio  # 2 desvios padrão
        
        anomalias = []
        for i, valor in enumerate(valores):
            if abs(valor - media) > limite:
                anomalias.append({
                    "indice": i,
                    "valor": valor,
                    "desvio": abs(valor - media) / desvio,
                    "timestamp": time.time()
                })
        
        return anomalias
    
    def _calcular_tendencias(self, valores: List[float]) -> Dict[str, Any]:
        """
        Calcula tendências nos valores.
        
        Args:
            valores: Lista de valores
            
        Returns:
            Dict[str, Any]: Tendências calculadas
        """
        if len(valores) < 2:
            return {}
        
        x = np.arange(len(valores))
        slope, intercept = np.polyfit(x, valores, 1)
        
        return {
            "inclinacao": slope,
            "intercepto": intercept,
            "r2": np.corrcoef(x, valores)[0, 1] ** 2,
            "timestamp": time.time()
        }

class GeradorAlertas:
    """
    Responsável por gerar alertas baseados na análise.
    
    Atributos:
        analisador: Referência ao analisador de métricas
        alertas_ativos: Conjunto de alertas ativos
        ultimo_alerta: Timestamp do último alerta por dimensão
        lock: Lock para thread safety
    """
    def __init__(self, analisador: AnalisadorMetricas):
        self.analisador = analisador
        self.alertas_ativos = set()
        self.ultimo_alerta = defaultdict(float)
        self.lock = threading.Lock()
    
    @log_operacao_critica
    def avaliar_alertas(self, resultados: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Avalia resultados e gera alertas.
        
        Args:
            resultados: Resultados da análise
            
        Returns:
            List[Dict[str, Any]]: Alertas gerados
        """
        alertas = []
        
        for resultado in resultados:
            dimensao = resultado["dimensao"]
            
            # Verifica anomalias
            for anomalia in resultado["anomalias"]:
                alerta = self._gerar_alerta_anomalia(dimensao, anomalia)
                if alerta:
                    alertas.append(alerta)
            
            # Verifica tendências
            if resultado["tendencias"]:
                alerta = self._gerar_alerta_tendencia(dimensao, resultado["tendencias"])
                if alerta:
                    alertas.append(alerta)
            
            # Verifica limites
            alerta = self._verificar_limites(dimensao, resultado["estatisticas"])
            if alerta:
                alertas.append(alerta)
        
        return alertas
    
    def _gerar_alerta_anomalia(self, dimensao: str, anomalia: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Gera alerta para anomalia.
        
        Args:
            dimensao: Dimensão da métrica
            anomalia: Dados da anomalia
            
        Returns:
            Optional[Dict[str, Any]]: Alerta gerado ou None
        """
        alerta_id = f"anomalia_{dimensao}_{int(time.time())}"
        
        # Verifica se já existe alerta ativo
        if alerta_id in self.alertas_ativos:
            return None
        
        # Verifica limite de alertas
        if not self._verificar_limite_alertas():
            return None
        
        # Gera alerta
        alerta = {
            "id": alerta_id,
            "tipo": "anomalia",
            "dimensao": dimensao,
            "severidade": "alta",
            "mensagem": f"Anomalia detectada em {dimensao}: desvio de {anomalia['desvio']:.2f} desvios",
            "timestamp": time.time(),
            "dados": anomalia
        }
        
        # Registra alerta
        with self.lock:
            self.alertas_ativos.add(alerta_id)
            self.ultimo_alerta[dimensao] = time.time()
        
        return alerta
    
    def _gerar_alerta_tendencia(self, dimensao: str, tendencias: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Gera alerta para tendência.
        
        Args:
            dimensao: Dimensão da métrica
            tendencias: Dados da tendência
            
        Returns:
            Optional[Dict[str, Any]]: Alerta gerado ou None
        """
        alerta_id = f"tendencia_{dimensao}_{int(time.time())}"
        
        # Verifica se já existe alerta ativo
        if alerta_id in self.alertas_ativos:
            return None
        
        # Verifica limite de alertas
        if not self._verificar_limite_alertas():
            return None
        
        # Define direção da tendência
        direcao = "subindo" if tendencias["inclinacao"] > 0 else "descendo"
        
        # Gera alerta
        alerta = {
            "id": alerta_id,
            "tipo": "tendencia",
            "dimensao": dimensao,
            "severidade": "media",
            "mensagem": f"Tendência significativa detectada: métricas {direcao} (inclinação: {tendencias['inclinacao']:.2f})",
            "timestamp": time.time(),
            "dados": tendencias
        }
        
        # Registra alerta
        with self.lock:
            self.alertas_ativos.add(alerta_id)
            self.ultimo_alerta[dimensao] = time.time()
        
        return alerta
    
    def _verificar_limites(self, dimensao: str, stats: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """
        Verifica se métricas ultrapassaram limites definidos.
        
        Args:
            dimensao: Dimensão da métrica
            stats: Estatísticas da métrica
            
        Returns:
            Optional[Dict[str, Any]]: Alerta gerado ou None
        """
        alerta_id = f"limite_{dimensao}_{int(time.time())}"
        
        # Verifica se já existe alerta ativo
        if alerta_id in self.alertas_ativos:
            return None
        
        # Verifica limite de alertas
        if not self._verificar_limite_alertas():
            return None
        
        # Define limites por dimensão
        limites = {
            "PERFORMANCE": {"max": 80, "min": 20},
            "DISPONIBILIDADE": {"min": 99.9},
            "SEGURANCA": {"max": 5},
            "CUSTO": {"max": 1000},
            "QUALIDADE": {"min": 80}
        }
        
        limite = limites.get(dimensao, {})
        alerta = None
        
        if "max" in limite and stats["media"] > limite["max"]:
            alerta = {
                "id": alerta_id,
                "tipo": "limite",
                "dimensao": dimensao,
                "severidade": "alta",
                "mensagem": f"Métrica {dimensao} acima do limite: {stats['media']:.2f} > {limite['max']}",
                "timestamp": time.time(),
                "dados": {"valor": stats["media"], "limite": limite["max"]}
            }
        elif "min" in limite and stats["media"] < limite["min"]:
            alerta = {
                "id": alerta_id,
                "tipo": "limite",
                "dimensao": dimensao,
                "severidade": "alta",
                "mensagem": f"Métrica {dimensao} abaixo do limite: {stats['media']:.2f} < {limite['min']}",
                "timestamp": time.time(),
                "dados": {"valor": stats["media"], "limite": limite["min"]}
            }
        
        if alerta:
            # Registra alerta
            with self.lock:
                self.alertas_ativos.add(alerta_id)
                self.ultimo_alerta[dimensao] = time.time()
        
        return alerta
    
    def _verificar_limite_alertas(self) -> bool:
        """
        Verifica se não excedeu o limite de alertas por minuto.
        
        Returns:
            bool: True se pode gerar mais alertas
        """
        agora = time.time()
        alertas_ultimo_minuto = sum(1 for t in self.ultimo_alerta.values() if agora - t < 60)
        return alertas_ultimo_minuto < config.limite_alertas
    
    def limpar_alertas_antigos(self):
        """
        Remove alertas mais antigos que 1 hora.
        """
        agora = time.time()
        with self.lock:
            self.alertas_ativos = {
                alerta_id for alerta_id in self.alertas_ativos
                if agora - self.ultimo_alerta.get(alerta_id.split("_")[1], 0) < 3600
            }

# Inicialização da API e rotas
if __name__ == "__main__":
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    # Inicializa componentes
    coletor = ColetorMetricas()
    analisador = AnalisadorMetricas(coletor)
    gerador_alertas = GeradorAlertas(analisador)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Verifica a saúde do serviço."""
        return jsonify({"status": "healthy"})
    
    @app.route('/ready', methods=['GET'])
    def ready_check():
        """
        Verifica se o serviço está pronto para operação.
            
        Returns:
            dict: Status de prontidão
        """
        if not coletor or not analisador or not gerador_alertas:
            return jsonify({"status": "not ready", "reason": "Components not initialized"}), 503
        return jsonify({"status": "ready", "timestamp": time.time()})
    
    @app.route('/api/metricas', methods=['GET'])
    def listar_metricas():
        """
        Lista todas as métricas coletadas.
        
        Returns:
            dict: Lista de métricas
        """
        try:
            metricas = coletor.coletar_metricas()
            return jsonify([m.to_dict() for m in metricas]), 200
        except Exception as e:
            logger.error(f"Erro ao listar métricas: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/metricas/<metrica_id>', methods=['GET'])
    def obter_metrica(metrica_id):
        """
        Obtém uma métrica específica.
        
        Args:
            metrica_id: ID da métrica
            
        Returns:
            dict: Dados da métrica
        """
        try:
            metricas = coletor.coletar_metricas()
            metrica = next((m for m in metricas if m.id == metrica_id), None)
            
            if not metrica:
                return jsonify({"error": f"Métrica {metrica_id} não encontrada"}), 404
            
            return jsonify(metrica.to_dict()), 200
        except Exception as e:
            logger.error(f"Erro ao obter métrica: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/analise', methods=['GET'])
    def analisar_metricas():
        """
        Realiza análise das métricas coletadas.
        
        Returns:
            dict: Resultados da análise
        """
        try:
            resultados = analisador.analisar_metricas()
            return jsonify(resultados), 200
        except Exception as e:
            logger.error(f"Erro ao analisar métricas: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/alertas', methods=['GET'])
    def gerar_alertas():
        """
        Gera alertas baseados na análise de métricas.
        
        Returns:
            dict: Lista de alertas gerados
        """
        try:
            resultados = analisador.analisar_metricas()
            alertas = gerador_alertas.avaliar_alertas(resultados)
            return jsonify(alertas), 200
        except Exception as e:
            logger.error(f"Erro ao gerar alertas: {e}")
            return jsonify({"error": str(e)}), 500
    
    # Inicia o servidor
    app.run(host='0.0.0.0', port=8080)
