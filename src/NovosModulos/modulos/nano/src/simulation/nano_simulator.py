"""
Simulador de Sistemas Nano
Fase Delta - Sistema AutoCura

Implementa:
- Simulação física de nanobots
- Dinâmica molecular simplificada
- Interações nano-escala
- Visualização 3D
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
import asyncio
from datetime import datetime
import json
import math

from ..interfaces.nanobot_interface import (
    NanobotInterface, NanobotType, NanobotState, 
    NanoPosition, NanoCommand, NanobotSwarm
)
from ..interfaces.molecular_interface import (
    MolecularStructure, Atom, Bond, AtomType, BondType
)


@dataclass
class PhysicsConstants:
    """Constantes físicas para simulação"""
    BOLTZMANN = 1.380649e-23  # J/K
    AVOGADRO = 6.02214076e23  # mol^-1
    ELEMENTARY_CHARGE = 1.602176634e-19  # C
    VACUUM_PERMITTIVITY = 8.854187817e-12  # F/m
    PLANCK = 6.62607015e-34  # J·s
    
    # Escalas
    NANO_TO_METER = 1e-9
    ANGSTROM_TO_METER = 1e-10
    
    # Parâmetros de simulação
    DEFAULT_TEMPERATURE = 310.15  # K (37°C - temperatura corporal)
    VISCOSITY_WATER = 0.001  # Pa·s
    DIFFUSION_COEFFICIENT = 1e-9  # m²/s (típico para nanopartículas)


@dataclass
class SimulationParameters:
    """Parâmetros da simulação"""
    time_step: float = 1e-12  # segundos (1 picosegundo)
    temperature: float = PhysicsConstants.DEFAULT_TEMPERATURE
    box_size: Tuple[float, float, float] = (1000.0, 1000.0, 1000.0)  # nm
    periodic_boundary: bool = True
    gravity_enabled: bool = False
    brownian_motion: bool = True
    electrostatic_interactions: bool = True
    van_der_waals: bool = True
    collision_detection: bool = True


class SimulatedNanobot(NanobotInterface):
    """Implementação simulada de um nanobot"""
    
    def __init__(self, bot_id: str, bot_type: NanobotType):
        super().__init__(bot_id, bot_type)
        self.velocity = np.array([0.0, 0.0, 0.0])  # nm/s
        self.force = np.array([0.0, 0.0, 0.0])  # pN (piconewtons)
        self.mass = self._calculate_mass()  # kg
        self.radius = self._calculate_radius()  # nm
        self.drag_coefficient = 6 * np.pi * PhysicsConstants.VISCOSITY_WATER * self.radius * PhysicsConstants.NANO_TO_METER
        
    def _calculate_mass(self) -> float:
        """Calcula massa baseada no tipo de nanobot"""
        # Massas típicas em kg
        mass_map = {
            NanobotType.MEDICAL: 1e-18,
            NanobotType.REPAIR: 2e-18,
            NanobotType.SENSOR: 0.5e-18,
            NanobotType.ASSEMBLER: 3e-18,
            NanobotType.COMMUNICATION: 0.3e-18,
            NanobotType.ENERGY: 1.5e-18,
            NanobotType.DEFENSIVE: 2.5e-18
        }
        return mass_map.get(self.bot_type, 1e-18)
    
    def _calculate_radius(self) -> float:
        """Calcula raio baseado no tipo de nanobot"""
        # Raios típicos em nm
        radius_map = {
            NanobotType.MEDICAL: 50,
            NanobotType.REPAIR: 75,
            NanobotType.SENSOR: 30,
            NanobotType.ASSEMBLER: 100,
            NanobotType.COMMUNICATION: 25,
            NanobotType.ENERGY: 60,
            NanobotType.DEFENSIVE: 80
        }
        return radius_map.get(self.bot_type, 50)
    
    async def execute_command(self, command: NanoCommand) -> Dict[str, Any]:
        """Executa comando no nanobot simulado"""
        self.command_queue.append(command)
        
        result = {
            "bot_id": self.bot_id,
            "command_id": command.command_id,
            "status": "executing",
            "timestamp": datetime.now().isoformat()
        }
        
        # Simula execução baseada no tipo de comando
        if command.action == "move":
            target = NanoPosition(**command.parameters["target"])
            success = await self.move_to(target, command.parameters.get("speed", 1.0))
            result["status"] = "completed" if success else "failed"
            
        elif command.action == "sense":
            result["sensor_data"] = self.get_sensor_data()
            result["status"] = "completed"
            
        elif command.action == "communicate":
            success = await self.communicate(
                command.parameters["message"],
                command.parameters.get("protocol", "molecular")
            )
            result["status"] = "completed" if success else "failed"
            
        elif command.action == "perform":
            action_result = await self.perform_action(
                command.parameters["action_type"],
                command.parameters.get("target")
            )
            result.update(action_result)
            
        else:
            result["status"] = "unknown_command"
        
        return result
    
    async def move_to(self, target: NanoPosition, speed: float = 1.0) -> bool:
        """Move nanobot para posição alvo (simulado)"""
        if not self.consume_energy(0.1 * speed):  # Consome energia proporcional à velocidade
            return False
        
        self.state = NanobotState.MOVING
        
        # Calcula direção
        current = np.array([self.position.x, self.position.y, self.position.z])
        target_array = np.array([target.x, target.y, target.z])
        direction = target_array - current
        distance = np.linalg.norm(direction)
        
        if distance < 0.1:  # Já está no alvo
            self.state = NanobotState.IDLE
            return True
        
        # Normaliza direção
        direction = direction / distance
        
        # Define velocidade máxima baseada no tipo
        max_speed = 100 * speed  # nm/s
        self.velocity = direction * max_speed
        
        # Simula movimento (será atualizado pelo simulador)
        await asyncio.sleep(0.1)  # Simula tempo de processamento
        
        return True
    
    async def perform_action(self, action: str, target: Any = None) -> Dict[str, Any]:
        """Executa ação específica do nanobot"""
        self.state = NanobotState.WORKING
        
        result = {
            "action": action,
            "bot_type": self.bot_type.value,
            "success": False,
            "details": {}
        }
        
        # Simula ações baseadas no tipo
        if self.bot_type == NanobotType.MEDICAL:
            if action == "deliver_drug":
                if self.consume_energy(5.0):
                    result["success"] = True
                    result["details"]["drug_delivered"] = self.payload.get("drug", "none")
                    self.payload = {}
                    
            elif action == "diagnose":
                if self.consume_energy(2.0):
                    result["success"] = True
                    result["details"]["diagnosis"] = self._simulate_diagnosis()
                    
        elif self.bot_type == NanobotType.REPAIR:
            if action == "repair_tissue":
                if self.consume_energy(10.0):
                    result["success"] = True
                    result["details"]["repair_complete"] = True
                    
        elif self.bot_type == NanobotType.SENSOR:
            if action == "detailed_scan":
                if self.consume_energy(3.0):
                    result["success"] = True
                    result["details"]["scan_data"] = self._simulate_detailed_scan()
                    
        elif self.bot_type == NanobotType.ASSEMBLER:
            if action == "assemble_structure":
                if self.consume_energy(15.0):
                    result["success"] = True
                    result["details"]["structure_assembled"] = True
                    
        # Simula tempo de execução
        await asyncio.sleep(0.2)
        
        self.state = NanobotState.IDLE
        return result
    
    async def communicate(self, message: Dict[str, Any], protocol: Any) -> bool:
        """Simula comunicação entre nanobots"""
        if not self.consume_energy(0.5):
            return False
        
        self.state = NanobotState.COMMUNICATING
        
        # Simula delay de comunicação baseado no protocolo
        delays = {
            "molecular": 0.1,
            "electromagnetic": 0.01,
            "acoustic": 0.05,
            "chemical": 0.2,
            "quantum": 0.001
        }
        
        await asyncio.sleep(delays.get(protocol, 0.1))
        
        self.state = NanobotState.IDLE
        return True
    
    def get_sensor_data(self) -> Dict[str, Any]:
        """Retorna dados simulados dos sensores"""
        # Simula leituras de sensores
        base_temp = 37.0  # Celsius
        
        sensor_data = {
            "temperature": base_temp + np.random.normal(0, 0.1),
            "pressure": 101.325 + np.random.normal(0, 1),  # kPa
            "ph": 7.4 + np.random.normal(0, 0.05),
            "position": self.position.to_dict(),
            "velocity": {
                "x": self.velocity[0],
                "y": self.velocity[1],
                "z": self.velocity[2]
            },
            "energy_level": self.energy_level,
            "nearby_objects": self._detect_nearby_objects()
        }
        
        # Dados específicos por tipo
        if self.bot_type == NanobotType.SENSOR:
            sensor_data.update({
                "chemical_concentration": {
                    "glucose": 5.0 + np.random.normal(0, 0.5),  # mmol/L
                    "oxygen": 95 + np.random.normal(0, 2),  # %
                    "co2": 40 + np.random.normal(0, 2)  # mmHg
                }
            })
        
        return sensor_data
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status completo do nanobot"""
        return {
            "bot_id": self.bot_id,
            "type": self.bot_type.value,
            "state": self.state.value,
            "position": self.position.to_dict(),
            "velocity": {
                "magnitude": np.linalg.norm(self.velocity),
                "vector": self.velocity.tolist()
            },
            "energy": self.energy_level,
            "mass": self.mass,
            "radius": self.radius,
            "operational": self.is_operational(),
            "command_queue_size": len(self.command_queue),
            "payload": self.payload
        }
    
    def _simulate_diagnosis(self) -> Dict[str, Any]:
        """Simula diagnóstico médico"""
        return {
            "cell_health": np.random.choice(["healthy", "damaged", "infected"], p=[0.7, 0.2, 0.1]),
            "inflammation_level": np.random.uniform(0, 10),
            "pathogen_detected": np.random.choice([True, False], p=[0.1, 0.9]),
            "tissue_integrity": np.random.uniform(70, 100)
        }
    
    def _simulate_detailed_scan(self) -> Dict[str, Any]:
        """Simula varredura detalhada"""
        return {
            "molecular_composition": {
                "proteins": np.random.uniform(10, 20),
                "lipids": np.random.uniform(5, 15),
                "carbohydrates": np.random.uniform(2, 8),
                "nucleic_acids": np.random.uniform(1, 5)
            },
            "structural_integrity": np.random.uniform(80, 100),
            "anomalies_detected": np.random.randint(0, 3)
        }
    
    def _detect_nearby_objects(self) -> List[Dict[str, Any]]:
        """Detecta objetos próximos (simulado)"""
        objects = []
        
        # Simula detecção de alguns objetos
        for i in range(np.random.randint(0, 5)):
            distance = np.random.uniform(10, 100)  # nm
            objects.append({
                "type": np.random.choice(["cell", "protein", "nanobot", "debris"]),
                "distance": distance,
                "direction": {
                    "x": np.random.uniform(-1, 1),
                    "y": np.random.uniform(-1, 1),
                    "z": np.random.uniform(-1, 1)
                }
            })
        
        return objects


