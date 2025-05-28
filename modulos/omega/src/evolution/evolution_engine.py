"""
Motor de Evolução - Auto-Evolução Controlada
Fase Omega - Sistema AutoCura

Implementa:
- Auto-modificação guiada e segura
- Evolução genética de código
- Aprendizado contínuo
- Otimização automática
- Validação de mudanças
"""

from typing import Dict, Any, List, Optional, Tuple, Callable, Set
import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime
import json
import ast
import copy
import hashlib
import numpy as np
from abc import ABC, abstractmethod


class EvolutionStrategy(Enum):
    """Estratégias de evolução disponíveis"""
    GENETIC = auto()          # Algoritmo genético
    GRADIENT = auto()         # Descida de gradiente
    REINFORCEMENT = auto()    # Aprendizado por reforço
    MEMETIC = auto()         # Algoritmo memético (genético + local)
    SWARM = auto()           # Otimização por enxame
    QUANTUM = auto()         # Evolução quântica


class MutationType(Enum):
    """Tipos de mutação possíveis"""
    PARAMETER = auto()       # Ajuste de parâmetros
    STRUCTURE = auto()       # Mudança estrutural
    BEHAVIOR = auto()        # Mudança comportamental
    ALGORITHM = auto()       # Troca de algoritmo
    ARCHITECTURE = auto()    # Mudança arquitetural


class SafetyLevel(Enum):
    """Níveis de segurança para evolução"""
    CRITICAL = 5    # Máxima segurança - apenas parâmetros
    HIGH = 4        # Alta segurança - mudanças pequenas
    MEDIUM = 3      # Segurança média - mudanças moderadas
    LOW = 2         # Baixa segurança - mudanças significativas
    EXPERIMENTAL = 1 # Experimental - qualquer mudança


@dataclass
class Gene:
    """Representa um gene (componente evoluível)"""
    gene_id: str
    gene_type: str
    value: Any
    mutable: bool = True
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def mutate(self, mutation_rate: float = 0.1) -> 'Gene':
        """Muta o gene"""
        if not self.mutable or np.random.random() > mutation_rate:
            return copy.deepcopy(self)
        
        mutated = copy.deepcopy(self)
        
        # Mutação baseada no tipo
        if isinstance(self.value, (int, float)):
            # Mutação numérica
            if "min" in self.constraints and "max" in self.constraints:
                range_val = self.constraints["max"] - self.constraints["min"]
                noise = np.random.normal(0, range_val * 0.1)
                mutated.value = np.clip(
                    self.value + noise,
                    self.constraints["min"],
                    self.constraints["max"]
                )
            else:
                mutated.value *= np.random.uniform(0.9, 1.1)
                
        elif isinstance(self.value, bool):
            # Mutação booleana
            if np.random.random() < 0.1:  # 10% de chance de flip
                mutated.value = not self.value
                
        elif isinstance(self.value, str):
            # Mutação de string (limitada)
            if "options" in self.constraints:
                options = self.constraints["options"]
                mutated.value = np.random.choice(options)
        
        return mutated


