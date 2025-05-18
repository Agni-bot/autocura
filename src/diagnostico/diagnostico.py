"""
Módulo de Diagnóstico

Este módulo é responsável por analisar métricas e gerar diagnósticos do sistema.
Ele integra:
1. Análise estatística de métricas
2. Detecção de padrões e anomalias
3. Geração de diagnósticos
4. Priorização de problemas

O módulo utiliza:
- Análise estatística
- Machine learning
- Regras de negócio para priorização
- Gemini API para análise contextual
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
from functools import wraps

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("Diagnostico")

class Config:
    """
    Configurações do sistema carregadas do ConfigMap.
    
    Atributos:
        score_minimo: Score mínimo para considerar um diagnóstico válido
        timeout_api: Timeout para chamadas de API
        api_token: Token de autenticação
        max_diagnosticos: Número máximo de diagnósticos por ciclo
        prioridades: Pesos para diferentes tipos de problema
    """
    def __init__(self):
        self.score_minimo = float(os.getenv('SCORE_MINIMO', '0.7'))
        self.timeout_api = int(os.getenv('TIMEOUT_API', '5'))
        self.api_token = os.getenv('API_TOKEN', '')
        self.max_diagnosticos = int(os.getenv('MAX_DIAGNOSTICOS', '10'))
        self.prioridades = {
            "CRITICO": float(os.getenv('PRIORIDADE_CRITICO', '5.0')),
            "ALTO": float(os.getenv('PRIORIDADE_ALTO', '4.0')),
            "MEDIO": float(os.getenv('PRIORIDADE_MEDIO', '3.0')),
            "BAIXO": float(os.getenv('PRIORIDADE_BAIXO', '2.0')),
            "INFO": float(os.getenv('PRIORIDADE_INFO', '1.0'))
        }

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
        dimensao: Dimensão da métrica
        timestamp: Momento da coleta
        labels: Labels adicionais
    """
    id: str
    nome: str
    valor: float
    dimensao: str
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    
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
            "dimensao": self.dimensao,
            "timestamp": self.timestamp,
            "labels": self.labels
        }

# Função para comunicação com o serviço de monitoramento
def obter_metricas_do_monitoramento(metrica_id=None):
    """
    Obtém métricas do serviço de monitoramento via API REST.
    
    Args:
        metrica_id: ID opcional da métrica específica
        
    Returns:
        Lista de métricas ou uma métrica específica
        
    Raises:
        ValueError: Se os dados retornados forem inválidos
        requests.exceptions.RequestException: Em caso de erro na requisição
    """
    try:
        base_url = f"{MONITORAMENTO_URL}/api/metricas"
        if metrica_id:
            url = f"{base_url}/{metrica_id}"
        else:
            url = base_url
            
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if metrica_id:
            # Retorna uma única métrica
            return MetricaDimensional(
                id=data["id"],
                nome=data["nome"],
                valor=data["valor"],
                timestamp=data["timestamp"],
                dimensao=data["dimensao"],
                unidade=data["unidade"],
                tags=data.get("tags", {}),
                metadados=data.get("metadados", {})
            )
        else:
            # Retorna lista de métricas
            metricas = []
            for item in data:
                metrica = MetricaDimensional(
                    id=item["id"],
                    nome=item["nome"],
                    valor=item["valor"],
                    timestamp=item["timestamp"],
                    dimensao=item["dimensao"],
                    unidade=item["unidade"],
                    tags=item.get("tags", {}),
                    metadados=item.get("metadados", {})
                )
                metricas.append(metrica)
            return metricas
            
    except Exception as e:
        logger.error(f"Erro ao obter métricas do monitoramento: {e}")
        return []

