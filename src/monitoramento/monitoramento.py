<<<<<<< HEAD
# Módulo de Monitoramento Multidimensional

import time
import threading
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
import logging
import json
from datetime import datetime
from fastapi import FastAPI
import random

# Configuração do FastAPI
app = FastAPI(title="Monitoramento Multidimensional")
=======
"""
Módulo de Monitoramento Multidimensional

Este módulo é responsável por coletar e analisar métricas em múltiplas dimensões do sistema.
Ele integra:
1. Coleta de métricas de diferentes fontes
2. Análise de tendências e padrões
3. Detecção de anomalias
4. Geração de alertas

O módulo utiliza:
- Prometheus para métricas de sistema
- Elasticsearch para logs
- Grafana para visualização
- AlertManager para notificações
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
>>>>>>> origin/main

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("MonitoramentoMultidimensional")

<<<<<<< HEAD
# Estruturas de dados para métricas
@dataclass
class MetricaDimensional:
    """
    Estrutura de dados para métricas multidimensionais com contexto temporal e espacial.
    
    Como cristais de dados que capturam a essência do sistema,
    cada métrica é um prisma que refrata a realidade operacional
    em dimensões que transcendem o óbvio.
=======
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
>>>>>>> origin/main
    """
    id: str
    nome: str
    valor: float
    timestamp: float
    dimensao: str
    unidade: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadados: Dict[str, Any] = field(default_factory=dict)
<<<<<<< HEAD
    contexto: Dict[str, Any] = field(default_factory=dict)
    confianca: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a métrica para formato de dicionário."""
=======
    
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
            "timestamp": self.timestamp,
            "dimensao": self.dimensao,
            "unidade": self.unidade,
            "tags": self.tags,
<<<<<<< HEAD
            "metadados": self.metadados,
            "contexto": self.contexto,
            "confianca": self.confianca
=======
            "metadados": self.metadados
>>>>>>> origin/main
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricaDimensional':
<<<<<<< HEAD
        """Cria uma instância de métrica a partir de um dicionário."""
=======
        """
        Cria uma instância de métrica a partir de um dicionário.
        
        Args:
            data: Dicionário com dados da métrica
            
        Returns:
            MetricaDimensional: Instância criada
        """
>>>>>>> origin/main
        return cls(
            id=data["id"],
            nome=data["nome"],
            valor=data["valor"],
            timestamp=data["timestamp"],
            dimensao=data["dimensao"],
            unidade=data["unidade"],
            tags=data.get("tags", {}),
<<<<<<< HEAD
            metadados=data.get("metadados", {}),
            contexto=data.get("contexto", {}),
            confianca=data.get("confianca", 1.0)
        )

# Armazenamento de métricas em memória
metricas_store: List[MetricaDimensional] = []

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/ready")
async def ready_check():
    return {"status": "ready", "timestamp": time.time()}

@app.get("/api/metricas")
async def get_metricas():
    # Se não houver métricas, gerar algumas de exemplo
    if not metricas_store:
        metricas_store.extend([
            MetricaDimensional(
                id=f"metric_{i}",
                nome=nome,
                valor=random.uniform(0, 100),
                timestamp=time.time(),
                dimensao=dim,
                unidade=unidade,
                tags={"ambiente": "producao"},
                metadados={"fonte": "simulador"}
            )
            for i, (nome, dim, unidade) in enumerate([
                ("cpu_usage", "recursos", "percentual"),
                ("memory_usage", "recursos", "percentual"),
                ("latency", "performance", "ms"),
                ("throughput", "performance", "rps"),
                ("error_rate", "qualidade", "percentual")
            ])
        ])
    
    return [metric.__dict__ for metric in metricas_store]

@app.get("/api/metricas/{metrica_id}")
async def get_metrica(metrica_id: str):
    for metrica in metricas_store:
        if metrica.id == metrica_id:
            return metrica.__dict__
    return {"error": "Métrica não encontrada"}, 404

class ColetorBase:
    """
    Classe base para todos os coletores de métricas.
    
    Como sentinelas silenciosas que observam o fluxo do tempo,
    os coletores capturam sinais sutis nas correntes de dados,
    testemunhas imparciais do comportamento do sistema.
    """
    def __init__(self, nome: str, intervalo: float = 1.0):
        self.nome = nome
        self.intervalo = intervalo
        self.ativo = False
        self.thread = None
        self.callbacks = []
        logger.info(f"Coletor {self.nome} inicializado com intervalo de {self.intervalo}s")
    
    def iniciar(self):
        """Inicia a coleta de métricas em uma thread separada."""
        if self.ativo:
            logger.warning(f"Coletor {self.nome} já está ativo")
            return
        
        self.ativo = True
        self.thread = threading.Thread(target=self._loop_coleta, daemon=True)
        self.thread.start()
        logger.info(f"Coletor {self.nome} iniciado")
    
    def parar(self):
        """Para a coleta de métricas."""
        self.ativo = False
        if self.thread:
            self.thread.join(timeout=2*self.intervalo)
        logger.info(f"Coletor {self.nome} parado")
    
    def registrar_callback(self, callback):
        """Registra uma função de callback para receber métricas coletadas."""
        self.callbacks.append(callback)
        logger.debug(f"Callback registrado para coletor {self.nome}")
    
    def _loop_coleta(self):
        """Loop principal de coleta que executa em uma thread separada."""
        while self.ativo:
            try:
                metricas = self.coletar()
                for metrica in metricas:
                    for callback in self.callbacks:
                        callback(metrica)
            except Exception as e:
                logger.error(f"Erro na coleta de {self.nome}: {str(e)}")
            
            time.sleep(self.intervalo)
    
    def coletar(self) -> List[MetricaDimensional]:
        """
        Método abstrato para coleta de métricas.
        Deve ser implementado pelas subclasses.
        """
        raise NotImplementedError("Subclasses devem implementar o método coletar()")