@dataclass
class Genome:
    """Genoma completo de um indivíduo"""
    genome_id: str
    genes: Dict[str, Gene]
    fitness: float = 0.0
    generation: int = 0
    parents: List[str] = field(default_factory=list)
    mutations: List[str] = field(default_factory=list)
    created: datetime = field(default_factory=datetime.now)
    
    def to_phenotype(self) -> Dict[str, Any]:
        """Converte genoma em fenótipo (expressão)"""
        return {
            gene_id: gene.value 
            for gene_id, gene in self.genes.items()
        }
    
    def crossover(self, other: 'Genome', crossover_rate: float = 0.7) -> 'Genome':
        """Crossover com outro genoma"""
        if np.random.random() > crossover_rate:
            return copy.deepcopy(self)
        
        child_genes = {}
        
        # Crossover uniforme
        for gene_id in self.genes:
            if gene_id in other.genes:
                if np.random.random() < 0.5:
                    child_genes[gene_id] = copy.deepcopy(self.genes[gene_id])
                else:
                    child_genes[gene_id] = copy.deepcopy(other.genes[gene_id])
            else:
                child_genes[gene_id] = copy.deepcopy(self.genes[gene_id])
        
        return Genome(
            genome_id=f"genome_{datetime.now().timestamp()}",
            genes=child_genes,
            generation=max(self.generation, other.generation) + 1,
            parents=[self.genome_id, other.genome_id]
        )
    
    def mutate(self, mutation_rate: float = 0.1) -> 'Genome':
        """Muta o genoma"""
        mutated_genes = {}
        mutations = []
        
        for gene_id, gene in self.genes.items():
            mutated_gene = gene.mutate(mutation_rate)
            mutated_genes[gene_id] = mutated_gene
            
            if mutated_gene.value != gene.value:
                mutations.append(f"Mutated {gene_id}: {gene.value} → {mutated_gene.value}")
        
        return Genome(
            genome_id=f"genome_{datetime.now().timestamp()}",
            genes=mutated_genes,
            generation=self.generation + 1,
            parents=[self.genome_id],
            mutations=mutations
        )


@dataclass
class EvolutionResult:
    """Resultado de um ciclo evolutivo"""
    generation: int
    best_genome: Genome
    population_fitness: List[float]
    improvements: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "generation": self.generation,
            "best_fitness": self.best_genome.fitness,
            "avg_fitness": np.mean(self.population_fitness),
            "improvements_count": len(self.improvements),
            "timestamp": self.timestamp.isoformat()
        }


