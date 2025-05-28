"""
Simulator Circuit - Sistema AutoCura
Fase GAMMA: Implementação de Circuito com Simulador

Implementa um simulador quântico básico para testar e executar
circuitos quânticos quando hardware real não está disponível.
"""

import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
from collections import defaultdict
import random

from ..interfaces.circuit_interface import QuantumCircuitInterface, QuantumGate, QuantumBackend

logger = logging.getLogger(__name__)


class SimulatorCircuit(QuantumCircuitInterface):
    """
    Implementação de circuito quântico usando simulador básico.
    Mantém o estado quântico completo em memória.
    """
    
    def __init__(self):
        super().__init__(QuantumBackend.SIMULATOR)
        self.gates = []  # Lista de portas aplicadas
        self.measurements = []  # Lista de medições
        self.statevector = None
        self.measured_qubits = set()
    
    def _initialize_backend(self) -> None:
        """Inicializa o simulador"""
        logger.info("Initializing quantum simulator backend")
        self.max_qubits = 20  # Limite prático para simulação
    
    def create_circuit(self, num_qubits: int, num_classical_bits: Optional[int] = None) -> None:
        """Cria um novo circuito quântico"""
        if num_qubits > self.max_qubits:
            raise ValueError(f"Simulator limited to {self.max_qubits} qubits")
        
        self.num_qubits = num_qubits
        self.num_classical_bits = num_classical_bits or num_qubits
        
        # Inicializar estado |00...0>
        self.statevector = np.zeros(2**num_qubits, dtype=complex)
        self.statevector[0] = 1.0
        
        # Limpar listas
        self.gates = []
        self.measurements = []
        self.measured_qubits = set()
        
        logger.info(f"Created circuit with {num_qubits} qubits and {self.num_classical_bits} classical bits")
    
    def add_gate(self, gate: QuantumGate, qubits: Union[int, List[int]], 
                 params: Optional[Dict[str, float]] = None) -> None:
        """Adiciona uma porta ao circuito"""
        if isinstance(qubits, int):
            qubits = [qubits]
        
        # Verificar validade dos qubits
        for q in qubits:
            if q >= self.num_qubits or q < 0:
                raise ValueError(f"Qubit index {q} out of range")
        
        # Armazenar porta
        self.gates.append({
            'gate': gate,
            'qubits': qubits,
            'params': params or {}
        })
        
        # Aplicar porta ao statevector
        self._apply_gate_to_statevector(gate, qubits, params)
    
    def add_measurement(self, qubit: int, classical_bit: int) -> None:
        """Adiciona medição de um qubit"""
        if qubit >= self.num_qubits or qubit < 0:
            raise ValueError(f"Qubit index {qubit} out of range")
        if classical_bit >= self.num_classical_bits or classical_bit < 0:
            raise ValueError(f"Classical bit index {classical_bit} out of range")
        
        self.measurements.append({
            'qubit': qubit,
            'classical_bit': classical_bit
        })
        self.measured_qubits.add(qubit)
    
    def execute(self, shots: int = 1024, optimization_level: int = 1) -> Dict[str, Any]:
        """Executa o circuito"""
        logger.info(f"Executing circuit with {shots} shots")
        
        if not self.measurements:
            # Se não há medições, retornar statevector
            return {
                'statevector': self.statevector.copy(),
                'counts': {},
                'memory': []
            }
        
        # Simular medições
        counts = defaultdict(int)
        memory = []
        
        for shot in range(shots):
            # Copiar statevector para esta execução
            shot_statevector = self.statevector.copy()
            
            # Realizar medições
            measurement_result = ['0'] * self.num_classical_bits
            
            for measurement in self.measurements:
                qubit = measurement['qubit']
                cbit = measurement['classical_bit']
                
                # Medir qubit
                result = self._measure_qubit(shot_statevector, qubit)
                measurement_result[cbit] = str(result)
                
                # Colapsar statevector
                shot_statevector = self._collapse_statevector(shot_statevector, qubit, result)
            
            # Registrar resultado
            bitstring = ''.join(measurement_result)
            counts[bitstring] += 1
            memory.append(bitstring)
        
        return {
            'counts': dict(counts),
            'memory': memory,
            'statevector': self.statevector.copy() if not self.measured_qubits else None
        }
    
    def get_statevector(self) -> np.ndarray:
        """Obtém o vetor de estado do circuito"""
        if self.measured_qubits:
            logger.warning("Statevector may not be pure after measurements")
        return self.statevector.copy()
    
    def optimize_circuit(self) -> None:
        """Otimiza o circuito reduzindo número de portas"""
        # Implementação básica: remover portas consecutivas que se cancelam
        optimized_gates = []
        
        i = 0
        while i < len(self.gates):
            current_gate = self.gates[i]
            
            # Verificar se próxima porta cancela a atual
            if i + 1 < len(self.gates):
                next_gate = self.gates[i + 1]
                
                if self._gates_cancel(current_gate, next_gate):
                    # Pular ambas as portas
                    i += 2
                    continue
            
            optimized_gates.append(current_gate)
            i += 1
        
        self.gates = optimized_gates
        logger.info(f"Circuit optimized: {len(self.gates)} gates remaining")
    
    def to_qasm(self) -> str:
        """Converte circuito para OpenQASM"""
        qasm_lines = [
            'OPENQASM 2.0;',
            'include "qelib1.inc";',
            f'qreg q[{self.num_qubits}];',
            f'creg c[{self.num_classical_bits}];',
            ''
        ]
        
        # Adicionar portas
        for gate_info in self.gates:
            gate = gate_info['gate']
            qubits = gate_info['qubits']
            params = gate_info['params']
            
            qasm_line = self._gate_to_qasm(gate, qubits, params)
            if qasm_line:
                qasm_lines.append(qasm_line)
        
        # Adicionar medições
        for measurement in self.measurements:
            qasm_lines.append(f"measure q[{measurement['qubit']}] -> c[{measurement['classical_bit']}];")
        
        return '\n'.join(qasm_lines)
    
    def from_qasm(self, qasm_str: str) -> None:
        """Carrega circuito de string QASM"""
        # Implementação simplificada
        lines = qasm_str.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Pular comentários e linhas vazias
            if not line or line.startswith('//') or line.startswith('OPENQASM') or line.startswith('include'):
                continue
            
            # Extrair qreg/creg
            if line.startswith('qreg'):
                # qreg q[n];
                n = int(line.split('[')[1].split(']')[0])
                self.create_circuit(n)
            elif line.startswith('creg'):
                # creg c[n];
                n = int(line.split('[')[1].split(']')[0])
                self.num_classical_bits = n
            else:
                # Tentar parsear porta
                self._parse_qasm_gate(line)
    
    def get_circuit_depth(self) -> int:
        """Retorna a profundidade do circuito"""
        if not self.gates:
            return 0
        
        # Calcular profundidade considerando paralelismo
        qubit_depths = [0] * self.num_qubits
        
        for gate_info in self.gates:
            qubits = gate_info['qubits']
            max_depth = max(qubit_depths[q] for q in qubits)
            
            for q in qubits:
                qubit_depths[q] = max_depth + 1
        
        return max(qubit_depths)
    
    def get_gate_count(self) -> Dict[str, int]:
        """Conta o número de cada tipo de porta"""
        gate_counts = defaultdict(int)
        
        for gate_info in self.gates:
            gate_name = gate_info['gate'].value
            gate_counts[gate_name] += 1
        
        return dict(gate_counts)
    
    def visualize(self, output_format: str = "text") -> str:
        """Visualiza o circuito"""
        if output_format != "text":
            logger.warning(f"Format {output_format} not supported, using text")
        
        # Criar visualização ASCII simples
        lines = []
        
        # Cabeçalho
        lines.append(f"Quantum Circuit ({self.num_qubits} qubits)")
        lines.append("=" * 50)
        
        # Linhas dos qubits
        qubit_lines = [f"q{i}: " for i in range(self.num_qubits)]
        
        # Adicionar portas
        for gate_info in self.gates:
            gate = gate_info['gate']
            qubits = gate_info['qubits']
            
            # Determinar símbolo da porta
            if gate == QuantumGate.H:
                symbol = "H"
            elif gate == QuantumGate.X:
                symbol = "X"
            elif gate == QuantumGate.Y:
                symbol = "Y"
            elif gate == QuantumGate.Z:
                symbol = "Z"
            elif gate == QuantumGate.CNOT:
                symbol = "●" if qubits[0] < qubits[1] else "○"
            else:
                symbol = gate.name[:3]
            
            # Adicionar às linhas apropriadas
            max_len = max(len(line) for line in qubit_lines)
            for i, line in enumerate(qubit_lines):
                if len(line) < max_len:
                    qubit_lines[i] += "-" * (max_len - len(line))
            
            if len(qubits) == 1:
                qubit_lines[qubits[0]] += f"-[{symbol}]-"
            elif len(qubits) == 2:
                # Porta de dois qubits
                control, target = qubits
                qubit_lines[control] += "-●-"
                qubit_lines[target] += "-⊕-" if gate == QuantumGate.CNOT else "-○-"
                
                # Conectar com linha vertical
                min_q = min(control, target)
                max_q = max(control, target)
                for q in range(min_q + 1, max_q):
                    qubit_lines[q] += "-│-"
        
        # Adicionar medições
        if self.measurements:
            max_len = max(len(line) for line in qubit_lines)
            for i, line in enumerate(qubit_lines):
                if len(line) < max_len:
                    qubit_lines[i] += "-" * (max_len - len(line))
            
            for measurement in self.measurements:
                qubit_lines[measurement['qubit']] += "-[M]-"
        
        lines.extend(qubit_lines)
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def _apply_gate_to_statevector(self, 
                                  gate: QuantumGate,
                                  qubits: List[int],
                                  params: Optional[Dict[str, float]]) -> None:
        """Aplica uma porta ao statevector"""
        
        if gate == QuantumGate.H:
            self._apply_hadamard(qubits[0])
        elif gate == QuantumGate.X:
            self._apply_pauli_x(qubits[0])
        elif gate == QuantumGate.Y:
            self._apply_pauli_y(qubits[0])
        elif gate == QuantumGate.Z:
            self._apply_pauli_z(qubits[0])
        elif gate == QuantumGate.S:
            self._apply_phase_s(qubits[0])
        elif gate == QuantumGate.T:
            self._apply_phase_t(qubits[0])
        elif gate == QuantumGate.RX:
            self._apply_rotation_x(qubits[0], params['angle'])
        elif gate == QuantumGate.RY:
            self._apply_rotation_y(qubits[0], params['angle'])
        elif gate == QuantumGate.RZ:
            self._apply_rotation_z(qubits[0], params['angle'])
        elif gate == QuantumGate.CNOT:
            self._apply_cnot(qubits[0], qubits[1])
        elif gate == QuantumGate.CZ:
            self._apply_cz(qubits[0], qubits[1])
        elif gate == QuantumGate.SWAP:
            self._apply_swap(qubits[0], qubits[1])
        elif gate == QuantumGate.TOFFOLI:
            self._apply_toffoli(qubits[0], qubits[1], qubits[2])
        else:
            logger.warning(f"Gate {gate} not implemented in simulator")
    
    def _apply_hadamard(self, qubit: int) -> None:
        """Aplica porta Hadamard"""
        H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        self._apply_single_qubit_gate(H, qubit)
    
    def _apply_pauli_x(self, qubit: int) -> None:
        """Aplica porta Pauli-X"""
        X = np.array([[0, 1], [1, 0]])
        self._apply_single_qubit_gate(X, qubit)
    
    def _apply_pauli_y(self, qubit: int) -> None:
        """Aplica porta Pauli-Y"""
        Y = np.array([[0, -1j], [1j, 0]])
        self._apply_single_qubit_gate(Y, qubit)
    
    def _apply_pauli_z(self, qubit: int) -> None:
        """Aplica porta Pauli-Z"""
        Z = np.array([[1, 0], [0, -1]])
        self._apply_single_qubit_gate(Z, qubit)
    
    def _apply_phase_s(self, qubit: int) -> None:
        """Aplica porta S (phase)"""
        S = np.array([[1, 0], [0, 1j]])
        self._apply_single_qubit_gate(S, qubit)
    
    def _apply_phase_t(self, qubit: int) -> None:
        """Aplica porta T"""
        T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]])
        self._apply_single_qubit_gate(T, qubit)
    
    def _apply_rotation_x(self, qubit: int, angle: float) -> None:
        """Aplica rotação em X"""
        c = np.cos(angle / 2)
        s = np.sin(angle / 2)
        RX = np.array([[c, -1j * s], [-1j * s, c]])
        self._apply_single_qubit_gate(RX, qubit)
    
    def _apply_rotation_y(self, qubit: int, angle: float) -> None:
        """Aplica rotação em Y"""
        c = np.cos(angle / 2)
        s = np.sin(angle / 2)
        RY = np.array([[c, -s], [s, c]])
        self._apply_single_qubit_gate(RY, qubit)
    
    def _apply_rotation_z(self, qubit: int, angle: float) -> None:
        """Aplica rotação em Z"""
        RZ = np.array([[np.exp(-1j * angle / 2), 0], 
                      [0, np.exp(1j * angle / 2)]])
        self._apply_single_qubit_gate(RZ, qubit)
    
    def _apply_single_qubit_gate(self, gate_matrix: np.ndarray, qubit: int) -> None:
        """Aplica matriz 2x2 em um qubit específico"""
        n = self.num_qubits
        
        # Para cada estado base computacional
        new_statevector = np.zeros_like(self.statevector)
        
        for state in range(2**n):
            # Extrair bit do qubit alvo
            qubit_bit = (state >> (n - qubit - 1)) & 1
            
            # Estados que diferem apenas no qubit alvo
            state0 = state & ~(1 << (n - qubit - 1))  # Bit do qubit = 0
            state1 = state | (1 << (n - qubit - 1))   # Bit do qubit = 1
            
            # Aplicar porta
            if qubit_bit == 0:
                new_statevector[state0] += gate_matrix[0, 0] * self.statevector[state0]
                new_statevector[state1] += gate_matrix[1, 0] * self.statevector[state0]
            else:
                new_statevector[state0] += gate_matrix[0, 1] * self.statevector[state1]
                new_statevector[state1] += gate_matrix[1, 1] * self.statevector[state1]
        
        self.statevector = new_statevector
    
    def _apply_cnot(self, control: int, target: int) -> None:
        """Aplica porta CNOT"""
        n = self.num_qubits
        new_statevector = self.statevector.copy()
        
        for state in range(2**n):
            control_bit = (state >> (n - control - 1)) & 1
            
            if control_bit == 1:
                # Flip target bit
                target_mask = 1 << (n - target - 1)
                flipped_state = state ^ target_mask
                
                # Trocar amplitudes
                new_statevector[state] = self.statevector[flipped_state]
                new_statevector[flipped_state] = self.statevector[state]
        
        self.statevector = new_statevector
    
    def _apply_cz(self, control: int, target: int) -> None:
        """Aplica porta CZ"""
        n = self.num_qubits
        
        for state in range(2**n):
            control_bit = (state >> (n - control - 1)) & 1
            target_bit = (state >> (n - target - 1)) & 1
            
            if control_bit == 1 and target_bit == 1:
                self.statevector[state] *= -1
    
    def _apply_swap(self, qubit1: int, qubit2: int) -> None:
        """Aplica porta SWAP"""
        n = self.num_qubits
        new_statevector = self.statevector.copy()
        
        for state in range(2**n):
            bit1 = (state >> (n - qubit1 - 1)) & 1
            bit2 = (state >> (n - qubit2 - 1)) & 1
            
            if bit1 != bit2:
                # Trocar bits
                mask1 = 1 << (n - qubit1 - 1)
                mask2 = 1 << (n - qubit2 - 1)
                swapped_state = state ^ mask1 ^ mask2
                
                new_statevector[swapped_state] = self.statevector[state]
        
        self.statevector = new_statevector
    
    def _apply_toffoli(self, control1: int, control2: int, target: int) -> None:
        """Aplica porta Toffoli (CCNOT)"""
        n = self.num_qubits
        new_statevector = self.statevector.copy()
        
        for state in range(2**n):
            control1_bit = (state >> (n - control1 - 1)) & 1
            control2_bit = (state >> (n - control2 - 1)) & 1
            
            if control1_bit == 1 and control2_bit == 1:
                # Flip target bit
                target_mask = 1 << (n - target - 1)
                flipped_state = state ^ target_mask
                
                # Trocar amplitudes
                new_statevector[state] = self.statevector[flipped_state]
                new_statevector[flipped_state] = self.statevector[state]
        
        self.statevector = new_statevector
    
    def _measure_qubit(self, statevector: np.ndarray, qubit: int) -> int:
        """Mede um qubit e retorna 0 ou 1"""
        n = self.num_qubits
        
        # Calcular probabilidade de medir 0
        prob_0 = 0.0
        for state in range(2**n):
            qubit_bit = (state >> (n - qubit - 1)) & 1
            if qubit_bit == 0:
                prob_0 += abs(statevector[state])**2
        
        # Decidir resultado da medição
        if random.random() < prob_0:
            return 0
        else:
            return 1
    
    def _collapse_statevector(self, 
                             statevector: np.ndarray,
                             qubit: int,
                             measurement: int) -> np.ndarray:
        """Colapsa statevector após medição"""
        n = self.num_qubits
        collapsed = statevector.copy()
        
        # Zerar estados incompatíveis com medição
        norm = 0.0
        for state in range(2**n):
            qubit_bit = (state >> (n - qubit - 1)) & 1
            
            if qubit_bit != measurement:
                collapsed[state] = 0.0
            else:
                norm += abs(collapsed[state])**2
        
        # Renormalizar
        if norm > 0:
            collapsed /= np.sqrt(norm)
        
        return collapsed
    
    def _gates_cancel(self, gate1: Dict, gate2: Dict) -> bool:
        """Verifica se duas portas se cancelam"""
        if gate1['qubits'] != gate2['qubits']:
            return False
        
        # Portas que são auto-inversas
        self_inverse = [QuantumGate.H, QuantumGate.X, QuantumGate.Y, 
                       QuantumGate.Z, QuantumGate.CNOT, QuantumGate.SWAP]
        
        if gate1['gate'] == gate2['gate'] and gate1['gate'] in self_inverse:
            return True
        
        # S e S†
        if (gate1['gate'] == QuantumGate.S and gate2['gate'] == QuantumGate.S and
            gate1.get('params', {}).get('dagger', False) != gate2.get('params', {}).get('dagger', False)):
            return True
        
        return False
    
    def _gate_to_qasm(self, 
                     gate: QuantumGate,
                     qubits: List[int],
                     params: Dict[str, float]) -> str:
        """Converte porta para linha QASM"""
        q_str = ', '.join(f'q[{q}]' for q in qubits)
        
        if gate == QuantumGate.H:
            return f"h {q_str};"
        elif gate == QuantumGate.X:
            return f"x {q_str};"
        elif gate == QuantumGate.Y:
            return f"y {q_str};"
        elif gate == QuantumGate.Z:
            return f"z {q_str};"
        elif gate == QuantumGate.S:
            return f"s {q_str};"
        elif gate == QuantumGate.T:
            return f"t {q_str};"
        elif gate == QuantumGate.RX:
            return f"rx({params['angle']}) {q_str};"
        elif gate == QuantumGate.RY:
            return f"ry({params['angle']}) {q_str};"
        elif gate == QuantumGate.RZ:
            return f"rz({params['angle']}) {q_str};"
        elif gate == QuantumGate.CNOT:
            return f"cx q[{qubits[0]}], q[{qubits[1]}];"
        elif gate == QuantumGate.CZ:
            return f"cz q[{qubits[0]}], q[{qubits[1]}];"
        elif gate == QuantumGate.SWAP:
            return f"swap q[{qubits[0]}], q[{qubits[1]}];"
        elif gate == QuantumGate.TOFFOLI:
            return f"ccx q[{qubits[0]}], q[{qubits[1]}], q[{qubits[2]}];"
        else:
            return f"// {gate.value} not supported in QASM"
    
    def _parse_qasm_gate(self, line: str) -> None:
        """Parseia linha QASM e adiciona porta"""
        # Implementação simplificada
        # Remove ponto e vírgula
        line = line.rstrip(';').strip()
        
        # Extrair porta e argumentos
        parts = line.split()
        if not parts:
            return
        
        gate_name = parts[0].lower()
        
        # Mapear para QuantumGate
        gate_map = {
            'h': QuantumGate.H,
            'x': QuantumGate.X,
            'y': QuantumGate.Y,
            'z': QuantumGate.Z,
            's': QuantumGate.S,
            't': QuantumGate.T,
            'cx': QuantumGate.CNOT,
            'cz': QuantumGate.CZ,
            'swap': QuantumGate.SWAP,
            'ccx': QuantumGate.TOFFOLI
        }
        
        if gate_name in gate_map:
            # Extrair qubits (simplificado)
            # Assumir formato q[n]
            qubits = []
            for part in parts[1:]:
                if 'q[' in part:
                    q = int(part.split('[')[1].split(']')[0])
                    qubits.append(q)
            
            if qubits:
                self.add_gate(gate_map[gate_name], qubits)
        elif gate_name.startswith('r'):
            # Rotações
            # rx(angle) q[n];
            if '(' in line:
                angle = float(line.split('(')[1].split(')')[0])
                qubit = int(line.split('q[')[1].split(']')[0])
                
                if gate_name == 'rx':
                    self.add_rotation_x(qubit, angle)
                elif gate_name == 'ry':
                    self.add_rotation_y(qubit, angle)
                elif gate_name == 'rz':
                    self.add_rotation_z(qubit, angle)
        elif gate_name == 'measure':
            # measure q[n] -> c[m];
            parts = line.split('->')
            qubit = int(parts[0].split('[')[1].split(']')[0])
            cbit = int(parts[1].split('[')[1].split(']')[0])
            self.add_measurement(qubit, cbit) 