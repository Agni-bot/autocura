"""
Interface para Controle de Nanobots
Fase Delta - Sistema AutoCura

Implementa:
- Interface abstrata para nanobots individuais
- Controle de swarm (enxame) de nanobots
- Comunicação nano-escala
- Protocolos de segurança
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple, Protocol
import numpy as np
from datetime import datetime
import asyncio
import json


class NanobotType(Enum):
    """Tipos de nanobots suportados"""
    MEDICAL = "medical"
    REPAIR = "repair"
    SENSOR = "sensor"
    ASSEMBLER = "assembler"
    COMMUNICATION = "communication"
    ENERGY = "energy"
    DEFENSIVE = "defensive"


class NanobotState(Enum):
    """Estados possíveis de um nanobot"""
    IDLE = "idle"
    ACTIVE = "active"
    MOVING = "moving"
    WORKING = "working"
    COMMUNICATING = "communicating"
    RECHARGING = "recharging"
    ERROR = "error"
    DESTROYED = "destroyed"


class CommunicationProtocol(Enum):
    """Protocolos de comunicação nano"""
    MOLECULAR = "molecular"
    ELECTROMAGNETIC = "electromagnetic"
    ACOUSTIC = "acoustic"
    CHEMICAL = "chemical"
    QUANTUM = "quantum"


@dataclass
class NanoPosition:
    """Posição 3D em escala nanométrica"""
    x: float  # nanômetros
    y: float
    z: float
    
    def distance_to(self, other: 'NanoPosition') -> float:
        """Calcula distância euclidiana"""
        return np.sqrt(
            (self.x - other.x)**2 + 
            (self.y - other.y)**2 + 
            (self.z - other.z)**2
        )
    
    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass
class NanoCommand:
    """Comando para nanobot"""
    command_id: str
    action: str
    parameters: Dict[str, Any]
    priority: int = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class NanobotInterface(ABC):
    """Interface abstrata para controle de nanobots individuais"""
    
    def __init__(self, bot_id: str, bot_type: NanobotType):
        self.bot_id = bot_id
        self.bot_type = bot_type
        self.state = NanobotState.IDLE
        self.position = NanoPosition(0.0, 0.0, 0.0)
        self.energy_level = 100.0  # Percentual
        self.payload = {}
        self.command_queue = []
        self.simulation_mode = True  # Sempre inicia em simulação
        
    @abstractmethod
    async def execute_command(self, command: NanoCommand) -> Dict[str, Any]:
        """Executa comando no nanobot"""
        pass
    
    @abstractmethod
    async def move_to(self, target: NanoPosition, speed: float = 1.0) -> bool:
        """Move nanobot para posição alvo"""
        pass
    
    @abstractmethod
    async def perform_action(self, action: str, target: Any = None) -> Dict[str, Any]:
        """Executa ação específica do tipo de nanobot"""
        pass
    
    @abstractmethod
    async def communicate(self, message: Dict[str, Any], protocol: CommunicationProtocol) -> bool:
        """Envia mensagem usando protocolo especificado"""
        pass
    
    @abstractmethod
    def get_sensor_data(self) -> Dict[str, Any]:
        """Obtém dados dos sensores do nanobot"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Retorna status completo do nanobot"""
        pass
    
    async def recharge(self, energy_source: Any = None) -> bool:
        """Recarrega energia do nanobot"""
        self.state = NanobotState.RECHARGING
        # Simulação de recarga
        if self.simulation_mode:
            await asyncio.sleep(0.1)  # Simula tempo de recarga
            self.energy_level = min(100.0, self.energy_level + 20.0)
        self.state = NanobotState.IDLE
        return True
    
    def consume_energy(self, amount: float) -> bool:
        """Consome energia para operação"""
        if self.energy_level >= amount:
            self.energy_level -= amount
            return True
        return False
    
    def is_operational(self) -> bool:
        """Verifica se nanobot está operacional"""
        return (
            self.state != NanobotState.DESTROYED and 
            self.energy_level > 0
        )


