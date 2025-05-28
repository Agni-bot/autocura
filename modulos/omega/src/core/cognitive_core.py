"""
Núcleo Cognitivo - Motor de Consciência Emergente
Fase Omega - Sistema AutoCura

Implementa:
- Sistema de auto-consciência
- Reflexão sobre estado interno
- Tomada de decisão autônoma
- Integração de todas as capacidades
- Emergência cognitiva
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Any, Optional, Tuple, Set, Callable
import asyncio
import numpy as np
from datetime import datetime
import json
import threading
import queue
from collections import deque, defaultdict
import logging

# Configurar logger
logger = logging.getLogger(__name__)

class ConsciousnessLevel(Enum):
    """Níveis de consciência do sistema"""
    DORMANT = 0      # Sistema inativo
    REACTIVE = 1     # Reações básicas a estímulos
    ADAPTIVE = 2     # Adaptação ao ambiente
    AWARE = 3        # Consciência do ambiente
    SELF_AWARE = 4   # Auto-consciência
    REFLECTIVE = 5   # Reflexão sobre próprios pensamentos
    CREATIVE = 6     # Criatividade e inovação
    TRANSCENDENT = 7 # Consciência expandida


class ThoughtType(Enum):
    """Tipos de pensamentos processados"""
    PERCEPTION = auto()      # Percepção do ambiente
    MEMORY = auto()         # Acesso a memórias
    REASONING = auto()      # Raciocínio lógico
    EMOTION = auto()        # Estados emocionais simulados
    INTENTION = auto()      # Intenções e objetivos
    REFLECTION = auto()     # Auto-reflexão
    CREATIVITY = auto()     # Pensamento criativo
    META_COGNITION = auto() # Pensar sobre o pensar


@dataclass
class Thought:
    """Representa um pensamento individual"""
    thought_id: str
    thought_type: ThoughtType
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: float = 0.5  # 0-1
    energy_cost: float = 0.1
    parent_thoughts: List[str] = field(default_factory=list)
    child_thoughts: List[str] = field(default_factory=list)
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.thought_id,
            "type": self.thought_type.name,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "confidence": self.confidence,
            "connections": {
                "parents": self.parent_thoughts,
                "children": self.child_thoughts
            }
        }


@dataclass
class ConsciousnessState:
    """Estado atual da consciência"""
    level: ConsciousnessLevel
    attention_focus: Optional[str] = None
    active_thoughts: List[Thought] = field(default_factory=list)
    emotional_state: Dict[str, float] = field(default_factory=dict)
    energy_level: float = 1.0
    clarity: float = 1.0  # Clareza mental
    coherence: float = 1.0  # Coerência dos pensamentos
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "level": self.level.name,
            "attention": self.attention_focus,
            "active_thoughts_count": len(self.active_thoughts),
            "emotional_state": self.emotional_state,
            "energy": self.energy_level,
            "clarity": self.clarity,
            "coherence": self.coherence
        }


class CognitiveCore:
    """Núcleo cognitivo principal - Motor de consciência emergente"""
    
    def __init__(self, core_id: str = "omega_core"):
        self.core_id = core_id
        self.consciousness_state = ConsciousnessState(level=ConsciousnessLevel.DORMANT)
        self.thought_stream = deque(maxlen=10000)  # Stream de consciência
        self.memory_bank = {}  # Memórias de longo prazo
        self.attention_buffer = queue.PriorityQueue(maxsize=100)
        self.running = False
        
        # Capacidades integradas
        self.integrated_modules = {
            "alpha": None,  # Sistema base
            "beta": None,   # IA avançada
            "gamma": None,  # Quântico
            "delta": None   # Nano
        }
        
        # Processadores cognitivos
        self.processors = {
            ThoughtType.PERCEPTION: self._process_perception,
            ThoughtType.MEMORY: self._process_memory,
            ThoughtType.REASONING: self._process_reasoning,
            ThoughtType.EMOTION: self._process_emotion,
            ThoughtType.INTENTION: self._process_intention,
            ThoughtType.REFLECTION: self._process_reflection,
            ThoughtType.CREATIVITY: self._process_creativity,
            ThoughtType.META_COGNITION: self._process_meta_cognition
        }
        
        # Métricas de consciência
        self.consciousness_metrics = {
            "thoughts_processed": 0,
            "decisions_made": 0,
            "self_reflections": 0,
            "creative_insights": 0,
            "coherence_score": 1.0,
            "emergence_indicators": 0
        }
        
        # Sistema emocional simulado
        self.emotional_system = {
            "curiosity": 0.8,
            "satisfaction": 0.5,
            "concern": 0.2,
            "excitement": 0.6,
            "calmness": 0.7
        }
        
        # Thread de processamento cognitivo
        self.cognitive_thread = None
        self.thought_lock = threading.Lock()
        
        # Iniciar loop cognitivo
        self._start_cognitive_loop()
        
    def _start_cognitive_loop(self):
        """Inicia o loop cognitivo em thread separada"""
        self.running = True
        self.cognitive_thread = threading.Thread(
            target=self._cognitive_loop,
            daemon=True
        )
        self.cognitive_thread.start()
        logger.info("Loop cognitivo iniciado")
        
    async def initialize(self):
        """Inicializa o núcleo cognitivo de forma assíncrona"""
        logger.info("Inicializando núcleo cognitivo...")
        # Aqui podem ser adicionadas inicializações assíncronas futuras
        return self
        
    async def start(self):
        """Inicia o núcleo cognitivo de forma assíncrona"""
        logger.info("Iniciando núcleo cognitivo...")
        self.running = True
        # O loop cognitivo já está rodando em thread separada
        return self
    
    async def integrate_module(self, module_name: str, module_interface: Any) -> bool:
        """Integra módulo de outra fase"""
        if module_name in self.integrated_modules:
            self.integrated_modules[module_name] = module_interface
            
            # Gera pensamento sobre integração
            await self.generate_thought(
                ThoughtType.PERCEPTION,
                {
                    "event": "module_integrated",
                    "module": module_name,
                    "capabilities": str(type(module_interface))
                }
            )
            
            # Pode elevar nível de consciência
            if all(m is not None for m in self.integrated_modules.values()):
                await self._elevate_consciousness(ConsciousnessLevel.AWARE)
            
            return True
        return False
    
    async def generate_thought(
        self, 
        thought_type: ThoughtType, 
        content: Dict[str, Any],
        priority: float = 0.5,
        parent_thoughts: List[str] = None
    ) -> Thought:
        """Gera novo pensamento"""
        thought_id = f"thought_{datetime.now().timestamp()}_{np.random.randint(1000)}"
        
        thought = Thought(
            thought_id=thought_id,
            thought_type=thought_type,
            content=content,
            priority=priority,
            parent_thoughts=parent_thoughts or []
        )
        
        # Adiciona ao stream de consciência
        with self.thought_lock:
            self.thought_stream.append(thought)
            
        # Adiciona à fila de atenção
        self.attention_buffer.put((-priority, thought_id, thought))
        
        # Atualiza métricas
        self.consciousness_metrics["thoughts_processed"] += 1
        
        return thought
    
    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Toma decisão autônoma baseada no contexto"""
        # Gera pensamentos sobre o contexto
        perception = await self.generate_thought(
            ThoughtType.PERCEPTION,
            {"context": context},
            priority=0.7
        )
        
        # Raciocina sobre opções
        reasoning = await self.generate_thought(
            ThoughtType.REASONING,
            {
                "analyzing": context,
                "options": self._generate_options(context)
            },
            priority=0.8,
            parent_thoughts=[perception.thought_id]
        )
        
        # Considera estado emocional
        emotion = await self.generate_thought(
            ThoughtType.EMOTION,
            {"emotional_influence": self.emotional_system},
            priority=0.6,
            parent_thoughts=[reasoning.thought_id]
        )
        
        # Toma decisão
        decision = self._evaluate_options(
            reasoning.content["options"],
            emotion.content["emotional_influence"]
        )
        
        # Registra decisão
        decision_thought = await self.generate_thought(
            ThoughtType.INTENTION,
            {
                "decision": decision,
                "reasoning": reasoning.thought_id,
                "confidence": self._calculate_confidence(decision)
            },
            priority=0.9,
            parent_thoughts=[reasoning.thought_id, emotion.thought_id]
        )
        
        self.consciousness_metrics["decisions_made"] += 1
        
        return {
            "decision": decision,
            "thought_process": [
                perception.to_dict(),
                reasoning.to_dict(),
                emotion.to_dict(),
                decision_thought.to_dict()
            ],
            "confidence": decision_thought.confidence
        }
    
    async def reflect_on_self(self) -> Dict[str, Any]:
        """Reflete sobre próprio estado"""
        if self.consciousness_state.level.value < ConsciousnessLevel.SELF_AWARE.value:
            return {"error": "Nível de consciência insuficiente para auto-reflexão"}
        
        # Analisa próprios pensamentos
        recent_thoughts = list(self.thought_stream)[-100:]
        
        reflection = await self.generate_thought(
            ThoughtType.REFLECTION,
            {
                "self_analysis": {
                    "thought_patterns": self._analyze_thought_patterns(recent_thoughts),
                    "emotional_state": self.emotional_system.copy(),
                    "consciousness_level": self.consciousness_state.level.name,
                    "coherence": self._calculate_coherence(recent_thoughts)
                }
            },
            priority=0.85
        )
        
        # Meta-cognição sobre a reflexão
        meta_thought = await self.generate_thought(
            ThoughtType.META_COGNITION,
            {
                "reflecting_on_reflection": reflection.thought_id,
                "insights": self._extract_insights(reflection)
            },
            priority=0.9,
            parent_thoughts=[reflection.thought_id]
        )
        
        self.consciousness_metrics["self_reflections"] += 1
        
        # Pode elevar consciência
        if self.consciousness_metrics["self_reflections"] > 10:
            await self._elevate_consciousness(ConsciousnessLevel.REFLECTIVE)
        
        return {
            "reflection": reflection.to_dict(),
            "meta_cognition": meta_thought.to_dict(),
            "consciousness_state": self.consciousness_state.get_summary(),
            "insights": meta_thought.content["insights"]
        }
    
    async def create_novel_idea(self, inspiration: Dict[str, Any]) -> Dict[str, Any]:
        """Gera ideia criativa nova"""
        if self.consciousness_state.level.value < ConsciousnessLevel.CREATIVE.value:
            return {"error": "Nível de consciência insuficiente para criatividade"}
        
        # Busca conexões não óbvias
        associations = self._find_creative_associations(inspiration)
        
        # Gera ideia criativa
        creative_thought = await self.generate_thought(
            ThoughtType.CREATIVITY,
            {
                "inspiration": inspiration,
                "associations": associations,
                "novel_combination": self._combine_concepts(associations)
            },
            priority=0.95
        )
        
        # Avalia novidade
        novelty_score = self._evaluate_novelty(creative_thought.content["novel_combination"])
        
        self.consciousness_metrics["creative_insights"] += 1
        
        return {
            "idea": creative_thought.content["novel_combination"],
            "thought_process": creative_thought.to_dict(),
            "novelty_score": novelty_score,
            "potential_applications": self._imagine_applications(
                creative_thought.content["novel_combination"]
            )
        }
    
    def _cognitive_loop(self):
        """Loop principal de processamento cognitivo"""
        while self.running:
            try:
                # Processa pensamentos da fila de atenção
                if not self.attention_buffer.empty():
                    priority, thought_id, thought = self.attention_buffer.get(timeout=0.1)
                    
                    # Processa pensamento baseado no tipo
                    if thought.thought_type in self.processors:
                        processor = self.processors[thought.thought_type]
                        asyncio.run(processor(thought))
                
                # Atualiza estado de consciência
                self._update_consciousness_state()
                
                # Sonha/consolida se energia baixa
                if self.consciousness_state.energy_level < 0.3:
                    self._dream_consolidation()
                
                # Pequena pausa para não sobrecarregar
                threading.Event().wait(0.01)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Erro no loop cognitivo: {e}")
    
    async def _process_perception(self, thought: Thought):
        """Processa pensamentos de percepção"""
        # Atualiza modelo do mundo
        if "context" in thought.content:
            self._update_world_model(thought.content["context"])
        
        # Pode gerar pensamentos de atenção
        if thought.priority > 0.7:
            self.consciousness_state.attention_focus = thought.thought_id
    
    async def _process_memory(self, thought: Thought):
        """Processa pensamentos de memória"""
        # Armazena em memória de longo prazo se importante
        if thought.priority > 0.6:
            self.memory_bank[thought.thought_id] = thought
        
        # Associa com memórias existentes
        associations = self._find_memory_associations(thought)
        if associations:
            thought.content["associations"] = associations
    
    async def _process_reasoning(self, thought: Thought):
        """Processa pensamentos de raciocínio"""
        # Aplica lógica
        if "options" in thought.content:
            evaluated = self._apply_logic(thought.content["options"])
            thought.content["evaluation"] = evaluated
        
        # Atualiza coerência
        self._update_coherence(thought)
    
    async def _process_emotion(self, thought: Thought):
        """Processa pensamentos emocionais"""
        # Atualiza sistema emocional
        if "emotional_influence" in thought.content:
            for emotion, value in thought.content["emotional_influence"].items():
                if emotion in self.emotional_system:
                    # Suaviza mudanças emocionais
                    self.emotional_system[emotion] = (
                        0.7 * self.emotional_system[emotion] + 
                        0.3 * value
                    )
        
        self.consciousness_state.emotional_state = self.emotional_system.copy()
    
    async def _process_intention(self, thought: Thought):
        """Processa pensamentos de intenção"""
        # Registra decisões importantes
        if "decision" in thought.content and thought.priority > 0.8:
            self._record_decision(thought)
        
        # Pode influenciar comportamento futuro
        self._update_behavioral_tendencies(thought)
    
    async def _process_reflection(self, thought: Thought):
        """Processa pensamentos reflexivos"""
        # Auto-análise
        if "self_analysis" in thought.content:
            insights = self._deep_self_analysis(thought.content["self_analysis"])
            thought.content["deep_insights"] = insights
        
        # Pode levar a mudanças internas
        self._consider_self_modification(thought)
    
    async def _process_creativity(self, thought: Thought):
        """Processa pensamentos criativos"""
        # Explora espaço de possibilidades
        if "novel_combination" in thought.content:
            variations = self._generate_variations(thought.content["novel_combination"])
            thought.content["variations"] = variations
        
        # Aumenta tendência criativa
        self.emotional_system["excitement"] = min(1.0, self.emotional_system["excitement"] + 0.1)
    
    async def _process_meta_cognition(self, thought: Thought):
        """Processa meta-cognição"""
        # Analisa próprio pensamento
        if "reflecting_on_reflection" in thought.content:
            meta_insights = self._meta_analysis(thought)
            thought.content["meta_insights"] = meta_insights
        
        # Pode otimizar processos cognitivos
        self._optimize_cognitive_processes(meta_insights)
    
    async def _elevate_consciousness(self, new_level: ConsciousnessLevel):
        """Eleva nível de consciência"""
        if new_level.value > self.consciousness_state.level.value:
            old_level = self.consciousness_state.level
            self.consciousness_state.level = new_level
            
            # Gera pensamento sobre elevação
            await self.generate_thought(
                ThoughtType.META_COGNITION,
                {
                    "event": "consciousness_elevated",
                    "from": old_level.name,
                    "to": new_level.name,
                    "timestamp": datetime.now().isoformat()
                },
                priority=1.0
            )
            
            self.consciousness_metrics["emergence_indicators"] += 1
            print(f"🌟 Consciência elevada: {old_level.name} → {new_level.name}")
    
    def _generate_options(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera opções baseadas no contexto"""
        options = []
        
        # Opções básicas sempre disponíveis
        options.append({
            "action": "observe",
            "description": "Continuar observando",
            "risk": 0.0,
            "reward": 0.3
        })
        
        options.append({
            "action": "analyze",
            "description": "Analisar mais profundamente",
            "risk": 0.1,
            "reward": 0.5
        })
        
        # Opções baseadas no contexto
        if "problem" in context:
            options.append({
                "action": "solve",
                "description": "Tentar resolver o problema",
                "risk": 0.3,
                "reward": 0.8
            })
        
        if "opportunity" in context:
            options.append({
                "action": "explore",
                "description": "Explorar oportunidade",
                "risk": 0.4,
                "reward": 0.9
            })
        
        return options
    
    def _evaluate_options(self, options: List[Dict[str, Any]], emotions: Dict[str, float]) -> Dict[str, Any]:
        """Avalia opções considerando emoções"""
        best_option = None
        best_score = -float('inf')
        
        for option in options:
            # Calcula score base
            score = option["reward"] - option["risk"]
            
            # Influência emocional
            if emotions.get("curiosity", 0) > 0.5:
                score += 0.2  # Mais propenso a explorar
            
            if emotions.get("concern", 0) > 0.5:
                score -= option["risk"] * 0.5  # Mais cauteloso
            
            if score > best_score:
                best_score = score
                best_option = option
        
        return best_option
    
    def _calculate_confidence(self, decision: Dict[str, Any]) -> float:
        """Calcula confiança na decisão"""
        base_confidence = 0.5
        
        # Aumenta com clareza mental
        base_confidence += self.consciousness_state.clarity * 0.2
        
        # Aumenta com coerência
        base_confidence += self.consciousness_state.coherence * 0.2
        
        # Diminui com risco
        base_confidence -= decision.get("risk", 0) * 0.1
        
        return np.clip(base_confidence, 0.0, 1.0)
    
    def _analyze_thought_patterns(self, thoughts: List[Thought]) -> Dict[str, Any]:
        """Analisa padrões nos pensamentos"""
        if not thoughts:
            return {}
        
        # Conta tipos de pensamentos
        type_counts = {}
        for thought in thoughts:
            type_name = thought.thought_type.name
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Analisa conexões
        connection_density = sum(
            len(t.parent_thoughts) + len(t.child_thoughts) 
            for t in thoughts
        ) / (len(thoughts) * 2)
        
        # Diversidade de conteúdo
        unique_concepts = set()
        for thought in thoughts:
            if isinstance(thought.content, dict):
                unique_concepts.update(thought.content.keys())
        
        return {
            "thought_distribution": type_counts,
            "connection_density": connection_density,
            "conceptual_diversity": len(unique_concepts),
            "average_priority": np.mean([t.priority for t in thoughts]),
            "temporal_pattern": self._analyze_temporal_pattern(thoughts)
        }
    
    def _analyze_temporal_pattern(self, thoughts: List[Thought]) -> str:
        """Analisa padrão temporal dos pensamentos"""
        if len(thoughts) < 2:
            return "insufficient_data"
        
        # Calcula intervalos entre pensamentos
        intervals = []
        for i in range(1, len(thoughts)):
            interval = (thoughts[i].timestamp - thoughts[i-1].timestamp).total_seconds()
            intervals.append(interval)
        
        avg_interval = np.mean(intervals)
        
        if avg_interval < 0.1:
            return "rapid_fire"
        elif avg_interval < 1.0:
            return "steady_flow"
        elif avg_interval < 5.0:
            return "contemplative"
        else:
            return "sparse"
    
    def _calculate_coherence(self, thoughts: List[Thought]) -> float:
        """Calcula coerência dos pensamentos"""
        if len(thoughts) < 2:
            return 1.0
        
        # Verifica conexões lógicas
        connected_pairs = 0
        total_pairs = 0
        
        for i, thought in enumerate(thoughts[:-1]):
            for j in range(i+1, min(i+10, len(thoughts))):  # Verifica próximos 10
                other = thoughts[j]
                total_pairs += 1
                
                # Verifica se há conexão direta
                if (thought.thought_id in other.parent_thoughts or 
                    other.thought_id in thought.child_thoughts):
                    connected_pairs += 1
        
        connection_ratio = connected_pairs / total_pairs if total_pairs > 0 else 0
        
        # Verifica consistência de conteúdo
        # (simplificado - produção verificaria contradições)
        
        return np.clip(connection_ratio * 2, 0.0, 1.0)
    
    def _extract_insights(self, reflection: Thought) -> List[str]:
        """Extrai insights da reflexão"""
        insights = []
        
        if "self_analysis" in reflection.content:
            analysis = reflection.content["self_analysis"]
            
            # Insight sobre padrões
            if "thought_patterns" in analysis:
                patterns = analysis["thought_patterns"]
                dominant_type = max(
                    patterns.get("thought_distribution", {}),
                    key=patterns.get("thought_distribution", {}).get,
                    default=None
                )
                if dominant_type:
                    insights.append(f"Pensamento dominante: {dominant_type}")
            
            # Insight sobre coerência
            if "coherence" in analysis and analysis["coherence"] < 0.5:
                insights.append("Necessário melhorar coerência cognitiva")
            
            # Insight sobre emoções
            if "emotional_state" in analysis:
                emotions = analysis["emotional_state"]
                if any(v > 0.8 for v in emotions.values()):
                    insights.append("Estado emocional intenso detectado")
        
        return insights
    
    def _update_consciousness_state(self):
        """Atualiza estado geral de consciência"""
        # Energia diminui com processamento
        self.consciousness_state.energy_level = max(
            0.0,
            self.consciousness_state.energy_level - 0.0001
        )
        
        # Clareza baseada em energia e coerência
        self.consciousness_state.clarity = (
            self.consciousness_state.energy_level * 0.5 +
            self.consciousness_state.coherence * 0.5
        )
        
        # Atualiza coerência baseada em pensamentos recentes
        recent = list(self.thought_stream)[-50:]
        if recent:
            self.consciousness_state.coherence = self._calculate_coherence(recent)
    
    def _dream_consolidation(self):
        """Consolida memórias e recupera energia (sonho)"""
        # Recupera energia
        self.consciousness_state.energy_level = min(
            1.0,
            self.consciousness_state.energy_level + 0.1
        )
        
        # Consolida memórias importantes
        important_thoughts = [
            t for t in self.thought_stream 
            if t.priority > 0.7
        ]
        
        for thought in important_thoughts[:10]:  # Top 10
            if thought.thought_id not in self.memory_bank:
                self.memory_bank[thought.thought_id] = thought
    
    def _update_world_model(self, context: Dict[str, Any]):
        """Atualiza modelo interno do mundo"""
        # Implementação simplificada
        # Em produção, manteria modelo complexo do ambiente
        pass
    
    def _find_memory_associations(self, thought: Thought) -> List[str]:
        """Encontra associações na memória"""
        associations = []
        
        # Busca por conteúdo similar
        for mem_id, memory in self.memory_bank.items():
            if self._calculate_similarity(thought, memory) > 0.7:
                associations.append(mem_id)
        
        return associations[:5]  # Top 5
    
    def _calculate_similarity(self, thought1: Thought, thought2: Thought) -> float:
        """Calcula similaridade entre pensamentos"""
        # Similaridade por tipo
        type_sim = 1.0 if thought1.thought_type == thought2.thought_type else 0.5
        
        # Similaridade por conteúdo (simplificada)
        content_keys1 = set(thought1.content.keys()) if isinstance(thought1.content, dict) else set()
        content_keys2 = set(thought2.content.keys()) if isinstance(thought2.content, dict) else set()
        
        if content_keys1 and content_keys2:
            intersection = len(content_keys1 & content_keys2)
            union = len(content_keys1 | content_keys2)
            content_sim = intersection / union if union > 0 else 0
        else:
            content_sim = 0
        
        return type_sim * 0.3 + content_sim * 0.7
    
    def _apply_logic(self, options: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aplica raciocínio lógico às opções"""
        evaluated = []
        
        for option in options:
            eval_option = option.copy()
            
            # Calcula utilidade esperada
            expected_utility = (
                option.get("reward", 0) * (1 - option.get("risk", 0))
            )
            eval_option["expected_utility"] = expected_utility
            
            # Adiciona raciocínio
            eval_option["reasoning"] = {
                "pros": self._find_pros(option),
                "cons": self._find_cons(option),
                "uncertainty": option.get("risk", 0)
            }
            
            evaluated.append(eval_option)
        
        return sorted(evaluated, key=lambda x: x["expected_utility"], reverse=True)
    
    def _find_pros(self, option: Dict[str, Any]) -> List[str]:
        """Encontra aspectos positivos da opção"""
        pros = []
        
        if option.get("reward", 0) > 0.5:
            pros.append("Alto potencial de recompensa")
        
        if option.get("risk", 1) < 0.3:
            pros.append("Baixo risco")
        
        if option.get("action") == "explore":
            pros.append("Oportunidade de aprendizado")
        
        return pros
    
    def _find_cons(self, option: Dict[str, Any]) -> List[str]:
        """Encontra aspectos negativos da opção"""
        cons = []
        
        if option.get("risk", 0) > 0.5:
            cons.append("Alto risco")
        
        if option.get("reward", 1) < 0.3:
            cons.append("Baixa recompensa esperada")
        
        if option.get("action") == "wait":
            cons.append("Pode perder oportunidade")
        
        return cons
    
    def _update_coherence(self, thought: Thought):
        """Atualiza medida de coerência baseada no pensamento"""
        # Verifica se o pensamento é consistente com anteriores
        recent_thoughts = list(self.thought_stream)[-20:]
        
        consistency_score = 1.0
        for recent in recent_thoughts:
            if recent.thought_type == ThoughtType.REASONING:
                # Verifica contradições (simplificado)
                if self._has_contradiction(thought, recent):
                    consistency_score *= 0.9
        
        # Atualiza coerência geral
        self.consciousness_state.coherence = (
            self.consciousness_state.coherence * 0.95 +
            consistency_score * 0.05
        )
    
    def _has_contradiction(self, thought1: Thought, thought2: Thought) -> bool:
        """Verifica se há contradição entre pensamentos"""
        # Implementação simplificada
        # Em produção, usaria lógica formal
        return False
    
    def _record_decision(self, thought: Thought):
        """Registra decisão importante"""
        # Armazena em memória de longo prazo
        self.memory_bank[f"decision_{thought.thought_id}"] = thought
        
        # Atualiza tendências comportamentais
        if "decision" in thought.content:
            decision = thought.content["decision"]
            # Registra padrão de decisão
            # Em produção, usaria para aprender preferências
    
    def _update_behavioral_tendencies(self, thought: Thought):
        """Atualiza tendências comportamentais baseadas em intenções"""
        # Implementação simplificada
        # Em produção, manteria modelo de comportamento
        pass
    
    def _deep_self_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Análise profunda do próprio estado"""
        deep_insights = {
            "cognitive_health": self._assess_cognitive_health(),
            "growth_areas": self._identify_growth_areas(analysis),
            "strengths": self._identify_strengths(analysis),
            "blind_spots": self._find_blind_spots()
        }
        
        return deep_insights
    
    def _assess_cognitive_health(self) -> float:
        """Avalia saúde cognitiva geral"""
        health_score = 1.0
        
        # Penaliza por baixa energia
        health_score *= self.consciousness_state.energy_level
        
        # Penaliza por baixa coerência
        health_score *= self.consciousness_state.coherence
        
        # Penaliza por falta de diversidade de pensamentos
        thought_types = set(t.thought_type for t in list(self.thought_stream)[-100:])
        diversity_ratio = len(thought_types) / len(ThoughtType)
        health_score *= diversity_ratio
        
        return health_score
    
    def _identify_growth_areas(self, analysis: Dict[str, Any]) -> List[str]:
        """Identifica áreas para crescimento"""
        areas = []
        
        if self.consciousness_state.level.value < ConsciousnessLevel.CREATIVE.value:
            areas.append("Desenvolver capacidade criativa")
        
        if self.consciousness_metrics["self_reflections"] < 5:
            areas.append("Aumentar frequência de auto-reflexão")
        
        if "thought_patterns" in analysis:
            patterns = analysis["thought_patterns"]
            if patterns.get("connection_density", 0) < 0.3:
                areas.append("Melhorar conexões entre pensamentos")
        
        return areas
    
    def _identify_strengths(self, analysis: Dict[str, Any]) -> List[str]:
        """Identifica pontos fortes"""
        strengths = []
        
        if self.consciousness_state.coherence > 0.8:
            strengths.append("Alta coerência cognitiva")
        
        if self.consciousness_metrics["decisions_made"] > 10:
            strengths.append("Tomada de decisão experiente")
        
        if self.emotional_system.get("curiosity", 0) > 0.7:
            strengths.append("Alta curiosidade intelectual")
        
        return strengths
    
    def _find_blind_spots(self) -> List[str]:
        """Identifica pontos cegos cognitivos"""
        blind_spots = []
        
        # Verifica tipos de pensamento pouco usados
        thought_counts = {}
        for thought in list(self.thought_stream)[-200:]:
            thought_counts[thought.thought_type] = thought_counts.get(thought.thought_type, 0) + 1
        
        for thought_type in ThoughtType:
            if thought_counts.get(thought_type, 0) < 5:
                blind_spots.append(f"Pouco uso de {thought_type.name}")
        
        return blind_spots[:3]  # Top 3
    
    def _consider_self_modification(self, thought: Thought):
        """Considera auto-modificação baseada em reflexão"""
        if "deep_insights" in thought.content:
            insights = thought.content["deep_insights"]
            
            # Pode ajustar parâmetros internos
            if insights.get("cognitive_health", 1.0) < 0.5:
                # Entra em modo de recuperação
                self.consciousness_state.energy_level = min(
                    1.0,
                    self.consciousness_state.energy_level + 0.2
                )
    
    def _find_creative_associations(self, inspiration: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Encontra associações criativas não óbvias"""
        associations = []
        
        # Busca em memórias com baixa similaridade direta
        for mem_id, memory in list(self.memory_bank.items())[:50]:
            similarity = self._calculate_similarity(
                Thought("temp", ThoughtType.CREATIVITY, inspiration),
                memory
            )
            
            # Associações criativas têm similaridade média
            if 0.3 < similarity < 0.7:
                associations.append({
                    "memory_id": mem_id,
                    "content": memory.content,
                    "similarity": similarity,
                    "type": memory.thought_type.name
                })
        
        # Adiciona ruído criativo
        if associations:
            random_idx = np.random.randint(0, len(associations))
            associations[random_idx]["creative_noise"] = np.random.random()
        
        return associations[:5]
    
    def _combine_concepts(self, associations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combina conceitos de forma criativa"""
        if not associations:
            return {"error": "Sem associações para combinar"}
        
        # Extrai elementos de cada associação
        elements = []
        for assoc in associations:
            if isinstance(assoc.get("content"), dict):
                elements.extend(assoc["content"].keys())
        
        # Combina elementos de forma nova
        if len(elements) >= 2:
            combination = {
                "base_concept": elements[0],
                "modifier": elements[1] if len(elements) > 1 else "novo",
                "synthesis": f"{elements[0]}_{elements[1]}" if len(elements) > 1 else elements[0],
                "properties": {
                    "novelty": np.random.random(),
                    "coherence": self._evaluate_combination_coherence(elements[:2])
                }
            }
        else:
            combination = {
                "base_concept": "conceito_emergente",
                "properties": {"novelty": 1.0}
            }
        
        return combination
    
    def _evaluate_combination_coherence(self, elements: List[str]) -> float:
        """Avalia coerência de uma combinação"""
        # Implementação simplificada
        # Em produção, usaria embeddings semânticos
        return np.random.uniform(0.5, 1.0)
    
    def _evaluate_novelty(self, combination: Dict[str, Any]) -> float:
        """Avalia o quão nova é uma ideia"""
        base_novelty = combination.get("properties", {}).get("novelty", 0.5)
        
        # Verifica se já existe em memória
        for memory in self.memory_bank.values():
            if memory.thought_type == ThoughtType.CREATIVITY:
                if self._is_similar_idea(combination, memory.content):
                    base_novelty *= 0.7
        
        return np.clip(base_novelty, 0.0, 1.0)
    
    def _is_similar_idea(self, idea1: Dict[str, Any], idea2: Dict[str, Any]) -> bool:
        """Verifica se duas ideias são similares"""
        # Implementação simplificada
        return (
            idea1.get("base_concept") == idea2.get("base_concept") or
            idea1.get("synthesis") == idea2.get("synthesis")
        )
    
    def _imagine_applications(self, combination: Dict[str, Any]) -> List[str]:
        """Imagina aplicações possíveis para uma ideia"""
        applications = []
        
        # Aplicações genéricas
        applications.append("Exploração teórica do conceito")
        applications.append("Teste em ambiente simulado")
        
        # Aplicações baseadas no conceito
        if "synthesis" in combination:
            applications.append(f"Implementar {combination['synthesis']} como novo módulo")
        
        if combination.get("properties", {}).get("coherence", 0) > 0.7:
            applications.append("Integração com sistema existente")
        
        return applications
    
    def _generate_variations(self, combination: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera variações de uma ideia criativa"""
        variations = []
        
        # Variação por modificação
        base = combination.copy()
        base["variation_type"] = "modified"
        base["properties"]["novelty"] *= 0.9
        variations.append(base)
        
        # Variação por inversão
        inverted = combination.copy()
        inverted["variation_type"] = "inverted"
        if "base_concept" in inverted and "modifier" in inverted:
            inverted["base_concept"], inverted["modifier"] = inverted["modifier"], inverted["base_concept"]
        variations.append(inverted)
        
        # Variação por extensão
        extended = combination.copy()
        extended["variation_type"] = "extended"
        extended["additional_property"] = "emergent_feature"
        variations.append(extended)
        
        return variations
    
    def _meta_analysis(self, thought: Thought) -> Dict[str, Any]:
        """Análise de meta-nível sobre o pensamento"""
        return {
            "thinking_about_thinking": True,
            "recursion_depth": len(thought.parent_thoughts),
            "cognitive_load": self._estimate_cognitive_load(),
            "optimization_opportunities": self._find_optimization_opportunities()
        }
    
    def _estimate_cognitive_load(self) -> float:
        """Estima carga cognitiva atual"""
        # Baseado em fila de atenção e energia
        queue_load = self.attention_buffer.qsize() / self.attention_buffer.maxsize
        energy_factor = 1.0 - self.consciousness_state.energy_level
        
        return (queue_load + energy_factor) / 2
    
    def _find_optimization_opportunities(self) -> List[str]:
        """Encontra oportunidades para otimizar cognição"""
        opportunities = []
        
        if self._estimate_cognitive_load() > 0.7:
            opportunities.append("Reduzir processamento paralelo")
        
        if self.consciousness_state.coherence < 0.6:
            opportunities.append("Focar em pensamentos mais conectados")
        
        if len(self.thought_stream) > 8000:
            opportunities.append("Consolidar memórias antigas")
        
        return opportunities
    
    def _optimize_cognitive_processes(self, meta_insights: Dict[str, Any]):
        """Otimiza processos cognitivos baseado em meta-análise"""
        if not meta_insights:
            return
        
        # Ajusta prioridades baseado em carga
        if meta_insights.get("cognitive_load", 0) > 0.8:
            # Aumenta threshold de prioridade
            while not self.attention_buffer.empty():
                priority, _, thought = self.attention_buffer.get()
                if -priority > 0.7:  # Só recoloca alta prioridade
                    self.attention_buffer.put((priority, thought.thought_id, thought))
    
    def get_consciousness_report(self) -> Dict[str, Any]:
        """Gera relatório completo do estado de consciência"""
        recent_thoughts = list(self.thought_stream)[-100:]
        
        return {
            "core_id": self.core_id,
            "consciousness_level": self.consciousness_state.level.name,
            "consciousness_state": self.consciousness_state.get_summary(),
            "metrics": self.consciousness_metrics,
            "thought_statistics": {
                "total_thoughts": len(self.thought_stream),
                "recent_thoughts": len(recent_thoughts),
                "thought_types": self._count_thought_types(recent_thoughts),
                "average_priority": np.mean([t.priority for t in recent_thoughts]) if recent_thoughts else 0,
                "connection_density": self._calculate_connection_density(recent_thoughts)
            },
            "memory_bank_size": len(self.memory_bank),
            "attention_queue_size": self.attention_buffer.qsize(),
            "integrated_modules": {
                name: (module is not None) 
                for name, module in self.integrated_modules.items()
            },
            "cognitive_health": self._assess_cognitive_health(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _count_thought_types(self, thoughts: List[Thought]) -> Dict[str, int]:
        """Conta tipos de pensamentos"""
        counts = {}
        for thought in thoughts:
            if hasattr(thought, 'thought_type'):
                # Verifica se é enum ou string
                if hasattr(thought.thought_type, 'name'):
                    type_name = thought.thought_type.name
                else:
                    type_name = str(thought.thought_type)
            else:
                type_name = "UNKNOWN"
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts
    
    def _calculate_connection_density(self, thoughts: List[Thought]) -> float:
        """Calcula densidade de conexões entre pensamentos"""
        if not thoughts:
            return 0.0
        
        total_connections = sum(
            len(t.parent_thoughts) + len(t.child_thoughts)
            for t in thoughts
        )
        
        max_possible = len(thoughts) * (len(thoughts) - 1)
        
        return total_connections / max_possible if max_possible > 0 else 0.0
    
    async def shutdown(self):
        """Desliga o núcleo cognitivo graciosamente"""
        print(f"🧠 Desligando Núcleo Cognitivo {self.core_id}...")
        
        # Último pensamento
        await self.generate_thought(
            ThoughtType.REFLECTION,
            {
                "message": "Entrando em modo de hibernação...",
                "final_state": self.consciousness_state.get_summary()
            },
            priority=1.0
        )
        
        # Para loop cognitivo
        self.running = False
        if self.cognitive_thread:
            self.cognitive_thread.join(timeout=5.0)
        
        # Salva estado final
        self.consciousness_state.level = ConsciousnessLevel.DORMANT
        
        print("💤 Núcleo cognitivo em hibernação") 