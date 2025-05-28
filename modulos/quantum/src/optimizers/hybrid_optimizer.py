"""
Hybrid Optimizer - Sistema AutoCura
Fase GAMMA: Otimização Híbrida Clássico-Quântica

Implementa algoritmos de otimização que combinam processamento
clássico e quântico, incluindo VQE (Variational Quantum Eigensolver)
e QAOA (Quantum Approximate Optimization Algorithm).
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np
from dataclasses import dataclass
from enum import Enum
import logging
from scipy.optimize import minimize
import time

from ..interfaces.circuit_interface import QuantumCircuitInterface, QuantumBackend, QuantumCircuitFactory

logger = logging.getLogger(__name__)


class OptimizationAlgorithm(Enum):
    """Algoritmos de otimização disponíveis"""
    VQE = "variational_quantum_eigensolver"
    QAOA = "quantum_approximate_optimization_algorithm"
    QITE = "quantum_imaginary_time_evolution"
    VQA = "variational_quantum_algorithm"
    ADAPT_VQE = "adaptive_vqe"


class ClassicalOptimizer(Enum):
    """Otimizadores clássicos para parte variacional"""
    COBYLA = "cobyla"
    NELDER_MEAD = "nelder_mead"
    POWELL = "powell"
    BFGS = "bfgs"
    L_BFGS_B = "l_bfgs_b"
    SLSQP = "slsqp"
    ADAM = "adam"
    SPSA = "spsa"  # Simultaneous Perturbation Stochastic Approximation


@dataclass
class OptimizationResult:
    """Resultado da otimização híbrida"""
    optimal_value: float
    optimal_parameters: np.ndarray
    num_iterations: int
    num_function_evaluations: int
    convergence_history: List[float]
    quantum_circuit_evaluations: int
    classical_optimization_time: float
    quantum_execution_time: float
    total_time: float
    algorithm: OptimizationAlgorithm
    success: bool
    message: str
    additional_info: Dict[str, Any]


class HybridOptimizer:
    """
    Otimizador híbrido que combina processamento clássico e quântico.
    Implementa VQE, QAOA e outros algoritmos variacionais.
    """
    
    def __init__(self, 
                 backend: QuantumBackend = QuantumBackend.SIMULATOR,
                 classical_optimizer: ClassicalOptimizer = ClassicalOptimizer.COBYLA,
                 shots: int = 1024):
        """
        Inicializa o otimizador híbrido.
        
        Args:
            backend: Backend quântico a usar
            classical_optimizer: Otimizador clássico para parâmetros
            shots: Número de medições por avaliação
        """
        self.backend = backend
        self.classical_optimizer = classical_optimizer
        self.shots = shots
        self.circuit_factory = QuantumCircuitFactory()
        self.convergence_history = []
        self.quantum_evaluations = 0
        self.start_time = None
        self.quantum_time = 0.0
        self.classical_time = 0.0
    
    def vqe(self, 
            hamiltonian: Union[np.ndarray, List[Tuple[float, str]]],
            ansatz: Callable[[List[float]], QuantumCircuitInterface],
            initial_params: Optional[np.ndarray] = None,
            num_qubits: int = None,
            max_iterations: int = 100,
            tolerance: float = 1e-6) -> OptimizationResult:
        """
        Variational Quantum Eigensolver - encontra autovalor mínimo do Hamiltoniano.
        
        Args:
            hamiltonian: Hamiltoniano como matriz ou lista de termos Pauli
            ansatz: Função que cria circuito parametrizado
            initial_params: Parâmetros iniciais (None = aleatórios)
            num_qubits: Número de qubits (inferido se None)
            max_iterations: Máximo de iterações
            tolerance: Tolerância para convergência
            
        Returns:
            Resultado da otimização
        """
        logger.info("Starting VQE optimization")
        self.start_time = time.time()
        self.convergence_history = []
        self.quantum_evaluations = 0
        
        # Inferir número de qubits se necessário
        if num_qubits is None:
            if isinstance(hamiltonian, np.ndarray):
                num_qubits = int(np.log2(hamiltonian.shape[0]))
            else:
                # Extrair de termos Pauli
                num_qubits = max(len(term[1]) for term in hamiltonian)
        
        # Inicializar parâmetros se não fornecidos
        if initial_params is None:
            # Estimar número de parâmetros criando circuito teste
            test_circuit = ansatz([0.0])  # Dummy params
            num_params = self._count_parameters(test_circuit)
            initial_params = np.random.uniform(0, 2*np.pi, num_params)
        
        # Função objetivo para VQE
        def objective_function(params):
            quantum_start = time.time()
            
            # Criar circuito com parâmetros atuais
            circuit = ansatz(params)
            
            # Calcular valor esperado do Hamiltoniano
            if isinstance(hamiltonian, np.ndarray):
                expectation = self._compute_expectation_matrix(circuit, hamiltonian)
            else:
                expectation = self._compute_expectation_pauli(circuit, hamiltonian)
            
            self.quantum_time += time.time() - quantum_start
            self.quantum_evaluations += 1
            self.convergence_history.append(expectation)
            
            if self.quantum_evaluations % 10 == 0:
                logger.info(f"VQE iteration {self.quantum_evaluations}: E = {expectation:.6f}")
            
            return expectation
        
        # Otimização clássica
        classical_start = time.time()
        result = self._optimize_classical(
            objective_function,
            initial_params,
            max_iterations,
            tolerance
        )
        self.classical_time = time.time() - classical_start
        
        total_time = time.time() - self.start_time
        
        return OptimizationResult(
            optimal_value=result.fun,
            optimal_parameters=result.x,
            num_iterations=result.nit if hasattr(result, 'nit') else len(self.convergence_history),
            num_function_evaluations=result.nfev if hasattr(result, 'nfev') else self.quantum_evaluations,
            convergence_history=self.convergence_history,
            quantum_circuit_evaluations=self.quantum_evaluations,
            classical_optimization_time=self.classical_time,
            quantum_execution_time=self.quantum_time,
            total_time=total_time,
            algorithm=OptimizationAlgorithm.VQE,
            success=result.success if hasattr(result, 'success') else True,
            message=result.message if hasattr(result, 'message') else "Optimization completed",
            additional_info={
                "num_qubits": num_qubits,
                "backend": self.backend.value,
                "classical_optimizer": self.classical_optimizer.value,
                "shots": self.shots
            }
        )
    
    def qaoa(self,
             cost_hamiltonian: Union[np.ndarray, List[Tuple[float, str]]],
             mixer_hamiltonian: Optional[Union[np.ndarray, List[Tuple[float, str]]]] = None,
             p: int = 1,
             initial_params: Optional[np.ndarray] = None,
             num_qubits: int = None,
             max_iterations: int = 100,
             tolerance: float = 1e-6) -> OptimizationResult:
        """
        Quantum Approximate Optimization Algorithm.
        
        Args:
            cost_hamiltonian: Hamiltoniano do problema
            mixer_hamiltonian: Hamiltoniano de mistura (None = X em todos qubits)
            p: Número de camadas QAOA
            initial_params: Parâmetros iniciais [gamma1, beta1, gamma2, beta2, ...]
            num_qubits: Número de qubits
            max_iterations: Máximo de iterações
            tolerance: Tolerância para convergência
            
        Returns:
            Resultado da otimização
        """
        logger.info(f"Starting QAOA optimization with p={p}")
        self.start_time = time.time()
        self.convergence_history = []
        self.quantum_evaluations = 0
        
        # Inferir número de qubits
        if num_qubits is None:
            if isinstance(cost_hamiltonian, np.ndarray):
                num_qubits = int(np.log2(cost_hamiltonian.shape[0]))
            else:
                num_qubits = max(len(term[1]) for term in cost_hamiltonian)
        
        # Mixer padrão se não fornecido
        if mixer_hamiltonian is None:
            mixer_hamiltonian = self._default_mixer_hamiltonian(num_qubits)
        
        # Inicializar parâmetros (2p parâmetros: p gammas e p betas)
        if initial_params is None:
            initial_params = np.random.uniform(0, 2*np.pi, 2*p)
        
        # Criar ansatz QAOA
        def qaoa_ansatz(params):
            circuit = self.circuit_factory.create_circuit(self.backend)
            circuit.create_circuit(num_qubits)
            
            # Estado inicial: superposição uniforme
            for i in range(num_qubits):
                circuit.add_hadamard(i)
            
            # Aplicar p camadas QAOA
            for layer in range(p):
                gamma = params[2*layer]
                beta = params[2*layer + 1]
                
                # Aplicar evolução do cost Hamiltonian
                self._apply_hamiltonian_evolution(circuit, cost_hamiltonian, gamma)
                
                # Aplicar evolução do mixer Hamiltonian
                self._apply_hamiltonian_evolution(circuit, mixer_hamiltonian, beta)
            
            return circuit
        
        # Usar VQE com ansatz QAOA
        return self.vqe(
            cost_hamiltonian,
            qaoa_ansatz,
            initial_params,
            num_qubits,
            max_iterations,
            tolerance
        )
    
    def optimize_variational(self,
                           cost_function: Callable[[np.ndarray], float],
                           ansatz: Callable[[List[float]], QuantumCircuitInterface],
                           initial_params: np.ndarray,
                           bounds: Optional[List[Tuple[float, float]]] = None,
                           constraints: Optional[List[Dict]] = None,
                           max_iterations: int = 100,
                           tolerance: float = 1e-6) -> OptimizationResult:
        """
        Otimização variacional genérica.
        
        Args:
            cost_function: Função custo a minimizar
            ansatz: Circuito parametrizado
            initial_params: Parâmetros iniciais
            bounds: Limites dos parâmetros
            constraints: Restrições da otimização
            max_iterations: Máximo de iterações
            tolerance: Tolerância
            
        Returns:
            Resultado da otimização
        """
        logger.info("Starting generic variational optimization")
        self.start_time = time.time()
        self.convergence_history = []
        self.quantum_evaluations = 0
        
        def objective_wrapper(params):
            quantum_start = time.time()
            circuit = ansatz(params)
            cost = cost_function(circuit)
            self.quantum_time += time.time() - quantum_start
            self.quantum_evaluations += 1
            self.convergence_history.append(cost)
            return cost
        
        # Otimização clássica
        classical_start = time.time()
        result = self._optimize_classical(
            objective_wrapper,
            initial_params,
            max_iterations,
            tolerance,
            bounds,
            constraints
        )
        self.classical_time = time.time() - classical_start
        
        total_time = time.time() - self.start_time
        
        return OptimizationResult(
            optimal_value=result.fun,
            optimal_parameters=result.x,
            num_iterations=result.nit if hasattr(result, 'nit') else len(self.convergence_history),
            num_function_evaluations=result.nfev if hasattr(result, 'nfev') else self.quantum_evaluations,
            convergence_history=self.convergence_history,
            quantum_circuit_evaluations=self.quantum_evaluations,
            classical_optimization_time=self.classical_time,
            quantum_execution_time=self.quantum_time,
            total_time=total_time,
            algorithm=OptimizationAlgorithm.VQA,
            success=result.success if hasattr(result, 'success') else True,
            message=result.message if hasattr(result, 'message') else "Optimization completed",
            additional_info={
                "backend": self.backend.value,
                "classical_optimizer": self.classical_optimizer.value,
                "shots": self.shots
            }
        )
    
    def _optimize_classical(self, 
                          objective: Callable,
                          initial_params: np.ndarray,
                          max_iterations: int,
                          tolerance: float,
                          bounds: Optional[List[Tuple[float, float]]] = None,
                          constraints: Optional[List[Dict]] = None):
        """Executa otimização clássica dos parâmetros"""
        
        method_map = {
            ClassicalOptimizer.COBYLA: 'COBYLA',
            ClassicalOptimizer.NELDER_MEAD: 'Nelder-Mead',
            ClassicalOptimizer.POWELL: 'Powell',
            ClassicalOptimizer.BFGS: 'BFGS',
            ClassicalOptimizer.L_BFGS_B: 'L-BFGS-B',
            ClassicalOptimizer.SLSQP: 'SLSQP'
        }
        
        if self.classical_optimizer in [ClassicalOptimizer.ADAM, ClassicalOptimizer.SPSA]:
            # Implementação customizada para ADAM e SPSA
            return self._custom_optimizer(
                objective,
                initial_params,
                max_iterations,
                tolerance,
                bounds
            )
        
        # Usar scipy.optimize
        return minimize(
            objective,
            initial_params,
            method=method_map[self.classical_optimizer],
            bounds=bounds,
            constraints=constraints,
            options={
                'maxiter': max_iterations,
                'ftol': tolerance,
                'disp': True
            }
        )
    
    def _custom_optimizer(self,
                         objective: Callable,
                         initial_params: np.ndarray,
                         max_iterations: int,
                         tolerance: float,
                         bounds: Optional[List[Tuple[float, float]]] = None):
        """Implementação de otimizadores customizados (ADAM, SPSA)"""
        
        if self.classical_optimizer == ClassicalOptimizer.SPSA:
            return self._spsa_optimizer(
                objective,
                initial_params,
                max_iterations,
                tolerance,
                bounds
            )
        elif self.classical_optimizer == ClassicalOptimizer.ADAM:
            return self._adam_optimizer(
                objective,
                initial_params,
                max_iterations,
                tolerance,
                bounds
            )
    
    def _spsa_optimizer(self,
                       objective: Callable,
                       initial_params: np.ndarray,
                       max_iterations: int,
                       tolerance: float,
                       bounds: Optional[List[Tuple[float, float]]] = None):
        """Simultaneous Perturbation Stochastic Approximation"""
        
        # Parâmetros SPSA
        a = 0.2
        c = 0.1
        A = max_iterations // 10
        alpha = 0.602
        gamma = 0.101
        
        params = initial_params.copy()
        best_value = float('inf')
        best_params = params.copy()
        
        for k in range(max_iterations):
            # Coeficientes adaptativos
            ak = a / (k + 1 + A) ** alpha
            ck = c / (k + 1) ** gamma
            
            # Perturbação aleatória
            delta = 2 * np.random.randint(0, 2, size=len(params)) - 1
            
            # Avaliações perturbadas
            params_plus = params + ck * delta
            params_minus = params - ck * delta
            
            # Aplicar bounds se fornecidos
            if bounds:
                params_plus = np.clip(params_plus, 
                                    [b[0] for b in bounds],
                                    [b[1] for b in bounds])
                params_minus = np.clip(params_minus,
                                     [b[0] for b in bounds],
                                     [b[1] for b in bounds])
            
            # Gradiente estimado
            y_plus = objective(params_plus)
            y_minus = objective(params_minus)
            gradient = (y_plus - y_minus) / (2 * ck * delta)
            
            # Atualização
            params = params - ak * gradient
            
            # Aplicar bounds
            if bounds:
                params = np.clip(params,
                               [b[0] for b in bounds],
                               [b[1] for b in bounds])
            
            # Verificar melhor valor
            current_value = objective(params)
            if current_value < best_value:
                best_value = current_value
                best_params = params.copy()
            
            # Verificar convergência
            if k > 0 and abs(self.convergence_history[-1] - self.convergence_history[-2]) < tolerance:
                break
        
        # Retornar resultado no formato scipy
        class SPSAResult:
            def __init__(self, x, fun, nit):
                self.x = x
                self.fun = fun
                self.nit = nit
                self.success = True
                self.message = "SPSA optimization completed"
        
        return SPSAResult(best_params, best_value, k + 1)
    
    def _adam_optimizer(self,
                       objective: Callable,
                       initial_params: np.ndarray,
                       max_iterations: int,
                       tolerance: float,
                       bounds: Optional[List[Tuple[float, float]]] = None):
        """Adaptive Moment Estimation (ADAM) optimizer"""
        
        # Hiperparâmetros ADAM
        learning_rate = 0.001
        beta1 = 0.9
        beta2 = 0.999
        epsilon = 1e-8
        
        params = initial_params.copy()
        m = np.zeros_like(params)  # Primeiro momento
        v = np.zeros_like(params)  # Segundo momento
        t = 0
        
        best_value = float('inf')
        best_params = params.copy()
        
        for iteration in range(max_iterations):
            t += 1
            
            # Calcular gradiente numérico
            gradient = self._numerical_gradient(objective, params)
            
            # Atualizar momentos
            m = beta1 * m + (1 - beta1) * gradient
            v = beta2 * v + (1 - beta2) * gradient**2
            
            # Correção de bias
            m_hat = m / (1 - beta1**t)
            v_hat = v / (1 - beta2**t)
            
            # Atualização dos parâmetros
            params = params - learning_rate * m_hat / (np.sqrt(v_hat) + epsilon)
            
            # Aplicar bounds
            if bounds:
                params = np.clip(params,
                               [b[0] for b in bounds],
                               [b[1] for b in bounds])
            
            # Avaliar função objetivo
            current_value = objective(params)
            
            if current_value < best_value:
                best_value = current_value
                best_params = params.copy()
            
            # Verificar convergência
            if iteration > 0 and abs(self.convergence_history[-1] - self.convergence_history[-2]) < tolerance:
                break
        
        # Retornar resultado
        class ADAMResult:
            def __init__(self, x, fun, nit):
                self.x = x
                self.fun = fun
                self.nit = nit
                self.success = True
                self.message = "ADAM optimization completed"
        
        return ADAMResult(best_params, best_value, iteration + 1)
    
    def _numerical_gradient(self, 
                          objective: Callable,
                          params: np.ndarray,
                          epsilon: float = 1e-5) -> np.ndarray:
        """Calcula gradiente numérico"""
        gradient = np.zeros_like(params)
        
        for i in range(len(params)):
            params_plus = params.copy()
            params_minus = params.copy()
            
            params_plus[i] += epsilon
            params_minus[i] -= epsilon
            
            gradient[i] = (objective(params_plus) - objective(params_minus)) / (2 * epsilon)
        
        return gradient
    
    def _compute_expectation_matrix(self,
                                  circuit: QuantumCircuitInterface,
                                  hamiltonian: np.ndarray) -> float:
        """Calcula valor esperado para Hamiltoniano matricial"""
        # Obter vetor de estado
        statevector = circuit.get_statevector()
        
        # Calcular <ψ|H|ψ>
        expectation = np.real(np.conj(statevector) @ hamiltonian @ statevector)
        
        return float(expectation)
    
    def _compute_expectation_pauli(self,
                                 circuit: QuantumCircuitInterface,
                                 pauli_terms: List[Tuple[float, str]]) -> float:
        """Calcula valor esperado para Hamiltoniano em termos de Pauli"""
        total_expectation = 0.0
        
        for coefficient, pauli_string in pauli_terms:
            # Criar cópia do circuito para medição
            measurement_circuit = self._copy_circuit(circuit)
            
            # Aplicar rotações para medir no basis correto
            for i, pauli in enumerate(pauli_string):
                if pauli == 'X':
                    measurement_circuit.add_rotation_y(i, -np.pi/2)
                elif pauli == 'Y':
                    measurement_circuit.add_rotation_x(i, np.pi/2)
                # Z não precisa rotação
            
            # Medir
            measurement_circuit.measure_all()
            
            # Executar e obter contagens
            results = measurement_circuit.execute(shots=self.shots)
            counts = results.get('counts', {})
            
            # Calcular valor esperado do termo Pauli
            pauli_expectation = 0.0
            total_counts = sum(counts.values())
            
            for bitstring, count in counts.items():
                # Calcular paridade
                parity = 1
                for i, pauli in enumerate(pauli_string):
                    if pauli != 'I' and bitstring[i] == '1':
                        parity *= -1
                
                pauli_expectation += parity * count / total_counts
            
            total_expectation += coefficient * pauli_expectation
        
        return total_expectation
    
    def _apply_hamiltonian_evolution(self,
                                   circuit: QuantumCircuitInterface,
                                   hamiltonian: Union[np.ndarray, List[Tuple[float, str]]],
                                   time: float) -> None:
        """Aplica evolução temporal exp(-iHt) ao circuito"""
        
        if isinstance(hamiltonian, list):
            # Hamiltoniano em termos de Pauli
            for coefficient, pauli_string in hamiltonian:
                angle = 2 * coefficient * time  # Factor 2 from Pauli matrices
                
                # Aplicar evolução do termo Pauli
                if pauli_string.count('I') == len(pauli_string) - 1:
                    # Termo com apenas um Pauli não-identidade
                    for i, pauli in enumerate(pauli_string):
                        if pauli == 'X':
                            circuit.add_rotation_x(i, angle)
                        elif pauli == 'Y':
                            circuit.add_rotation_y(i, angle)
                        elif pauli == 'Z':
                            circuit.add_rotation_z(i, angle)
                else:
                    # Termo com múltiplos Paulis - usar decomposição
                    self._apply_pauli_evolution(circuit, pauli_string, angle)
        else:
            # Hamiltoniano matricial - usar decomposição
            logger.warning("Matrix Hamiltonian evolution not fully implemented")
    
    def _apply_pauli_evolution(self,
                             circuit: QuantumCircuitInterface,
                             pauli_string: str,
                             angle: float) -> None:
        """Aplica evolução de string de Pauli multi-qubit"""
        # Encontrar qubits não-identidade
        active_qubits = [(i, p) for i, p in enumerate(pauli_string) if p != 'I']
        
        if len(active_qubits) == 0:
            return  # Evolução global phase
        
        # Transformar para base Z
        for i, pauli in active_qubits:
            if pauli == 'X':
                circuit.add_hadamard(i)
            elif pauli == 'Y':
                circuit.add_rotation_x(i, np.pi/2)
        
        # Aplicar CNOTs para criar paridade
        for i in range(len(active_qubits) - 1):
            circuit.add_cnot(active_qubits[i][0], active_qubits[-1][0])
        
        # Aplicar rotação Z
        circuit.add_rotation_z(active_qubits[-1][0], angle)
        
        # Desfazer CNOTs
        for i in range(len(active_qubits) - 2, -1, -1):
            circuit.add_cnot(active_qubits[i][0], active_qubits[-1][0])
        
        # Voltar da base Z
        for i, pauli in active_qubits:
            if pauli == 'X':
                circuit.add_hadamard(i)
            elif pauli == 'Y':
                circuit.add_rotation_x(i, -np.pi/2)
    
    def _default_mixer_hamiltonian(self, num_qubits: int) -> List[Tuple[float, str]]:
        """Cria mixer Hamiltoniano padrão (soma de X)"""
        terms = []
        for i in range(num_qubits):
            pauli_string = 'I' * i + 'X' + 'I' * (num_qubits - i - 1)
            terms.append((1.0, pauli_string))
        return terms
    
    def _count_parameters(self, circuit: QuantumCircuitInterface) -> int:
        """Conta número de parâmetros no circuito"""
        # Implementação simplificada - contar rotações
        gate_counts = circuit.get_gate_count()
        param_gates = ['rotation_x', 'rotation_y', 'rotation_z']
        return sum(gate_counts.get(gate, 0) for gate in param_gates)
    
    def _copy_circuit(self, circuit: QuantumCircuitInterface) -> QuantumCircuitInterface:
        """Cria cópia do circuito"""
        # Salvar em QASM e recarregar
        qasm = circuit.to_qasm()
        new_circuit = self.circuit_factory.create_circuit(self.backend)
        new_circuit.from_qasm(qasm)
        return new_circuit 