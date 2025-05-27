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
from enum import Enum
from pathlib import Path
from ..core.base import BaseComponent
from ..services.diagnostico.rede_neural import Diagnostico

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TipoAcao(Enum):
    """Tipos de ações possíveis no sistema."""
    CRITICA = "critica"
    CORRETIVA = "corretiva"
    PREVENTIVA = "preventiva"
    MONITORAMENTO = "monitoramento"

class PrioridadeAcao(Enum):
    """Níveis de prioridade para ações."""
    ALTA = 0
    MEDIA = 1
    BAIXA = 2

@dataclass
class Acao:
    """Classe que representa uma ação emergente gerada pelo sistema."""
    id: str
    tipo: TipoAcao
    descricao: str
    prioridade: PrioridadeAcao
    timestamp: datetime
    diagnostico: Diagnostico
    parametros: Dict[str, Any]
    status: str
    resultado: Optional[Dict[str, Any]] = None
    dependencias: List[str] = None
    tempo_estimado: float = 0.0
    probabilidade_sucesso: float = 0.0

    def __post_init__(self):
        if self.dependencias is None:
            self.dependencias = []

class PlanoAcao:
    """Classe que representa um plano de ação completo."""
    
    def __init__(self, acoes: List[Acao]):
        self.id = str(uuid.uuid4())
        self.acoes = acoes
        self.timestamp = datetime.now()
        self.status = "pendente"
        self.resultado = None
        
        # Ordena ações por prioridade
        self.acoes_ordenadas = sorted(
            self.acoes,
            key=lambda x: x.prioridade.value
        )
        
        # Calcula tempo estimado total
        self.tempo_estimado = sum(
            acao.tempo_estimado for acao in self.acoes
        )
        
        # Calcula probabilidade de sucesso
        self.probabilidade_sucesso = min(
            acao.probabilidade_sucesso for acao in self.acoes
        ) if self.acoes else 0.0
    
    def adicionar_acao(self, acao: Acao) -> None:
        """Adiciona uma ação ao plano."""
        self.acoes.append(acao)
        self.acoes_ordenadas = sorted(
            self.acoes,
            key=lambda x: x.prioridade.value
        )
        self.tempo_estimado += acao.tempo_estimado
        if self.acoes:
            self.probabilidade_sucesso = min(
                acao.probabilidade_sucesso for acao in self.acoes
            )
    
    def remover_acao(self, acao_id: str) -> bool:
        """Remove uma ação do plano."""
        for i, acao in enumerate(self.acoes):
            if acao.id == acao_id:
                self.acoes.pop(i)
                self.acoes_ordenadas = sorted(
                    self.acoes,
                    key=lambda x: x.prioridade.value
                )
                self.tempo_estimado -= acao.tempo_estimado
                if self.acoes:
                    self.probabilidade_sucesso = min(
                        acao.probabilidade_sucesso for acao in self.acoes
                    )
                else:
                    self.probabilidade_sucesso = 0.0
                return True
        return False
    
    def atualizar_status(self, status: str, resultado: Optional[Dict[str, Any]] = None) -> None:
        """Atualiza o status do plano."""
        self.status = status
        if resultado:
            self.resultado = resultado

class GeradorAcoes(BaseComponent):
    """Gerador de ações emergentes baseado em diagnósticos."""
    
    def __init__(self, name: str = "GeradorAcoes"):
        super().__init__(name)
        self.mapeamento_acoes: Dict[str, Dict[str, Any]] = {}
        self.tempo_estimado_padrao: float = 30.0
        self.probabilidade_sucesso_padrao: float = 0.8
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
        config_path = Path(__file__).parents[2] / "config" / "acoes_config.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_file = json.load(f)
                if "mapeamento_acoes" in config_file:
                    self.mapeamento_acoes.update(config_file["mapeamento_acoes"])
                    
                # Carrega valores padrão
                tempos_padrao = config_file.get("tempos_padrao", {})
                self.tempo_estimado_padrao = tempos_padrao.get("tempo_estimado_padrao", 30.0)
                self.probabilidade_sucesso_padrao = tempos_padrao.get("probabilidade_sucesso_padrao", 0.8)
                
                logger.info("Configurações carregadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
            raise
    
    def _salvar_historico(self) -> None:
        """Salva o histórico de planos de ação."""
        # TODO: Implementar persistência do histórico
        pass
    
    def gerar_acao(self, diagnostico, severidade: str = "ALTA") -> Optional[Acao]:
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
        
        # Determina tipo e prioridade baseado na severidade
        tipo = TipoAcao.CRITICA if severidade == "ALTA" else TipoAcao.CORRETIVA
        prioridade = PrioridadeAcao.ALTA if severidade == "ALTA" else PrioridadeAcao.MEDIA
        
        # Cria ação
        acao = Acao(
            id=acao_id,
            tipo=tipo,
            descricao=config["descricao"],
            prioridade=prioridade,
            timestamp=datetime.now(),
            diagnostico=diagnostico,
            parametros=config["parametros"],
            status="pendente",
            tempo_estimado=self.tempo_estimado_padrao,
            probabilidade_sucesso=self.probabilidade_sucesso_padrao
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

    async def gerar_acoes(self, diagnostico: Dict[str, Any]) -> List[Acao]:
        """Gera uma lista de ações baseada no diagnóstico."""
        acoes = []
        from src.services.diagnostico.rede_neural import Diagnostico as DiagnosticoNN
        from datetime import datetime
        severidade = diagnostico.get('severidade', 'ALTA')
        # Gera ação para cada métrica afetada
        for metrica in diagnostico['metricas_afetadas']:
            diag_metrica = DiagnosticoNN(
                timestamp=datetime.fromisoformat(diagnostico['timestamp']),
                anomalia_detectada=True,
                score_anomalia=1.0,
                padrao_detectado=metrica,
                confianca=1.0,
                metricas_relevantes=[metrica],
                recomendacoes=[f"Ação recomendada para {metrica}"]
            )
            acao = self.gerar_acao(diag_metrica, severidade=severidade)
            if acao:
                acoes.append(acao)
        return acoes
    
    async def gerar_plano_acao(
        self,
        diagnostico: Dict[str, Any],
        feedback: Optional[Dict[str, Any]] = None
    ) -> PlanoAcao:
        """Gera um plano de ação completo baseado no diagnóstico e feedback."""
        # Gera ações
        acoes = await self.gerar_acoes(diagnostico)
        
        # Se houver feedback, ajusta as ações
        if feedback:
            # Encontra a ação que falhou
            for acao in acoes:
                if acao.id == feedback['acao_id']:
                    # Ajusta parâmetros baseado no feedback
                    if not feedback['sucesso']:
                        # Aumenta tempo estimado e reduz probabilidade
                        acao.tempo_estimado *= 1.5
                        acao.probabilidade_sucesso *= 0.8
                        
                        # Adiciona ação alternativa
                        acao_alt = self.gerar_acao(acao.diagnostico)
                        if acao_alt:
                            acao_alt.descricao = f"Ação alternativa para {acao.descricao}"
                            acao_alt.dependencias = [acao.id]
                            acoes.append(acao_alt)
        
        # Cria plano
        plano = PlanoAcao(acoes)
        
        logger.info(f"Plano de ação gerado: {plano.id} com {len(acoes)} ações")
        return plano 