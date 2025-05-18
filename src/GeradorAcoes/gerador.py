"""
Módulo de Geração de Ações

Este módulo é responsável por gerar e gerenciar ações corretivas baseadas em diagnósticos.
Ele integra:
1. Geração de hotfixes
2. Refatoração de código
3. Redesign de componentes
4. Orquestração de ações através de planos
5. Execução automática de ações

O módulo utiliza:
- Algoritmos genéticos para priorização
- Templates de ações
- Histórico de efetividade para aprendizado
- Gemini API para análise
- Kubernetes para execução
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
try:
    from observabilidade.acao_necessaria import TelaAcaoNecessaria, AcaoNecessaria
except ModuleNotFoundError:
    from src.observabilidade.acao_necessaria import TelaAcaoNecessaria, AcaoNecessaria
from executor.executor import ExecutorAcoes, ResultadoExecucao

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("GeradorAcoes")

class Config:
    """
    Configurações do sistema carregadas do ConfigMap.
    
    Atributos:
        score_minimo: Score mínimo para considerar uma ação válida
        timeout_api: Timeout para chamadas de API
        api_token: Token de autenticação
        max_acoes_redesign: Número máximo de ações de redesign por ciclo
        prioridades: Pesos para diferentes tipos de ação
    """
    def __init__(self):
        self.score_minimo = float(os.getenv('SCORE_MINIMO', '0.7'))
        self.timeout_api = int(os.getenv('TIMEOUT_API', '5'))
        self.api_token = os.getenv('API_TOKEN', '')
        self.max_acoes_redesign = int(os.getenv('MAX_ACOES_REDESIGN', '3'))
        self.prioridades = {
            "HOTFIX": float(os.getenv('PRIORIDADE_HOTFIX', '2.0')),
            "REFATORACAO": float(os.getenv('PRIORIDADE_REFATORACAO', '1.5')),
            "REDESIGN": float(os.getenv('PRIORIDADE_REDESIGN', '1.0'))
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

@dataclass
class PadraoAnomalia:
    """
    Representa um padrão de anomalia detectado.
    
    Atributos:
        id: Identificador único
        nome: Nome do padrão
        dimensoes: Dimensões afetadas
        descricao: Descrição detalhada
        severidade: Nível de severidade (0-1)
    """
    id: str
    nome: str
    dimensoes: List[str]
    descricao: str
    severidade: float
    
    def __post_init__(self):
        if not 0 <= self.severidade <= 1:
            raise ValueError("Severidade deve estar entre 0 e 1")

@dataclass
class Diagnostico:
    """
    Representa um diagnóstico completo do sistema.
    
    Atributos:
        id: Identificador único
        timestamp: Momento do diagnóstico
        anomalias_detectadas: Lista de anomalias com confiança
        metricas_analisadas: Métricas consideradas
        contexto: Contexto adicional
    """
    id: str
    timestamp: float
    anomalias_detectadas: List[Tuple[PadraoAnomalia, float]]
    metricas_analisadas: List[str]
    contexto: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        for _, confianca in self.anomalias_detectadas:
            if not 0 <= confianca <= 1:
                raise ValueError("Confiança deve estar entre 0 e 1")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Diagnostico':
        """
        Cria uma instância de Diagnostico a partir de um dicionário.
        
        Args:
            data: Dicionário com dados do diagnóstico
            
        Returns:
            Diagnostico: Instância criada
        """
        anomalias = []
        for anom_data in data.get("anomalias_detectadas", []):
            padrao = PadraoAnomalia(
                id=anom_data["anomalia"]["id"],
                nome=anom_data["anomalia"]["nome"],
                dimensoes=anom_data["anomalia"]["dimensoes"],
                descricao=anom_data["anomalia"].get("descricao", ""),
                severidade=anom_data["anomalia"].get("severidade", 0.5)
            )
            confianca = anom_data["confianca"]
            anomalias.append((padrao, confianca))
            
        return cls(
            id=data["id"],
            timestamp=data["timestamp"],
            anomalias_detectadas=anomalias,
            metricas_analisadas=data.get("metricas_analisadas", []),
            contexto=data.get("contexto", {})
        )

@log_operacao_critica
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
        base_url = "http://monitoramento:8080/api/metricas"
        if metrica_id:
            url = f"{base_url}/{metrica_id}"
        else:
            url = base_url
            
        headers = {
            "Authorization": f"Bearer {config.api_token}"
        }
        
        response = requests.get(url, headers=headers, timeout=config.timeout_api)
        response.raise_for_status()
        
        data = response.json()
        
        if metrica_id:
            # Valida dados da métrica
            if not all(k in data for k in ["id", "nome", "valor", "timestamp", "dimensao", "unidade"]):
                raise ValueError("Dados da métrica incompletos")
                
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
            # Valida lista de métricas
            if not isinstance(data, list):
                raise ValueError("Dados retornados não são uma lista de métricas")
                
            metricas = []
            for item in data:
                if not all(k in item for k in ["id", "nome", "valor", "timestamp", "dimensao", "unidade"]):
                    logger.warning(f"Métrica inválida encontrada: {item}")
                    continue
                    
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
            
    except requests.Timeout:
        logger.error("Timeout ao obter métricas do monitoramento")
        return []
    except requests.ConnectionError:
        logger.error("Erro de conexão ao obter métricas do monitoramento")
        return []
    except requests.HTTPError as e:
        logger.error(f"Erro HTTP ao obter métricas: {e.response.status_code}")
        return []
    except ValueError as e:
        logger.error(f"Erro de validação de dados: {e}")
        return []
    except Exception as e:
        logger.error(f"Erro inesperado ao obter métricas: {e}")
        return []

@log_operacao_critica
def obter_diagnostico(diagnostico_id):
    """
    Obtém um diagnóstico do serviço de diagnóstico via API REST.
    
    Args:
        diagnostico_id: ID do diagnóstico
        
    Returns:
        Objeto Diagnostico ou None se ocorrer erro
        
    Raises:
        ValueError: Se os dados retornados forem inválidos
        requests.exceptions.RequestException: Em caso de erro na requisição
    """
    try:
        url = f"http://diagnostico:8080/api/diagnosticos/{diagnostico_id}"
        headers = {
            "Authorization": f"Bearer {config.api_token}"
        }
        
        response = requests.get(url, headers=headers, timeout=config.timeout_api)
        response.raise_for_status()
        
        data = response.json()
        
        # Valida dados do diagnóstico
        if not all(k in data for k in ["id", "timestamp", "anomalias_detectadas"]):
            raise ValueError("Dados do diagnóstico incompletos")
            
        return Diagnostico.from_dict(data)
        
    except requests.Timeout:
        logger.error("Timeout ao obter diagnóstico")
        return None
    except requests.ConnectionError:
        logger.error("Erro de conexão ao obter diagnóstico")
        return None
    except requests.HTTPError as e:
        logger.error(f"Erro HTTP ao obter diagnóstico: {e.response.status_code}")
        return None
    except ValueError as e:
        logger.error(f"Erro de validação de dados: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao obter diagnóstico: {e}")
        return None

class TipoAcao(Enum):
    """
    Enumeração dos tipos de ações corretivas.
    
    HOTFIX: Ação imediata para estabilização
    REFATORACAO: Solução estrutural de médio prazo
    REDESIGN: Evolução preventiva de longo prazo
    """
    HOTFIX = auto()
    REFATORACAO = auto()
    REDESIGN = auto()

@dataclass
class AcaoCorretiva:
    """
    Representa uma ação corretiva.
    
    Atributos:
        id: Identificador único
        tipo: Tipo da ação (hotfix, refatoração, redesign)
        descricao: Descrição da ação
        contexto: Contexto da ação
        impacto_esperado: Impacto esperado
        referencias_manual: Referências do manual
        timestamp: Momento da criação
        status: Status da ação
        aprovador: Aprovador da ação
        comentarios: Comentários adicionais
    """
    id: str
    tipo: str
    descricao: str
    contexto: Dict[str, Any]
    impacto_esperado: str
    referencias_manual: List[str]
    timestamp: float
    status: str = "PENDENTE"
    aprovador: Optional[str] = None
    comentarios: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a ação para formato de dicionário.
        
        Returns:
            dict: Representação em dicionário
        """
        return {
            "id": self.id,
            "tipo": self.tipo,
            "descricao": self.descricao,
            "contexto": self.contexto,
            "impacto_esperado": self.impacto_esperado,
            "referencias_manual": self.referencias_manual,
            "timestamp": self.timestamp,
            "status": self.status,
            "aprovador": self.aprovador,
            "comentarios": self.comentarios
        }

