"""
Módulo de diagnóstico do sistema AutoCura.

Este módulo implementa funcionalidades avançadas de diagnóstico, incluindo:
- Detecção de problemas
- Análise de causa raiz
- Geração de recomendações
- Histórico de diagnósticos
- Integração com métricas e logs
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class Severidade(Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

class StatusDiagnostico(Enum):
    ATIVO = "ativo"
    RESOLVIDO = "resolvido"
    EM_ANALISE = "em_analise"
    FALSO_POSITIVO = "falso_positivo"

@dataclass
class Problema:
    id: str
    titulo: str
    descricao: str
    causa_raiz: str
    recomendacoes: List[str]
    timestamp: datetime
    status: StatusDiagnostico
    severidade: Severidade
    componentes_afetados: List[str]
    metricas: Dict[str, float]
    logs: List[str]
    metadata: Dict[str, Any]

class SistemaDiagnostico:
    def __init__(self):
        self.problemas: Dict[str, Problema] = {}
        self.historico: List[Dict] = []
        self._configurar_logging()

    def _configurar_logging(self):
        """Configura logging específico para diagnóstico."""
        handler = logging.FileHandler('diagnostico.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    def analisar_metricas(self, metricas: Dict[str, float]) -> List[Problema]:
        """
        Analisa métricas do sistema e identifica problemas potenciais.
        
        Args:
            metricas: Dicionário com métricas do sistema
            
        Returns:
            Lista de problemas identificados
        """
        problemas = []
        
        # Análise de CPU
        if metricas.get('cpu_uso', 0) > 90:
            problemas.append(self._criar_problema_cpu(metricas))
            
        # Análise de Memória
        if metricas.get('memoria_uso', 0) > 85:
            problemas.append(self._criar_problema_memoria(metricas))
            
        # Análise de Latência
        if metricas.get('latencia_media', 0) > 1000:  # ms
            problemas.append(self._criar_problema_latencia(metricas))
            
        return problemas

    def _criar_problema_cpu(self, metricas: Dict[str, float]) -> Problema:
        """Cria um problema relacionado a uso alto de CPU."""
        return Problema(
            id=f"cpu_{datetime.utcnow().timestamp()}",
            titulo="Alto uso de CPU",
            descricao=f"CPU atingiu {metricas['cpu_uso']}% de utilização",
            causa_raiz="Possível vazamento de memória ou processo com alto consumo",
            recomendacoes=[
                "Verificar processos com alto consumo de CPU",
                "Analisar logs de aplicação",
                "Considerar escalonamento horizontal"
            ],
            timestamp=datetime.utcnow(),
            status=StatusDiagnostico.ATIVO,
            severidade=Severidade.ALTA,
            componentes_afetados=["CPU"],
            metricas=metricas,
            logs=[],
            metadata={"tipo": "recursos", "componente": "cpu"}
        )

    def _criar_problema_memoria(self, metricas: Dict[str, float]) -> Problema:
        """Cria um problema relacionado a uso alto de memória."""
        return Problema(
            id=f"mem_{datetime.utcnow().timestamp()}",
            titulo="Alto uso de memória",
            descricao=f"Memória atingiu {metricas['memoria_uso']}% de utilização",
            causa_raiz="Possível vazamento de memória ou cache excessivo",
            recomendacoes=[
                "Verificar processos com alto consumo de memória",
                "Limpar caches não utilizados",
                "Considerar aumento de memória"
            ],
            timestamp=datetime.utcnow(),
            status=StatusDiagnostico.ATIVO,
            severidade=Severidade.ALTA,
            componentes_afetados=["Memória"],
            metricas=metricas,
            logs=[],
            metadata={"tipo": "recursos", "componente": "memoria"}
        )

    def _criar_problema_latencia(self, metricas: Dict[str, float]) -> Problema:
        """Cria um problema relacionado a alta latência."""
        return Problema(
            id=f"lat_{datetime.utcnow().timestamp()}",
            titulo="Alta latência detectada",
            descricao=f"Latência média de {metricas['latencia_media']}ms",
            causa_raiz="Possível gargalo de rede ou processamento",
            recomendacoes=[
                "Verificar conexões de rede",
                "Otimizar consultas ao banco de dados",
                "Considerar CDN para conteúdo estático"
            ],
            timestamp=datetime.utcnow(),
            status=StatusDiagnostico.ATIVO,
            severidade=Severidade.MEDIA,
            componentes_afetados=["Rede", "Aplicação"],
            metricas=metricas,
            logs=[],
            metadata={"tipo": "performance", "componente": "latencia"}
        )

    def registrar_problema(self, problema: Problema):
        """
        Registra um novo problema no sistema.
        
        Args:
            problema: Instância de Problema a ser registrada
        """
        self.problemas[problema.id] = problema
        self.historico.append({
            "id": problema.id,
            "timestamp": problema.timestamp,
            "tipo": problema.metadata.get("tipo"),
            "severidade": problema.severidade.value,
            "status": problema.status.value
        })
        logger.info(f"Problema registrado: {problema.id} - {problema.titulo}")

    def obter_problema(self, problema_id: str) -> Optional[Problema]:
        """
        Obtém detalhes de um problema específico.
        
        Args:
            problema_id: ID do problema
            
        Returns:
            Instância de Problema ou None se não encontrado
        """
        return self.problemas.get(problema_id)

    def listar_problemas(
        self,
        status: Optional[StatusDiagnostico] = None,
        severidade: Optional[Severidade] = None
    ) -> List[Problema]:
        """
        Lista problemas com filtros opcionais.
        
        Args:
            status: Filtro por status
            severidade: Filtro por severidade
            
        Returns:
            Lista de problemas filtrados
        """
        problemas = self.problemas.values()
        
        if status:
            problemas = [p for p in problemas if p.status == status]
            
        if severidade:
            problemas = [p for p in problemas if p.severidade == severidade]
            
        return list(problemas)

    def obter_historico(
        self,
        inicio: Optional[datetime] = None,
        fim: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Obtém histórico de problemas com filtros temporais.
        
        Args:
            inicio: Data/hora inicial
            fim: Data/hora final
            
        Returns:
            Lista de registros históricos
        """
        historico = self.historico
        
        if inicio:
            historico = [h for h in historico if h["timestamp"] >= inicio]
            
        if fim:
            historico = [h for h in historico if h["timestamp"] <= fim]
            
        return historico

    def atualizar_status(self, problema_id: str, novo_status: StatusDiagnostico):
        """
        Atualiza o status de um problema.
        
        Args:
            problema_id: ID do problema
            novo_status: Novo status a ser definido
        """
        if problema_id in self.problemas:
            self.problemas[problema_id].status = novo_status
            logger.info(f"Status atualizado para {problema_id}: {novo_status.value}")

    def adicionar_recomendacao(self, problema_id: str, recomendacao: str):
        """
        Adiciona uma nova recomendação a um problema.
        
        Args:
            problema_id: ID do problema
            recomendacao: Nova recomendação
        """
        if problema_id in self.problemas:
            self.problemas[problema_id].recomendacoes.append(recomendacao)
            logger.info(f"Nova recomendação adicionada ao problema {problema_id}")

    def adicionar_log(self, problema_id: str, log: str):
        """
        Adiciona um novo log a um problema.
        
        Args:
            problema_id: ID do problema
            log: Nova entrada de log
        """
        if problema_id in self.problemas:
            self.problemas[problema_id].logs.append(log)
            logger.info(f"Novo log adicionado ao problema {problema_id}") 