@dataclass
class PadraoAnomalia:
    """
    Representa um padrão de anomalia detectado.
    
    Atributos:
        id: Identificador único
        tipo: Tipo do padrão
        descricao: Descrição do padrão
        metricas: Métricas relacionadas
        score: Score de confiança
        timestamp: Momento da detecção
        contexto: Contexto adicional
    """
    id: str
    tipo: str
    descricao: str
    metricas: List[MetricaDimensional]
    score: float
    timestamp: float
    contexto: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o padrão para formato de dicionário.
        
        Returns:
            dict: Representação em dicionário
        """
        return {
            "id": self.id,
            "tipo": self.tipo,
            "descricao": self.descricao,
            "metricas": [m.to_dict() for m in self.metricas],
            "score": self.score,
            "timestamp": self.timestamp,
            "contexto": self.contexto
        }

@dataclass
class Diagnostico:
    """
    Representa um diagnóstico do sistema.
    
    Atributos:
        id: Identificador único
        tipo: Tipo do diagnóstico
        descricao: Descrição do diagnóstico
        causa_raiz: Causa raiz identificada
        impacto: Impacto estimado
        prioridade: Prioridade do diagnóstico
        padroes: Padrões relacionados
        timestamp: Momento da geração
        contexto: Contexto adicional
    """
    id: str
    tipo: str
    descricao: str
    causa_raiz: str
    impacto: str
    prioridade: int
    padroes: List[PadraoAnomalia]
    timestamp: float
    contexto: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o diagnóstico para formato de dicionário.
        
        Returns:
            dict: Representação em dicionário
        """
        return {
            "id": self.id,
            "tipo": self.tipo,
            "descricao": self.descricao,
            "causa_raiz": self.causa_raiz,
            "impacto": self.impacto,
            "prioridade": self.prioridade,
            "padroes": [p.to_dict() for p in self.padroes],
            "timestamp": self.timestamp,
            "contexto": self.contexto
        }

