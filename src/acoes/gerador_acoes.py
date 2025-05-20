"""
Módulo de geração de ações do sistema de autocura.
Responsável por gerar e gerenciar planos de ação baseados em diagnósticos.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid
import json
import logging
from ..core.base import BaseComponent

logger = logging.getLogger(__name__)

@dataclass
class Acao:
    """Representa uma ação a ser executada pelo sistema."""
    
    id: str
    tipo: str
    parametros: Dict[str, Any]
    prioridade: int
    timestamp_criacao: float
    status: str = "pendente"
    resultado: Optional[Dict[str, Any]] = None
    timestamp_execucao: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Acao":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            tipo=data["tipo"],
            parametros=data["parametros"],
            prioridade=data.get("prioridade", 1),
            timestamp_criacao=data.get("timestamp_criacao", datetime.now().timestamp()),
            status=data.get("status", "pendente"),
            resultado=data.get("resultado"),
            timestamp_execucao=data.get("timestamp_execucao")
        )

@dataclass
class PlanoAcao:
    """Representa um plano de ação contendo múltiplas ações."""
    
    id: str
    diagnostico_id: str
    acoes: List[Acao]
    timestamp_criacao: float
    status: str = "criado"
    resultado: Optional[Dict[str, Any]] = None
    timestamp_conclusao: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanoAcao":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            diagnostico_id=data["diagnostico_id"],
            acoes=[Acao.from_dict(a) for a in data["acoes"]],
            timestamp_criacao=data.get("timestamp_criacao", datetime.now().timestamp()),
            status=data.get("status", "criado"),
            resultado=data.get("resultado"),
            timestamp_conclusao=data.get("timestamp_conclusao")
        )

class GeradorAcoes(BaseComponent):
    """Gerador de ações baseado em diagnósticos do sistema."""
    
    def __init__(self, name: str = "GeradorAcoes"):
        super().__init__(name)
        self._historico_planos: List[PlanoAcao] = []
        self._acoes_disponiveis: Dict[str, Dict[str, Any]] = {
            "reiniciar_servico": {
                "descricao": "Reinicia um serviço específico",
                "parametros": ["servico_id"]
            },
            "escalar_recursos": {
                "descricao": "Ajusta a alocação de recursos",
                "parametros": ["recurso", "quantidade"]
            },
            "limpar_cache": {
                "descricao": "Limpa o cache do sistema",
                "parametros": ["tipo_cache"]
            },
            "otimizar_consulta": {
                "descricao": "Otimiza uma consulta específica",
                "parametros": ["consulta_id"]
            }
        }
    
    def initialize(self) -> None:
        """Inicializa o gerador de ações."""
        logger.info("Inicializando Gerador de Ações")
        self._carregar_configuracoes()
    
    def shutdown(self) -> None:
        """Desliga o gerador de ações de forma segura."""
        logger.info("Desligando Gerador de Ações")
        self._salvar_historico()
    
    def _carregar_configuracoes(self) -> None:
        """Carrega configurações do gerador de ações."""
        config = self.get_config()
        if "acoes_disponiveis" in config:
            self._acoes_disponiveis.update(config["acoes_disponiveis"])
    
    def _salvar_historico(self) -> None:
        """Salva o histórico de planos de ação."""
        # TODO: Implementar persistência do histórico
        pass
    
    def gerar_plano_acao(self, diagnostico_id: str, contexto: Dict[str, Any]) -> PlanoAcao:
        """Gera um plano de ação baseado no diagnóstico e contexto."""
        logger.info(f"Gerando plano de ação para diagnóstico {diagnostico_id}")
        
        acoes = self._gerar_acoes_para_diagnostico(contexto)
        plano = PlanoAcao(
            id=str(uuid.uuid4()),
            diagnostico_id=diagnostico_id,
            acoes=acoes,
            timestamp_criacao=datetime.now().timestamp()
        )
        
        self._historico_planos.append(plano)
        return plano
    
    def _gerar_acoes_para_diagnostico(self, contexto: Dict[str, Any]) -> List[Acao]:
        """Gera ações específicas baseadas no contexto do diagnóstico."""
        acoes = []
        
        # Exemplo de lógica de geração de ações
        if contexto.get("tipo_anomalia") == "sobrecarga":
            acoes.append(Acao(
                id=str(uuid.uuid4()),
                tipo="escalar_recursos",
                parametros={
                    "recurso": "cpu",
                    "quantidade": contexto.get("nivel_gravidade", 1.0) * 2
                },
                prioridade=1,
                timestamp_criacao=datetime.now().timestamp()
            ))
        
        elif contexto.get("tipo_anomalia") == "latencia_alta":
            acoes.append(Acao(
                id=str(uuid.uuid4()),
                tipo="otimizar_consulta",
                parametros={
                    "consulta_id": contexto.get("consulta_id", "default")
                },
                prioridade=2,
                timestamp_criacao=datetime.now().timestamp()
            ))
        
        return acoes
    
    def obter_plano_acao(self, plano_id: str) -> Optional[PlanoAcao]:
        """Obtém um plano de ação pelo ID."""
        for plano in self._historico_planos:
            if plano.id == plano_id:
                return plano
        return None
    
    def atualizar_status_plano(self, plano_id: str, status: str, resultado: Optional[Dict[str, Any]] = None) -> bool:
        """Atualiza o status de um plano de ação."""
        plano = self.obter_plano_acao(plano_id)
        if not plano:
            return False
        
        plano.status = status
        if resultado:
            plano.resultado = resultado
        if status in ["concluido", "falhou"]:
            plano.timestamp_conclusao = datetime.now().timestamp()
        
        return True 