@dataclass
class PlanoAcao:
    """
    Representa um plano de ação.
    
    Atributos:
        id: Identificador único
        diagnosticos: Lista de diagnósticos relacionados
        acoes: Lista de ações corretivas
        prioridade: Prioridade do plano
        status: Status do plano
        timestamp: Momento da criação
        contexto: Contexto adicional
    """
    id: str
    diagnosticos: List[Any]  # TODO: Importar tipo Diagnostico
    acoes: List[AcaoCorretiva]
    prioridade: int
    status: str = "PENDENTE"
    timestamp: float = field(default_factory=time.time)
    contexto: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o plano para formato de dicionário.
        
        Returns:
            dict: Representação em dicionário
        """
        return {
            "id": self.id,
            "diagnosticos": [d.to_dict() for d in self.diagnosticos],
            "acoes": [a.to_dict() for a in self.acoes],
            "prioridade": self.prioridade,
            "status": self.status,
            "timestamp": self.timestamp,
            "contexto": self.contexto
        }

class GeradorHotfix:
    """
    Gera ações de hotfix para problemas críticos.
    
    Responsabilidades:
    1. Identificar problemas críticos
    2. Gerar ações de correção rápida
    3. Priorizar hotfixes
    4. Validar efetividade
    """
    def __init__(self):
        self.lock = threading.Lock()
        logger.info("GeradorHotfix inicializado")
    
    @log_operacao_critica
    def gerar_hotfix(self, diagnostico: Any) -> Optional[AcaoCorretiva]:
        """
        Gera uma ação de hotfix para um diagnóstico.
        
        Args:
            diagnostico: Diagnóstico que requer hotfix
            
        Returns:
            Optional[AcaoCorretiva]: Ação gerada ou None
        """
        # Verifica se diagnóstico requer hotfix
        if not self._requer_hotfix(diagnostico):
            return None
        
        # Gera descrição
        descricao = self._gerar_descricao(diagnostico)
        
        # Gera contexto
        contexto = self._gerar_contexto(diagnostico)
        
        # Estima impacto
        impacto = self._estimar_impacto(diagnostico)
        
        # Obtém referências
        referencias = self._obter_referencias(diagnostico)
        
        # Integração com Gemini API para análise contextual
        prompt = (
            f"Analise o impacto de executar a seguinte ação corretiva no sistema: {descricao}. "
            f"Contexto: {json.dumps(contexto)}. "
            f"Quais os riscos, benefícios e recomendações?"
        )
        try:
            analise_gemini = chamar_gemini_api(prompt)
            comentario_gemini = analise_gemini.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', str(analise_gemini))
        except Exception as e:
            comentario_gemini = f"[Erro ao consultar Gemini API: {e}]"
        
        # Cria ação
        return AcaoCorretiva(
            id=f"hotfix_{int(time.time())}",
            tipo="HOTFIX",
            descricao=descricao,
            contexto=contexto,
            impacto_esperado=impacto,
            referencias_manual=referencias,
            timestamp=time.time(),
            comentarios=[comentario_gemini]
        )
    
    def _requer_hotfix(self, diagnostico: Any) -> bool:
        """
        Verifica se um diagnóstico requer hotfix.
        
        Args:
            diagnostico: Diagnóstico a ser verificado
            
        Returns:
            bool: True se requer hotfix
        """
        # TODO: Implementar lógica mais sofisticada
        return diagnostico.prioridade >= 4
    
    def _gerar_descricao(self, diagnostico: Any) -> str:
        """
        Gera descrição para o hotfix.
        
        Args:
            diagnostico: Diagnóstico base
            
        Returns:
            str: Descrição gerada
        """
        return f"Hotfix para {diagnostico.causa_raiz}: {diagnostico.descricao}"
    
    def _gerar_contexto(self, diagnostico: Any) -> Dict[str, Any]:
        """
        Gera contexto para o hotfix.
        
        Args:
            diagnostico: Diagnóstico base
            
        Returns:
            Dict[str, Any]: Contexto gerado
        """
        return {
            "diagnostico_id": diagnostico.id,
            "causa_raiz": diagnostico.causa_raiz,
            "impacto": diagnostico.impacto,
            "padroes": [p.to_dict() for p in diagnostico.padroes]
        }
    
    def _estimar_impacto(self, diagnostico: Any) -> str:
        """
        Estima impacto do hotfix.
        
        Args:
            diagnostico: Diagnóstico base
            
        Returns:
            str: Impacto estimado
        """
        return f"Correção imediata de {diagnostico.impacto}"
    
    def _obter_referencias(self, diagnostico: Any) -> List[str]:
        """
        Obtém referências do manual.
        
        Args:
            diagnostico: Diagnóstico base
            
        Returns:
            List[str]: Referências obtidas
        """
        # TODO: Implementar busca no manual
        return ["Manual de Hotfix", "Procedimentos de Emergência"]

class MotorRefatoracao:
    """
    Gera ações de refatoração para melhorias de código.
    
    Responsabilidades:
    1. Identificar oportunidades de refatoração
    2. Gerar ações de melhoria
    3. Priorizar refatorações
    4. Validar qualidade
    """
    def __init__(self):
        self.lock = threading.Lock()
        logger.info("MotorRefatoracao inicializado")
    
    @log_operacao_critica
    def gerar_refatoracao(self, diagnostico: Any) -> Optional[AcaoCorretiva]:
        """
        Gera uma ação de refatoração para um diagnóstico.
        
        Args:
            diagnostico: Diagnóstico que requer refatoração
            
        Returns:
            Optional[AcaoCorretiva]: Ação gerada ou None
        """
        # Verifica se diagnóstico requer refatoração
        if not self._requer_refatoracao(diagnostico):
            return None
        
        # Gera descrição
        descricao = self._gerar_descricao(diagnostico)
        
        # Gera contexto
        contexto = self._gerar_contexto(diagnostico)
        
        # Estima impacto
        impacto = self._estimar_impacto(diagnostico)
        
        # Obtém referências
        referencias = self._obter_referencias(diagnostico)
        
        # Integração com Gemini API para análise contextual
        prompt = (
            f"Analise o impacto de executar a seguinte ação corretiva de refatoração no sistema: {descricao}. "
            f"Contexto: {json.dumps(contexto)}. "
            f"Quais os riscos, benefícios e recomendações?"
        )
        try:
            analise_gemini = chamar_gemini_api(prompt)
            comentario_gemini = analise_gemini.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', str(analise_gemini))
        except Exception as e:
            comentario_gemini = f"[Erro ao consultar Gemini API: {e}]"
        
        # Cria ação
        return AcaoCorretiva(
            id=f"refatoracao_{int(time.time())}",
            tipo="REFATORACAO",
            descricao=descricao,
            contexto=contexto,
            impacto_esperado=impacto,
            referencias_manual=referencias,
            timestamp=time.time(),
            comentarios=[comentario_gemini]
        )
    
    def _requer_refatoracao(self, diagnostico: Any) -> bool:
        """
        Verifica se um diagnóstico requer refatoração.
        
        Args:
            diagnostico: Diagnóstico a ser verificado
            
        Returns:
            bool: True se requer refatoração
        """
        # TODO: Implementar lógica mais sofisticada
        return diagnostico.prioridade >= 3
    
    def _gerar_descricao(self, diagnostico: Any) -> str:
        """
        Gera descrição para a refatoração.
        
        Args:
            diagnostico: Diagnóstico base
            
        Returns:
            str: Descrição gerada
        """
        return f"Refatoração para {diagnostico.causa_raiz}: {diagnostico.descricao}"
    
    def _gerar_contexto(self, diagnostico: Any) -> Dict[str, Any]:
        """
        Gera contexto para a refatoração.
        
        Args:
            diagnostico: Diagnóstico base
            
        Returns:
            Dict[str, Any]: Contexto gerado
        """
        return {
            "diagnostico_id": diagnostico.id,
            "causa_raiz": diagnostico.causa_raiz,
            "impacto": diagnostico.impacto,
            "padroes": [p.to_dict() for p in diagnostico.padroes]
        }
    
    def _estimar_impacto(self, diagnostico: Any) -> str:
        """
        Estima impacto da refatoração.
        
        Args:
            diagnostico: Diagnóstico base
            
        Returns:
            str: Impacto estimado
        """
        return f"Melhoria de qualidade para {diagnostico.impacto}"
    
    def _obter_referencias(self, diagnostico: Any) -> List[str]:
        """
        Obtém referências do manual.
        
        Args:
            diagnostico: Diagnóstico base
            
        Returns:
            List[str]: Referências obtidas
        """
        # TODO: Implementar busca no manual
        return ["Manual de Refatoração", "Padrões de Código"]

class ProjetorRedesign:
    """
    Gera ações de redesign para melhorias arquiteturais.
    
    Responsabilidades:
    1. Identificar oportunidades de redesign
    2. Gerar ações de melhoria arquitetural
    3. Priorizar redesigns
    4. Validar viabilidade
    """
    def __init__(self):
        self.lock = threading.Lock()
        logger.info("ProjetorRedesign inicializado")
    
    @log_operacao_critica
    def gerar_redesign(self, diagnostico: Any) -> Optional[AcaoCorretiva]:
        """
        Gera uma ação de redesign para um diagnóstico.
        
        Args:
            diagnostico: Diagnóstico que requer redesign
            
        Returns:
            Optional[AcaoCorretiva]: Ação gerada ou None
        """
        # Verifica se diagnóstico requer redesign
        if not self._requer_redesign(diagnostico):
            return None
        
        # Gera descrição
        descricao = self._gerar_descricao(diagnostico)
        
        # Gera contexto
        contexto = self._gerar_contexto(diagnostico)
        
        # Estima impacto
        impacto = self._estimar_impacto(diagnostico)
        
        # Obtém referências
        referencias = self._obter_referencias(diagnostico)
        
        # Integração com Gemini API para análise contextual
        prompt = (
            f"Analise o impacto de executar a seguinte ação corretiva de redesign no sistema: {descricao}. "
            f"Contexto: {json.dumps(contexto)}. "
            f"Quais os riscos, benefícios e recomendações?"
        )
        try:
            analise_gemini = chamar_gemini_api(prompt)
            comentario_gemini = analise_gemini.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', str(analise_gemini))
        except Exception as e:
            comentario_gemini = f"[Erro ao consultar Gemini API: {e}]"
        
        # Cria ação
        return AcaoCorretiva(
            id=f"redesign_{int(time.time())}",
            tipo="REDESIGN",
            descricao=descricao,
            contexto=contexto,
            impacto_esperado=impacto,
            referencias_manual=referencias,
            timestamp=time.time(),
            comentarios=[comentario_gemini]
        )
    
    def _requer_redesign(self, diagnostico: Any) -> bool:
        """
        Verifica se um diagnóstico requer redesign.
        
        Args:
            diagnostico: Diagnóstico a ser verificado
            
        Returns:
            bool: True se requer redesign
        """
        # TODO: Implementar lógica mais sofisticada
        return diagnostico.prioridade >= 2
    
    def _gerar_descricao(self, diagnostico: Any) -> str:
        """
        Gera descrição para o redesign.
        
        Args:
            diagnostico: Diagnóstico base
            
        Returns:
            str: Descrição gerada
        """
        return f"Redesign para {diagnostico.causa_raiz}: {diagnostico.descricao}"
    
    def _gerar_contexto(self, diagnostico: Any) -> Dict[str, Any]:
        """
        Gera contexto para o redesign.
        
        Args:
            diagnostico: Diagnóstico base
            
        Returns:
            Dict[str, Any]: Contexto gerado
        """
        return {
            "diagnostico_id": diagnostico.id,
            "causa_raiz": diagnostico.causa_raiz,
            "impacto": diagnostico.impacto,
            "padroes": [p.to_dict() for p in diagnostico.padroes]
        }
    
    def _estimar_impacto(self, diagnostico: Any) -> str:
        """
        Estima impacto do redesign.
        
        Args:
            diagnostico: Diagnóstico base
            
        Returns:
            str: Impacto estimado
        """
        return f"Melhoria arquitetural para {diagnostico.impacto}"
    
    def _obter_referencias(self, diagnostico: Any) -> List[str]:
        """
        Obtém referências do manual.
        
        Args:
            diagnostico: Diagnóstico base
            
        Returns:
            List[str]: Referências obtidas
        """
        # TODO: Implementar busca no manual
        return ["Manual de Arquitetura", "Padrões de Design"]

class GeradorAcoes:
    """
    Gera e gerencia ações corretivas.
    
    Responsabilidades:
    1. Coordenar geração de ações
    2. Priorizar ações
    3. Criar planos de ação
    4. Validar efetividade
    5. Executar ações automaticamente
    """
    def __init__(self):
        self.gerador_hotfix = GeradorHotfix()
        self.motor_refatoracao = MotorRefatoracao()
        self.projetor_redesign = ProjetorRedesign()
        self.executor = ExecutorAcoes()
        self.lock = threading.Lock()
        logger.info("GeradorAcoes inicializado")
    
    @log_operacao_critica
    def gerar_acoes(self, diagnosticos: List[Any]) -> List[PlanoAcao]:
        """
        Gera ações para uma lista de diagnósticos.
        
        Args:
            diagnosticos: Lista de diagnósticos
            
        Returns:
            List[PlanoAcao]: Lista de planos de ação
        """
        # Ordena diagnósticos por prioridade
        diagnosticos.sort(key=lambda d: d.prioridade, reverse=True)
        
        # Gera ações para cada diagnóstico
        planos = []
        for diagnostico in diagnosticos:
            plano = self._gerar_plano(diagnostico)
            if plano:
                planos.append(plano)
        
        return planos
    
    def _gerar_plano(self, diagnostico: Any) -> Optional[PlanoAcao]:
        """
        Gera um plano de ação para um diagnóstico.
        
        Args:
            diagnostico: Diagnóstico base
            
        Returns:
            Optional[PlanoAcao]: Plano gerado ou None
        """
        # Gera ações
        acoes = []
        
        # Tenta gerar hotfix
        hotfix = self.gerador_hotfix.gerar_hotfix(diagnostico)
        if hotfix:
            acoes.append(hotfix)
        
        # Tenta gerar refatoração
        refatoracao = self.motor_refatoracao.gerar_refatoracao(diagnostico)
        if refatoracao:
            acoes.append(refatoracao)
        
        # Tenta gerar redesign
        redesign = self.projetor_redesign.gerar_redesign(diagnostico)
        if redesign:
            acoes.append(redesign)
        
        # Se não gerou nenhuma ação, retorna None
        if not acoes:
            return None
        
        # Cria plano
        return PlanoAcao(
            id=f"plano_{int(time.time())}",
            diagnosticos=[diagnostico],
            acoes=acoes,
            prioridade=diagnostico.prioridade
        )
    
    def executar_plano(self, plano: PlanoAcao) -> Dict[str, Any]:
        """
        Executa um plano de ação.
        
        Args:
            plano: Plano a ser executado
            
        Returns:
            Dict[str, Any]: Resultado da execução
        """
        resultados = []
        
        # Ordena ações por prioridade
        plano.acoes.sort(key=lambda a: a.prioridade)
        
        # Executa cada ação
        for acao in plano.acoes:
            try:
                resultado = self.executor.executar_acao(acao)
                resultados.append({
                    "acao_id": acao.id,
                    "sucesso": resultado.sucesso,
                    "mensagem": resultado.mensagem,
                    "detalhes": resultado.detalhes
                })
                
                # Se falhou e não é reversível, para execução
                if not resultado.sucesso and not acao.reversivel:
                    break
                    
            except Exception as e:
                logger.error(f"Erro ao executar ação {acao.id}: {e}")
                resultados.append({
                    "acao_id": acao.id,
                    "sucesso": False,
                    "mensagem": str(e),
                    "detalhes": {"erro": str(e)}
                })
                break
        
        return {
            "plano_id": plano.id,
            "timestamp": time.time(),
            "resultados": resultados
        }

def chamar_gemini_api(prompt):
    """
    Chama a API do Gemini para análise de ações.
    
    Args:
        prompt: Texto para análise
        
    Returns:
        dict: Resposta da API
        
    Raises:
        requests.exceptions.RequestException: Em caso de erro na requisição
    """
    api_key = os.getenv("GEMINI_API_KEY")
    endpoint = os.getenv("GEMINI_API_ENDPOINT")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    response = requests.post(endpoint, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()

# Inicialização da API e rotas
if __name__ == "__main__":
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    # Inicializa componentes
    gerador = GeradorAcoes()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Verifica a saúde do serviço."""
        if not gerador:
            return jsonify({"status": "not ready", "reason": "Components not initialized"}), 503
        return jsonify({"status": "ready", "timestamp": time.time()})
    
    @app.route('/api/acoes', methods=['POST'])
    def gerar_acoes():
        """
        Gera ações baseadas nos diagnósticos fornecidos.
        
        Returns:
            dict: Lista de planos de ação gerados
        """
        try:
            data = request.get_json()
            diagnosticos = data["diagnosticos"]  # TODO: Converter para objetos Diagnostico
            
            planos = gerador.gerar_acoes(diagnosticos)
            return jsonify([p.to_dict() for p in planos]), 200
        except Exception as e:
            logger.error(f"Erro ao gerar ações: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/executar', methods=['POST'])
    def executar_plano():
        """
        Executa um plano de ação.
        
        Returns:
            dict: Resultado da execução
        """
        try:
            data = request.get_json()
            plano = data["plano"]  # TODO: Converter para objeto PlanoAcao
            
            resultado = gerador.executar_plano(plano)
            return jsonify(resultado), 200
        except Exception as e:
            logger.error(f"Erro ao executar plano: {e}")
            return jsonify({"error": str(e)}), 500
    
    # Inicia o servidor
    app.run(host='0.0.0.0', port=8080)