class ColetorThroughput(ColetorBase):
    """
    Coletor especializado em métricas de throughput operacional.
    
    Como um contador de batimentos cardíacos do sistema,
    mede o pulso das operações, o ritmo vital
    que sustenta o fluxo de processamento.
    """
    def __init__(self, nome: str, intervalo: float = 1.0, janela_media: int = 10):
        super().__init__(nome, intervalo)
        self.janela_media = janela_media
        self.historico = deque(maxlen=janela_media)
        self.contador = 0
        self.ultimo_timestamp = time.time()
    
    def registrar_operacao(self, quantidade: int = 1, contexto: Dict[str, Any] = None):
        """Registra a ocorrência de operações para cálculo de throughput."""
        self.contador += quantidade
    
    def coletar(self) -> List[MetricaDimensional]:
        """Coleta métricas de throughput baseadas no contador de operações."""
        agora = time.time()
        delta_t = agora - self.ultimo_timestamp
        
        if delta_t > 0:
            taxa = self.contador / delta_t
            self.historico.append(taxa)
            media_movel = sum(self.historico) / len(self.historico)
            
            # Reset para próxima janela
            self.contador = 0
            self.ultimo_timestamp = agora
            
            # Criação das métricas
            metrica_instantanea = MetricaDimensional(
                id=f"{self.nome}_instantaneo",
                nome=f"{self.nome}_instantaneo",
                valor=taxa,
                timestamp=agora,
                dimensao="throughput",
                unidade="ops/s"
            )
            
            metrica_media = MetricaDimensional(
                id=f"{self.nome}_media_movel",
                nome=f"{self.nome}_media_movel",
                valor=media_movel,
                timestamp=agora,
                dimensao="throughput",
                unidade="ops/s"
            )
            
            return [metrica_instantanea, metrica_media]
        
        return []


class ColetorErros(ColetorBase):
    """
    Coletor especializado em métricas de erros contextuais.
    
    Como um arqueólogo de falhas que escava nas camadas do tempo,
    cataloga os vestígios de exceções e anomalias,
    preservando o contexto em que ocorreram.
    """
    def __init__(self, nome: str, intervalo: float = 1.0, categorias: List[str] = None):
        super().__init__(nome, intervalo)
        self.categorias = categorias or ["geral"]
        self.contadores = {cat: 0 for cat in self.categorias}
        self.contextos = {cat: [] for cat in self.categorias}
        self.lock = threading.Lock()
    
    def registrar_erro(self, categoria: str = "geral", contexto: Dict[str, Any] = None):
        """Registra a ocorrência de um erro com seu contexto."""
        with self.lock:
            if categoria not in self.contadores:
                self.contadores[categoria] = 0
                self.contextos[categoria] = []
            
            self.contadores[categoria] += 1
            if contexto:
                self.contextos[categoria].append(contexto)
    
    def coletar(self) -> List[MetricaDimensional]:
        """Coleta métricas de erros baseadas nos contadores por categoria."""
        metricas = []
        agora = time.time()
        
        with self.lock:
            for categoria, contador in self.contadores.items():
                # Contexto agregado para esta categoria
                contexto_agregado = {
                    "categoria": categoria,
                    "exemplos": self.contextos[categoria][-5:] if self.contextos[categoria] else []
                }
                
                metrica = MetricaDimensional(
                    id=f"{self.nome}_{categoria}",
                    nome=f"{self.nome}_{categoria}",
                    valor=contador,
                    timestamp=agora,
                    dimensao="erros",
                    unidade="contagem"
                )
                
                metricas.append(metrica)
                
                # Reset dos contadores após coleta
                self.contadores[categoria] = 0
                self.contextos[categoria] = []
        
        return metricas


class ColetorLatencia(ColetorBase):
    """
    Coletor especializado em métricas de latência cognitiva.
    
    Como um cronometrista do pensamento artificial,
    mede os intervalos entre estímulo e resposta,
    o tempo de viagem das ideias através do labirinto neural.
    """
    def __init__(self, nome: str, intervalo: float = 1.0, percentis: List[float] = None):
        super().__init__(nome, intervalo)
        self.percentis = percentis or [50, 90, 95, 99]
        self.medicoes = []
        self.lock = threading.Lock()
    
    def registrar_latencia(self, valor: float, contexto: Dict[str, Any] = None):
        """Registra uma medição de latência com seu contexto."""
        with self.lock:
            self.medicoes.append((valor, contexto or {}))
    
    def coletar(self) -> List[MetricaDimensional]:
        """Coleta métricas de latência baseadas nas medições registradas."""
        metricas = []
        agora = time.time()
        
        with self.lock:
            if not self.medicoes:
                return []
            
            # Extrai valores de latência
            valores = [m[0] for m in self.medicoes]
            contextos = [m[1] for m in self.medicoes]
            
            # Calcula estatísticas
            media = np.mean(valores)
            mediana = np.median(valores)
            percentis_calc = np.percentile(valores, self.percentis)
            
            # Cria métricas para média e mediana
            metrica_media = MetricaDimensional(
                id=f"{self.nome}_media",
                nome=f"{self.nome}_media",
                valor=media,
                timestamp=agora,
                dimensao="latencia",
                unidade="ms"
            )
            
            metrica_mediana = MetricaDimensional(
                id=f"{self.nome}_mediana",
                nome=f"{self.nome}_mediana",
                valor=mediana,
                timestamp=agora,
                dimensao="latencia",
                unidade="ms"
            )
            
            metricas.extend([metrica_media, metrica_mediana])
            
            # Cria métricas para percentis
            for i, p in enumerate(self.percentis):
                metrica_percentil = MetricaDimensional(
                    id=f"{self.nome}_p{p}",
                    nome=f"{self.nome}_p{p}",
                    valor=percentis_calc[i],
                    timestamp=agora,
                    dimensao="latencia",
                    unidade="ms"
                )
                metricas.append(metrica_percentil)
            
            # Reset das medições após coleta
            self.medicoes = []
        
        return metricas


