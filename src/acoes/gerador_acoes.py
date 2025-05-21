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
from src.diagnostico.rede_neural import Diagnostico

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Acao:
    """Classe que representa uma ação emergente gerada pelo sistema."""
    id: str
    tipo: str
    descricao: str
    prioridade: int
    timestamp: datetime
    diagnostico: Diagnostico
    parametros: Dict[str, Any]
    status: str
    resultado: Optional[Dict[str, Any]] = None

class GeradorAcoes(BaseComponent):
    """Gerador de ações emergentes baseado em diagnósticos."""
    
    def __init__(self, name: str = "GeradorAcoes"):
        super().__init__(name)
        self.mapeamento_acoes = {
            "alta_cpu": {
                "tipo": "escalar_horizontal",
                "descricao": "Escalar horizontalmente para distribuir carga",
                "prioridade": 2,
                "parametros": {
                    "min_replicas": 2,
                    "max_replicas": 5,
                    "target_cpu": 70
                }
            },
            "alta_memoria": {
                "tipo": "otimizar_memoria",
                "descricao": "Otimizar uso de memória e limpar cache",
                "prioridade": 2,
                "parametros": {
                    "clear_cache": True,
                    "gc_threshold": 85,
                    "max_memory": "2Gi"
                }
            },
            "alta_latencia": {
                "tipo": "otimizar_performance",
                "descricao": "Otimizar performance e reduzir latência",
                "prioridade": 1,
                "parametros": {
                    "enable_cache": True,
                    "timeout": 30,
                    "max_retries": 3
                }
            },
            "alta_taxa_erro": {
                "tipo": "corrigir_erros",
                "descricao": "Corrigir erros e implementar retry",
                "prioridade": 0,  # Máxima prioridade
                "parametros": {
                    "retry_strategy": "exponential",
                    "max_retries": 5,
                    "circuit_breaker": True
                }
            }
        }
        
        self.historico_acoes: List[Acao] = []
        
        logger.info("Gerador de ações emergentes inicializado")
    
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
            self.mapeamento_acoes.update(config["acoes_disponiveis"])
    
    def _salvar_historico(self) -> None:
        """Salva o histórico de planos de ação."""
        # TODO: Implementar persistência do histórico
        pass
    
    def gerar_acao(self, diagnostico: Diagnostico) -> Optional[Acao]:
        """Gera uma ação emergente baseada no diagnóstico."""
        if not diagnostico.anomalia_detectada:
            logger.info("Nenhuma anomalia detectada, nenhuma ação necessária")
            return None
        
        # Obtém configuração da ação
        config = self.mapeamento_acoes.get(diagnostico.padrao_detectado)
        if not config:
            logger.warning(
                f"Padrão desconhecido: {diagnostico.padrao_detectado}, "
                "nenhuma ação gerada"
            )
            return None
        
        # Gera ID único
        acao_id = f"acao_{len(self.historico_acoes) + 1}"
        
        # Cria ação
        acao = Acao(
            id=acao_id,
            tipo=config["tipo"],
            descricao=config["descricao"],
            prioridade=config["prioridade"],
            timestamp=datetime.now(),
            diagnostico=diagnostico,
            parametros=config["parametros"],
            status="pendente"
        )
        
        # Adiciona ao histórico
        self.historico_acoes.append(acao)
        
        logger.info(f"Ação gerada: {acao_id} - {acao.tipo}")
        return acao

    def obter_acoes_pendentes(self) -> List[Acao]:
        """Retorna lista de ações pendentes ordenadas por prioridade."""
        return sorted(
            [a for a in self.historico_acoes if a.status == "pendente"],
            key=lambda x: x.prioridade
        )

    def atualizar_status_acao(
        self,
        acao_id: str,
        status: str,
        resultado: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Atualiza o status de uma ação."""
        for acao in self.historico_acoes:
            if acao.id == acao_id:
                acao.status = status
                if resultado:
                    acao.resultado = resultado
                logger.info(f"Status da ação {acao_id} atualizado para {status}")
                return True
        
        logger.warning(f"Ação {acao_id} não encontrada")
        return False

    def obter_historico_acoes(
        self,
        tipo: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Acao]:
        """Retorna histórico de ações com filtros opcionais."""
        acoes = self.historico_acoes
        
        if tipo:
            acoes = [a for a in acoes if a.tipo == tipo]
        
        if status:
            acoes = [a for a in acoes if a.status == status]
        
        return sorted(acoes, key=lambda x: x.timestamp, reverse=True)

    def obter_estatisticas_acoes(self) -> Dict[str, Any]:
        """Retorna estatísticas sobre as ações geradas."""
        total = len(self.historico_acoes)
        
        if total == 0:
            return {
                "total": 0,
                "por_tipo": {},
                "por_status": {},
                "taxa_sucesso": 0.0
            }
        
        # Contagem por tipo
        por_tipo = {}
        for acao in self.historico_acoes:
            por_tipo[acao.tipo] = por_tipo.get(acao.tipo, 0) + 1
        
        # Contagem por status
        por_status = {}
        for acao in self.historico_acoes:
            por_status[acao.status] = por_status.get(acao.status, 0) + 1
        
        # Taxa de sucesso
        sucessos = por_status.get("sucesso", 0)
        taxa_sucesso = (sucessos / total) * 100
        
        return {
            "total": total,
            "por_tipo": por_tipo,
            "por_status": por_status,
            "taxa_sucesso": taxa_sucesso
        }

    def limpar_historico(self, dias: int = 30):
        """Limpa histórico de ações mais antigas que o número de dias especificado."""
        from datetime import timedelta
        
        data_limite = datetime.now() - timedelta(days=dias)
        self.historico_acoes = [
            a for a in self.historico_acoes
            if a.timestamp > data_limite
        ]
        
        logger.info(
            f"Histórico de ações limpo, mantendo apenas ações dos últimos {dias} dias"
        )

# Stub para evitar erro de importação
class PlanoAcao:
    pass 