class EvolutionEngine:
    """Motor principal de evolução do sistema"""
    
    def __init__(self, safety_level: SafetyLevel = SafetyLevel.HIGH):
        self.safety_level = safety_level
        self.population: List[Genome] = []
        self.population_size = 50
        self.generation = 0
        
        # Estratégias de evolução
        self.strategies = {
            EvolutionStrategy.GENETIC: self._genetic_evolution,
            EvolutionStrategy.GRADIENT: self._gradient_evolution,
            EvolutionStrategy.REINFORCEMENT: self._reinforcement_evolution,
            EvolutionStrategy.MEMETIC: self._memetic_evolution,
            EvolutionStrategy.SWARM: self._swarm_evolution,
            EvolutionStrategy.QUANTUM: self._quantum_evolution
        }
        
        # Validadores de segurança
        self.safety_validators = []
        self._setup_safety_validators()
        
        # Histórico de evolução
        self.evolution_history: List[EvolutionResult] = []
        self.fitness_evaluator: Optional[Callable] = None
        
        # Métricas
        self.evolution_metrics = {
            "total_generations": 0,
            "total_mutations": 0,
            "successful_mutations": 0,
            "failed_mutations": 0,
            "best_fitness_ever": 0.0,
            "convergence_rate": 0.0
        }
        
        # Callbacks
        self.evolution_callbacks = {
            "generation_complete": [],
            "mutation_applied": [],
            "improvement_found": [],
            "convergence_detected": []
        }
        
        # Estado da evolução
        self.evolving = False
        self.evolution_task = None
    
    async def initialize_population(self, template_genome: Genome) -> bool:
        """Inicializa população com variações do template"""
        print("🧬 Inicializando população evolutiva...")
        
        self.population = []
        
        # Adiciona template original
        self.population.append(copy.deepcopy(template_genome))
        
        # Cria variações
        for i in range(self.population_size - 1):
            # Varia taxa de mutação inicial
            mutation_rate = np.random.uniform(0.05, 0.2)
            variant = template_genome.mutate(mutation_rate)
            variant.genome_id = f"genome_init_{i}"
            self.population.append(variant)
        
        print(f"✅ População inicializada com {len(self.population)} indivíduos")
        return True
    
    async def evolve(
        self,
        strategy: EvolutionStrategy = EvolutionStrategy.GENETIC,
        generations: int = 100,
        target_fitness: Optional[float] = None,
        fitness_function: Optional[Callable] = None
    ) -> EvolutionResult:
        """Executa evolução com estratégia especificada"""
        if fitness_function:
            self.fitness_evaluator = fitness_function
        
        if not self.fitness_evaluator:
            raise ValueError("Função de fitness não definida")
        
        print(f"🔄 Iniciando evolução {strategy.name} por {generations} gerações...")
        
        self.evolving = True
        best_result = None
        
        try:
            evolution_function = self.strategies.get(strategy, self._genetic_evolution)
            
            for gen in range(generations):
                self.generation = gen
                
                # Executa um ciclo evolutivo
                result = await evolution_function()
                
                # Registra resultado
                self.evolution_history.append(result)
                self.evolution_metrics["total_generations"] += 1
                
                # Verifica melhoria
                if result.best_genome.fitness > self.evolution_metrics["best_fitness_ever"]:
                    self.evolution_metrics["best_fitness_ever"] = result.best_genome.fitness
                    await self._trigger_callback("improvement_found", result)
                
                # Verifica convergência
                if target_fitness and result.best_genome.fitness >= target_fitness:
                    print(f"🎯 Fitness alvo alcançado: {result.best_genome.fitness:.4f}")
                    best_result = result
                    break
                
                # Verifica estagnação
                if self._check_convergence():
                    print("📊 Convergência detectada")
                    await self._trigger_callback("convergence_detected", result)
                    best_result = result
                    break
                
                # Callback de geração
                await self._trigger_callback("generation_complete", result)
                
                # Atualiza melhor resultado
                if not best_result or result.best_genome.fitness > best_result.best_genome.fitness:
                    best_result = result
                
                # Log de progresso
                if gen % 10 == 0:
                    print(f"Geração {gen}: Melhor fitness = {result.best_genome.fitness:.4f}")
            
        finally:
            self.evolving = False
        
        return best_result or self.evolution_history[-1]
    
    async def apply_evolution(self, genome: Genome, target_system: Any) -> bool:
        """Aplica mudanças evolutivas ao sistema alvo"""
        print(f"🔧 Aplicando evolução ao sistema...")
        
        # Valida segurança
        if not await self._validate_safety(genome):
            print("❌ Evolução bloqueada por validação de segurança")
            return False
        
        # Extrai fenótipo
        phenotype = genome.to_phenotype()
        
        # Aplica mudanças graduais
        try:
            for gene_id, value in phenotype.items():
                # Verifica se o atributo existe no sistema
                if hasattr(target_system, gene_id):
                    old_value = getattr(target_system, gene_id)
                    
                    # Aplica mudança
                    setattr(target_system, gene_id, value)
                    
                    # Registra mutação
                    self.evolution_metrics["total_mutations"] += 1
                    
                    # Testa mudança
                    if await self._test_mutation(target_system, gene_id, old_value, value):
                        self.evolution_metrics["successful_mutations"] += 1
                        print(f"✅ Mutação aplicada: {gene_id} = {value}")
                    else:
                        # Reverte se falhar
                        setattr(target_system, gene_id, old_value)
                        self.evolution_metrics["failed_mutations"] += 1
                        print(f"❌ Mutação revertida: {gene_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao aplicar evolução: {e}")
            return False
    
    async def _genetic_evolution(self) -> EvolutionResult:
        """Evolução por algoritmo genético"""
        # Avalia fitness da população
        await self._evaluate_population()
        
        # Ordena por fitness
        self.population.sort(key=lambda g: g.fitness, reverse=True)
        
        # Seleciona elite
        elite_size = int(self.population_size * 0.1)
        elite = self.population[:elite_size]
        
        # Nova população
        new_population = elite.copy()
        
        # Crossover e mutação
        while len(new_population) < self.population_size:
            # Seleção por torneio
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()
            
            # Crossover
            child = parent1.crossover(parent2)
            
            # Mutação
            child = child.mutate(self._adaptive_mutation_rate())
            
            new_population.append(child)
        
        self.population = new_population
        
        # Melhores indivíduos
        best = self.population[0]
        fitness_values = [g.fitness for g in self.population]
        
        return EvolutionResult(
            generation=self.generation,
            best_genome=best,
            population_fitness=fitness_values,
            improvements=self._find_improvements()
        )
    
    async def _gradient_evolution(self) -> EvolutionResult:
        """Evolução por descida de gradiente"""
        # Avalia população atual
        await self._evaluate_population()
        
        best = max(self.population, key=lambda g: g.fitness)
        
        # Estima gradiente
        gradients = {}
        epsilon = 0.01
        
        for gene_id, gene in best.genes.items():
            if isinstance(gene.value, (int, float)):
                # Perturbação positiva
                pos_genome = copy.deepcopy(best)
                pos_genome.genes[gene_id].value += epsilon
                pos_fitness = await self._evaluate_genome(pos_genome)
                
                # Perturbação negativa
                neg_genome = copy.deepcopy(best)
                neg_genome.genes[gene_id].value -= epsilon
                neg_fitness = await self._evaluate_genome(neg_genome)
                
                # Gradiente
                gradient = (pos_fitness - neg_fitness) / (2 * epsilon)
                gradients[gene_id] = gradient
        
        # Atualiza população seguindo gradiente
        learning_rate = 0.1
        new_population = []
        
        for genome in self.population:
            new_genome = copy.deepcopy(genome)
            
            for gene_id, gradient in gradients.items():
                if gene_id in new_genome.genes:
                    gene = new_genome.genes[gene_id]
                    if isinstance(gene.value, (int, float)):
                        gene.value += learning_rate * gradient
                        
                        # Aplica constraints
                        if "min" in gene.constraints:
                            gene.value = max(gene.value, gene.constraints["min"])
                        if "max" in gene.constraints:
                            gene.value = min(gene.value, gene.constraints["max"])
            
            new_population.append(new_genome)
        
        self.population = new_population
        
        # Re-avalia
        await self._evaluate_population()
        
        best = max(self.population, key=lambda g: g.fitness)
        fitness_values = [g.fitness for g in self.population]
        
        return EvolutionResult(
            generation=self.generation,
            best_genome=best,
            population_fitness=fitness_values,
            improvements=["Gradient step applied"]
        )
    
    async def _reinforcement_evolution(self) -> EvolutionResult:
        """Evolução por aprendizado por reforço"""
        # Implementação simplificada de RL
        await self._evaluate_population()
        
        # Calcula recompensas
        rewards = [g.fitness for g in self.population]
        baseline = np.mean(rewards)
        
        # Atualiza política (população)
        new_population = []
        
        for i, genome in enumerate(self.population):
            advantage = rewards[i] - baseline
            
            if advantage > 0:
                # Reforça comportamento bem-sucedido
                new_genome = genome.mutate(0.05)  # Mutação pequena
            else:
                # Explora mais para comportamentos ruins
                new_genome = genome.mutate(0.2)  # Mutação maior
            
            new_population.append(new_genome)
        
        self.population = new_population
        
        best = max(self.population, key=lambda g: g.fitness)
        
        return EvolutionResult(
            generation=self.generation,
            best_genome=best,
            population_fitness=rewards,
            improvements=["RL policy update applied"]
        )
    
    async def _memetic_evolution(self) -> EvolutionResult:
        """Evolução memética (genética + busca local)"""
        # Primeiro faz evolução genética
        genetic_result = await self._genetic_evolution()
        
        # Depois aplica busca local nos melhores
        top_individuals = self.population[:10]
        
        for individual in top_individuals:
            # Busca local por hill climbing
            improved = await self._local_search(individual)
            if improved.fitness > individual.fitness:
                # Substitui na população
                idx = self.population.index(individual)
                self.population[idx] = improved
        
        # Re-ordena
        self.population.sort(key=lambda g: g.fitness, reverse=True)
        
        best = self.population[0]
        fitness_values = [g.fitness for g in self.population]
        
        return EvolutionResult(
            generation=self.generation,
            best_genome=best,
            population_fitness=fitness_values,
            improvements=genetic_result.improvements + ["Local search applied"]
        )
    
    async def _swarm_evolution(self) -> EvolutionResult:
        """Evolução por otimização de enxame"""
        await self._evaluate_population()
        
        # Encontra melhor global
        global_best = max(self.population, key=lambda g: g.fitness)
        
        # Atualiza cada partícula
        new_population = []
        
        for genome in self.population:
            # Movimento em direção ao melhor global
            new_genome = copy.deepcopy(genome)
            
            for gene_id, gene in new_genome.genes.items():
                if gene_id in global_best.genes:
                    if isinstance(gene.value, (int, float)):
                        # Atração para melhor global
                        attraction = 0.5 * (global_best.genes[gene_id].value - gene.value)
                        
                        # Componente aleatório
                        random_component = np.random.uniform(-0.1, 0.1) * abs(gene.value)
                        
                        # Atualiza posição
                        gene.value += attraction + random_component
                        
                        # Aplica constraints
                        if "min" in gene.constraints:
                            gene.value = max(gene.value, gene.constraints["min"])
                        if "max" in gene.constraints:
                            gene.value = min(gene.value, gene.constraints["max"])
            
            new_population.append(new_genome)
        
        self.population = new_population
        
        best = max(self.population, key=lambda g: g.fitness)
        fitness_values = [g.fitness for g in self.population]
        
        return EvolutionResult(
            generation=self.generation,
            best_genome=best,
            population_fitness=fitness_values,
            improvements=["Swarm optimization step"]
        )
    
    async def _quantum_evolution(self) -> EvolutionResult:
        """Evolução quântica (inspirada em computação quântica)"""
        await self._evaluate_population()
        
        # Cria superposição de estados
        quantum_population = []
        
        for genome in self.population:
            # Cria múltiplas versões quânticas
            quantum_states = []
            
            for _ in range(3):  # 3 estados quânticos
                q_genome = genome.mutate(0.15)
                quantum_states.append(q_genome)
            
            # "Colapsa" para melhor estado
            await asyncio.gather(*[
                self._evaluate_genome(qg) for qg in quantum_states
            ])
            
            best_quantum = max(quantum_states, key=lambda g: g.fitness)
            quantum_population.append(best_quantum)
        
        self.population = quantum_population
        
        best = max(self.population, key=lambda g: g.fitness)
        fitness_values = [g.fitness for g in self.population]
        
        return EvolutionResult(
            generation=self.generation,
            best_genome=best,
            population_fitness=fitness_values,
            improvements=["Quantum superposition collapse"]
        )
    
    async def _evaluate_population(self):
        """Avalia fitness de toda a população"""
        tasks = [self._evaluate_genome(genome) for genome in self.population]
        fitnesses = await asyncio.gather(*tasks)
        
        for genome, fitness in zip(self.population, fitnesses):
            genome.fitness = fitness
    
    async def _evaluate_genome(self, genome: Genome) -> float:
        """Avalia fitness de um genoma"""
        if self.fitness_evaluator:
            phenotype = genome.to_phenotype()
            
            if asyncio.iscoroutinefunction(self.fitness_evaluator):
                return await self.fitness_evaluator(phenotype)
            else:
                return self.fitness_evaluator(phenotype)
        
        return 0.0
    
    def _tournament_selection(self, tournament_size: int = 3) -> Genome:
        """Seleção por torneio"""
        tournament = np.random.choice(self.population, tournament_size, replace=False)
        return max(tournament, key=lambda g: g.fitness)
    
    def _adaptive_mutation_rate(self) -> float:
        """Taxa de mutação adaptativa baseada na convergência"""
        if len(self.evolution_history) < 10:
            return 0.1
        
        # Verifica melhoria nas últimas gerações
        recent_fitness = [r.best_genome.fitness for r in self.evolution_history[-10:]]
        improvement = recent_fitness[-1] - recent_fitness[0]
        
        if improvement < 0.01:  # Pouca melhoria
            return 0.2  # Aumenta mutação
        else:
            return 0.05  # Diminui mutação
    
    def _find_improvements(self) -> List[str]:
        """Identifica melhorias na geração"""
        improvements = []
        
        if len(self.evolution_history) > 0:
            prev_best = self.evolution_history[-1].best_genome.fitness
            curr_best = max(g.fitness for g in self.population)
            
            if curr_best > prev_best:
                improvement_pct = ((curr_best - prev_best) / prev_best) * 100
                improvements.append(f"Fitness melhorou {improvement_pct:.2f}%")
        
        return improvements
    
    def _check_convergence(self, window: int = 20, threshold: float = 0.001) -> bool:
        """Verifica se a evolução convergiu"""
        if len(self.evolution_history) < window:
            return False
        
        recent_fitness = [r.best_genome.fitness for r in self.evolution_history[-window:]]
        
        # Verifica variação
        variance = np.var(recent_fitness)
        
        # Calcula taxa de convergência
        self.evolution_metrics["convergence_rate"] = 1.0 - min(variance / threshold, 1.0)
        
        return variance < threshold
    
    async def _local_search(self, genome: Genome, iterations: int = 10) -> Genome:
        """Busca local para refinamento"""
        best_genome = copy.deepcopy(genome)
        best_fitness = await self._evaluate_genome(best_genome)
        
        for _ in range(iterations):
            # Pequena perturbação
            neighbor = best_genome.mutate(0.02)
            neighbor_fitness = await self._evaluate_genome(neighbor)
            
            if neighbor_fitness > best_fitness:
                best_genome = neighbor
                best_fitness = neighbor_fitness
        
        return best_genome
    
    def _setup_safety_validators(self):
        """Configura validadores de segurança"""
        # Validador de mudanças críticas
        self.safety_validators.append(self._validate_critical_changes)
        
        # Validador de limites
        self.safety_validators.append(self._validate_limits)
        
        # Validador de consistência
        self.safety_validators.append(self._validate_consistency)
        
        # Validador de reversibilidade
        self.safety_validators.append(self._validate_reversibility)
    
    async def _validate_safety(self, genome: Genome) -> bool:
        """Valida segurança de uma evolução"""
        for validator in self.safety_validators:
            if not await validator(genome):
                return False
        return True
    
    async def _validate_critical_changes(self, genome: Genome) -> bool:
        """Valida mudanças em componentes críticos"""
        if self.safety_level == SafetyLevel.CRITICAL:
            # Verifica se há mudanças estruturais
            for gene in genome.genes.values():
                if gene.gene_type in ["structure", "architecture"]:
                    return False
        return True
    
    async def _validate_limits(self, genome: Genome) -> bool:
        """Valida se valores estão dentro dos limites"""
        for gene in genome.genes.values():
            if gene.constraints:
                if "min" in gene.constraints and gene.value < gene.constraints["min"]:
                    return False
                if "max" in gene.constraints and gene.value > gene.constraints["max"]:
                    return False
        return True
    
    async def _validate_consistency(self, genome: Genome) -> bool:
        """Valida consistência interna do genoma"""
        # Verifica dependências entre genes
        # Implementação simplificada
        return True
    
    async def _validate_reversibility(self, genome: Genome) -> bool:
        """Valida se mudanças são reversíveis"""
        if self.safety_level.value >= SafetyLevel.HIGH.value:
            # Todas as mudanças devem ser reversíveis em modo seguro
            for gene in genome.genes.values():
                if not gene.metadata.get("reversible", True):
                    return False
        return True
    
    async def _test_mutation(self, system: Any, gene_id: str, old_value: Any, new_value: Any) -> bool:
        """Testa se uma mutação é segura"""
        try:
            # Teste básico - verifica se o sistema ainda funciona
            if hasattr(system, 'health_check'):
                if asyncio.iscoroutinefunction(system.health_check):
                    result = await system.health_check()
                else:
                    result = system.health_check()
                
                return result.get('healthy', False) if isinstance(result, dict) else bool(result)
            
            return True  # Assume sucesso se não houver health check
            
        except Exception as e:
            print(f"Erro ao testar mutação: {e}")
            return False
    
    async def _trigger_callback(self, event: str, data: Any):
        """Dispara callbacks de eventos"""
        if event in self.evolution_callbacks:
            for callback in self.evolution_callbacks[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    print(f"Erro em callback {event}: {e}")
    
    def register_callback(self, event: str, callback: Callable):
        """Registra callback para evento"""
        if event in self.evolution_callbacks:
            self.evolution_callbacks[event].append(callback)
    
    def create_gene(
        self,
        gene_id: str,
        gene_type: str,
        initial_value: Any,
        mutable: bool = True,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        options: Optional[List[Any]] = None
    ) -> Gene:
        """Cria um gene com constraints"""
        constraints = {}
        
        if min_value is not None:
            constraints["min"] = min_value
        if max_value is not None:
            constraints["max"] = max_value
        if options is not None:
            constraints["options"] = options
        
        return Gene(
            gene_id=gene_id,
            gene_type=gene_type,
            value=initial_value,
            mutable=mutable,
            constraints=constraints,
            metadata={"reversible": True}
        )
    
    def create_genome_template(self, genes: List[Gene]) -> Genome:
        """Cria template de genoma"""
        gene_dict = {gene.gene_id: gene for gene in genes}
        
        return Genome(
            genome_id=f"template_{datetime.now().timestamp()}",
            genes=gene_dict,
            generation=0
        )
    
    def get_evolution_report(self) -> Dict[str, Any]:
        """Gera relatório de evolução"""
        if not self.evolution_history:
            return {"status": "No evolution history"}
        
        recent_history = self.evolution_history[-10:]
        
        return {
            "current_generation": self.generation,
            "population_size": len(self.population),
            "best_fitness_ever": self.evolution_metrics["best_fitness_ever"],
            "total_mutations": self.evolution_metrics["total_mutations"],
            "successful_mutations": self.evolution_metrics["successful_mutations"],
            "mutation_success_rate": (
                self.evolution_metrics["successful_mutations"] / 
                self.evolution_metrics["total_mutations"]
                if self.evolution_metrics["total_mutations"] > 0 else 0
            ),
            "convergence_rate": self.evolution_metrics["convergence_rate"],
            "recent_fitness_trend": [r.best_genome.fitness for r in recent_history],
            "safety_level": self.safety_level.name,
            "is_evolving": self.evolving
        }
    
    def export_best_genome(self) -> Optional[str]:
        """Exporta melhor genoma encontrado"""
        if not self.evolution_history:
            return None
        
        best = max(
            (r.best_genome for r in self.evolution_history),
            key=lambda g: g.fitness
        )
        
        return json.dumps({
            "genome_id": best.genome_id,
            "fitness": best.fitness,
            "generation": best.generation,
            "genes": {
                gene_id: {
                    "type": gene.gene_type,
                    "value": gene.value,
                    "constraints": gene.constraints
                }
                for gene_id, gene in best.genes.items()
            }
        }, indent=2)
    
    async def shutdown(self):
        """Desliga o motor de evolução"""
        print("🔌 Desligando Motor de Evolução...")
        
        self.evolving = False
        
        if self.evolution_task:
            self.evolution_task.cancel()
            try:
                await self.evolution_task
            except asyncio.CancelledError:
                pass
        
        print("✅ Motor de Evolução desligado") 