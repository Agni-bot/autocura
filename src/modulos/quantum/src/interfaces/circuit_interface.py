"""
Interface Quantum Circuit - Sistema AutoCura
Fase GAMMA: Preparação Quântica

Esta interface abstrai diferentes backends quânticos (Qiskit, Cirq, PennyLane)
permitindo que o sistema use o melhor disponível.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple
from enum import Enum
import numpy as np
import logging

# Configurar logging
logger = logging.getLogger(__name__)


class QuantumBackend(Enum):
    """Backends quânticos suportados"""
    QISKIT = "qiskit"
    CIRQ = "cirq"
    PENNYLANE = "pennylane"
    SIMULATOR = "simulator"
    IBM_QUANTUM = "ibm_quantum"
    AWS_BRAKET = "aws_braket"
    AZURE_QUANTUM = "azure_quantum"


class QuantumGate(Enum):
    """Portas quânticas universais"""
    # Portas de um qubit
    H = "hadamard"
    X = "pauli_x"
    Y = "pauli_y"
    Z = "pauli_z"
    S = "phase_s"
    T = "phase_t"
    RX = "rotation_x"
    RY = "rotation_y"
    RZ = "rotation_z"
    
    # Portas de dois qubits
    CNOT = "controlled_not"
    CZ = "controlled_z"
    SWAP = "swap"
    
    # Portas de três qubits
    TOFFOLI = "toffoli"
    FREDKIN = "fredkin"


class QuantumCircuitInterface(ABC):
    """
    Interface abstrata para circuitos quânticos.
    Permite uso transparente de diferentes backends.
    """
    
    def __init__(self, backend: QuantumBackend = QuantumBackend.SIMULATOR):
        self.backend = backend
        self.circuit = None
        self.num_qubits = 0
        self.num_classical_bits = 0
        self._initialize_backend()
    
    @abstractmethod
    def _initialize_backend(self) -> None:
        """Inicializa o backend específico"""
        pass
    
    @abstractmethod
    def create_circuit(self, num_qubits: int, num_classical_bits: Optional[int] = None) -> Any:
        """
        Cria um novo circuito quântico.
        
        Args:
            num_qubits: Número de qubits
            num_classical_bits: Número de bits clássicos (para medições)
            
        Returns:
            Circuito no formato do backend
        """
        pass
    
    @abstractmethod
    def add_gate(self, gate: QuantumGate, qubits: Union[int, List[int]], 
                 params: Optional[Dict[str, float]] = None) -> None:
        """
        Adiciona uma porta ao circuito.
        
        Args:
            gate: Tipo de porta quântica
            qubits: Índice(s) do(s) qubit(s)
            params: Parâmetros da porta (ex: ângulo de rotação)
        """
        pass
    
    @abstractmethod
    def add_measurement(self, qubit: int, classical_bit: int) -> None:
        """
        Adiciona medição de um qubit.
        
        Args:
            qubit: Índice do qubit a medir
            classical_bit: Índice do bit clássico para armazenar resultado
        """
        pass
    
    @abstractmethod
    def execute(self, shots: int = 1024, optimization_level: int = 1) -> Dict[str, Any]:
        """
        Executa o circuito.
        
        Args:
            shots: Número de execuções
            optimization_level: Nível de otimização do circuito
            
        Returns:
            Resultados da execução
        """
        pass
    
    @abstractmethod
    def get_statevector(self) -> np.ndarray:
        """
        Obtém o vetor de estado do circuito.
        
        Returns:
            Vetor de estado complexo
        """
        pass
    
    @abstractmethod
    def optimize_circuit(self) -> None:
        """Otimiza o circuito reduzindo número de portas"""
        pass
    
    @abstractmethod
    def to_qasm(self) -> str:
        """
        Converte circuito para OpenQASM.
        
        Returns:
            String QASM do circuito
        """
        pass
    
    @abstractmethod
    def from_qasm(self, qasm_str: str) -> None:
        """
        Carrega circuito de string QASM.
        
        Args:
            qasm_str: String OpenQASM
        """
        pass
    
    def add_hadamard(self, qubit: int) -> None:
        """Adiciona porta Hadamard"""
        self.add_gate(QuantumGate.H, qubit)
    
    def add_cnot(self, control: int, target: int) -> None:
        """Adiciona porta CNOT"""
        self.add_gate(QuantumGate.CNOT, [control, target])
    
    def add_rotation_x(self, qubit: int, angle: float) -> None:
        """Adiciona rotação em X"""
        self.add_gate(QuantumGate.RX, qubit, {"angle": angle})
    
    def add_rotation_y(self, qubit: int, angle: float) -> None:
        """Adiciona rotação em Y"""
        self.add_gate(QuantumGate.RY, qubit, {"angle": angle})
    
    def add_rotation_z(self, qubit: int, angle: float) -> None:
        """Adiciona rotação em Z"""
        self.add_gate(QuantumGate.RZ, qubit, {"angle": angle})
    
    def create_bell_pair(self, qubit1: int, qubit2: int) -> None:
        """
        Cria um par de Bell (estado emaranhado).
        
        Args:
            qubit1: Primeiro qubit
            qubit2: Segundo qubit
        """
        self.add_hadamard(qubit1)
        self.add_cnot(qubit1, qubit2)
    
    def create_ghz_state(self, qubits: List[int]) -> None:
        """
        Cria estado GHZ (Greenberger-Horne-Zeilinger).
        
        Args:
            qubits: Lista de qubits para emaranhar
        """
        if len(qubits) < 2:
            raise ValueError("GHZ state requires at least 2 qubits")
        
        self.add_hadamard(qubits[0])
        for i in range(1, len(qubits)):
            self.add_cnot(qubits[0], qubits[i])
    
    def measure_all(self) -> None:
        """Mede todos os qubits"""
        for i in range(self.num_qubits):
            if i < self.num_classical_bits:
                self.add_measurement(i, i)
    
    def get_circuit_depth(self) -> int:
        """
        Retorna a profundidade do circuito.
        
        Returns:
            Número de camadas de portas
        """
        # Implementação específica do backend
        return 0
    
    def get_gate_count(self) -> Dict[str, int]:
        """
        Conta o número de cada tipo de porta.
        
        Returns:
            Dicionário com contagem de portas
        """
        # Implementação específica do backend
        return {}
    
    def visualize(self, output_format: str = "text") -> Union[str, Any]:
        """
        Visualiza o circuito.
        
        Args:
            output_format: Formato de saída (text, mpl, latex)
            
        Returns:
            Representação visual do circuito
        """
        # Implementação específica do backend
        return "Circuit visualization"
    
    def transpile(self, backend_name: str, optimization_level: int = 1) -> Any:
        """
        Transpila circuito para hardware específico.
        
        Args:
            backend_name: Nome do backend alvo
            optimization_level: Nível de otimização
            
        Returns:
            Circuito transpilado
        """
        logger.info(f"Transpiling circuit for {backend_name}")
        # Implementação específica
        return self.circuit
    
    def get_unitary(self) -> np.ndarray:
        """
        Obtém matriz unitária do circuito.
        
        Returns:
            Matriz unitária complexa
        """
        # Implementação específica do backend
        return np.eye(2**self.num_qubits, dtype=complex)
    
    def add_barrier(self, qubits: Optional[List[int]] = None) -> None:
        """
        Adiciona barreira para separar seções do circuito.
        
        Args:
            qubits: Qubits onde adicionar barreira (None = todos)
        """
        # Implementação específica do backend
        pass
    
    def reset(self, qubit: int) -> None:
        """
        Reseta um qubit para |0⟩.
        
        Args:
            qubit: Índice do qubit
        """
        # Implementação específica do backend
        pass
    
    def save_circuit(self, filename: str) -> None:
        """
        Salva circuito em arquivo.
        
        Args:
            filename: Nome do arquivo
        """
        qasm = self.to_qasm()
        with open(filename, 'w') as f:
            f.write(qasm)
        logger.info(f"Circuit saved to {filename}")
    
    def load_circuit(self, filename: str) -> None:
        """
        Carrega circuito de arquivo.
        
        Args:
            filename: Nome do arquivo
        """
        with open(filename, 'r') as f:
            qasm = f.read()
        self.from_qasm(qasm)
        logger.info(f"Circuit loaded from {filename}")
    
    def get_quantum_info(self) -> Dict[str, Any]:
        """
        Obtém informações quânticas do circuito.
        
        Returns:
            Dicionário com métricas quânticas
        """
        return {
            "num_qubits": self.num_qubits,
            "num_classical_bits": self.num_classical_bits,
            "depth": self.get_circuit_depth(),
            "gate_counts": self.get_gate_count(),
            "backend": self.backend.value
        }


class QuantumCircuitFactory:
    """Factory para criar circuitos com o backend apropriado"""
    
    @staticmethod
    def create_circuit(backend: QuantumBackend = QuantumBackend.SIMULATOR) -> QuantumCircuitInterface:
        """
        Cria circuito com o backend especificado.
        
        Args:
            backend: Backend quântico a usar
            
        Returns:
            Instância de QuantumCircuitInterface
        """
        if backend == QuantumBackend.QISKIT:
            from ..circuits.qiskit_circuit import QiskitCircuit
            return QiskitCircuit()
        elif backend == QuantumBackend.CIRQ:
            from ..circuits.cirq_circuit import CirqCircuit
            return CirqCircuit()
        elif backend == QuantumBackend.PENNYLANE:
            from ..circuits.pennylane_circuit import PennyLaneCircuit
            return PennyLaneCircuit()
        else:
            from ..circuits.simulator_circuit import SimulatorCircuit
            return SimulatorCircuit()
    
    @staticmethod
    def get_available_backends() -> List[QuantumBackend]:
        """
        Retorna lista de backends disponíveis.
        
        Returns:
            Lista de backends que podem ser usados
        """
        available = [QuantumBackend.SIMULATOR]  # Sempre disponível
        
        try:
            import qiskit
            available.append(QuantumBackend.QISKIT)
        except ImportError:
            pass
        
        try:
            import cirq
            available.append(QuantumBackend.CIRQ)
        except ImportError:
            pass
        
        try:
            import pennylane
            available.append(QuantumBackend.PENNYLANE)
        except ImportError:
            pass
        
        return available 