class ColetorRecursosFractais(ColetorBase):
    """
    Coletor especializado em métricas de consumo de recursos fractais.
    
    Como um cartógrafo de paisagens computacionais,
    mapeia o terreno multidimensional dos recursos,
    revelando padrões auto-similares em diferentes escalas.
    """
    def __init__(self, nome: str, intervalo: float = 1.0, dimensoes: List[str] = None):
        super().__init__(nome, intervalo)
        self.dimensoes = dimensoes or ["cpu", "memoria", "io", "rede"]
        self.leituras = {dim: [] for dim in self.dimensoes}
        self.escalas = [0.1, 1.0, 10.0]  # Escalas de tempo para análise fractal
    
    def registrar_consumo(self, dimensao: str, valor: float, escala: float = 1.0, contexto: Dict[str, Any] = None):
        """Registra uma medição de consumo de recurso com escala e contexto."""
        if dimensao in self.dimensoes:
            self.leituras[dimensao].append((valor, escala, contexto or {}))
    
    def _calcular_dimensao_fractal(self, valores: List[float]) -> float:
        """
        Calcula uma aproximação da dimensão fractal usando o método box-counting.
        Esta é uma implementação simplificada para demonstração.
        """
        if len(valores) < 10:
            return 1.0  # Valor padrão para poucas amostras
        
        # Normaliza valores
        valores_norm = np.array(valores) / max(valores)
        
        # Calcula dimensão fractal aproximada
        steps = min(5, len(valores) // 2)
        counts = []
        scales = []
        
        for step in range(1, steps + 1):
            box_size = 1.0 / step
            boxes = np.ceil(valores_norm / box_size)
            unique_boxes = len(np.unique(boxes))
            counts.append(unique_boxes)
            scales.append(box_size)
        
        if len(counts) < 2:
            return 1.0
        
        # Regressão log-log
        log_counts = np.log(counts)
        log_scales = np.log(scales)
        
        # Calcula inclinação (dimensão fractal)
        slope, _ = np.polyfit(log_scales, log_counts, 1)
        return abs(slope)
    
    def coletar(self) -> List[MetricaDimensional]:
        """Coleta métricas de consumo de recursos com análise fractal."""
        metricas = []
        agora = time.time()
        
        for dimensao in self.dimensoes:
            if not self.leituras[dimensao]:
                continue
            
            # Extrai valores por escala
            por_escala = {}
            for valor, escala, _ in self.leituras[dimensao]:
                if escala not in por_escala:
                    por_escala[escala] = []
                por_escala[escala].append(valor)
            
            # Calcula métricas por escala
            for escala, valores in por_escala.items():
                media = np.mean(valores)
                variacao = np.std(valores) if len(valores) > 1 else 0
                
                metrica = MetricaDimensional(
                    id=f"{self.nome}_{dimensao}_escala_{escala}",
                    nome=f"{self.nome}_{dimensao}_escala_{escala}",
                    valor=media,
                    timestamp=agora,
                    dimensao="recursos",
                    unidade="percentual"
                )
                metricas.append(metrica)
            
            # Calcula dimensão fractal se houver dados suficientes
            todos_valores = [v for v, _, _ in self.leituras[dimensao]]
            if len(todos_valores) >= 10:
                dim_fractal = self._calcular_dimensao_fractal(todos_valores)
                
                metrica_fractal = MetricaDimensional(
                    id=f"{self.nome}_{dimensao}_dimensao_fractal",
                    nome=f"{self.nome}_{dimensao}_dimensao_fractal",
                    valor=dim_fractal,
                    timestamp=agora,
                    dimensao="fractal",
                    unidade="dimensao"
                )
                metricas.append(metrica_fractal)
            
            # Reset das leituras após coleta
            self.leituras[dimensao] = []
        
        return metricas


class AgregadorTemporal:
    """
    Agrega métricas em diferentes janelas temporais.
    
    Como um tecelão do tempo que entrelaça os fios dos eventos,
    cria padrões visíveis nas tramas do passado,
    revelando tendências ocultas nas dobras temporais.
    """
    def __init__(self, janelas: List[int] = None):
        self.janelas = janelas or [60, 300, 900, 3600]  # segundos
        self.metricas = {}  # Dict[str, Dict[int, List[MetricaDimensional]]]
        self.lock = threading.Lock()
        logger.info(f"AgregadorTemporal inicializado com janelas: {self.janelas}")
    
    def adicionar_metrica(self, metrica: MetricaDimensional):
        """
        Adiciona uma métrica às janelas temporais.
        
        Args:
            metrica: Métrica a ser adicionada
        """
        with self.lock:
            nome_chave = f"{metrica.dimensao}:{metrica.nome}"
            
            if nome_chave not in self.metricas:
                self.metricas[nome_chave] = {janela: [] for janela in self.janelas}
            
            # Adiciona a métrica a cada janela
            agora = time.time()
            for janela in self.janelas:
                # Remove métricas antigas
                self.metricas[nome_chave][janela] = [
                    m for m in self.metricas[nome_chave][janela]
                    if agora - m.timestamp <= janela
                ]
                
                # Adiciona nova métrica
                self.metricas[nome_chave][janela].append(metrica)
    
    def obter_metricas_janela(self, dimensao: str, nome: str, janela: int) -> List[MetricaDimensional]:
        """
        Obtém métricas de uma janela temporal específica.
        
        Args:
            dimensao: Dimensão da métrica
            nome: Nome da métrica
            janela: Tamanho da janela em segundos
            
        Returns:
            Lista de métricas na janela
        """
        with self.lock:
            nome_chave = f"{dimensao}:{nome}"
            
            if nome_chave not in self.metricas or janela not in self.metricas[nome_chave]:
                return []
            
            # Filtra métricas dentro da janela
            agora = time.time()
            return [
                m for m in self.metricas[nome_chave][janela]
                if agora - m.timestamp <= janela
            ]
    
    def calcular_estatisticas(self, dimensao: str, nome: str, janela: int) -> Dict[str, float]:
        """
        Calcula estatísticas para uma métrica em uma janela temporal.
        
        Args:
            dimensao: Dimensão da métrica
            nome: Nome da métrica
            janela: Tamanho da janela em segundos
            
        Returns:
            Dicionário com estatísticas (média, mediana, min, max, etc.)
        """
        metricas = self.obter_metricas_janela(dimensao, nome, janela)
        
        if not metricas:
            return {
                "contagem": 0,
                "media": None,
                "mediana": None,
                "min": None,
                "max": None,
                "desvio_padrao": None
            }
        
        valores = [m.valor for m in metricas]
        
        return {
            "contagem": len(valores),
            "media": np.mean(valores),
            "mediana": np.median(valores),
            "min": min(valores),
            "max": max(valores),
            "desvio_padrao": np.std(valores) if len(valores) > 1 else 0
        }
    
    def detectar_tendencia(self, dimensao: str, nome: str, janela: int) -> Dict[str, Any]:
        """
        Detecta tendência para uma métrica em uma janela temporal.
        
        Args:
            dimensao: Dimensão da métrica
            nome: Nome da métrica
            janela: Tamanho da janela em segundos
            
        Returns:
            Dicionário com informações de tendência
        """
        metricas = self.obter_metricas_janela(dimensao, nome, janela)
        
        if len(metricas) < 3:
            return {
                "direcao": "estavel",
                "inclinacao": 0,
                "confianca": 0,
                "amostras": len(metricas)
            }
        
        # Ordena por timestamp
        metricas.sort(key=lambda m: m.timestamp)
        
        # Extrai valores e timestamps
        valores = np.array([m.valor for m in metricas])
        timestamps = np.array([m.timestamp for m in metricas])
        
        # Normaliza timestamps para começar de 0
        timestamps = timestamps - timestamps[0]
        
        # Regressão linear
        if len(timestamps) > 1:
            inclinacao, intercepto = np.polyfit(timestamps, valores, 1)
            
            # Calcula valores previstos
            valores_previstos = inclinacao * timestamps + intercepto
            
            # Calcula erro quadrático médio
            mse = np.mean((valores - valores_previstos) ** 2)
            
            # Calcula variância total
            variancia_total = np.var(valores)
            
            # Calcula R² (coeficiente de determinação)
            r2 = 1 - (mse / variancia_total) if variancia_total > 0 else 0
            
            # Determina direção
            if abs(inclinacao) < 0.001 or r2 < 0.3:
                direcao = "estavel"
            elif inclinacao > 0:
                direcao = "crescente"
            else:
                direcao = "decrescente"
            
            return {
                "direcao": direcao,
                "inclinacao": inclinacao,
                "confianca": r2,
                "amostras": len(metricas)
            }
        
        return {
            "direcao": "estavel",
            "inclinacao": 0,
            "confianca": 0,
            "amostras": len(metricas)
        }


class ProcessadorContexto:
    """
    Enriquece dados brutos com informações contextuais.
    
    Como um alquimista de dados que transmuta sinais em significados,
    destila a essência contextual das métricas brutas,
    revelando a narrativa oculta nos números.
    """
    def __init__(self):
        self.contextos_globais = {}
        self.processadores = {}
        self.lock = threading.Lock()
        logger.info("ProcessadorContexto inicializado")
    
    def adicionar_contexto_global(self, chave: str, valor: Any):
        """
        Adiciona uma informação ao contexto global.
        
        Args:
            chave: Chave do contexto
            valor: Valor do contexto
        """
        with self.lock:
            self.contextos_globais[chave] = valor
    
    def registrar_processador(self, dimensao: str, processador: Callable[[MetricaDimensional, Dict[str, Any]], Dict[str, Any]]):
        """
        Registra um processador de contexto para uma dimensão específica.
        
        Args:
            dimensao: Dimensão da métrica
            processador: Função que recebe (metrica, contexto_global) e retorna contexto adicional
        """
        with self.lock:
            if dimensao not in self.processadores:
                self.processadores[dimensao] = []
            
            self.processadores[dimensao].append(processador)
            logger.info(f"Processador de contexto registrado para dimensão '{dimensao}'")
    
    def processar(self, metrica: MetricaDimensional) -> MetricaDimensional:
        """
        Processa uma métrica, enriquecendo seu contexto.
        
        Args:
            metrica: Métrica a ser processada
            
        Returns:
            Métrica com contexto enriquecido
        """
        with self.lock:
            # Cria cópia da métrica para não modificar a original
            nova_metrica = MetricaDimensional(
                id=metrica.id,
                nome=metrica.nome,
                valor=metrica.valor,
                timestamp=metrica.timestamp,
                dimensao=metrica.dimensao,
                unidade=metrica.unidade,
                contexto=metrica.contexto.copy(),
                confianca=metrica.confianca
            )
            
            # Adiciona contexto global
            for chave, valor in self.contextos_globais.items():
                if chave not in nova_metrica.contexto:
                    nova_metrica.contexto[chave] = valor
            
            # Aplica processadores específicos da dimensão
            if metrica.dimensao in self.processadores:
                for processador in self.processadores[metrica.dimensao]:
                    try:
                        contexto_adicional = processador(metrica, self.contextos_globais)
                        if contexto_adicional:
                            nova_metrica.contexto.update(contexto_adicional)
                    except Exception as e:
                        logger.error(f"Erro no processador de contexto: {str(e)}")
            
            return nova_metrica


class AnalisadorFluxoContínuo:
    """
    Processa streams de dados em tempo real.
    
    Como um observador atento no rio de dados que flui incessantemente,
    identifica padrões efêmeros nas correntes de informação,
    capturando insights antes que se dissolvam no oceano do tempo.
    """
    def __init__(self, tamanho_janela: int = 100):
        self.janela_deslizante = {}  # Dict[str, deque]
        self.callbacks = {}  # Dict[str, List[Callable]]
        self.tamanho_janela = tamanho_janela
        self.lock = threading.Lock()
        logger.info(f"AnalisadorFluxoContínuo inicializado com janela de {tamanho_janela}")
    
    def registrar_callback(self, dimensao: str, callback: Callable[[List[MetricaDimensional]], None]):
        """
        Registra um callback para processar métricas de uma dimensão específica.
        
        Args:
            dimensao: Dimensão da métrica
            callback: Função que recebe lista de métricas e processa
        """
        with self.lock:
            if dimensao not in self.callbacks:
                self.callbacks[dimensao] = []
            
            self.callbacks[dimensao].append(callback)
            logger.info(f"Callback registrado para dimensão '{dimensao}'")
    
    def processar_metrica(self, metrica: MetricaDimensional):
        """
        Processa uma métrica, adicionando-a à janela deslizante e notificando callbacks.
        
        Args:
            metrica: Métrica a ser processada
        """
        with self.lock:
            dimensao = metrica.dimensao
            
            # Inicializa janela se não existir
            if dimensao not in self.janela_deslizante:
                self.janela_deslizante[dimensao] = deque(maxlen=self.tamanho_janela)
            
            # Adiciona métrica à janela
            self.janela_deslizante[dimensao].append(metrica)
            
            # Notifica callbacks
            if dimensao in self.callbacks:
                janela_atual = list(self.janela_deslizante[dimensao])
                for callback in self.callbacks[dimensao]:
                    try:
                        callback(janela_atual)
                    except Exception as e:
                        logger.error(f"Erro no callback de fluxo contínuo: {str(e)}")
    
    def obter_janela(self, dimensao: str) -> List[MetricaDimensional]:
        """
        Obtém a janela atual de métricas para uma dimensão.
        
        Args:
            dimensao: Dimensão da métrica
            
        Returns:
            Lista de métricas na janela
        """
        with self.lock:
            if dimensao not in self.janela_deslizante:
                return []
            
            return list(self.janela_deslizante[dimensao])
    
    def calcular_estatisticas_janela(self, dimensao: str) -> Dict[str, Dict[str, Any]]:
        """
        Calcula estatísticas para todas as métricas na janela de uma dimensão.
        
        Args:
            dimensao: Dimensão da métrica
            
        Returns:
            Dicionário com estatísticas por nome de métrica
        """
        janela = self.obter_janela(dimensao)
        
        if not janela:
            return {}
        
        # Agrupa por nome
        por_nome = {}
        for metrica in janela:
            if metrica.nome not in por_nome:
                por_nome[metrica.nome] = []
            por_nome[metrica.nome].append(metrica)
        
        # Calcula estatísticas por nome
        estatisticas = {}
        for nome, metricas in por_nome.items():
            valores = [m.valor for m in metricas]
            
            estatisticas[nome] = {
                "contagem": len(valores),
                "media": np.mean(valores),
                "mediana": np.median(valores),
                "min": min(valores),
                "max": max(valores),
                "desvio_padrao": np.std(valores) if len(valores) > 1 else 0,
                "ultima_atualizacao": max(m.timestamp for m in metricas)
            }
        
        return estatisticas


# Exemplo de uso
if __name__ == "__main__":
    import uvicorn
    
    # Inicializa os coletores
    coletor_throughput = ColetorThroughput("api_requests", intervalo=5.0)
    coletor_erros = ColetorErros("api_errors", intervalo=5.0)
    coletor_latencia = ColetorLatencia("api_latencia", intervalo=5.0)
    
    # Inicia os coletores
    logger.info("Módulo random importado com sucesso")
    logger.info(f"Coletor {coletor_throughput.nome} inicializado com intervalo de {coletor_throughput.intervalo}s")
    logger.info(f"Coletor {coletor_erros.nome} inicializado com intervalo de {coletor_erros.intervalo}s")
    logger.info(f"Coletor {coletor_latencia.nome} inicializado com intervalo de {coletor_latencia.intervalo}s")
    
    coletor_throughput.iniciar()
    coletor_erros.iniciar()
    coletor_latencia.iniciar()
    
    # Registra algumas operações para teste
    logger.info("Tentando registrar operação com random.randint")
    valor = random.randint(1, 10)
    logger.info(f"Valor gerado: {valor}")
    coletor_throughput.registrar_operacao(valor)
    
    # Inicia o servidor
    uvicorn.run(app, host="0.0.0.0", port=8080)
=======
            metadados=data.get("metadados", {})
        )

