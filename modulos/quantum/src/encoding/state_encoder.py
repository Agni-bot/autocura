"""
Quantum State Encoder - Sistema AutoCura
Fase GAMMA: Codificação de Estados Quânticos

Implementa diferentes métodos de codificação de dados clássicos
em estados quânticos, incluindo amplitude encoding, basis encoding,
angle encoding e outros métodos avançados.
"""

from typing import List, Union, Tuple, Optional, Dict, Any
import numpy as np
from enum import Enum
import logging
from abc import ABC, abstractmethod

from ..interfaces.circuit_interface import QuantumCircuitInterface, QuantumGate

logger = logging.getLogger(__name__)


class EncodingMethod(Enum):
    """Métodos de codificação disponíveis"""
    AMPLITUDE = "amplitude_encoding"
    BASIS = "basis_encoding"
    ANGLE = "angle_encoding"
    DENSE_ANGLE = "dense_angle_encoding"
    IQP = "instantaneous_quantum_polynomial"
    HAMILTONIAN = "hamiltonian_encoding"
    SQUEEZED = "squeezed_encoding"
    BINARY = "binary_encoding"


class QuantumStateEncoder:
    """
    Codificador de estados quânticos.
    Transforma dados clássicos em estados quânticos usando diferentes métodos.
    """
    
    def __init__(self, method: EncodingMethod = EncodingMethod.AMPLITUDE):
        """
        Inicializa o codificador.
        
        Args:
            method: Método de codificação padrão
        """
        self.method = method
        self.encoding_info = {}
    
    def encode(self, 
               data: Union[np.ndarray, List[float]],
               circuit: QuantumCircuitInterface,
               method: Optional[EncodingMethod] = None,
               normalize: bool = True) -> Dict[str, Any]:
        """
        Codifica dados em estado quântico.
        
        Args:
            data: Dados a codificar
            circuit: Circuito onde adicionar a codificação
            method: Método de codificação (usa padrão se None)
            normalize: Se deve normalizar os dados
            
        Returns:
            Informações sobre a codificação
        """
        method = method or self.method
        data = np.array(data)
        
        if normalize and method in [EncodingMethod.AMPLITUDE, EncodingMethod.ANGLE]:
            data = self._normalize_data(data, method)
        
        logger.info(f"Encoding data using {method.value}")
        
        if method == EncodingMethod.AMPLITUDE:
            return self.encode_amplitude(data, circuit)
        elif method == EncodingMethod.BASIS:
            return self.encode_basis(data, circuit)
        elif method == EncodingMethod.ANGLE:
            return self.encode_angle(data, circuit)
        elif method == EncodingMethod.DENSE_ANGLE:
            return self.encode_dense_angle(data, circuit)
        elif method == EncodingMethod.IQP:
            return self.encode_iqp(data, circuit)
        elif method == EncodingMethod.HAMILTONIAN:
            return self.encode_hamiltonian(data, circuit)
        elif method == EncodingMethod.BINARY:
            return self.encode_binary(data, circuit)
        else:
            raise ValueError(f"Encoding method {method} not implemented")
    
    def encode_amplitude(self, 
                        data: np.ndarray,
                        circuit: QuantumCircuitInterface) -> Dict[str, Any]:
        """
        Amplitude Encoding: codifica dados como amplitudes do estado quântico.
        Requer log2(N) qubits para N dados.
        
        Args:
            data: Vetor de dados (tamanho deve ser potência de 2)
            circuit: Circuito alvo
            
        Returns:
            Informações da codificação
        """
        # Verificar e ajustar tamanho
        n_data = len(data)
        n_qubits = int(np.ceil(np.log2(n_data)))
        n_states = 2**n_qubits
        
        if n_data != n_states:
            # Padding com zeros
            data = np.pad(data, (0, n_states - n_data), mode='constant')
            logger.warning(f"Data padded from {n_data} to {n_states} elements")
        
        # Normalizar para estado quântico válido
        norm = np.linalg.norm(data)
        if norm > 0:
            data = data / norm
        else:
            raise ValueError("Cannot encode zero vector")
        
        # Criar estado inicial |00...0>
        if circuit.num_qubits < n_qubits:
            raise ValueError(f"Circuit needs at least {n_qubits} qubits")
        
        # Implementar codificação usando decomposição
        self._amplitude_encoding_circuit(data, circuit, list(range(n_qubits)))
        
        return {
            "method": "amplitude",
            "num_qubits": n_qubits,
            "original_size": n_data,
            "padded_size": n_states,
            "normalization_factor": norm,
            "compression_ratio": n_data / n_qubits
        }
    
    def encode_basis(self,
                    data: Union[int, List[int], np.ndarray],
                    circuit: QuantumCircuitInterface) -> Dict[str, Any]:
        """
        Basis Encoding: codifica inteiros como estados da base computacional.
        
        Args:
            data: Inteiro ou lista de bits
            circuit: Circuito alvo
            
        Returns:
            Informações da codificação
        """
        if isinstance(data, int):
            # Converter inteiro para binário
            binary_str = format(data, f'0{circuit.num_qubits}b')
            bits = [int(b) for b in binary_str]
        else:
            bits = list(data)
        
        if len(bits) > circuit.num_qubits:
            raise ValueError(f"Need at least {len(bits)} qubits")
        
        # Aplicar X gates onde bit = 1
        for i, bit in enumerate(bits):
            if bit == 1:
                circuit.add_gate(QuantumGate.X, i)
        
        return {
            "method": "basis",
            "num_qubits": len(bits),
            "encoded_value": int(''.join(map(str, bits)), 2),
            "bit_string": ''.join(map(str, bits))
        }
    
    def encode_angle(self,
                    data: np.ndarray,
                    circuit: QuantumCircuitInterface,
                    rotation_axis: str = 'Y') -> Dict[str, Any]:
        """
        Angle Encoding: codifica dados como ângulos de rotação.
        
        Args:
            data: Vetor de dados
            circuit: Circuito alvo
            rotation_axis: Eixo de rotação ('X', 'Y', ou 'Z')
            
        Returns:
            Informações da codificação
        """
        n_features = len(data)
        if n_features > circuit.num_qubits:
            raise ValueError(f"Need at least {n_features} qubits")
        
        # Mapear dados para ângulos [0, 2π]
        angles = 2 * np.pi * data
        
        # Aplicar rotações
        for i, angle in enumerate(angles):
            if rotation_axis == 'X':
                circuit.add_rotation_x(i, angle)
            elif rotation_axis == 'Y':
                circuit.add_rotation_y(i, angle)
            elif rotation_axis == 'Z':
                circuit.add_rotation_z(i, angle)
            else:
                raise ValueError(f"Invalid rotation axis: {rotation_axis}")
        
        return {
            "method": "angle",
            "num_qubits": n_features,
            "rotation_axis": rotation_axis,
            "angles": angles.tolist(),
            "encoding_density": 1.0  # 1 feature per qubit
        }
    
    def encode_dense_angle(self,
                         data: np.ndarray,
                         circuit: QuantumCircuitInterface) -> Dict[str, Any]:
        """
        Dense Angle Encoding: codifica múltiplos dados por qubit usando
        diferentes eixos de rotação.
        
        Args:
            data: Vetor de dados
            circuit: Circuito alvo
            
        Returns:
            Informações da codificação
        """
        n_features = len(data)
        n_qubits = circuit.num_qubits
        features_per_qubit = int(np.ceil(n_features / n_qubits))
        
        if features_per_qubit > 3:
            logger.warning("More than 3 features per qubit, using repeated encoding")
        
        # Pad dados se necessário
        padded_size = n_qubits * features_per_qubit
        if n_features < padded_size:
            data = np.pad(data, (0, padded_size - n_features), mode='constant')
        
        # Reshape para (n_qubits, features_per_qubit)
        data_matrix = data.reshape(n_qubits, features_per_qubit)
        
        # Aplicar rotações
        axes = ['X', 'Y', 'Z']
        for q in range(n_qubits):
            for f in range(min(features_per_qubit, 3)):
                angle = 2 * np.pi * data_matrix[q, f]
                axis = axes[f % 3]
                
                if axis == 'X':
                    circuit.add_rotation_x(q, angle)
                elif axis == 'Y':
                    circuit.add_rotation_y(q, angle)
                elif axis == 'Z':
                    circuit.add_rotation_z(q, angle)
        
        return {
            "method": "dense_angle",
            "num_qubits": n_qubits,
            "num_features": n_features,
            "features_per_qubit": features_per_qubit,
            "encoding_density": n_features / n_qubits
        }
    
    def encode_iqp(self,
                   data: np.ndarray,
                   circuit: QuantumCircuitInterface,
                   depth: int = 2) -> Dict[str, Any]:
        """
        IQP (Instantaneous Quantum Polynomial) Encoding:
        Codifica dados usando portas diagonais e emaranhamento.
        
        Args:
            data: Vetor de dados
            circuit: Circuito alvo
            depth: Profundidade do circuito IQP
            
        Returns:
            Informações da codificação
        """
        n_features = len(data)
        n_qubits = circuit.num_qubits
        
        if n_features > n_qubits:
            data = data[:n_qubits]
            logger.warning(f"Truncated data from {n_features} to {n_qubits} features")
        
        # Inicializar em superposição
        for q in range(n_qubits):
            circuit.add_hadamard(q)
        
        # Aplicar camadas IQP
        for d in range(depth):
            # Rotações Z baseadas nos dados
            for i in range(min(n_features, n_qubits)):
                angle = np.pi * data[i] * (d + 1)
                circuit.add_rotation_z(i, angle)
            
            # Emaranhamento com CZ gates
            for i in range(n_qubits - 1):
                for j in range(i + 1, n_qubits):
                    if i < n_features and j < n_features:
                        # Ângulo baseado no produto dos features
                        angle = np.pi * data[i] * data[j] * (d + 1)
                        circuit.add_gate(QuantumGate.CZ, [i, j])
                        circuit.add_rotation_z(j, angle)
        
        return {
            "method": "iqp",
            "num_qubits": n_qubits,
            "num_features": min(n_features, n_qubits),
            "depth": depth,
            "total_gates": depth * (n_qubits + n_qubits * (n_qubits - 1) // 2)
        }
    
    def encode_hamiltonian(self,
                          data: np.ndarray,
                          circuit: QuantumCircuitInterface,
                          time: float = 1.0) -> Dict[str, Any]:
        """
        Hamiltonian Encoding: codifica dados como parâmetros de um Hamiltoniano
        e aplica evolução temporal.
        
        Args:
            data: Vetor de dados
            circuit: Circuito alvo
            time: Tempo de evolução
            
        Returns:
            Informações da codificação
        """
        n_features = len(data)
        n_qubits = circuit.num_qubits
        
        # Inicializar em superposição
        for q in range(n_qubits):
            circuit.add_hadamard(q)
        
        # Construir Hamiltoniano baseado nos dados
        # H = Σ data[i] * Z_i + Σ data[i]*data[j] * Z_i*Z_j
        
        # Termos de um qubit
        for i in range(min(n_features, n_qubits)):
            angle = 2 * data[i] * time
            circuit.add_rotation_z(i, angle)
        
        # Termos de dois qubits
        for i in range(min(n_features, n_qubits)):
            for j in range(i + 1, min(n_features, n_qubits)):
                # Implementar exp(-i * data[i]*data[j] * Z_i*Z_j * time)
                angle = 2 * data[i] * data[j] * time
                
                circuit.add_cnot(i, j)
                circuit.add_rotation_z(j, angle)
                circuit.add_cnot(i, j)
        
        return {
            "method": "hamiltonian",
            "num_qubits": n_qubits,
            "num_features": min(n_features, n_qubits),
            "evolution_time": time,
            "hamiltonian_terms": min(n_features, n_qubits) + 
                               min(n_features, n_qubits) * (min(n_features, n_qubits) - 1) // 2
        }
    
    def encode_binary(self,
                     data: Union[int, str, bytes],
                     circuit: QuantumCircuitInterface) -> Dict[str, Any]:
        """
        Binary Encoding: codifica dados binários diretamente.
        
        Args:
            data: Dados binários (int, string binária ou bytes)
            circuit: Circuito alvo
            
        Returns:
            Informações da codificação
        """
        # Converter para string binária
        if isinstance(data, int):
            binary_str = bin(data)[2:]  # Remove '0b'
        elif isinstance(data, str):
            # Assumir que é string binária
            binary_str = data.replace(' ', '')
        elif isinstance(data, bytes):
            binary_str = ''.join(format(byte, '08b') for byte in data)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
        
        # Verificar tamanho
        if len(binary_str) > circuit.num_qubits:
            raise ValueError(f"Need at least {len(binary_str)} qubits")
        
        # Aplicar codificação
        for i, bit in enumerate(binary_str):
            if bit == '1':
                circuit.add_gate(QuantumGate.X, i)
        
        return {
            "method": "binary",
            "num_qubits": len(binary_str),
            "binary_string": binary_str,
            "encoded_length": len(binary_str)
        }
    
    def decode_amplitude(self,
                        circuit: QuantumCircuitInterface,
                        shots: int = 8192) -> np.ndarray:
        """
        Decodifica estado quântico para amplitudes clássicas.
        
        Args:
            circuit: Circuito a decodificar
            shots: Número de medições para estimativa
            
        Returns:
            Vetor de amplitudes estimadas
        """
        # Executar tomografia de estado ou usar statevector
        try:
            # Tentar obter statevector diretamente
            statevector = circuit.get_statevector()
            return np.abs(statevector)
        except:
            # Fallback para estimativa por medições
            logger.warning("Using measurement-based amplitude estimation")
            
            # Implementar tomografia simplificada
            n_qubits = circuit.num_qubits
            amplitudes = np.zeros(2**n_qubits)
            
            # Medir em base computacional
            circuit_copy = self._copy_circuit(circuit)
            circuit_copy.measure_all()
            results = circuit_copy.execute(shots=shots)
            
            counts = results.get('counts', {})
            total = sum(counts.values())
            
            for bitstring, count in counts.items():
                index = int(bitstring, 2)
                amplitudes[index] = np.sqrt(count / total)
            
            return amplitudes
    
    def decode_basis(self,
                    circuit: QuantumCircuitInterface,
                    shots: int = 1) -> int:
        """
        Decodifica estado da base computacional.
        
        Args:
            circuit: Circuito a decodificar
            shots: Número de medições
            
        Returns:
            Valor inteiro decodificado
        """
        circuit_copy = self._copy_circuit(circuit)
        circuit_copy.measure_all()
        results = circuit_copy.execute(shots=shots)
        
        counts = results.get('counts', {})
        # Retornar resultado mais frequente
        most_frequent = max(counts, key=counts.get)
        return int(most_frequent, 2)
    
    def _normalize_data(self,
                       data: np.ndarray,
                       method: EncodingMethod) -> np.ndarray:
        """Normaliza dados para codificação"""
        if method == EncodingMethod.AMPLITUDE:
            # Normalizar para norma 1
            norm = np.linalg.norm(data)
            if norm > 0:
                return data / norm
            else:
                raise ValueError("Cannot normalize zero vector")
        elif method == EncodingMethod.ANGLE:
            # Normalizar para [0, 1]
            min_val = np.min(data)
            max_val = np.max(data)
            if max_val > min_val:
                return (data - min_val) / (max_val - min_val)
            else:
                return np.zeros_like(data)
        else:
            return data
    
    def _amplitude_encoding_circuit(self,
                                  amplitudes: np.ndarray,
                                  circuit: QuantumCircuitInterface,
                                  qubits: List[int]) -> None:
        """
        Implementa circuito para amplitude encoding.
        Usa decomposição recursiva.
        """
        n_qubits = len(qubits)
        
        if n_qubits == 1:
            # Caso base: rotação Y para codificar 2 amplitudes
            if abs(amplitudes[0]) > 1e-10:
                theta = 2 * np.arccos(abs(amplitudes[0]))
                circuit.add_rotation_y(qubits[0], theta)
            
            # Adicionar fase se necessário
            if np.angle(amplitudes[1]) != 0:
                circuit.add_rotation_z(qubits[0], np.angle(amplitudes[1]))
        else:
            # Dividir amplitudes em duas metades
            mid = len(amplitudes) // 2
            first_half = amplitudes[:mid]
            second_half = amplitudes[mid:]
            
            # Calcular normas
            norm_first = np.linalg.norm(first_half)
            norm_second = np.linalg.norm(second_half)
            
            # Rotação controlada para distribuir amplitudes
            if norm_first > 1e-10 and norm_second > 1e-10:
                theta = 2 * np.arccos(norm_first / np.sqrt(norm_first**2 + norm_second**2))
                
                # Aplicar rotação Y no qubit mais significativo
                circuit.add_rotation_y(qubits[0], theta)
                
                # Codificar recursivamente
                if norm_first > 1e-10:
                    self._amplitude_encoding_circuit(
                        first_half / norm_first,
                        circuit,
                        qubits[1:]
                    )
                
                # Aplicar X para acessar segunda metade
                circuit.add_gate(QuantumGate.X, qubits[0])
                
                if norm_second > 1e-10:
                    self._amplitude_encoding_circuit(
                        second_half / norm_second,
                        circuit,
                        qubits[1:]
                    )
                
                # Desfazer X
                circuit.add_gate(QuantumGate.X, qubits[0])
    
    def _copy_circuit(self, circuit: QuantumCircuitInterface) -> QuantumCircuitInterface:
        """Cria cópia do circuito"""
        # Implementação simplificada
        from ..interfaces.circuit_interface import QuantumCircuitFactory
        factory = QuantumCircuitFactory()
        new_circuit = factory.create_circuit(circuit.backend)
        
        # Copiar via QASM
        qasm = circuit.to_qasm()
        new_circuit.from_qasm(qasm)
        
        return new_circuit
    
    def get_encoding_efficiency(self,
                              method: EncodingMethod,
                              n_features: int,
                              n_qubits: int) -> Dict[str, float]:
        """
        Calcula métricas de eficiência para método de codificação.
        
        Args:
            method: Método de codificação
            n_features: Número de features
            n_qubits: Número de qubits disponíveis
            
        Returns:
            Métricas de eficiência
        """
        if method == EncodingMethod.AMPLITUDE:
            max_features = 2**n_qubits
            efficiency = min(n_features / max_features, 1.0)
            compression = n_features / n_qubits if n_qubits > 0 else 0
        elif method == EncodingMethod.BASIS:
            max_features = n_qubits
            efficiency = min(n_features / max_features, 1.0)
            compression = 1.0
        elif method == EncodingMethod.ANGLE:
            max_features = n_qubits
            efficiency = min(n_features / max_features, 1.0)
            compression = 1.0
        elif method == EncodingMethod.DENSE_ANGLE:
            max_features = 3 * n_qubits
            efficiency = min(n_features / max_features, 1.0)
            compression = min(n_features / n_qubits, 3.0) if n_qubits > 0 else 0
        else:
            efficiency = 1.0
            compression = n_features / n_qubits if n_qubits > 0 else 0
        
        return {
            "efficiency": efficiency,
            "compression_ratio": compression,
            "max_features": max_features if 'max_features' in locals() else n_features,
            "utilization": min(n_features / n_qubits, 1.0) if n_qubits > 0 else 0
        } 