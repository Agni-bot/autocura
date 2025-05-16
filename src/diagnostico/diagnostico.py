<<<<<<< HEAD
# Módulo de Diagnóstico por Rede Neural de Alta Ordem

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from typing import Dict, List, Any, Tuple, Optional, Union, Callable
=======
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
>>>>>>> origin/main
from dataclasses import dataclass, field
import logging
import json
import time
import threading
from collections import deque, defaultdict
<<<<<<< HEAD
import networkx as nx
from scipy import stats
import random
import math
from datetime import datetime
import requests
import os
=======
import random
import math
from datetime import datetime
import copy
import uuid
from enum import Enum, auto
import requests
import os
from functools import wraps
>>>>>>> origin/main

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

<<<<<<< HEAD
logger = logging.getLogger("DiagnosticoRedeNeural")

# Configuração das URLs dos serviços
MONITORAMENTO_URL = os.getenv('MONITORAMENTO_URL', 'http://monitoramento:8080')

# Classe local para substituir importação direta
@dataclass
class MetricaDimensional:
    """Classe local que substitui a importação de monitoramento.monitoramento.MetricaDimensional"""
    id: str
    nome: str
    valor: float
    timestamp: float
    dimensao: str
    unidade: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadados: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricaDimensional':
        """Cria uma instância de métrica a partir de um dicionário."""
        return cls(
            id=data["id"],
            nome=data["nome"],
            valor=data["valor"],
            timestamp=data["timestamp"],
            dimensao=data["dimensao"],
            unidade=data["unidade"],
            tags=data.get("tags", {}),
            metadados=data.get("metadados", {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a métrica para formato de dicionário."""
=======
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
>>>>>>> origin/main
        return {
            "id": self.id,
            "nome": self.nome,
            "valor": self.valor,
<<<<<<< HEAD
            "timestamp": self.timestamp,
            "dimensao": self.dimensao,
            "unidade": self.unidade,
            "tags": self.tags,
            "metadados": self.metadados
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
=======
            "dimensao": self.dimensao,
            "timestamp": self.timestamp,
            "labels": self.labels
        }

class DimensaoMonitoramento(Enum):
    """
    Enumeração das dimensões de monitoramento.
    
    Valores:
        PERFORMANCE: Métricas de performance
        DISPONIBILIDADE: Métricas de disponibilidade
        SEGURANCA: Métricas de segurança
        CUSTO: Métricas de custo
        QUALIDADE: Métricas de qualidade
    """
    PERFORMANCE = "performance"
    DISPONIBILIDADE = "disponibilidade"
    SEGURANCA = "seguranca"
    CUSTO = "custo"
    QUALIDADE = "qualidade"
>>>>>>> origin/main

@dataclass
class PadraoAnomalia:
    """
<<<<<<< HEAD
    Representa um padrão de anomalia detectado no sistema.
    
    Como uma constelação de sintomas no céu da cognição,
    cada padrão é uma assinatura única de desequilíbrio,
    um hieróglifo que conta a história de uma perturbação.
    """
    id: str
    nome: str
    dimensoes: List[str]
    metricas_relacionadas: List[str]
    limiar_confianca: float
    padrao_temporal: Optional[List[float]] = None
    funcao_deteccao: Optional[Callable] = None
    descricao: str = ""
    
    def corresponde(self, metricas: List[MetricaDimensional], contexto: Dict[str, Any] = None) -> Tuple[bool, float]:
        """
        Verifica se um conjunto de métricas corresponde a este padrão de anomalia.
        Retorna um tuple (corresponde, confianca).
        """
        if self.funcao_deteccao:
            try:
                return self.funcao_deteccao(metricas, contexto or {})
            except Exception as e:
                logger.error(f"Erro na função de detecção do padrão {self.id}: {str(e)}")
                return False, 0.0
        
        # Implementação padrão se não houver função personalizada
        # Verifica se as métricas necessárias estão presentes
        nomes_metricas = set(m.nome for m in metricas)
        if not all(m in nomes_metricas for m in self.metricas_relacionadas):
            return False, 0.0
        
        # Filtra métricas relevantes
        metricas_relevantes = [m for m in metricas if m.nome in self.metricas_relacionadas]
        
        # Verifica padrão temporal se disponível
        if self.padrao_temporal and len(metricas_relevantes) >= len(self.padrao_temporal):
            # Ordena por timestamp
            metricas_relevantes.sort(key=lambda m: m.timestamp)
            
            # Normaliza valores
            valores = [m.valor for m in metricas_relevantes[-len(self.padrao_temporal):]]
            valores_norm = [(v - min(valores)) / (max(valores) - min(valores) + 1e-10) for v in valores]
            
            # Compara com o padrão
            padrao_norm = [(p - min(self.padrao_temporal)) / (max(self.padrao_temporal) - min(self.padrao_temporal) + 1e-10) 
                          for p in self.padrao_temporal]
            
            # Calcula similaridade (correlação)
            corr, _ = stats.pearsonr(valores_norm, padrao_norm)
            confianca = max(0, (corr + 1) / 2)  # Mapeia de [-1,1] para [0,1]
            
            return confianca >= self.limiar_confianca, confianca
        
        # Implementação simplificada: verifica se alguma métrica está fora dos limites normais
        # Assume que o contexto contém informações sobre limites normais
        if contexto and "limites" in contexto:
            limites = contexto["limites"]
            anomalias = []
            
            for metrica in metricas_relevantes:
                if metrica.nome in limites:
                    min_val, max_val = limites[metrica.nome]
                    if metrica.valor < min_val or metrica.valor > max_val:
                        anomalias.append((metrica.nome, metrica.valor, min_val, max_val))
            
            confianca = len(anomalias) / len(metricas_relevantes) if metricas_relevantes else 0
            return confianca >= self.limiar_confianca, confianca
        
        return False, 0.0

=======
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
>>>>>>> origin/main

@dataclass
class Diagnostico:
    """
<<<<<<< HEAD
    Resultado de um processo de diagnóstico.
    
    Como um mapa da verdade emergente nas sombras dos dados,
    cada diagnóstico é uma narrativa causal que conecta
    os fragmentos dispersos em uma história coerente.
    """
    id: str
    timestamp: float
    anomalias_detectadas: List[Tuple[PadraoAnomalia, float]]
    metricas_analisadas: List[str]
    causa_raiz: Optional[str] = None
    confianca: float = 0.0
    recomendacoes: List[str] = field(default_factory=list)
    contexto: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o diagnóstico para formato de dicionário."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "anomalias_detectadas": [
                {
                    "anomalia": {
                        "id": anomalia.id,
                        "nome": anomalia.nome,
                        "dimensoes": anomalia.dimensoes,
                        "descricao": anomalia.descricao,
                        "severidade": getattr(anomalia, "severidade", 0.5)
                    },
                    "confianca": conf
                }
                for anomalia, conf in self.anomalias_detectadas
            ],
            "metricas_analisadas": self.metricas_analisadas,
            "causa_raiz": self.causa_raiz,
            "confianca": self.confianca,
            "recomendacoes": self.recomendacoes,
            "contexto": self.contexto
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], catalogo_anomalias: Dict[str, PadraoAnomalia]) -> 'Diagnostico':
        """Cria uma instância de diagnóstico a partir de um dicionário."""
        anomalias_detectadas = [
            (catalogo_anomalias[a["anomalia"]["id"]], a["confianca"])
            for a in data["anomalias_detectadas"]
            if a["anomalia"]["id"] in catalogo_anomalias
        ]
        
        return cls(
            id=data["id"],
            timestamp=data["timestamp"],
            anomalias_detectadas=anomalias_detectadas,
            metricas_analisadas=data["metricas_analisadas"],
            causa_raiz=data.get("causa_raiz"),
            confianca=data.get("confianca", 0.0),
            recomendacoes=data.get("recomendacoes", []),
            contexto=data.get("contexto", {})
        )


class MotorRegrasEspecialistas:
    """
    Implementa árvores de decisão dinâmicas para diagnóstico.
    
    Como um oráculo digital que consulta o conhecimento acumulado,
    destila sabedoria de experiências passadas em regras adaptativas,
    um jardim de caminhos decisórios que se bifurcam e convergem.
    """
    def __init__(self):
        self.regras = []
        self.historico_execucoes = deque(maxlen=1000)
        self.lock = threading.Lock()
        logger.info("MotorRegrasEspecialistas inicializado")
    
    def adicionar_regra(self, condicao: Callable, acao: Callable, prioridade: int = 0, 
                       nome: str = None, descricao: str = None):
        """
        Adiciona uma regra ao motor.
        
        Args:
            condicao: Função que recebe (metricas, contexto) e retorna um booleano
            acao: Função que recebe (metricas, contexto) e retorna um resultado
            prioridade: Valor numérico para ordenação de regras (maior = mais prioritário)
            nome: Nome identificador da regra
            descricao: Descrição detalhada da regra
        """
        nome = nome or f"regra_{len(self.regras)}"
        
        with self.lock:
            self.regras.append({
                "nome": nome,
                "descricao": descricao,
                "condicao": condicao,
                "acao": acao,
                "prioridade": prioridade,
                "execucoes": 0,
                "sucessos": 0,
                "ultima_execucao": None
            })
            # Ordena regras por prioridade
            self.regras.sort(key=lambda r: r["prioridade"], reverse=True)
        
        logger.info(f"Regra '{nome}' adicionada com prioridade {prioridade}")
    
    def executar(self, metricas: List[MetricaDimensional], contexto: Dict[str, Any] = None) -> List[Any]:
        """
        Executa todas as regras aplicáveis e retorna os resultados.
        
        Args:
            metricas: Lista de métricas para análise
            contexto: Dicionário com informações contextuais
            
        Returns:
            Lista de resultados das ações executadas
        """
        contexto = contexto or {}
        resultados = []
        
        with self.lock:
            for regra in self.regras:
                try:
                    # Verifica se a condição é satisfeita
                    if regra["condicao"](metricas, contexto):
                        # Executa a ação
                        resultado = regra["acao"](metricas, contexto)
                        
                        # Atualiza estatísticas
                        regra["execucoes"] += 1
                        regra["ultima_execucao"] = time.time()
                        if resultado is not None:
                            regra["sucessos"] += 1
                        
                        # Registra execução no histórico
                        self.historico_execucoes.append({
                            "regra": regra["nome"],
                            "timestamp": regra["ultima_execucao"],
                            "resultado": resultado is not None,
                            "contexto": {k: contexto[k] for k in contexto if isinstance(contexto[k], (str, int, float, bool))}
                        })
                        
                        # Adiciona resultado à lista
                        if resultado is not None:
                            resultados.append(resultado)
                    
                except Exception as e:
                    logger.error(f"Erro ao executar regra '{regra['nome']}': {str(e)}")
        
        return resultados
    
    def avaliar_desempenho(self) -> Dict[str, Any]:
        """
        Avalia o desempenho das regras com base no histórico de execuções.
        Retorna estatísticas sobre cada regra.
        """
        with self.lock:
            estatisticas = []
            
            for regra in self.regras:
                taxa_sucesso = regra["sucessos"] / regra["execucoes"] if regra["execucoes"] > 0 else 0
                
                estatisticas.append({
                    "nome": regra["nome"],
                    "execucoes": regra["execucoes"],
                    "sucessos": regra["sucessos"],
                    "taxa_sucesso": taxa_sucesso,
                    "ultima_execucao": regra["ultima_execucao"],
                    "prioridade": regra["prioridade"]
                })
            
            # Análise do histórico recente
            recentes = list(self.historico_execucoes)[-100:]
            regras_recentes = set(e["regra"] for e in recentes)
            
            analise_recente = {
                "total_execucoes": len(recentes),
                "regras_ativas": len(regras_recentes),
                "taxa_sucesso_global": sum(1 for e in recentes if e["resultado"]) / len(recentes) if recentes else 0
            }
            
            return {
                "estatisticas_regras": estatisticas,
                "analise_recente": analise_recente,
                "total_regras": len(self.regras)
            }
    
    def otimizar_prioridades(self):
        """
        Ajusta as prioridades das regras com base no desempenho histórico.
        Regras com maior taxa de sucesso recebem prioridade mais alta.
        """
        with self.lock:
            # Calcula novas prioridades
            for regra in self.regras:
                if regra["execucoes"] > 10:  # Só ajusta regras com histórico suficiente
                    taxa_sucesso = regra["sucessos"] / regra["execucoes"]
                    # Ajusta prioridade mantendo a ordem relativa original
                    nova_prioridade = regra["prioridade"] * (0.8 + 0.4 * taxa_sucesso)
                    regra["prioridade"] = nova_prioridade
            
            # Reordena regras
            self.regras.sort(key=lambda r: r["prioridade"], reverse=True)
            
            logger.info("Prioridades das regras otimizadas com base no desempenho histórico")


class RedeNeuralHierarquica:
    """
    Implementa uma rede neural hierárquica para análise de padrões em múltiplos níveis.
    
    Como uma teia de neurônios artificiais que se estende em dimensões aninhadas,
    cada camada percebe o mundo em uma escala diferente de abstração,
    tecendo significados complexos a partir de sinais elementares.
    """
    def __init__(self, dimensoes_entrada: List[str], camadas_ocultas: List[int] = None):
        self.dimensoes_entrada = dimensoes_entrada
        self.camadas_ocultas = camadas_ocultas or [64, 32, 16]
        self.modelos = {}
        self.preprocessadores = {}
        self.historico_treinamento = {}
        self.lock = threading.Lock()
        
        logger.info(f"RedeNeuralHierarquica inicializada com dimensões: {dimensoes_entrada}")
    
    def _criar_modelo(self, nome: str, dim_entrada: int) -> keras.Model:
        """Cria um modelo de rede neural para uma dimensão específica."""
        modelo = keras.Sequential([
            keras.layers.Dense(self.camadas_ocultas[0], activation='relu', input_shape=(dim_entrada,)),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.3)
        ])
        
        # Adiciona camadas ocultas
        for unidades in self.camadas_ocultas[1:]:
            modelo.add(keras.layers.Dense(unidades, activation='relu'))
            modelo.add(keras.layers.BatchNormalization())
            modelo.add(keras.layers.Dropout(0.3))
        
        # Camada de saída para classificação de anomalias
        modelo.add(keras.layers.Dense(1, activation='sigmoid'))
        
        modelo.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC(), keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        return modelo
    
    def adicionar_modelo(self, nome: str, colunas_entrada: List[str]):
        """
        Adiciona um novo modelo para uma dimensão específica.
        
        Args:
            nome: Nome identificador do modelo
            colunas_entrada: Lista de nomes de colunas/métricas usadas como entrada
        """
        with self.lock:
            if nome in self.modelos:
                logger.warning(f"Modelo '{nome}' já existe e será substituído")
            
            # Cria modelo
            modelo = self._criar_modelo(nome, len(colunas_entrada))
            
            # Armazena modelo e metadados
            self.modelos[nome] = {
                "modelo": modelo,
                "colunas": colunas_entrada,
                "treinado": False,
                "criado_em": time.time()
            }
            
            # Inicializa histórico de treinamento
            self.historico_treinamento[nome] = []
            
            logger.info(f"Modelo '{nome}' adicionado com {len(colunas_entrada)} entradas")
    
    def treinar(self, nome: str, dados_x: np.ndarray, dados_y: np.ndarray, 
               validacao: float = 0.2, epocas: int = 50, batch_size: int = 32):
        """
        Treina um modelo específico com dados fornecidos.
        
        Args:
            nome: Nome do modelo a ser treinado
            dados_x: Matriz de features de entrada
            dados_y: Vetor de labels (0 = normal, 1 = anomalia)
            validacao: Fração dos dados a ser usada para validação
            epocas: Número de épocas de treinamento
            batch_size: Tamanho do batch para treinamento
        
        Returns:
            Histórico de treinamento
        """
        with self.lock:
            if nome not in self.modelos:
                logger.error(f"Modelo '{nome}' não encontrado")
                return None
            
            modelo_info = self.modelos[nome]
            modelo = modelo_info["modelo"]
            
            # Treina o modelo
            historico = modelo.fit(
                dados_x, dados_y,
                validation_split=validacao,
                epochs=epocas,
                batch_size=batch_size,
                verbose=0
            )
            
            # Atualiza status do modelo
            modelo_info["treinado"] = True
            modelo_info["ultima_atualizacao"] = time.time()
            
            # Registra histórico de treinamento
            metricas = {
                "acuracia": float(historico.history['accuracy'][-1]),
                "perda": float(historico.history['loss'][-1]),
                "val_acuracia": float(historico.history['val_accuracy'][-1]),
                "val_perda": float(historico.history['val_loss'][-1])
            }
            
            self.historico_treinamento[nome].append({
                "timestamp": time.time(),
                "epocas": epocas,
                "tamanho_dados": len(dados_x),
                "metricas": metricas
            })
            
            logger.info(f"Modelo '{nome}' treinado com {len(dados_x)} exemplos. Acurácia: {metricas['acuracia']:.4f}")
            
            return historico.history
    
    def detectar_anomalias(self, nome: str, dados: np.ndarray, limiar: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detecta anomalias usando um modelo específico.
        
        Args:
            nome: Nome do modelo a ser usado
            dados: Matriz de features de entrada
            limiar: Limiar de probabilidade para classificação como anomalia
            
        Returns:
            Tuple (previsões binárias, probabilidades)
        """
        with self.lock:
            if nome not in self.modelos:
                logger.error(f"Modelo '{nome}' não encontrado")
                return np.array([]), np.array([])
            
            modelo_info = self.modelos[nome]
            
            if not modelo_info["treinado"]:
                logger.warning(f"Modelo '{nome}' não foi treinado ainda")
                return np.array([]), np.array([])
            
            modelo = modelo_info["modelo"]
            
            # Faz previsões
            probabilidades = modelo.predict(dados, verbose=0)
            previsoes = (probabilidades >= limiar).astype(int)
            
            return previsoes.flatten(), probabilidades.flatten()
    
    def avaliar_modelo(self, nome: str, dados_x: np.ndarray, dados_y: np.ndarray) -> Dict[str, float]:
        """
        Avalia o desempenho de um modelo com dados de teste.
        
        Args:
            nome: Nome do modelo a ser avaliado
            dados_x: Matriz de features de entrada
            dados_y: Vetor de labels (0 = normal, 1 = anomalia)
            
        Returns:
            Dicionário com métricas de avaliação
        """
        with self.lock:
            if nome not in self.modelos:
                logger.error(f"Modelo '{nome}' não encontrado")
                return {}
            
            modelo_info = self.modelos[nome]
            
            if not modelo_info["treinado"]:
                logger.warning(f"Modelo '{nome}' não foi treinado ainda")
                return {}
            
            modelo = modelo_info["modelo"]
            
            # Avalia o modelo
            resultados = modelo.evaluate(dados_x, dados_y, verbose=0)
            
            # Cria dicionário de métricas
            metricas = dict(zip(modelo.metrics_names, resultados))
            
            return {k: float(v) for k, v in metricas.items()}
    
    def salvar_modelo(self, nome: str, diretorio: str):
        """
        Salva um modelo em disco.
        
        Args:
            nome: Nome do modelo a ser salvo
            diretorio: Diretório onde o modelo será salvo
        """
        with self.lock:
            if nome not in self.modelos:
                logger.error(f"Modelo '{nome}' não encontrado")
                return
            
            modelo_info = self.modelos[nome]
            modelo = modelo_info["modelo"]
            
            # Cria diretório se não existir
            os.makedirs(diretorio, exist_ok=True)
            
            # Salva modelo
            caminho_modelo = os.path.join(diretorio, f"{nome}_modelo.h5")
            modelo.save(caminho_modelo)
            
            # Salva metadados
            metadados = {
                "colunas": modelo_info["colunas"],
                "treinado": modelo_info["treinado"],
                "criado_em": modelo_info["criado_em"],
                "ultima_atualizacao": modelo_info.get("ultima_atualizacao"),
                "historico": self.historico_treinamento[nome]
            }
            
            caminho_metadados = os.path.join(diretorio, f"{nome}_metadados.json")
            with open(caminho_metadados, 'w') as f:
                json.dump(metadados, f)
            
            logger.info(f"Modelo '{nome}' salvo em {diretorio}")
    
    def carregar_modelo(self, nome: str, diretorio: str):
        """
        Carrega um modelo do disco.
        
        Args:
            nome: Nome do modelo a ser carregado
            diretorio: Diretório onde o modelo está salvo
        """
        with self.lock:
            # Verifica se arquivos existem
            caminho_modelo = os.path.join(diretorio, f"{nome}_modelo.h5")
            caminho_metadados = os.path.join(diretorio, f"{nome}_metadados.json")
            
            if not os.path.exists(caminho_modelo) or not os.path.exists(caminho_metadados):
                logger.error(f"Arquivos do modelo '{nome}' não encontrados em {diretorio}")
                return
            
            # Carrega metadados
            with open(caminho_metadados, 'r') as f:
                metadados = json.load(f)
            
            # Carrega modelo
            modelo = keras.models.load_model(caminho_modelo)
            
            # Armazena modelo e metadados
            self.modelos[nome] = {
                "modelo": modelo,
                "colunas": metadados["colunas"],
                "treinado": metadados["treinado"],
                "criado_em": metadados["criado_em"],
                "ultima_atualizacao": metadados.get("ultima_atualizacao")
            }
            
            # Carrega histórico de treinamento
            self.historico_treinamento[nome] = metadados.get("historico", [])
            
            logger.info(f"Modelo '{nome}' carregado de {diretorio}")
=======
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
>>>>>>> origin/main

# Inicialização da API e rotas
if __name__ == "__main__":
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
<<<<<<< HEAD
    # Catálogo de padrões de anomalia
    catalogo_anomalias = {}
    
    # Motor de regras
    motor_regras = MotorRegrasEspecialistas()
    
    # Rede neural
    rede_neural = RedeNeuralHierarquica(["throughput", "erros", "latencia", "recursos"])
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "timestamp": time.time()})
    
    @app.route('/ready', methods=['GET'])
    def ready_check():
        # Verifica se os componentes essenciais estão inicializados
        if not motor_regras or not rede_neural:
=======
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
>>>>>>> origin/main
            return jsonify({"status": "not ready", "reason": "Components not initialized"}), 503
        return jsonify({"status": "ready", "timestamp": time.time()})
    
    @app.route('/api/diagnosticos', methods=['POST'])
<<<<<<< HEAD
    def criar_diagnostico():
        try:
            data = request.json
            
            # Obtém métricas do monitoramento se não fornecidas
            if 'metricas' not in data:
                metricas = obter_metricas_do_monitoramento()
            else:
                metricas = []
                for metrica_data in data['metricas']:
                    metrica = MetricaDimensional(
                        id=metrica_data["id"],
                        nome=metrica_data["nome"],
                        valor=metrica_data["valor"],
                        timestamp=metrica_data["timestamp"],
                        dimensao=metrica_data["dimensao"],
                        unidade=metrica_data["unidade"],
                        tags=metrica_data.get("tags", {}),
                        metadados=metrica_data.get("metadados", {})
                    )
                    metricas.append(metrica)
            
            # Contexto para diagnóstico
            contexto = data.get('contexto', {})
            
            # Detecta anomalias
            anomalias_detectadas = []
            
            for padrao_id, padrao in catalogo_anomalias.items():
                corresponde, confianca = padrao.corresponde(metricas, contexto)
                if corresponde:
                    anomalias_detectadas.append((padrao, confianca))
            
            # Cria diagnóstico
            diagnostico_id = f"diag_{int(time.time())}_{random.randint(1000, 9999)}"
            
            diagnostico = Diagnostico(
                id=diagnostico_id,
                timestamp=time.time(),
                anomalias_detectadas=anomalias_detectadas,
                metricas_analisadas=[m.id for m in metricas],
                contexto=contexto
            )
            
            # Executa regras para enriquecer diagnóstico
            resultados_regras = motor_regras.executar(metricas, contexto)
            
            # Adiciona recomendações das regras
            for resultado in resultados_regras:
                if isinstance(resultado, str):
                    diagnostico.recomendacoes.append(resultado)
                elif isinstance(resultado, dict) and "recomendacao" in resultado:
                    diagnostico.recomendacoes.append(resultado["recomendacao"])
            
            return jsonify(diagnostico.to_dict()), 200
            
        except Exception as e:
            logger.error(f"Erro ao criar diagnóstico: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/diagnosticos/<diagnostico_id>', methods=['GET'])
    def obter_diagnostico(diagnostico_id):
        # Implementação simplificada - em um sistema real, buscaria do banco de dados
        return jsonify({
            "id": diagnostico_id,
            "timestamp": time.time(),
            "anomalias_detectadas": [],
            "metricas_analisadas": [],
            "causa_raiz": None,
            "confianca": 0.0,
            "recomendacoes": [],
            "contexto": {}
        }), 200
    
=======
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
    
>>>>>>> origin/main
    # Inicia o servidor
    app.run(host='0.0.0.0', port=8080)