class DimensaoMonitoramento(Enum):
    """
    Enumeração das dimensões de monitoramento.
    
    PERFORMANCE: Métricas de desempenho
    DISPONIBILIDADE: Métricas de disponibilidade
    SEGURANCA: Métricas de segurança
    CUSTO: Métricas de custo
    QUALIDADE: Métricas de qualidade
    """
    PERFORMANCE = auto()
    DISPONIBILIDADE = auto()
    SEGURANCA = auto()
    CUSTO = auto()
    QUALIDADE = auto()

class ColetorMetricas:
    """
    Coleta métricas de diferentes fontes do sistema.
    
    Responsabilidades:
    1. Coletar métricas de diferentes fontes
    2. Normalizar dados coletados
    3. Validar métricas
    4. Armazenar dados coletados
    """
    def __init__(self):
        self.metricas = defaultdict(list)
        self.lock = threading.Lock()
        self.ultima_coleta = 0
        logger.info("ColetorMetricas inicializado")
    
    @log_operacao_critica
    def coletar_metricas(self) -> List[MetricaDimensional]:
        """
        Coleta métricas de todas as fontes configuradas.
        
        Returns:
            List[MetricaDimensional]: Lista de métricas coletadas
        """
        metricas = []
        
        # Coleta métricas de performance
        metricas.extend(self._coletar_metricas_performance())
        
        # Coleta métricas de disponibilidade
        metricas.extend(self._coletar_metricas_disponibilidade())
        
        # Coleta métricas de segurança
        metricas.extend(self._coletar_metricas_seguranca())
        
        # Coleta métricas de custo
        metricas.extend(self._coletar_metricas_custo())
        
        # Coleta métricas de qualidade
        metricas.extend(self._coletar_metricas_qualidade())
        
        # Armazena métricas
        with self.lock:
            for metrica in metricas:
                self.metricas[metrica.dimensao].append(metrica)
            
            # Limpa métricas antigas
            self._limpar_metricas_antigas()
            
            self.ultima_coleta = time.time()
        
        return metricas
    
    def _coletar_metricas_performance(self) -> List[MetricaDimensional]:
        """
        Coleta métricas de performance.
        
        Returns:
            List[MetricaDimensional]: Métricas de performance
        """
        metricas = []
        
        # CPU
        cpu_usage = self._obter_metrica_prometheus('cpu_usage')
        if cpu_usage is not None:
            metricas.append(MetricaDimensional(
                id=f"cpu_usage_{int(time.time())}",
                nome="CPU Usage",
                valor=cpu_usage,
                timestamp=time.time(),
                dimensao=DimensaoMonitoramento.PERFORMANCE.name,
                unidade="%"
            ))
        
        # Memory
        memory_usage = self._obter_metrica_prometheus('memory_usage')
        if memory_usage is not None:
            metricas.append(MetricaDimensional(
                id=f"memory_usage_{int(time.time())}",
                nome="Memory Usage",
                valor=memory_usage,
                timestamp=time.time(),
                dimensao=DimensaoMonitoramento.PERFORMANCE.name,
                unidade="%"
            ))
        
        # Latência
        latency = self._obter_metrica_prometheus('request_latency')
        if latency is not None:
            metricas.append(MetricaDimensional(
                id=f"latency_{int(time.time())}",
                nome="Request Latency",
                valor=latency,
                timestamp=time.time(),
                dimensao=DimensaoMonitoramento.PERFORMANCE.name,
                unidade="ms"
            ))
        
        return metricas

    def _coletar_metricas_disponibilidade(self) -> List[MetricaDimensional]:
        """
        Coleta métricas de disponibilidade.
        
        Returns:
            List[MetricaDimensional]: Métricas de disponibilidade
        """
        metricas = []
        
        # Uptime
        uptime = self._obter_metrica_prometheus('service_uptime')
        if uptime is not None:
            metricas.append(MetricaDimensional(
                id=f"uptime_{int(time.time())}",
                nome="Service Uptime",
                valor=uptime,
                timestamp=time.time(),
                dimensao=DimensaoMonitoramento.DISPONIBILIDADE.name,
                unidade="%"
            ))
        
        # Erros
        error_rate = self._obter_metrica_prometheus('error_rate')
        if error_rate is not None:
            metricas.append(MetricaDimensional(
                id=f"error_rate_{int(time.time())}",
                nome="Error Rate",
                valor=error_rate,
                timestamp=time.time(),
                dimensao=DimensaoMonitoramento.DISPONIBILIDADE.name,
                unidade="%"
            ))
        
        return metricas
    
    def _coletar_metricas_seguranca(self) -> List[MetricaDimensional]:
        """
        Coleta métricas de segurança.
        
        Returns:
            List[MetricaDimensional]: Métricas de segurança
        """
        metricas = []
        
        # Tentativas de login
        login_attempts = self._obter_metrica_prometheus('failed_login_attempts')
        if login_attempts is not None:
            metricas.append(MetricaDimensional(
                id=f"login_attempts_{int(time.time())}",
                nome="Failed Login Attempts",
                valor=login_attempts,
                timestamp=time.time(),
                dimensao=DimensaoMonitoramento.SEGURANCA.name,
                unidade="count"
            ))
        
        # Vulnerabilidades
        vulnerabilities = self._obter_metrica_prometheus('security_vulnerabilities')
        if vulnerabilities is not None:
            metricas.append(MetricaDimensional(
                id=f"vulnerabilities_{int(time.time())}",
                nome="Security Vulnerabilities",
                valor=vulnerabilities,
                timestamp=time.time(),
                dimensao=DimensaoMonitoramento.SEGURANCA.name,
                unidade="count"
            ))
        
        return metricas

    def _coletar_metricas_custo(self) -> List[MetricaDimensional]:
        """
        Coleta métricas de custo.
        
        Returns:
            List[MetricaDimensional]: Métricas de custo
        """
        metricas = []
        
        # Custo de infraestrutura
        infra_cost = self._obter_metrica_prometheus('infrastructure_cost')
        if infra_cost is not None:
            metricas.append(MetricaDimensional(
                id=f"infra_cost_{int(time.time())}",
                nome="Infrastructure Cost",
                valor=infra_cost,
                timestamp=time.time(),
                dimensao=DimensaoMonitoramento.CUSTO.name,
                unidade="USD"
            ))
        
        # Custo de operação
        op_cost = self._obter_metrica_prometheus('operational_cost')
        if op_cost is not None:
            metricas.append(MetricaDimensional(
                id=f"op_cost_{int(time.time())}",
                nome="Operational Cost",
                valor=op_cost,
                timestamp=time.time(),
                dimensao=DimensaoMonitoramento.CUSTO.name,
                unidade="USD"
            ))
        
        return metricas
    
    def _coletar_metricas_qualidade(self) -> List[MetricaDimensional]:
        """
        Coleta métricas de qualidade.
        
        Returns:
            List[MetricaDimensional]: Métricas de qualidade
        """
        metricas = []
        
        # Cobertura de testes
        test_coverage = self._obter_metrica_prometheus('test_coverage')
        if test_coverage is not None:
            metricas.append(MetricaDimensional(
                id=f"test_coverage_{int(time.time())}",
                nome="Test Coverage",
                valor=test_coverage,
                timestamp=time.time(),
                dimensao=DimensaoMonitoramento.QUALIDADE.name,
                unidade="%"
            ))
        
        # Qualidade do código
        code_quality = self._obter_metrica_prometheus('code_quality_score')
        if code_quality is not None:
            metricas.append(MetricaDimensional(
                id=f"code_quality_{int(time.time())}",
                nome="Code Quality Score",
                valor=code_quality,
                timestamp=time.time(),
                dimensao=DimensaoMonitoramento.QUALIDADE.name,
                unidade="score"
            ))
        
        return metricas
    
    def _obter_metrica_prometheus(self, query: str) -> Optional[float]:
        """
        Obtém uma métrica do Prometheus.
        
        Args:
            query: Query PromQL
            
        Returns:
            float: Valor da métrica ou None se não encontrada
        """
        try:
            url = f"http://prometheus:9090/api/v1/query"
            params = {
                "query": query
            }
            
            response = requests.get(url, params=params, timeout=config.timeout_api)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] == "success" and data["data"]["result"]:
                return float(data["data"]["result"][0]["value"][1])
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter métrica do Prometheus: {e}")
            return None
    
    def _limpar_metricas_antigas(self):
        """
        Remove métricas mais antigas que o período de retenção.
        """
        cutoff = time.time() - config.retencao_dados
        
        for dimensao in self.metricas:
            self.metricas[dimensao] = [
                m for m in self.metricas[dimensao]
                if m.timestamp > cutoff
            ]