class NanoSimulator:
    """Simulador principal de sistemas nano"""
    
    def __init__(self, params: SimulationParameters = None):
        self.params = params or SimulationParameters()
        self.nanobots: Dict[str, SimulatedNanobot] = {}
        self.molecules: Dict[str, MolecularStructure] = {}
        self.time = 0.0  # Tempo de simulação em segundos
        self.history: List[Dict[str, Any]] = []
        self.running = False
        self.visualization_data = []
        
        # Callbacks para eventos
        self.event_callbacks: Dict[str, List[Callable]] = {
            "collision": [],
            "reaction": [],
            "assembly": [],
            "communication": []
        }
    
    def add_nanobot(self, nanobot: SimulatedNanobot) -> bool:
        """Adiciona nanobot à simulação"""
        if nanobot.bot_id not in self.nanobots:
            self.nanobots[nanobot.bot_id] = nanobot
            self._place_randomly(nanobot)
            return True
        return False
    
    def add_molecule(self, molecule: MolecularStructure) -> bool:
        """Adiciona molécula à simulação"""
        if molecule.structure_id not in self.molecules:
            self.molecules[molecule.structure_id] = molecule
            return True
        return False
    
    async def run_simulation(self, duration: float, real_time: bool = False):
        """Executa simulação por duração especificada"""
        self.running = True
        start_time = self.time
        end_time = start_time + duration
        
        while self.time < end_time and self.running:
            # Atualiza física
            self._update_physics()
            
            # Processa interações
            await self._process_interactions()
            
            # Atualiza tempo
            self.time += self.params.time_step
            
            # Registra estado
            if int(self.time * 1e12) % 1000 == 0:  # A cada nanosegundo
                self._record_state()
            
            # Delay para simulação em tempo real
            if real_time:
                await asyncio.sleep(self.params.time_step)
        
        self.running = False
    
    def stop_simulation(self):
        """Para a simulação"""
        self.running = False
    
    def _update_physics(self):
        """Atualiza física de todos os nanobots"""
        for nanobot in self.nanobots.values():
            if not nanobot.is_operational():
                continue
            
            # Reseta forças
            nanobot.force = np.zeros(3)
            
            # Aplica forças
            if self.params.brownian_motion:
                self._apply_brownian_force(nanobot)
            
            if self.params.gravity_enabled:
                self._apply_gravity(nanobot)
            
            # Força de arrasto
            self._apply_drag_force(nanobot)
            
            # Forças intermoleculares
            if self.params.electrostatic_interactions:
                self._apply_electrostatic_forces(nanobot)
            
            if self.params.van_der_waals:
                self._apply_van_der_waals_forces(nanobot)
            
            # Integração de movimento (Verlet)
            self._integrate_motion(nanobot)
            
            # Aplica condições de contorno
            self._apply_boundary_conditions(nanobot)
            
            # Detecção de colisão
            if self.params.collision_detection:
                self._check_collisions(nanobot)
    
    def _apply_brownian_force(self, nanobot: SimulatedNanobot):
        """Aplica força browniana (movimento térmico aleatório)"""
        # Força browniana: F = sqrt(2 * k_B * T * gamma / dt) * N(0,1)
        kT = PhysicsConstants.BOLTZMANN * self.params.temperature
        magnitude = np.sqrt(2 * kT * nanobot.drag_coefficient / self.params.time_step)
        
        # Força aleatória em cada direção
        brownian_force = magnitude * np.random.normal(0, 1, 3) * 1e12  # Converte para pN
        nanobot.force += brownian_force
    
    def _apply_gravity(self, nanobot: SimulatedNanobot):
        """Aplica força gravitacional (geralmente negligível em nanoescala)"""
        g = 9.81  # m/s²
        gravity_force = nanobot.mass * g * 1e12  # Converte para pN
        nanobot.force[2] -= gravity_force
    
    def _apply_drag_force(self, nanobot: SimulatedNanobot):
        """Aplica força de arrasto viscoso"""
        # Lei de Stokes: F = -gamma * v
        drag_force = -nanobot.drag_coefficient * nanobot.velocity * 1e3  # Converte para pN
        nanobot.force += drag_force
    
    def _apply_electrostatic_forces(self, nanobot: SimulatedNanobot):
        """Aplica forças eletrostáticas entre partículas carregadas"""
        # Simplificado - apenas entre nanobots
        for other_id, other in self.nanobots.items():
            if other_id == nanobot.bot_id or not other.is_operational():
                continue
            
            # Calcula vetor distância
            r_vec = np.array([
                other.position.x - nanobot.position.x,
                other.position.y - nanobot.position.y,
                other.position.z - nanobot.position.z
            ])
            
            r = np.linalg.norm(r_vec)
            if r < 1.0:  # Evita singularidade
                r = 1.0
            
            # Lei de Coulomb simplificada (assumindo cargas unitárias)
            k_e = 1 / (4 * np.pi * PhysicsConstants.VACUUM_PERMITTIVITY)
            q1 = q2 = PhysicsConstants.ELEMENTARY_CHARGE  # Carga elementar
            
            force_magnitude = k_e * q1 * q2 / (r * PhysicsConstants.NANO_TO_METER)**2
            force_magnitude *= 1e12  # Converte para pN
            
            # Aplica força na direção correta
            if r > 0:
                force_direction = r_vec / r
                nanobot.force += force_magnitude * force_direction
    
    def _apply_van_der_waals_forces(self, nanobot: SimulatedNanobot):
        """Aplica forças de van der Waals (Lennard-Jones)"""
        epsilon = 1e-21  # J (energia de poço)
        sigma = 2.0  # nm (distância de equilíbrio)
        
        for other_id, other in self.nanobots.items():
            if other_id == nanobot.bot_id or not other.is_operational():
                continue
            
            # Calcula distância
            r_vec = np.array([
                other.position.x - nanobot.position.x,
                other.position.y - nanobot.position.y,
                other.position.z - nanobot.position.z
            ])
            
            r = np.linalg.norm(r_vec)
            if r < 0.1:  # Evita singularidade
                r = 0.1
            
            # Potencial Lennard-Jones: V(r) = 4ε[(σ/r)^12 - (σ/r)^6]
            # Força: F = -dV/dr
            sigma_r = sigma / r
            force_magnitude = 24 * epsilon / r * (2 * sigma_r**12 - sigma_r**6)
            force_magnitude *= 1e12 / PhysicsConstants.NANO_TO_METER  # Converte para pN
            
            # Aplica força
            if r > 0:
                force_direction = r_vec / r
                nanobot.force += force_magnitude * force_direction
    
    def _integrate_motion(self, nanobot: SimulatedNanobot):
        """Integra equações de movimento usando método de Verlet"""
        # Aceleração: a = F/m
        acceleration = nanobot.force / (nanobot.mass * 1e12)  # nm/s²
        
        # Atualiza velocidade: v = v + a*dt
        nanobot.velocity += acceleration * self.params.time_step
        
        # Atualiza posição: x = x + v*dt
        new_position = np.array([
            nanobot.position.x + nanobot.velocity[0] * self.params.time_step,
            nanobot.position.y + nanobot.velocity[1] * self.params.time_step,
            nanobot.position.z + nanobot.velocity[2] * self.params.time_step
        ])
        
        nanobot.position = NanoPosition(new_position[0], new_position[1], new_position[2])
    
    def _apply_boundary_conditions(self, nanobot: SimulatedNanobot):
        """Aplica condições de contorno (periódicas ou reflexivas)"""
        if self.params.periodic_boundary:
            # Condições periódicas
            nanobot.position.x = nanobot.position.x % self.params.box_size[0]
            nanobot.position.y = nanobot.position.y % self.params.box_size[1]
            nanobot.position.z = nanobot.position.z % self.params.box_size[2]
        else:
            # Condições reflexivas
            for i, (pos, vel, size) in enumerate([
                (nanobot.position.x, nanobot.velocity[0], self.params.box_size[0]),
                (nanobot.position.y, nanobot.velocity[1], self.params.box_size[1]),
                (nanobot.position.z, nanobot.velocity[2], self.params.box_size[2])
            ]):
                if pos < 0:
                    if i == 0:
                        nanobot.position.x = -pos
                    elif i == 1:
                        nanobot.position.y = -pos
                    else:
                        nanobot.position.z = -pos
                    nanobot.velocity[i] = -vel
                elif pos > size:
                    if i == 0:
                        nanobot.position.x = 2 * size - pos
                    elif i == 1:
                        nanobot.position.y = 2 * size - pos
                    else:
                        nanobot.position.z = 2 * size - pos
                    nanobot.velocity[i] = -vel
    
    def _check_collisions(self, nanobot: SimulatedNanobot):
        """Verifica e processa colisões"""
        for other_id, other in self.nanobots.items():
            if other_id == nanobot.bot_id or not other.is_operational():
                continue
            
            distance = nanobot.position.distance_to(other.position)
            min_distance = nanobot.radius + other.radius
            
            if distance < min_distance:
                # Colisão detectada
                self._handle_collision(nanobot, other)
    
    def _handle_collision(self, bot1: SimulatedNanobot, bot2: SimulatedNanobot):
        """Processa colisão entre dois nanobots"""
        # Calcula velocidades após colisão elástica
        m1, m2 = bot1.mass, bot2.mass
        v1, v2 = bot1.velocity, bot2.velocity
        
        # Vetor normal de colisão
        n = np.array([
            bot2.position.x - bot1.position.x,
            bot2.position.y - bot1.position.y,
            bot2.position.z - bot1.position.z
        ])
        n = n / np.linalg.norm(n)
        
        # Velocidades relativas
        v_rel = v1 - v2
        v_rel_n = np.dot(v_rel, n)
        
        # Novas velocidades (conservação de momento)
        if v_rel_n > 0:  # Bots se aproximando
            impulse = 2 * v_rel_n / (1/m1 + 1/m2)
            bot1.velocity -= impulse * n / m1
            bot2.velocity += impulse * n / m2
        
        # Separa bots para evitar sobreposição
        overlap = (bot1.radius + bot2.radius) - bot1.position.distance_to(bot2.position)
        if overlap > 0:
            separation = n * overlap / 2
            bot1.position.x -= separation[0]
            bot1.position.y -= separation[1]
            bot1.position.z -= separation[2]
            bot2.position.x += separation[0]
            bot2.position.y += separation[1]
            bot2.position.z += separation[2]
        
        # Dispara evento de colisão
        self._trigger_event("collision", {
            "bot1": bot1.bot_id,
            "bot2": bot2.bot_id,
            "time": self.time,
            "impact_velocity": v_rel_n
        })
    
    async def _process_interactions(self):
        """Processa interações entre nanobots e moléculas"""
        # Interações nanobot-nanobot
        for bot1_id, bot1 in self.nanobots.items():
            if not bot1.is_operational():
                continue
            
            for bot2_id, bot2 in self.nanobots.items():
                if bot1_id >= bot2_id or not bot2.is_operational():
                    continue
                
                distance = bot1.position.distance_to(bot2.position)
                
                # Comunicação de curto alcance
                if distance < 100 and bot1.state == NanobotState.COMMUNICATING:
                    self._trigger_event("communication", {
                        "sender": bot1_id,
                        "receiver": bot2_id,
                        "distance": distance,
                        "time": self.time
                    })
        
        # Interações nanobot-molécula
        for bot in self.nanobots.values():
            if bot.bot_type == NanobotType.ASSEMBLER and bot.is_operational():
                # Verifica moléculas próximas para montagem
                for mol in self.molecules.values():
                    # Simplificado - verifica distância ao centro de massa
                    mol_center = self._get_molecule_center(mol)
                    bot_pos = np.array([bot.position.x, bot.position.y, bot.position.z])
                    
                    if np.linalg.norm(mol_center - bot_pos) < 200:
                        self._trigger_event("assembly", {
                            "nanobot": bot.bot_id,
                            "molecule": mol.structure_id,
                            "time": self.time
                        })
    
    def _place_randomly(self, nanobot: SimulatedNanobot):
        """Posiciona nanobot aleatoriamente na caixa de simulação"""
        nanobot.position = NanoPosition(
            np.random.uniform(0, self.params.box_size[0]),
            np.random.uniform(0, self.params.box_size[1]),
            np.random.uniform(0, self.params.box_size[2])
        )
    
    def _get_molecule_center(self, molecule: MolecularStructure) -> np.ndarray:
        """Calcula centro de massa da molécula"""
        if not molecule.atoms:
            return np.zeros(3)
        
        total_mass = 0.0
        weighted_pos = np.zeros(3)
        
        for atom in molecule.atoms.values():
            mass = atom.atom_type.atomic_mass
            total_mass += mass
            weighted_pos += mass * np.array(atom.position)
        
        return weighted_pos / total_mass if total_mass > 0 else np.zeros(3)
    
    def _record_state(self):
        """Registra estado atual da simulação"""
        state = {
            "time": self.time,
            "nanobots": {
                bot_id: {
                    "position": bot.position.to_dict(),
                    "velocity": bot.velocity.tolist(),
                    "energy": bot.energy_level,
                    "state": bot.state.value
                }
                for bot_id, bot in self.nanobots.items()
            },
            "statistics": self._calculate_statistics()
        }
        
        self.history.append(state)
        self.visualization_data.append(self._prepare_visualization_frame())
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calcula estatísticas da simulação"""
        if not self.nanobots:
            return {}
        
        velocities = [np.linalg.norm(bot.velocity) for bot in self.nanobots.values()]
        energies = [bot.energy_level for bot in self.nanobots.values()]
        
        # Temperatura cinética
        total_kinetic_energy = sum(
            0.5 * bot.mass * np.linalg.norm(bot.velocity)**2 
            for bot in self.nanobots.values()
        )
        
        kinetic_temperature = (2 * total_kinetic_energy) / (3 * len(self.nanobots) * PhysicsConstants.BOLTZMANN)
        
        return {
            "avg_velocity": np.mean(velocities) if velocities else 0,
            "max_velocity": np.max(velocities) if velocities else 0,
            "avg_energy": np.mean(energies) if energies else 0,
            "kinetic_temperature": kinetic_temperature,
            "operational_bots": sum(1 for bot in self.nanobots.values() if bot.is_operational())
        }
    
    def _prepare_visualization_frame(self) -> Dict[str, Any]:
        """Prepara dados para visualização"""
        return {
            "time": self.time,
            "nanobots": [
                {
                    "id": bot.bot_id,
                    "type": bot.bot_type.value,
                    "position": bot.position.to_dict(),
                    "radius": bot.radius,
                    "color": self._get_bot_color(bot),
                    "state": bot.state.value
                }
                for bot in self.nanobots.values()
            ],
            "molecules": [
                {
                    "id": mol.structure_id,
                    "atoms": [
                        {
                            "position": atom.position,
                            "type": atom.atom_type.symbol,
                            "radius": self._get_atom_radius(atom.atom_type)
                        }
                        for atom in mol.atoms.values()
                    ]
                }
                for mol in self.molecules.values()
            ]
        }
    
    def _get_bot_color(self, bot: SimulatedNanobot) -> str:
        """Retorna cor para visualização baseada no tipo"""
        color_map = {
            NanobotType.MEDICAL: "#FF0000",      # Vermelho
            NanobotType.REPAIR: "#00FF00",       # Verde
            NanobotType.SENSOR: "#0000FF",       # Azul
            NanobotType.ASSEMBLER: "#FFFF00",    # Amarelo
            NanobotType.COMMUNICATION: "#FF00FF", # Magenta
            NanobotType.ENERGY: "#00FFFF",       # Ciano
            NanobotType.DEFENSIVE: "#FFA500"     # Laranja
        }
        return color_map.get(bot.bot_type, "#FFFFFF")
    
    def _get_atom_radius(self, atom_type: AtomType) -> float:
        """Retorna raio atômico para visualização"""
        radius_map = {
            "H": 0.25, "C": 0.7, "N": 0.65, "O": 0.6,
            "P": 1.0, "S": 1.0, "Si": 1.1, "Fe": 1.4, "Au": 1.44
        }
        return radius_map.get(atom_type.symbol, 0.5)
    
    def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """Dispara callbacks de evento"""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                callback(data)
    
    def register_event_callback(self, event_type: str, callback: Callable):
        """Registra callback para evento"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
    
    def get_simulation_report(self) -> Dict[str, Any]:
        """Gera relatório completo da simulação"""
        return {
            "duration": self.time,
            "time_steps": len(self.history),
            "parameters": {
                "time_step": self.params.time_step,
                "temperature": self.params.temperature,
                "box_size": self.params.box_size,
                "physics_enabled": {
                    "brownian_motion": self.params.brownian_motion,
                    "electrostatic": self.params.electrostatic_interactions,
                    "van_der_waals": self.params.van_der_waals,
                    "collisions": self.params.collision_detection
                }
            },
            "nanobots": {
                "total": len(self.nanobots),
                "types": {
                    bot_type.value: sum(1 for bot in self.nanobots.values() if bot.bot_type == bot_type)
                    for bot_type in NanobotType
                },
                "operational": sum(1 for bot in self.nanobots.values() if bot.is_operational())
            },
            "molecules": {
                "total": len(self.molecules),
                "total_atoms": sum(len(mol.atoms) for mol in self.molecules.values()),
                "total_bonds": sum(len(mol.bonds) for mol in self.molecules.values())
            },
            "final_statistics": self._calculate_statistics() if self.history else {},
            "events_summary": self._summarize_events()
        }
    
    def _summarize_events(self) -> Dict[str, int]:
        """Resumo de eventos ocorridos"""
        # Implementação simplificada - contaria eventos reais
        return {
            "collisions": 0,
            "communications": 0,
            "assemblies": 0,
            "reactions": 0
        }
    
    def export_visualization(self, filename: str, format: str = "json"):
        """Exporta dados de visualização"""
        if format == "json":
            with open(filename, 'w') as f:
                json.dump({
                    "metadata": {
                        "duration": self.time,
                        "frames": len(self.visualization_data),
                        "box_size": self.params.box_size
                    },
                    "frames": self.visualization_data
                }, f, indent=2)
        else:
            raise ValueError(f"Formato não suportado: {format}") 