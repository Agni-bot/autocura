# Módulo de Monitoramento Multidimensional

import time
import threading
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from collections import deque
import logging
import json
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("MonitoramentoMultidimensional")

@dataclass
class MetricaDimensional:
    """
    Estrutura de dados para métricas multidimensionais com contexto temporal e espacial.
    
    Como cristais de dados que capturam a essência do sistema,
    cada métrica é um prisma que refrata a realidade operacional
    em dimensões que transcendem o óbvio.
    """
    nome: str
    valor: float
    timestamp: float
    contexto: Dict[str, Any]
    dimensao: str
    unidade: str
    confianca: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a métrica para formato de dicionário."""
        return {
            "nome": self.nome,
            "valor": self.valor,
            "timestamp": self.timestamp,
            "contexto": self.contexto,
            "dimensao": self.dimensao,
            "unidade": self.unidade,
            "confianca": self.confianca
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricaDimensional':
        """Cria uma instância de métrica a partir de um dicionário."""
        return cls(
            nome=data["nome"],
            valor=data["valor"],
            timestamp=data["timestamp"],
            contexto=data["contexto"],
            dimensao=data["dimensao"],
            unidade=data["unidade"],
            confianca=data.get("confianca", 1.0)
        )


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
                nome=f"{self.nome}_instantaneo",
                valor=taxa,
                timestamp=agora,
                contexto={"tipo": "instantaneo"},
                dimensao="throughput",
                unidade="ops/s"
            )
            
            metrica_media = MetricaDimensional(
                nome=f"{self.nome}_media_movel",
                valor=media_movel,
                timestamp=agora,
                contexto={"tipo": "media_movel", "janela": self.janela_media},
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
                    nome=f"{self.nome}_{categoria}",
                    valor=contador,
                    timestamp=agora,
                    contexto=contexto_agregado,
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
                nome=f"{self.nome}_media",
                valor=media,
                timestamp=agora,
                contexto={"tipo": "media", "amostras": len(valores)},
                dimensao="latencia",
                unidade="ms"
            )
            
            metrica_mediana = MetricaDimensional(
                nome=f"{self.nome}_mediana",
                valor=mediana,
                timestamp=agora,
                contexto={"tipo": "mediana", "amostras": len(valores)},
                dimensao="latencia",
                unidade="ms"
            )
            
            metricas.extend([metrica_media, metrica_mediana])
            
            # Cria métricas para percentis
            for i, p in enumerate(self.percentis):
                metrica_percentil = MetricaDimensional(
                    nome=f"{self.nome}_p{p}",
                    valor=percentis_calc[i],
                    timestamp=agora,
                    contexto={"tipo": "percentil", "percentil": p, "amostras": len(valores)},
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
                    nome=f"{self.nome}_{dimensao}_escala_{escala}",
                    valor=media,
                    timestamp=agora,
                    contexto={
                        "dimensao": dimensao,
                        "escala": escala,
                        "variacao": variacao,
                        "amostras": len(valores)
                    },
                    dimensao="recursos",
                    unidade="percentual"
                )
                metricas.append(metrica)
            
            # Calcula dimensão fractal se houver dados suficientes
            todos_valores = [v for v, _, _ in self.leituras[dimensao]]
            if len(todos_valores) >= 10:
                dim_fractal = self._calcular_dimensao_fractal(todos_valores)
                
                metrica_fractal = MetricaDimensional(
                    nome=f"{self.nome}_{dimensao}_dimensao_fractal",
                    valor=dim_fractal,
                    timestamp=agora,
                    contexto={
                        "dimensao": dimensao,
                        "amostras": len(todos_valores)
                    },
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
        logger.info(f"Agregador
(Content truncated due to size limit. Use line ranges to read in chunks)