"""
Swarm Intelligence Coordinator - Fase Beta
==========================================

Coordenador de múltiplos agentes para tomada de decisão coletiva
e comportamento emergente inteligente.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import uuid

logger = logging.getLogger(__name__)

class ConsensusType(Enum):
    """Tipos de consenso disponíveis"""
    BYZANTINE_FAULT_TOLERANT = "byzantine_fault_tolerant"
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_CONSENSUS = "weighted_consensus"
    EMERGENT_CONSENSUS = "emergent_consensus"

class AgentRole(Enum):
    """Papéis dos agentes no swarm"""
    RESEARCHER = "researcher"
    ML_ENGINEER = "ml_engineer"
    SOFTWARE_ENGINEER = "software_engineer"
    DATA_SCIENTIST = "data_scientist"
    ETHICS_SPECIALIST = "ethics_specialist"
    ORCHESTRATOR = "orchestrator"

@dataclass
class AgentDecision:
    """Decisão de um agente individual"""
    agent_id: str
    role: AgentRole
    decision: Dict[str, Any]
    confidence: float
    reasoning: str
    timestamp: str
    weight: float = 1.0

@dataclass
class SwarmDecision:
    """Decisão coletiva do swarm"""
    decision_id: str
    problem: Dict[str, Any]
    individual_decisions: List[AgentDecision]
    consensus_decision: Dict[str, Any]
    consensus_type: ConsensusType
    confidence: float
    reasoning: str
    timestamp: str
    execution_approved: bool = False

class SwarmCoordinator:
    """
    Coordenador de Swarm Intelligence para decisões coletivas
    """
    
    def __init__(self, consensus_mechanism: ConsensusType = ConsensusType.BYZANTINE_FAULT_TOLERANT):
        """
        Inicializa o coordenador de swarm
        
        Args:
            consensus_mechanism: Tipo de consenso a ser usado
        """
        self.consensus_mechanism = consensus_mechanism
        self.agents = {}
        self.active_decisions = {}
        self.decision_history = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Configurações de consenso
        self.consensus_config = {
            ConsensusType.BYZANTINE_FAULT_TOLERANT: {
                "min_agents": 4,
                "fault_tolerance": 0.33,
                "min_confidence": 0.7
            },
            ConsensusType.MAJORITY_VOTE: {
                "min_agents": 3,
                "min_confidence": 0.6
            },
            ConsensusType.WEIGHTED_CONSENSUS: {
                "min_agents": 3,
                "min_confidence": 0.65
            },
            ConsensusType.EMERGENT_CONSENSUS: {
                "min_agents": 5,
                "emergence_threshold": 0.8,
                "min_confidence": 0.75
            }
        }
        
        logger.info(f"SwarmCoordinator inicializado com consenso: {consensus_mechanism.value}")
    
    def register_agent(self, agent_id: str, role: AgentRole, weight: float = 1.0) -> bool:
        """
        Registra um novo agente no swarm
        
        Args:
            agent_id: ID único do agente
            role: Papel do agente
            weight: Peso da decisão do agente
            
        Returns:
            bool: True se registrado com sucesso
        """
        try:
            self.agents[agent_id] = {
                "role": role,
                "weight": weight,
                "active": True,
                "decisions_count": 0,
                "success_rate": 1.0,
                "last_activity": datetime.now().isoformat()
            }
            
            logger.info(f"Agente {agent_id} ({role.value}) registrado com peso {weight}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao registrar agente {agent_id}: {e}")
            return False
    
    async def coordinate_decision(self, problem: Dict[str, Any]) -> SwarmDecision:
        """
        Coordena uma decisão coletiva do swarm
        
        Args:
            problem: Problema a ser resolvido
            
        Returns:
            SwarmDecision: Decisão coletiva
        """
        decision_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Iniciando coordenação de decisão {decision_id}")
            
            # Validar se temos agentes suficientes
            active_agents = [aid for aid, info in self.agents.items() if info["active"]]
            min_agents = self.consensus_config[self.consensus_mechanism]["min_agents"]
            
            if len(active_agents) < min_agents:
                raise ValueError(f"Agentes insuficientes: {len(active_agents)} < {min_agents}")
            
            # Coletar decisões individuais
            individual_decisions = await self._collect_individual_decisions(
                decision_id, problem, active_agents
            )
            
            # Aplicar consenso
            consensus_decision = await self._apply_consensus(individual_decisions, problem)
            
            # Criar decisão do swarm
            swarm_decision = SwarmDecision(
                decision_id=decision_id,
                problem=problem,
                individual_decisions=individual_decisions,
                consensus_decision=consensus_decision["decision"],
                consensus_type=self.consensus_mechanism,
                confidence=consensus_decision["confidence"],
                reasoning=consensus_decision["reasoning"],
                timestamp=datetime.now().isoformat(),
                execution_approved=consensus_decision["confidence"] >= 
                    self.consensus_config[self.consensus_mechanism]["min_confidence"]
            )
            
            # Armazenar decisão
            self.active_decisions[decision_id] = swarm_decision
            self.decision_history.append(swarm_decision)
            
            logger.info(f"Decisão {decision_id} coordenada com confiança {consensus_decision['confidence']:.2f}")
            
            return swarm_decision
            
        except Exception as e:
            logger.error(f"Erro na coordenação de decisão {decision_id}: {e}")
            raise
    
    async def _collect_individual_decisions(
        self, 
        decision_id: str, 
        problem: Dict[str, Any], 
        agent_ids: List[str]
    ) -> List[AgentDecision]:
        """
        Coleta decisões individuais de todos os agentes
        
        Args:
            decision_id: ID da decisão
            problem: Problema a ser resolvido
            agent_ids: Lista de IDs dos agentes
            
        Returns:
            List[AgentDecision]: Lista de decisões individuais
        """
        tasks = []
        
        for agent_id in agent_ids:
            task = asyncio.create_task(
                self._get_agent_decision(decision_id, agent_id, problem)
            )
            tasks.append(task)
        
        # Aguardar todas as decisões com timeout
        try:
            decisions = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30.0
            )
            
            # Filtrar decisões válidas
            valid_decisions = [
                d for d in decisions 
                if isinstance(d, AgentDecision)
            ]
            
            logger.info(f"Coletadas {len(valid_decisions)} decisões válidas de {len(agent_ids)} agentes")
            
            return valid_decisions
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout na coleta de decisões para {decision_id}")
            return []
    
    async def _get_agent_decision(
        self, 
        decision_id: str, 
        agent_id: str, 
        problem: Dict[str, Any]
    ) -> AgentDecision:
        """
        Obtém decisão de um agente específico
        
        Args:
            decision_id: ID da decisão
            agent_id: ID do agente
            problem: Problema a ser resolvido
            
        Returns:
            AgentDecision: Decisão do agente
        """
        try:
            agent_info = self.agents[agent_id]
            
            # Simular processamento do agente (será substituído por IA real)
            await asyncio.sleep(0.1)  # Simular tempo de processamento
            
            # Por enquanto, gerar decisão simulada baseada no papel
            decision = await self._simulate_agent_decision(agent_info["role"], problem)
            
            agent_decision = AgentDecision(
                agent_id=agent_id,
                role=agent_info["role"],
                decision=decision["decision"],
                confidence=decision["confidence"],
                reasoning=decision["reasoning"],
                timestamp=datetime.now().isoformat(),
                weight=agent_info["weight"]
            )
            
            # Atualizar estatísticas do agente
            self.agents[agent_id]["decisions_count"] += 1
            self.agents[agent_id]["last_activity"] = datetime.now().isoformat()
            
            return agent_decision
            
        except Exception as e:
            logger.error(f"Erro ao obter decisão do agente {agent_id}: {e}")
            raise
    
    async def _simulate_agent_decision(self, role: AgentRole, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simula decisão de um agente baseada em seu papel
        (Será substituído por IA real na implementação completa)
        
        Args:
            role: Papel do agente
            problem: Problema a ser resolvido
            
        Returns:
            Dict: Decisão simulada
        """
        # Simulações específicas por papel
        role_behaviors = {
            AgentRole.RESEARCHER: {
                "focus": "inovação e pesquisa",
                "confidence_base": 0.8,
                "decision_style": "exploratório"
            },
            AgentRole.ML_ENGINEER: {
                "focus": "implementação técnica",
                "confidence_base": 0.85,
                "decision_style": "pragmático"
            },
            AgentRole.SOFTWARE_ENGINEER: {
                "focus": "arquitetura e escalabilidade",
                "confidence_base": 0.9,
                "decision_style": "estruturado"
            },
            AgentRole.DATA_SCIENTIST: {
                "focus": "análise de dados",
                "confidence_base": 0.75,
                "decision_style": "analítico"
            },
            AgentRole.ETHICS_SPECIALIST: {
                "focus": "ética e segurança",
                "confidence_base": 0.95,
                "decision_style": "conservador"
            },
            AgentRole.ORCHESTRATOR: {
                "focus": "coordenação geral",
                "confidence_base": 0.8,
                "decision_style": "equilibrado"
            }
        }
        
        behavior = role_behaviors.get(role, role_behaviors[AgentRole.ORCHESTRATOR])
        
        return {
            "decision": {
                "action": f"Ação recomendada pelo {role.value}",
                "priority": "alta" if behavior["confidence_base"] > 0.8 else "média",
                "focus_area": behavior["focus"],
                "style": behavior["decision_style"]
            },
            "confidence": behavior["confidence_base"],
            "reasoning": f"Decisão baseada em {behavior['focus']} com estilo {behavior['decision_style']}"
        }
    
    async def _apply_consensus(
        self, 
        decisions: List[AgentDecision], 
        problem: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aplica o mecanismo de consenso às decisões individuais
        
        Args:
            decisions: Lista de decisões individuais
            problem: Problema original
            
        Returns:
            Dict: Decisão de consenso
        """
        if self.consensus_mechanism == ConsensusType.BYZANTINE_FAULT_TOLERANT:
            return await self._byzantine_consensus(decisions)
        elif self.consensus_mechanism == ConsensusType.MAJORITY_VOTE:
            return await self._majority_vote_consensus(decisions)
        elif self.consensus_mechanism == ConsensusType.WEIGHTED_CONSENSUS:
            return await self._weighted_consensus(decisions)
        elif self.consensus_mechanism == ConsensusType.EMERGENT_CONSENSUS:
            return await self._emergent_consensus(decisions)
        else:
            raise ValueError(f"Mecanismo de consenso não suportado: {self.consensus_mechanism}")
    
    async def _byzantine_consensus(self, decisions: List[AgentDecision]) -> Dict[str, Any]:
        """
        Implementa consenso Byzantine Fault Tolerant
        
        Args:
            decisions: Lista de decisões
            
        Returns:
            Dict: Decisão de consenso
        """
        # Implementação simplificada do BFT
        # Em produção, seria um algoritmo BFT completo
        
        if len(decisions) < 4:
            raise ValueError("BFT requer pelo menos 4 agentes")
        
        # Agrupar decisões similares
        decision_groups = {}
        for decision in decisions:
            key = str(decision.decision.get("action", ""))
            if key not in decision_groups:
                decision_groups[key] = []
            decision_groups[key].append(decision)
        
        # Encontrar grupo majoritário
        largest_group = max(decision_groups.values(), key=len)
        
        if len(largest_group) >= len(decisions) * 0.67:  # 2/3 majority
            avg_confidence = sum(d.confidence for d in largest_group) / len(largest_group)
            
            return {
                "decision": largest_group[0].decision,
                "confidence": avg_confidence,
                "reasoning": f"Consenso BFT com {len(largest_group)}/{len(decisions)} agentes"
            }
        else:
            return {
                "decision": {"action": "Consenso não alcançado"},
                "confidence": 0.0,
                "reasoning": "Falha em alcançar consenso BFT (2/3 majority)"
            }
    
    async def _majority_vote_consensus(self, decisions: List[AgentDecision]) -> Dict[str, Any]:
        """
        Implementa consenso por voto majoritário
        
        Args:
            decisions: Lista de decisões
            
        Returns:
            Dict: Decisão de consenso
        """
        if not decisions:
            return {
                "decision": {"action": "Nenhuma decisão disponível"},
                "confidence": 0.0,
                "reasoning": "Nenhuma decisão para processar"
            }
        
        # Voto simples - decisão com maior confiança
        best_decision = max(decisions, key=lambda d: d.confidence)
        avg_confidence = sum(d.confidence for d in decisions) / len(decisions)
        
        return {
            "decision": best_decision.decision,
            "confidence": avg_confidence,
            "reasoning": f"Voto majoritário - melhor confiança: {best_decision.confidence:.2f}"
        }
    
    async def _weighted_consensus(self, decisions: List[AgentDecision]) -> Dict[str, Any]:
        """
        Implementa consenso ponderado por peso dos agentes
        
        Args:
            decisions: Lista de decisões
            
        Returns:
            Dict: Decisão de consenso
        """
        if not decisions:
            return {
                "decision": {"action": "Nenhuma decisão disponível"},
                "confidence": 0.0,
                "reasoning": "Nenhuma decisão para processar"
            }
        
        # Calcular score ponderado
        total_weight = sum(d.weight for d in decisions)
        weighted_confidence = sum(d.confidence * d.weight for d in decisions) / total_weight
        
        # Decisão com maior score ponderado
        best_decision = max(decisions, key=lambda d: d.confidence * d.weight)
        
        return {
            "decision": best_decision.decision,
            "confidence": weighted_confidence,
            "reasoning": f"Consenso ponderado - score: {best_decision.confidence * best_decision.weight:.2f}"
        }
    
    async def _emergent_consensus(self, decisions: List[AgentDecision]) -> Dict[str, Any]:
        """
        Implementa consenso emergente baseado em padrões
        
        Args:
            decisions: Lista de decisões
            
        Returns:
            Dict: Decisão de consenso
        """
        # Implementação simplificada de emergência
        # Em produção, usaria algoritmos de emergência mais sofisticados
        
        if len(decisions) < 5:
            return await self._weighted_consensus(decisions)
        
        # Detectar padrões emergentes
        patterns = {}
        for decision in decisions:
            for key, value in decision.decision.items():
                if key not in patterns:
                    patterns[key] = {}
                if value not in patterns[key]:
                    patterns[key][value] = 0
                patterns[key][value] += decision.confidence * decision.weight
        
        # Construir decisão emergente
        emergent_decision = {}
        total_confidence = 0
        
        for key, values in patterns.items():
            best_value = max(values.items(), key=lambda x: x[1])
            emergent_decision[key] = best_value[0]
            total_confidence += best_value[1]
        
        avg_confidence = total_confidence / len(patterns) if patterns else 0
        
        return {
            "decision": emergent_decision,
            "confidence": min(avg_confidence / 10, 1.0),  # Normalizar
            "reasoning": f"Consenso emergente com {len(patterns)} padrões detectados"
        }
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """
        Retorna status atual do swarm
        
        Returns:
            Dict: Status do swarm
        """
        active_agents = sum(1 for info in self.agents.values() if info["active"])
        
        return {
            "total_agents": len(self.agents),
            "active_agents": active_agents,
            "consensus_mechanism": self.consensus_mechanism.value,
            "active_decisions": len(self.active_decisions),
            "total_decisions": len(self.decision_history),
            "agents": {
                aid: {
                    "role": info["role"].value,
                    "weight": info["weight"],
                    "active": info["active"],
                    "decisions_count": info["decisions_count"],
                    "success_rate": info["success_rate"]
                }
                for aid, info in self.agents.items()
            }
        }
    
    def export_decision_history(self) -> List[Dict[str, Any]]:
        """
        Exporta histórico de decisões
        
        Returns:
            List[Dict]: Histórico serializado
        """
        return [asdict(decision) for decision in self.decision_history] 