class NanobotSwarm:
    """Gerenciador de swarm (enxame) de nanobots"""
    
    def __init__(self, swarm_id: str):
        self.swarm_id = swarm_id
        self.nanobots: Dict[str, NanobotInterface] = {}
        self.formation = "distributed"  # Formação do enxame
        self.objective = None
        self.communication_mesh = {}  # Rede de comunicação
        self.consensus_threshold = 0.7  # 70% para consenso
        
    def add_nanobot(self, nanobot: NanobotInterface) -> bool:
        """Adiciona nanobot ao swarm"""
        if nanobot.bot_id not in self.nanobots:
            self.nanobots[nanobot.bot_id] = nanobot
            self._update_communication_mesh()
            return True
        return False
    
    def remove_nanobot(self, bot_id: str) -> bool:
        """Remove nanobot do swarm"""
        if bot_id in self.nanobots:
            del self.nanobots[bot_id]
            self._update_communication_mesh()
            return True
        return False
    
    async def execute_swarm_command(self, command: NanoCommand) -> Dict[str, Any]:
        """Executa comando em todo o swarm"""
        results = {}
        tasks = []
        
        for bot_id, nanobot in self.nanobots.items():
            if nanobot.is_operational():
                task = asyncio.create_task(
                    nanobot.execute_command(command)
                )
                tasks.append((bot_id, task))
        
        # Aguarda execução paralela
        for bot_id, task in tasks:
            try:
                result = await task
                results[bot_id] = result
            except Exception as e:
                results[bot_id] = {"error": str(e)}
        
        return {
            "swarm_id": self.swarm_id,
            "command": command.action,
            "results": results,
            "success_rate": self._calculate_success_rate(results)
        }
    
    async def form_structure(self, formation: str, center: NanoPosition) -> bool:
        """Organiza swarm em formação específica"""
        self.formation = formation
        positions = self._calculate_formation_positions(formation, center)
        
        tasks = []
        for i, (bot_id, nanobot) in enumerate(self.nanobots.items()):
            if i < len(positions) and nanobot.is_operational():
                task = asyncio.create_task(
                    nanobot.move_to(positions[i])
                )
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return all(r is True for r in results if not isinstance(r, Exception))
    
    async def collective_decision(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tomada de decisão coletiva do swarm"""
        votes = {i: 0 for i in range(len(options))}
        
        # Cada nanobot vota baseado em seus sensores
        for nanobot in self.nanobots.values():
            if nanobot.is_operational():
                sensor_data = nanobot.get_sensor_data()
                vote = self._evaluate_option(sensor_data, options)
                votes[vote] += 1
        
        # Determina consenso
        total_votes = sum(votes.values())
        if total_votes == 0:
            return {"decision": None, "consensus": False}
        
        best_option = max(votes, key=votes.get)
        consensus_level = votes[best_option] / total_votes
        
        return {
            "decision": options[best_option] if consensus_level >= self.consensus_threshold else None,
            "consensus": consensus_level >= self.consensus_threshold,
            "consensus_level": consensus_level,
            "votes": votes
        }
    
    async def distributed_sensing(self) -> Dict[str, Any]:
        """Coleta dados distribuída de todos os sensores"""
        sensor_data = {}
        
        tasks = []
        for bot_id, nanobot in self.nanobots.items():
            if nanobot.is_operational():
                sensor_data[bot_id] = nanobot.get_sensor_data()
        
        # Agrega dados
        aggregated = self._aggregate_sensor_data(sensor_data)
        
        return {
            "swarm_id": self.swarm_id,
            "timestamp": datetime.now().isoformat(),
            "individual_data": sensor_data,
            "aggregated_data": aggregated,
            "coverage_area": self._calculate_coverage()
        }
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Status completo do swarm"""
        operational_count = sum(
            1 for n in self.nanobots.values() 
            if n.is_operational()
        )
        
        return {
            "swarm_id": self.swarm_id,
            "total_nanobots": len(self.nanobots),
            "operational": operational_count,
            "formation": self.formation,
            "objective": self.objective,
            "average_energy": self._calculate_average_energy(),
            "communication_integrity": self._check_communication_integrity(),
            "swarm_health": operational_count / len(self.nanobots) if self.nanobots else 0
        }
    
    def _update_communication_mesh(self):
        """Atualiza rede de comunicação entre nanobots"""
        self.communication_mesh = {}
        
        # Cria mesh baseado em proximidade
        for bot1_id, bot1 in self.nanobots.items():
            connections = []
            for bot2_id, bot2 in self.nanobots.items():
                if bot1_id != bot2_id:
                    distance = bot1.position.distance_to(bot2.position)
                    if distance < 1000:  # 1 micrômetro de alcance
                        connections.append(bot2_id)
            self.communication_mesh[bot1_id] = connections
    
    def _calculate_formation_positions(self, formation: str, center: NanoPosition) -> List[NanoPosition]:
        """Calcula posições para formação específica"""
        positions = []
        n = len(self.nanobots)
        
        if formation == "sphere":
            # Distribui em esfera
            for i in range(n):
                theta = 2 * np.pi * i / n
                phi = np.arccos(1 - 2 * (i + 0.5) / n)
                r = 500  # raio de 500nm
                
                x = center.x + r * np.sin(phi) * np.cos(theta)
                y = center.y + r * np.sin(phi) * np.sin(theta)
                z = center.z + r * np.cos(phi)
                
                positions.append(NanoPosition(x, y, z))
                
        elif formation == "line":
            # Formação em linha
            spacing = 100  # 100nm entre bots
            for i in range(n):
                positions.append(NanoPosition(
                    center.x + i * spacing,
                    center.y,
                    center.z
                ))
                
        elif formation == "grid":
            # Grade 3D
            side = int(np.ceil(n ** (1/3)))
            spacing = 200
            
            for i in range(n):
                x_idx = i % side
                y_idx = (i // side) % side
                z_idx = i // (side * side)
                
                positions.append(NanoPosition(
                    center.x + x_idx * spacing,
                    center.y + y_idx * spacing,
                    center.z + z_idx * spacing
                ))
        
        else:  # distributed (padrão)
            # Distribuição aleatória em volume
            for i in range(n):
                positions.append(NanoPosition(
                    center.x + np.random.uniform(-1000, 1000),
                    center.y + np.random.uniform(-1000, 1000),
                    center.z + np.random.uniform(-1000, 1000)
                ))
        
        return positions
    
    def _calculate_success_rate(self, results: Dict[str, Any]) -> float:
        """Calcula taxa de sucesso de comando"""
        if not results:
            return 0.0
        
        success_count = sum(
            1 for r in results.values() 
            if isinstance(r, dict) and "error" not in r
        )
        
        return success_count / len(results)
    
    def _evaluate_option(self, sensor_data: Dict[str, Any], options: List[Dict[str, Any]]) -> int:
        """Avalia opções baseado em dados de sensor (simplificado)"""
        # Implementação simplificada - escolhe baseado em hash
        data_hash = hash(json.dumps(sensor_data, sort_keys=True))
        return data_hash % len(options)
    
    def _aggregate_sensor_data(self, sensor_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Agrega dados de múltiplos sensores"""
        if not sensor_data:
            return {}
        
        # Exemplo de agregação simples
        aggregated = {
            "temperature": [],
            "pressure": [],
            "chemical_concentration": {},
            "anomalies": []
        }
        
        for bot_id, data in sensor_data.items():
            if "temperature" in data:
                aggregated["temperature"].append(data["temperature"])
            if "pressure" in data:
                aggregated["pressure"].append(data["pressure"])
            if "anomaly" in data and data["anomaly"]:
                aggregated["anomalies"].append({
                    "bot_id": bot_id,
                    "type": data.get("anomaly_type", "unknown")
                })
        
        # Calcula médias
        if aggregated["temperature"]:
            aggregated["avg_temperature"] = np.mean(aggregated["temperature"])
        if aggregated["pressure"]:
            aggregated["avg_pressure"] = np.mean(aggregated["pressure"])
        
        return aggregated
    
    def _calculate_coverage(self) -> Dict[str, float]:
        """Calcula área/volume de cobertura do swarm"""
        if not self.nanobots:
            return {"volume": 0, "surface_area": 0}
        
        positions = [bot.position for bot in self.nanobots.values()]
        
        # Calcula bounding box
        x_coords = [p.x for p in positions]
        y_coords = [p.y for p in positions]
        z_coords = [p.z for p in positions]
        
        volume = (
            (max(x_coords) - min(x_coords)) *
            (max(y_coords) - min(y_coords)) *
            (max(z_coords) - min(z_coords))
        )
        
        # Aproximação de área de superfície
        surface_area = 2 * (
            (max(x_coords) - min(x_coords)) * (max(y_coords) - min(y_coords)) +
            (max(x_coords) - min(x_coords)) * (max(z_coords) - min(z_coords)) +
            (max(y_coords) - min(y_coords)) * (max(z_coords) - min(z_coords))
        )
        
        return {
            "volume": volume,
            "surface_area": surface_area,
            "unit": "nm³ and nm²"
        }
    
    def _calculate_average_energy(self) -> float:
        """Calcula energia média do swarm"""
        if not self.nanobots:
            return 0.0
        
        total_energy = sum(bot.energy_level for bot in self.nanobots.values())
        return total_energy / len(self.nanobots)
    
    def _check_communication_integrity(self) -> float:
        """Verifica integridade da rede de comunicação"""
        if not self.nanobots:
            return 0.0
        
        # Verifica se todos os bots operacionais estão conectados
        operational_bots = [
            bot_id for bot_id, bot in self.nanobots.items()
            if bot.is_operational()
        ]
        
        if not operational_bots:
            return 0.0
        
        connected = set()
        to_check = [operational_bots[0]]
        
        # BFS para verificar conectividade
        while to_check:
            current = to_check.pop(0)
            if current in connected:
                continue
            
            connected.add(current)
            
            if current in self.communication_mesh:
                for neighbor in self.communication_mesh[current]:
                    if neighbor in operational_bots and neighbor not in connected:
                        to_check.append(neighbor)
        
        return len(connected) / len(operational_bots)


class NanobotProtocol(Protocol):
    """Protocolo para implementações específicas de nanobots"""
    
    def initialize_hardware(self) -> bool:
        """Inicializa hardware real quando disponível"""
        ...
    
    def calibrate_sensors(self) -> Dict[str, Any]:
        """Calibra sensores do nanobot"""
        ...
    
    def self_diagnostic(self) -> Dict[str, Any]:
        """Executa diagnóstico interno"""
        ...
    
    def emergency_shutdown(self) -> bool:
        """Desligamento de emergência"""
        ... 