class AnalisadorMetricas:
    """
    Analisa métricas para identificar padrões e anomalias.
    
    Responsabilidades:
    1. Analisar métricas por dimensão
    2. Detectar anomalias
    3. Identificar padrões
    4. Calcular tendências
    """
    def __init__(self):
        self.lock = threading.Lock()
        logger.info("AnalisadorMetricas inicializado")
    
    @log_operacao_critica
    def analisar_metricas(self, metricas: List[MetricaDimensional]) -> List[PadraoAnomalia]:
        """
        Analisa uma lista de métricas.
        
        Args:
            metricas: Lista de métricas a analisar
            
        Returns:
            List[PadraoAnomalia]: Lista de padrões detectados
        """
        padroes = []
        
        # Agrupa métricas por dimensão
        metricas_por_dimensao = defaultdict(list)
        for metrica in metricas:
            metricas_por_dimensao[metrica.dimensao].append(metrica)
        
        # Analisa cada dimensão
        for dimensao, metricas_dimensao in metricas_por_dimensao.items():
            padroes.extend(self._analisar_dimensao(dimensao, metricas_dimensao))
        
        return padroes
    
    def _analisar_dimensao(self, dimensao: str, metricas: List[MetricaDimensional]) -> List[PadraoAnomalia]:
        """
        Analisa métricas de uma dimensão.
        
        Args:
            dimensao: Dimensão das métricas
            metricas: Lista de métricas da dimensão
            
        Returns:
            List[PadraoAnomalia]: Lista de padrões detectados
        """
        padroes = []
        
        # Extrai valores
        valores = [m.valor for m in metricas]
        
        # Detecta anomalias
        anomalias = self._detectar_anomalias(valores)
        
        # Calcula tendências
        tendencias = self._calcular_tendencias(valores)
        
        # Gera padrões
        if anomalias:
            padroes.append(self._gerar_padrao_anomalia(dimensao, metricas, anomalias))
        
        if tendencias["significativa"]:
            padroes.append(self._gerar_padrao_tendencia(dimensao, metricas, tendencias))
        
        return padroes
    
    def _detectar_anomalias(self, valores: List[float]) -> List[Dict[str, Any]]:
        """
        Detecta anomalias em uma série de valores.
        
        Args:
            valores: Lista de valores
            
        Returns:
            List[Dict[str, Any]]: Lista de anomalias detectadas
        """
        anomalias = []
        
        # Calcula z-scores
        media = np.mean(valores)
        desvio = np.std(valores)
        z_scores = [(v - media) / desvio for v in valores]
        
        # Identifica valores com z-score > 3
        for i, z in enumerate(z_scores):
            if abs(z) > 3:
                anomalias.append({
                    "indice": i,
                    "valor": valores[i],
                    "z_score": z
                })
        
        return anomalias
    
    def _calcular_tendencias(self, valores: List[float]) -> Dict[str, Any]:
        """
        Calcula tendências em uma série de valores.
        
        Args:
            valores: Lista de valores
            
        Returns:
            Dict[str, Any]: Resultados da análise de tendências
        """
        # Ajusta regressão linear
        x = np.arange(len(valores))
        slope, intercept = np.polyfit(x, valores, 1)
        
        # Calcula R²
        y_pred = slope * x + intercept
        r2 = np.corrcoef(valores, y_pred)[0, 1] ** 2
        
        return {
            "slope": slope,
            "intercept": intercept,
            "r2": r2,
            "significativa": abs(slope) > 0.1 and r2 > 0.7  # TODO: Ajustar limites
        }
    
    def _gerar_padrao_anomalia(self, dimensao: str, metricas: List[MetricaDimensional], anomalias: List[Dict[str, Any]]) -> PadraoAnomalia:
        """
        Gera um padrão de anomalia.
        
        Args:
            dimensao: Dimensão das métricas
            metricas: Lista de métricas
            anomalias: Lista de anomalias detectadas
            
        Returns:
            PadraoAnomalia: Padrão gerado
        """
        # Calcula score baseado no número e severidade das anomalias
        score = min(1.0, sum(abs(a["z_score"]) for a in anomalias) / (len(anomalias) * 5))
        
        return PadraoAnomalia(
            id=f"anomalia_{int(time.time())}",
            tipo="ANOMALIA",
            descricao=f"Anomalias detectadas em {dimensao}",
            metricas=metricas,
            score=score,
            timestamp=time.time(),
            contexto={
                "anomalias": anomalias,
                "dimensao": dimensao
            }
        )
    
    def _gerar_padrao_tendencia(self, dimensao: str, metricas: List[MetricaDimensional], tendencias: Dict[str, Any]) -> PadraoAnomalia:
        """
        Gera um padrão de tendência.
        
        Args:
            dimensao: Dimensão das métricas
            metricas: Lista de métricas
            tendencias: Dados das tendências
            
        Returns:
            PadraoAnomalia: Padrão gerado
        """
        # Calcula score baseado na significância da tendência
        score = min(1.0, (abs(tendencias["slope"]) * tendencias["r2"]) / 0.1)
        
        return PadraoAnomalia(
            id=f"tendencia_{int(time.time())}",
            tipo="TENDENCIA",
            descricao=f"Tendência significativa em {dimensao}",
            metricas=metricas,
            score=score,
            timestamp=time.time(),
            contexto={
                "tendencias": tendencias,
                "dimensao": dimensao
            }
        )