class AnalisadorMetricas:
    """
    Analisa métricas coletadas para identificar padrões e anomalias.
    
    Responsabilidades:
    1. Analisar tendências nas métricas
    2. Detectar anomalias
    3. Calcular estatísticas
    4. Gerar insights
    """
    def __init__(self):
        self.coletor = ColetorMetricas()
        self.lock = threading.Lock()
        logger.info("AnalisadorMetricas inicializado")
    
    @log_operacao_critica
    def analisar_metricas(self) -> Dict[str, Any]:
        """
        Analisa todas as métricas coletadas.
        
        Returns:
            Dict[str, Any]: Resultados da análise
        """
        # Coleta métricas
        metricas = self.coletor.coletar_metricas()
        
        # Agrupa por dimensão
        metricas_por_dimensao = defaultdict(list)
        for metrica in metricas:
            metricas_por_dimensao[metrica.dimensao].append(metrica)
        
        # Analisa cada dimensão
        resultados = {}
        for dimensao, metricas_dimensao in metricas_por_dimensao.items():
            resultados[dimensao] = self._analisar_dimensao(metricas_dimensao)
        
        return resultados
    
    def _analisar_dimensao(self, metricas: List[MetricaDimensional]) -> Dict[str, Any]:
        """
        Analisa métricas de uma dimensão específica.
        
        Args:
            metricas: Lista de métricas da dimensão
            
        Returns:
            Dict[str, Any]: Resultados da análise
        """
        if not metricas:
            return {}
        
        # Converte para DataFrame
        df = pd.DataFrame([m.to_dict() for m in metricas])
        
        # Calcula estatísticas básicas
        stats = {
            "media": df["valor"].mean(),
            "mediana": df["valor"].median(),
            "desvio_padrao": df["valor"].std(),
            "min": df["valor"].min(),
            "max": df["valor"].max()
        }
        
        # Detecta anomalias
        anomalias = self._detectar_anomalias(df)
        
        # Calcula tendências
        tendencias = self._calcular_tendencias(df)
        
            return {
            "estatisticas": stats,
            "anomalias": anomalias,
            "tendencias": tendencias
        }
    
    def _detectar_anomalias(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detecta anomalias nas métricas usando Z-score.
        
        Args:
            df: DataFrame com as métricas
            
        Returns:
            List[Dict[str, Any]]: Lista de anomalias detectadas
        """
        anomalias = []
        
        # Calcula Z-score
        z_scores = np.abs((df["valor"] - df["valor"].mean()) / df["valor"].std())
        
        # Identifica anomalias (Z-score > 3)
        anomalias_idx = z_scores[z_scores > 3].index
        
        for idx in anomalias_idx:
            anomalias.append({
                "timestamp": df.loc[idx, "timestamp"],
                "valor": df.loc[idx, "valor"],
                "z_score": z_scores[idx],
                "nome": df.loc[idx, "nome"]
            })
        
        return anomalias
    
    def _calcular_tendencias(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calcula tendências nas métricas usando regressão linear.
        
        Args:
            df: DataFrame com as métricas
            
        Returns:
            Dict[str, float]: Coeficientes da regressão
        """
        # Prepara dados para regressão
        X = (df["timestamp"] - df["timestamp"].min()).values.reshape(-1, 1)
        y = df["valor"].values
        
        # Calcula regressão linear
        slope, intercept = np.polyfit(X.flatten(), y, 1)
            
            return {
            "inclinacao": slope,
            "intercepto": intercept
        }

class GeradorAlertas:
    """
    Gera alertas baseados na análise de métricas.
    
    Responsabilidades:
    1. Definir regras de alerta
    2. Avaliar condições de alerta
    3. Gerar notificações
    4. Gerenciar estado dos alertas
    """
    def __init__(self):
        self.alertas_ativos = set()
        self.ultimo_alerta = defaultdict(float)
        self.lock = threading.Lock()
        logger.info("GeradorAlertas inicializado")
    
    @log_operacao_critica
    def avaliar_alertas(self, resultados_analise: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Avalia condições de alerta baseado nos resultados da análise.
        
        Args:
            resultados_analise: Resultados da análise de métricas
            
        Returns:
            List[Dict[str, Any]]: Lista de alertas gerados
        """
        alertas = []
        
        for dimensao, resultado in resultados_analise.items():
            # Verifica anomalias
            for anomalia in resultado.get("anomalias", []):
                alerta = self._gerar_alerta_anomalia(dimensao, anomalia)
                if alerta:
                    alertas.append(alerta)
            
            # Verifica tendências
            tendencias = resultado.get("tendencias", {})
            if abs(tendencias.get("inclinacao", 0)) > 0.1:  # Tendência significativa
                alerta = self._gerar_alerta_tendencia(dimensao, tendencias)
                if alerta:
                    alertas.append(alerta)
            
            # Verifica limites
            stats = resultado.get("estatisticas", {})
            alerta = self._verificar_limites(dimensao, stats)
            if alerta:
                alertas.append(alerta)
        
        return alertas
    
    def _gerar_alerta_anomalia(self, dimensao: str, anomalia: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Gera alerta para uma anomalia detectada.
        
        Args:
            dimensao: Dimensão da métrica
            anomalia: Dados da anomalia
            
        Returns:
            Optional[Dict[str, Any]]: Alerta gerado ou None
        """
        alerta_id = f"anomalia_{dimensao}_{anomalia['nome']}_{int(anomalia['timestamp'])}"
        
        # Verifica se já existe alerta ativo
        if alerta_id in self.alertas_ativos:
            return None
        
        # Verifica limite de alertas
        if not self._verificar_limite_alertas():
            return None
        
        alerta = {
            "id": alerta_id,
            "tipo": "anomalia",
            "dimensao": dimensao,
            "severidade": "alta" if anomalia["z_score"] > 5 else "media",
            "mensagem": f"Anomalia detectada em {anomalia['nome']}: {anomalia['valor']} (Z-score: {anomalia['z_score']:.2f})",
            "timestamp": time.time(),
            "dados": anomalia
        }
        
        # Registra alerta
        with self.lock:
            self.alertas_ativos.add(alerta_id)
            self.ultimo_alerta[dimensao] = time.time()
            
        return alerta
    
    def _gerar_alerta_tendencia(self, dimensao: str, tendencias: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """
        Gera alerta para uma tendência significativa.
        
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
        
        direcao = "aumentando" if tendencias["inclinacao"] > 0 else "diminuindo"
        
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
    analisador = AnalisadorMetricas()
    gerador_alertas = GeradorAlertas()
    
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
>>>>>>> origin/main
