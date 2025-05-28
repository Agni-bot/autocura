"""
Behavior Emergence Engine - Fase Beta
====================================

Sistema que observa, identifica e reforça comportamentos emergentes
benéficos no sistema AutoCura.
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

class PatternType(Enum):
    """Tipos de padrões emergentes"""
    BEHAVIORAL = "behavioral"
    PERFORMANCE = "performance"
    COLLABORATIVE = "collaborative"
    ADAPTIVE = "adaptive"
    INNOVATIVE = "innovative"

class EmergenceLevel(Enum):
    """Níveis de emergência"""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    REVOLUTIONARY = "revolutionary"

@dataclass
class EmergentPattern:
    """Padrão emergente identificado"""
    pattern_id: str
    pattern_type: PatternType
    description: str
    emergence_level: EmergenceLevel
    confidence: float
    frequency: int
    impact_score: float
    first_observed: str
    last_observed: str
    agents_involved: List[str]
    context: Dict[str, Any]
    reinforcement_count: int = 0
    success_rate: float = 0.0

@dataclass
class BehaviorEvent:
    """Evento comportamental observado"""
    event_id: str
    agent_id: str
    action: str
    context: Dict[str, Any]
    outcome: Dict[str, Any]
    timestamp: str
    success: bool
    impact: float

class BehaviorEmergence:
    """
    Motor de Emergência Comportamental
    
    Observa comportamentos do sistema e identifica padrões emergentes
    que podem ser benéficos para reforçar ou prejudiciais para mitigar.
    """
    
    def __init__(self, observation_window: int = 1000, pattern_threshold: float = 0.7):
        """
        Inicializa o motor de emergência
        
        Args:
            observation_window: Janela de observação de eventos
            pattern_threshold: Limiar para identificação de padrões
        """
        self.observation_window = observation_window
        self.pattern_threshold = pattern_threshold
        
        # Armazenamento de dados
        self.behavior_events = deque(maxlen=observation_window)
        self.identified_patterns = {}
        self.reinforced_patterns = {}
        self.suppressed_patterns = {}
        
        # Configurações de análise
        self.analysis_config = {
            "min_frequency": 3,
            "min_confidence": 0.6,
            "impact_weight": 0.3,
            "novelty_weight": 0.4,
            "consistency_weight": 0.3
        }
        
        # Métricas de emergência
        self.emergence_metrics = {
            "total_patterns": 0,
            "beneficial_patterns": 0,
            "harmful_patterns": 0,
            "reinforcement_success": 0.0,
            "suppression_success": 0.0
        }
        
        logger.info("BehaviorEmergence inicializado")
    
    def observe_behavior(self, agent_id: str, action: str, context: Dict[str, Any], 
                        outcome: Dict[str, Any], success: bool, impact: float) -> str:
        """
        Observa um comportamento e registra o evento
        
        Args:
            agent_id: ID do agente
            action: Ação realizada
            context: Contexto da ação
            outcome: Resultado da ação
            success: Se a ação foi bem-sucedida
            impact: Impacto da ação (0.0 a 1.0)
            
        Returns:
            str: ID do evento registrado
        """
        event_id = f"event_{len(self.behavior_events)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        event = BehaviorEvent(
            event_id=event_id,
            agent_id=agent_id,
            action=action,
            context=context,
            outcome=outcome,
            timestamp=datetime.now().isoformat(),
            success=success,
            impact=impact
        )
        
        self.behavior_events.append(event)
        
        # Trigger análise se temos eventos suficientes
        if len(self.behavior_events) >= self.analysis_config["min_frequency"]:
            asyncio.create_task(self._analyze_recent_patterns())
        
        logger.debug(f"Comportamento observado: {agent_id} -> {action} (sucesso: {success})")
        
        return event_id
    
    async def _analyze_recent_patterns(self) -> None:
        """
        Analisa padrões emergentes nos eventos recentes
        """
        try:
            # Analisar diferentes tipos de padrões
            behavioral_patterns = await self._detect_behavioral_patterns()
            performance_patterns = await self._detect_performance_patterns()
            collaborative_patterns = await self._detect_collaborative_patterns()
            adaptive_patterns = await self._detect_adaptive_patterns()
            innovative_patterns = await self._detect_innovative_patterns()
            
            # Consolidar todos os padrões
            all_patterns = (
                behavioral_patterns + performance_patterns + 
                collaborative_patterns + adaptive_patterns + innovative_patterns
            )
            
            # Processar novos padrões
            for pattern in all_patterns:
                await self._process_new_pattern(pattern)
                
        except Exception as e:
            logger.error(f"Erro na análise de padrões: {e}")
    
    async def _detect_behavioral_patterns(self) -> List[EmergentPattern]:
        """
        Detecta padrões comportamentais emergentes
        
        Returns:
            List[EmergentPattern]: Padrões comportamentais identificados
        """
        patterns = []
        
        # Agrupar eventos por ação
        action_groups = defaultdict(list)
        for event in list(self.behavior_events)[-50:]:  # Últimos 50 eventos
            action_groups[event.action].append(event)
        
        for action, events in action_groups.items():
            if len(events) >= self.analysis_config["min_frequency"]:
                # Calcular métricas do padrão
                success_rate = sum(1 for e in events if e.success) / len(events)
                avg_impact = statistics.mean(e.impact for e in events)
                agents_involved = list(set(e.agent_id for e in events))
                
                # Determinar nível de emergência
                emergence_level = self._calculate_emergence_level(
                    frequency=len(events),
                    success_rate=success_rate,
                    impact=avg_impact,
                    novelty=self._calculate_novelty(action)
                )
                
                if success_rate >= self.analysis_config["min_confidence"]:
                    pattern = EmergentPattern(
                        pattern_id=f"behavioral_{action}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        pattern_type=PatternType.BEHAVIORAL,
                        description=f"Padrão comportamental: {action}",
                        emergence_level=emergence_level,
                        confidence=success_rate,
                        frequency=len(events),
                        impact_score=avg_impact,
                        first_observed=events[0].timestamp,
                        last_observed=events[-1].timestamp,
                        agents_involved=agents_involved,
                        context={
                            "action": action,
                            "success_rate": success_rate,
                            "avg_impact": avg_impact,
                            "sample_contexts": [e.context for e in events[:3]]
                        }
                    )
                    patterns.append(pattern)
        
        return patterns
    
    async def _detect_performance_patterns(self) -> List[EmergentPattern]:
        """
        Detecta padrões de performance emergentes
        
        Returns:
            List[EmergentPattern]: Padrões de performance identificados
        """
        patterns = []
        
        # Analisar tendências de performance por agente
        agent_performance = defaultdict(list)
        for event in list(self.behavior_events)[-100:]:
            agent_performance[event.agent_id].append(event.impact)
        
        for agent_id, impacts in agent_performance.items():
            if len(impacts) >= 5:
                # Calcular tendência
                trend = self._calculate_trend(impacts)
                avg_performance = statistics.mean(impacts)
                
                if abs(trend) > 0.1 and avg_performance > 0.6:  # Tendência significativa
                    emergence_level = EmergenceLevel.MODERATE if trend > 0 else EmergenceLevel.WEAK
                    
                    pattern = EmergentPattern(
                        pattern_id=f"performance_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        pattern_type=PatternType.PERFORMANCE,
                        description=f"Padrão de performance: {agent_id} ({'melhoria' if trend > 0 else 'declínio'})",
                        emergence_level=emergence_level,
                        confidence=min(abs(trend) * 2, 1.0),
                        frequency=len(impacts),
                        impact_score=avg_performance,
                        first_observed=list(self.behavior_events)[0].timestamp,
                        last_observed=list(self.behavior_events)[-1].timestamp,
                        agents_involved=[agent_id],
                        context={
                            "trend": trend,
                            "avg_performance": avg_performance,
                            "performance_history": impacts[-10:]
                        }
                    )
                    patterns.append(pattern)
        
        return patterns
    
    async def _detect_collaborative_patterns(self) -> List[EmergentPattern]:
        """
        Detecta padrões colaborativos emergentes
        
        Returns:
            List[EmergentPattern]: Padrões colaborativos identificados
        """
        patterns = []
        
        # Analisar colaborações entre agentes
        collaborations = defaultdict(int)
        collaboration_success = defaultdict(list)
        
        # Janela temporal para detectar colaborações
        time_window = timedelta(minutes=5)
        events_list = list(self.behavior_events)
        
        for i, event1 in enumerate(events_list):
            event1_time = datetime.fromisoformat(event1.timestamp)
            
            for event2 in events_list[i+1:i+10]:  # Próximos 10 eventos
                event2_time = datetime.fromisoformat(event2.timestamp)
                
                if event2_time - event1_time <= time_window and event1.agent_id != event2.agent_id:
                    # Possível colaboração
                    collab_key = tuple(sorted([event1.agent_id, event2.agent_id]))
                    collaborations[collab_key] += 1
                    
                    # Avaliar sucesso da colaboração
                    combined_success = (event1.success and event2.success)
                    combined_impact = (event1.impact + event2.impact) / 2
                    collaboration_success[collab_key].append((combined_success, combined_impact))
        
        # Identificar padrões colaborativos significativos
        for collab_key, count in collaborations.items():
            if count >= 3:  # Pelo menos 3 colaborações
                successes = collaboration_success[collab_key]
                success_rate = sum(1 for s, _ in successes if s) / len(successes)
                avg_impact = statistics.mean(i for _, i in successes)
                
                if success_rate >= 0.7:  # Alta taxa de sucesso
                    pattern = EmergentPattern(
                        pattern_id=f"collaborative_{collab_key[0]}_{collab_key[1]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        pattern_type=PatternType.COLLABORATIVE,
                        description=f"Padrão colaborativo entre {collab_key[0]} e {collab_key[1]}",
                        emergence_level=EmergenceLevel.MODERATE,
                        confidence=success_rate,
                        frequency=count,
                        impact_score=avg_impact,
                        first_observed=events_list[0].timestamp,
                        last_observed=events_list[-1].timestamp,
                        agents_involved=list(collab_key),
                        context={
                            "collaboration_count": count,
                            "success_rate": success_rate,
                            "avg_impact": avg_impact
                        }
                    )
                    patterns.append(pattern)
        
        return patterns
    
    async def _detect_adaptive_patterns(self) -> List[EmergentPattern]:
        """
        Detecta padrões adaptativos emergentes
        
        Returns:
            List[EmergentPattern]: Padrões adaptativos identificados
        """
        patterns = []
        
        # Analisar adaptação a contextos específicos
        context_adaptations = defaultdict(lambda: defaultdict(list))
        
        for event in list(self.behavior_events)[-50:]:
            # Extrair características do contexto
            context_key = self._extract_context_signature(event.context)
            context_adaptations[event.agent_id][context_key].append(event)
        
        for agent_id, contexts in context_adaptations.items():
            for context_key, events in contexts.items():
                if len(events) >= 3:
                    # Verificar se há melhoria ao longo do tempo
                    impacts = [e.impact for e in sorted(events, key=lambda x: x.timestamp)]
                    trend = self._calculate_trend(impacts)
                    
                    if trend > 0.1:  # Melhoria significativa
                        pattern = EmergentPattern(
                            pattern_id=f"adaptive_{agent_id}_{context_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            pattern_type=PatternType.ADAPTIVE,
                            description=f"Padrão adaptativo: {agent_id} em contexto {context_key}",
                            emergence_level=EmergenceLevel.MODERATE,
                            confidence=min(trend * 2, 1.0),
                            frequency=len(events),
                            impact_score=statistics.mean(impacts),
                            first_observed=events[0].timestamp,
                            last_observed=events[-1].timestamp,
                            agents_involved=[agent_id],
                            context={
                                "context_signature": context_key,
                                "adaptation_trend": trend,
                                "improvement": impacts[-1] - impacts[0]
                            }
                        )
                        patterns.append(pattern)
        
        return patterns
    
    async def _detect_innovative_patterns(self) -> List[EmergentPattern]:
        """
        Detecta padrões inovativos emergentes
        
        Returns:
            List[EmergentPattern]: Padrões inovativos identificados
        """
        patterns = []
        
        # Detectar ações nunca vistas antes ou combinações únicas
        action_history = set()
        recent_innovations = []
        
        for event in list(self.behavior_events):
            action_signature = f"{event.action}_{self._extract_context_signature(event.context)}"
            
            if action_signature not in action_history:
                # Possível inovação
                if event.success and event.impact > 0.7:
                    recent_innovations.append(event)
                action_history.add(action_signature)
        
        # Agrupar inovações por agente
        agent_innovations = defaultdict(list)
        for innovation in recent_innovations[-20:]:  # Últimas 20 inovações
            agent_innovations[innovation.agent_id].append(innovation)
        
        for agent_id, innovations in agent_innovations.items():
            if len(innovations) >= 2:  # Pelo menos 2 inovações
                avg_impact = statistics.mean(i.impact for i in innovations)
                
                pattern = EmergentPattern(
                    pattern_id=f"innovative_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    pattern_type=PatternType.INNOVATIVE,
                    description=f"Padrão inovativo: {agent_id}",
                    emergence_level=EmergenceLevel.STRONG,
                    confidence=0.8,  # Alta confiança para inovações bem-sucedidas
                    frequency=len(innovations),
                    impact_score=avg_impact,
                    first_observed=innovations[0].timestamp,
                    last_observed=innovations[-1].timestamp,
                    agents_involved=[agent_id],
                    context={
                        "innovation_count": len(innovations),
                        "avg_impact": avg_impact,
                        "innovations": [i.action for i in innovations]
                    }
                )
                patterns.append(pattern)
        
        return patterns
    
    async def _process_new_pattern(self, pattern: EmergentPattern) -> None:
        """
        Processa um novo padrão identificado
        
        Args:
            pattern: Padrão emergente identificado
        """
        # Verificar se já conhecemos este padrão
        existing_pattern = self._find_similar_pattern(pattern)
        
        if existing_pattern:
            # Atualizar padrão existente
            await self._update_existing_pattern(existing_pattern, pattern)
        else:
            # Novo padrão
            self.identified_patterns[pattern.pattern_id] = pattern
            self.emergence_metrics["total_patterns"] += 1
            
            # Decidir se reforçar ou suprimir
            if await self._should_reinforce_pattern(pattern):
                await self.reinforce_beneficial(pattern.pattern_id)
            elif await self._should_suppress_pattern(pattern):
                await self._suppress_harmful_pattern(pattern.pattern_id)
            
            logger.info(f"Novo padrão identificado: {pattern.description} (confiança: {pattern.confidence:.2f})")
    
    def _find_similar_pattern(self, pattern: EmergentPattern) -> Optional[str]:
        """
        Encontra padrão similar já identificado
        
        Args:
            pattern: Padrão para comparar
            
        Returns:
            Optional[str]: ID do padrão similar, se encontrado
        """
        for existing_id, existing_pattern in self.identified_patterns.items():
            if (existing_pattern.pattern_type == pattern.pattern_type and
                self._calculate_pattern_similarity(existing_pattern, pattern) > 0.8):
                return existing_id
        return None
    
    def _calculate_pattern_similarity(self, pattern1: EmergentPattern, pattern2: EmergentPattern) -> float:
        """
        Calcula similaridade entre dois padrões
        
        Args:
            pattern1: Primeiro padrão
            pattern2: Segundo padrão
            
        Returns:
            float: Similaridade (0.0 a 1.0)
        """
        # Similaridade baseada em agentes envolvidos e contexto
        agents_similarity = len(set(pattern1.agents_involved) & set(pattern2.agents_involved)) / \
                           max(len(set(pattern1.agents_involved) | set(pattern2.agents_involved)), 1)
        
        # Similaridade de impacto
        impact_similarity = 1.0 - abs(pattern1.impact_score - pattern2.impact_score)
        
        # Similaridade de confiança
        confidence_similarity = 1.0 - abs(pattern1.confidence - pattern2.confidence)
        
        return (agents_similarity + impact_similarity + confidence_similarity) / 3
    
    async def _update_existing_pattern(self, existing_id: str, new_pattern: EmergentPattern) -> None:
        """
        Atualiza padrão existente com nova observação
        
        Args:
            existing_id: ID do padrão existente
            new_pattern: Nova observação do padrão
        """
        existing = self.identified_patterns[existing_id]
        
        # Atualizar métricas
        existing.frequency += new_pattern.frequency
        existing.confidence = (existing.confidence + new_pattern.confidence) / 2
        existing.impact_score = (existing.impact_score + new_pattern.impact_score) / 2
        existing.last_observed = new_pattern.last_observed
        
        # Atualizar agentes envolvidos
        existing.agents_involved = list(set(existing.agents_involved + new_pattern.agents_involved))
        
        logger.debug(f"Padrão atualizado: {existing_id}")
    
    async def _should_reinforce_pattern(self, pattern: EmergentPattern) -> bool:
        """
        Determina se um padrão deve ser reforçado
        
        Args:
            pattern: Padrão a avaliar
            
        Returns:
            bool: True se deve ser reforçado
        """
        return (pattern.confidence >= 0.7 and 
                pattern.impact_score >= 0.6 and
                pattern.emergence_level in [EmergenceLevel.MODERATE, EmergenceLevel.STRONG, EmergenceLevel.REVOLUTIONARY])
    
    async def _should_suppress_pattern(self, pattern: EmergentPattern) -> bool:
        """
        Determina se um padrão deve ser suprimido
        
        Args:
            pattern: Padrão a avaliar
            
        Returns:
            bool: True se deve ser suprimido
        """
        return (pattern.confidence >= 0.7 and 
                pattern.impact_score < 0.3)  # Padrões prejudiciais
    
    async def reinforce_beneficial(self, pattern_id: str) -> bool:
        """
        Reforça um padrão benéfico identificado
        
        Args:
            pattern_id: ID do padrão a reforçar
            
        Returns:
            bool: True se reforçado com sucesso
        """
        try:
            if pattern_id not in self.identified_patterns:
                return False
            
            pattern = self.identified_patterns[pattern_id]
            
            # Implementar reforço específico por tipo
            if pattern.pattern_type == PatternType.BEHAVIORAL:
                await self._reinforce_behavioral_pattern(pattern)
            elif pattern.pattern_type == PatternType.COLLABORATIVE:
                await self._reinforce_collaborative_pattern(pattern)
            elif pattern.pattern_type == PatternType.INNOVATIVE:
                await self._reinforce_innovative_pattern(pattern)
            
            # Registrar reforço
            pattern.reinforcement_count += 1
            self.reinforced_patterns[pattern_id] = pattern
            self.emergence_metrics["beneficial_patterns"] += 1
            
            logger.info(f"Padrão reforçado: {pattern.description}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao reforçar padrão {pattern_id}: {e}")
            return False
    
    async def _reinforce_behavioral_pattern(self, pattern: EmergentPattern) -> None:
        """
        Reforça um padrão comportamental específico
        
        Args:
            pattern: Padrão comportamental a reforçar
        """
        # Aumentar peso dos agentes que demonstram este comportamento
        for agent_id in pattern.agents_involved:
            # Notificar sistema de swarm para aumentar peso do agente
            logger.info(f"Reforçando comportamento de {agent_id}: {pattern.context.get('action')}")
    
    async def _reinforce_collaborative_pattern(self, pattern: EmergentPattern) -> None:
        """
        Reforça um padrão colaborativo específico
        
        Args:
            pattern: Padrão colaborativo a reforçar
        """
        # Promover colaborações entre os agentes identificados
        logger.info(f"Promovendo colaboração entre: {pattern.agents_involved}")
    
    async def _reinforce_innovative_pattern(self, pattern: EmergentPattern) -> None:
        """
        Reforça um padrão inovativo específico
        
        Args:
            pattern: Padrão inovativo a reforçar
        """
        # Dar mais autonomia para agentes inovativos
        for agent_id in pattern.agents_involved:
            logger.info(f"Aumentando autonomia inovativa de {agent_id}")
    
    async def _suppress_harmful_pattern(self, pattern_id: str) -> bool:
        """
        Suprime um padrão prejudicial
        
        Args:
            pattern_id: ID do padrão a suprimir
            
        Returns:
            bool: True se suprimido com sucesso
        """
        try:
            if pattern_id not in self.identified_patterns:
                return False
            
            pattern = self.identified_patterns[pattern_id]
            
            # Implementar supressão
            for agent_id in pattern.agents_involved:
                logger.warning(f"Suprimindo comportamento prejudicial de {agent_id}: {pattern.description}")
            
            self.suppressed_patterns[pattern_id] = pattern
            self.emergence_metrics["harmful_patterns"] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao suprimir padrão {pattern_id}: {e}")
            return False
    
    def _calculate_emergence_level(self, frequency: int, success_rate: float, 
                                 impact: float, novelty: float) -> EmergenceLevel:
        """
        Calcula o nível de emergência de um padrão
        
        Args:
            frequency: Frequência do padrão
            success_rate: Taxa de sucesso
            impact: Impacto médio
            novelty: Nível de novidade
            
        Returns:
            EmergenceLevel: Nível de emergência calculado
        """
        score = (
            (frequency / 10) * 0.2 +
            success_rate * 0.3 +
            impact * 0.3 +
            novelty * 0.2
        )
        
        if score >= 0.9:
            return EmergenceLevel.REVOLUTIONARY
        elif score >= 0.7:
            return EmergenceLevel.STRONG
        elif score >= 0.5:
            return EmergenceLevel.MODERATE
        else:
            return EmergenceLevel.WEAK
    
    def _calculate_novelty(self, action: str) -> float:
        """
        Calcula o nível de novidade de uma ação
        
        Args:
            action: Ação a avaliar
            
        Returns:
            float: Nível de novidade (0.0 a 1.0)
        """
        # Contar quantas vezes esta ação foi vista
        action_count = sum(1 for event in self.behavior_events if event.action == action)
        total_events = len(self.behavior_events)
        
        if total_events == 0:
            return 1.0
        
        # Novidade inversamente proporcional à frequência
        frequency_ratio = action_count / total_events
        return max(0.0, 1.0 - frequency_ratio * 2)
    
    def _calculate_trend(self, values: List[float]) -> float:
        """
        Calcula tendência em uma série de valores
        
        Args:
            values: Lista de valores
            
        Returns:
            float: Tendência (-1.0 a 1.0)
        """
        if len(values) < 2:
            return 0.0
        
        # Regressão linear simples
        n = len(values)
        x = list(range(n))
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        # Coeficiente angular
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Normalizar para -1.0 a 1.0
        return max(-1.0, min(1.0, slope))
    
    def _extract_context_signature(self, context: Dict[str, Any]) -> str:
        """
        Extrai assinatura do contexto para agrupamento
        
        Args:
            context: Contexto a processar
            
        Returns:
            str: Assinatura do contexto
        """
        # Simplificação: usar chaves principais do contexto
        key_elements = []
        for key in sorted(context.keys())[:3]:  # Primeiras 3 chaves
            value = str(context[key])[:10]  # Primeiros 10 caracteres
            key_elements.append(f"{key}:{value}")
        
        return "_".join(key_elements)
    
    def get_emergence_status(self) -> Dict[str, Any]:
        """
        Retorna status atual da emergência
        
        Returns:
            Dict: Status da emergência
        """
        return {
            "total_events": len(self.behavior_events),
            "identified_patterns": len(self.identified_patterns),
            "reinforced_patterns": len(self.reinforced_patterns),
            "suppressed_patterns": len(self.suppressed_patterns),
            "metrics": self.emergence_metrics,
            "recent_patterns": [
                {
                    "id": pid,
                    "type": pattern.pattern_type.value,
                    "description": pattern.description,
                    "confidence": pattern.confidence,
                    "emergence_level": pattern.emergence_level.value
                }
                for pid, pattern in list(self.identified_patterns.items())[-5:]
            ]
        }
    
    def export_patterns(self) -> Dict[str, Any]:
        """
        Exporta todos os padrões identificados
        
        Returns:
            Dict: Padrões exportados
        """
        return {
            "identified_patterns": {
                pid: asdict(pattern) for pid, pattern in self.identified_patterns.items()
            },
            "reinforced_patterns": {
                pid: asdict(pattern) for pid, pattern in self.reinforced_patterns.items()
            },
            "suppressed_patterns": {
                pid: asdict(pattern) for pid, pattern in self.suppressed_patterns.items()
            },
            "metrics": self.emergence_metrics
        } 