class GeradorDiagnosticos:
    """
    Gera diagnósticos baseados em padrões de anomalia.
    
    Responsabilidades:
    1. Analisar padrões de anomalia
    2. Identificar causas raiz
    3. Estimar impactos
    4. Priorizar diagnósticos
    """
    def __init__(self):
        self.lock = threading.Lock()
        logger.info("GeradorDiagnosticos inicializado")
    
    @log_operacao_critica
    def gerar_diagnosticos(self, padroes: List[PadraoAnomalia]) -> List[Diagnostico]:
        """
        Gera diagnósticos para uma lista de padrões.
        
        Args:
            padroes: Lista de padrões de anomalia
            
        Returns:
            List[Diagnostico]: Lista de diagnósticos gerados
        """
        diagnosticos = []
        
        # Ordena padrões por score
        padroes.sort(key=lambda p: p.score, reverse=True)
        
        # Gera diagnóstico para cada padrão
        for padrao in padroes:
            diagnostico = self._gerar_diagnostico(padrao)
            if diagnostico:
                diagnosticos.append(diagnostico)
        
        return diagnosticos
    
    def _gerar_diagnostico(self, padrao: PadraoAnomalia) -> Optional[Diagnostico]:
        """
        Gera um diagnóstico para um padrão.
        
        Args:
            padrao: Padrão de anomalia
            
        Returns:
            Optional[Diagnostico]: Diagnóstico gerado ou None
        """
        # Verifica score mínimo
        if padrao.score < config.score_minimo:
            return None
        
        # Identifica causa raiz
        causa_raiz = self._identificar_causa_raiz(padrao)
        
        # Estima impacto
        impacto = self._estimar_impacto(padrao)
        
        # Determina prioridade
        prioridade = self._determinar_prioridade(padrao)
        
        # Gera descrição
        descricao = self._gerar_descricao(padrao, causa_raiz, impacto)
        
        # Cria diagnóstico
        return Diagnostico(
            id=f"diagnostico_{int(time.time())}",
            tipo=padrao.tipo,
            descricao=descricao,
            causa_raiz=causa_raiz,
            impacto=impacto,
            prioridade=prioridade,
            padroes=[padrao],
            timestamp=time.time()
        )
    
    def _identificar_causa_raiz(self, padrao: PadraoAnomalia) -> str:
        """
        Identifica a causa raiz de um padrão.
        
        Args:
            padrao: Padrão de anomalia
            
        Returns:
            str: Causa raiz identificada
        """
        # TODO: Implementar análise mais sofisticada
        if padrao.tipo == "ANOMALIA":
            return f"Anomalia detectada em {padrao.contexto['dimensao']}"
        else:
            return f"Tendência significativa em {padrao.contexto['dimensao']}"
    
    def _estimar_impacto(self, padrao: PadraoAnomalia) -> str:
        """
        Estima o impacto de um padrão.
        
        Args:
            padrao: Padrão de anomalia
            
        Returns:
            str: Impacto estimado
        """
        # TODO: Implementar análise mais sofisticada
        if padrao.tipo == "ANOMALIA":
            return f"Impacto crítico em {padrao.contexto['dimensao']}"
        else:
            return f"Impacto progressivo em {padrao.contexto['dimensao']}"
    
    def _determinar_prioridade(self, padrao: PadraoAnomalia) -> int:
        """
        Determina a prioridade de um padrão.
        
        Args:
            padrao: Padrão de anomalia
            
        Returns:
            int: Prioridade determinada
        """
        # TODO: Implementar lógica mais sofisticada
        if padrao.score > 0.9:
            return 5  # CRÍTICO
        elif padrao.score > 0.7:
            return 4  # ALTO
        elif padrao.score > 0.5:
            return 3  # MÉDIO
        elif padrao.score > 0.3:
            return 2  # BAIXO
        else:
            return 1  # INFO
    
    def _gerar_descricao(self, padrao: PadraoAnomalia, causa_raiz: str, impacto: str) -> str:
        """
        Gera uma descrição para o diagnóstico.
        
        Args:
            padrao: Padrão de anomalia
            causa_raiz: Causa raiz identificada
            impacto: Impacto estimado
            
        Returns:
            str: Descrição gerada
        """
        return f"{padrao.descricao}. Causa raiz: {causa_raiz}. Impacto: {impacto}"

# Inicialização da API e rotas
if __name__ == "__main__":
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    # Inicializa componentes
    analisador = AnalisadorMetricas()
    gerador = GeradorDiagnosticos()
    
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
        if not analisador or not gerador:
            return jsonify({"status": "not ready", "reason": "Components not initialized"}), 503
        return jsonify({"status": "ready", "timestamp": time.time()})
    
    @app.route('/api/diagnosticos', methods=['POST'])
    def gerar_diagnosticos():
        """
        Gera diagnósticos baseados nas métricas fornecidas.
        
        Returns:
            dict: Lista de diagnósticos gerados
        """
        try:
            data = request.get_json()
            metricas = [MetricaDimensional(**m) for m in data["metricas"]]
            
            # Analisa métricas
            padroes = analisador.analisar_metricas(metricas)
            
            # Gera diagnósticos
            diagnosticos = gerador.gerar_diagnosticos(padroes)
            
            return jsonify([d.to_dict() for d in diagnosticos]), 200
        except Exception as e:
            logger.error(f"Erro ao gerar diagnósticos: {e}")
            return jsonify({"error": str(e)}), 500
    
    # Inicia o servidor
    app.run(host='0.0.0.0', port=8080)
