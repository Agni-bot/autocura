"""
Evolution Sandbox - Fase Beta
============================

Ambiente seguro para testar evoluções do sistema AutoCura
de forma isolada antes da implementação em produção.
"""

import asyncio
import docker
import tempfile
import shutil
import json
import logging
import subprocess
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid
import psutil

logger = logging.getLogger(__name__)

class SandboxType(Enum):
    """Tipos de sandbox disponíveis"""
    DOCKER = "docker"
    VIRTUAL_ENV = "virtual_env"
    PROCESS = "process"
    MEMORY = "memory"

class TestStatus(Enum):
    """Status dos testes"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"

class IsolationLevel(Enum):
    """Níveis de isolamento"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"

@dataclass
class SandboxConfig:
    """Configuração do sandbox"""
    sandbox_id: str
    sandbox_type: SandboxType
    isolation_level: IsolationLevel
    resource_limits: Dict[str, Any]
    timeout: int
    allowed_operations: List[str]
    blocked_operations: List[str]
    network_access: bool
    file_system_access: bool

@dataclass
class EvolutionTest:
    """Teste de evolução"""
    test_id: str
    sandbox_id: str
    evolution_code: str
    test_cases: List[Dict[str, Any]]
    expected_outcomes: List[Dict[str, Any]]
    status: TestStatus
    results: Dict[str, Any]
    start_time: str
    end_time: Optional[str]
    duration: Optional[float]
    resource_usage: Dict[str, Any]

@dataclass
class SandboxMetrics:
    """Métricas do sandbox"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    file_operations: int
    process_count: int
    uptime: float

class EvolutionSandbox:
    """
    Sandbox de Evolução
    
    Ambiente isolado e seguro para testar evoluções do sistema
    antes de aplicá-las em produção.
    """
    
    def __init__(self):
        """Inicializa o sandbox de evolução"""
        self.active_sandboxes = {}
        self.completed_tests = {}
        self.sandbox_configs = {}
        
        # Configurações padrão
        self.default_configs = {
            SandboxType.DOCKER: {
                "image": "python:3.11-slim",
                "memory_limit": "512m",
                "cpu_limit": "0.5",
                "network": "none",
                "read_only": True
            },
            SandboxType.VIRTUAL_ENV: {
                "python_version": "3.11",
                "isolated_packages": True,
                "temp_directory": True
            },
            SandboxType.PROCESS: {
                "memory_limit": 256 * 1024 * 1024,  # 256MB
                "cpu_limit": 50,  # 50% CPU
                "timeout": 300    # 5 minutos
            },
            SandboxType.MEMORY: {
                "memory_limit": 128 * 1024 * 1024,  # 128MB
                "execution_timeout": 60  # 1 minuto
            }
        }
        
        # Limites de segurança
        self.security_limits = {
            "max_sandboxes": 10,
            "max_test_duration": 3600,  # 1 hora
            "max_memory_per_sandbox": 1024 * 1024 * 1024,  # 1GB
            "max_cpu_per_sandbox": 1.0,  # 100% de 1 core
            "max_file_operations": 1000,
            "max_network_requests": 100
        }
        
        # Operações bloqueadas por segurança
        self.blocked_operations = [
            "os.system",
            "subprocess.run",
            "eval",
            "exec",
            "compile",
            "__import__",
            "open.*w",  # Escrita em arquivos
            "socket.socket",
            "urllib.request",
            "requests.get",
            "docker.*",
            "kubernetes.*"
        ]
        
        # Inicializar Docker client se disponível
        try:
            self.docker_client = docker.from_env()
            self.docker_available = True
        except Exception as e:
            logger.warning(f"Docker não disponível: {e}")
            self.docker_client = None
            self.docker_available = False
        
        logger.info("EvolutionSandbox inicializado")
    
    async def create_sandbox(
        self, 
        sandbox_type: SandboxType = SandboxType.PROCESS,
        isolation_level: IsolationLevel = IsolationLevel.HIGH,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Cria um novo sandbox
        
        Args:
            sandbox_type: Tipo de sandbox
            isolation_level: Nível de isolamento
            custom_config: Configuração customizada
            
        Returns:
            str: ID do sandbox criado
        """
        if len(self.active_sandboxes) >= self.security_limits["max_sandboxes"]:
            raise RuntimeError("Limite máximo de sandboxes atingido")
        
        sandbox_id = f"sandbox_{uuid.uuid4().hex[:8]}"
        
        # Configurar sandbox
        config = await self._create_sandbox_config(
            sandbox_id, sandbox_type, isolation_level, custom_config
        )
        
        # Inicializar sandbox baseado no tipo
        if sandbox_type == SandboxType.DOCKER:
            await self._create_docker_sandbox(config)
        elif sandbox_type == SandboxType.VIRTUAL_ENV:
            await self._create_venv_sandbox(config)
        elif sandbox_type == SandboxType.PROCESS:
            await self._create_process_sandbox(config)
        elif sandbox_type == SandboxType.MEMORY:
            await self._create_memory_sandbox(config)
        
        self.sandbox_configs[sandbox_id] = config
        self.active_sandboxes[sandbox_id] = {
            "config": config,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "tests_run": 0,
            "metrics": SandboxMetrics(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={"bytes_sent": 0, "bytes_recv": 0},
                file_operations=0,
                process_count=0,
                uptime=0.0
            )
        }
        
        logger.info(f"Sandbox criado: {sandbox_id} ({sandbox_type.value})")
        
        return sandbox_id
    
    async def test_evolution(
        self, 
        sandbox_id: str, 
        evolution_code: str,
        test_cases: List[Dict[str, Any]],
        expected_outcomes: List[Dict[str, Any]]
    ) -> EvolutionTest:
        """
        Testa uma evolução no sandbox
        
        Args:
            sandbox_id: ID do sandbox
            evolution_code: Código da evolução
            test_cases: Casos de teste
            expected_outcomes: Resultados esperados
            
        Returns:
            EvolutionTest: Resultado do teste
        """
        if sandbox_id not in self.active_sandboxes:
            raise ValueError(f"Sandbox não encontrado: {sandbox_id}")
        
        test_id = f"test_{uuid.uuid4().hex[:8]}"
        
        test = EvolutionTest(
            test_id=test_id,
            sandbox_id=sandbox_id,
            evolution_code=evolution_code,
            test_cases=test_cases,
            expected_outcomes=expected_outcomes,
            status=TestStatus.PENDING,
            results={},
            start_time=datetime.now().isoformat(),
            end_time=None,
            duration=None,
            resource_usage={}
        )
        
        try:
            logger.info(f"Iniciando teste {test_id} no sandbox {sandbox_id}")
            
            test.status = TestStatus.RUNNING
            start_time = datetime.now()
            
            # Validar código antes da execução
            if not await self._validate_evolution_code(evolution_code):
                test.status = TestStatus.FAILED
                test.results = {"error": "Código não passou na validação de segurança"}
                return test
            
            # Executar teste baseado no tipo de sandbox
            config = self.sandbox_configs[sandbox_id]
            
            if config.sandbox_type == SandboxType.DOCKER:
                results = await self._test_in_docker(sandbox_id, evolution_code, test_cases)
            elif config.sandbox_type == SandboxType.VIRTUAL_ENV:
                results = await self._test_in_venv(sandbox_id, evolution_code, test_cases)
            elif config.sandbox_type == SandboxType.PROCESS:
                results = await self._test_in_process(sandbox_id, evolution_code, test_cases)
            elif config.sandbox_type == SandboxType.MEMORY:
                results = await self._test_in_memory(sandbox_id, evolution_code, test_cases)
            else:
                raise ValueError(f"Tipo de sandbox não suportado: {config.sandbox_type}")
            
            # Avaliar resultados
            test.results = results
            test.status = await self._evaluate_test_results(results, expected_outcomes)
            
            # Calcular duração
            end_time = datetime.now()
            test.end_time = end_time.isoformat()
            test.duration = (end_time - start_time).total_seconds()
            
            # Coletar métricas de recursos
            test.resource_usage = await self._collect_resource_metrics(sandbox_id)
            
            # Atualizar estatísticas do sandbox
            self.active_sandboxes[sandbox_id]["tests_run"] += 1
            
            logger.info(f"Teste {test_id} concluído: {test.status.value}")
            
        except asyncio.TimeoutError:
            test.status = TestStatus.TIMEOUT
            test.results = {"error": "Teste excedeu tempo limite"}
            logger.warning(f"Teste {test_id} excedeu tempo limite")
            
        except Exception as e:
            test.status = TestStatus.ERROR
            test.results = {"error": str(e)}
            logger.error(f"Erro no teste {test_id}: {e}")
        
        finally:
            test.end_time = test.end_time or datetime.now().isoformat()
            self.completed_tests[test_id] = test
        
        return test
    
    async def _create_sandbox_config(
        self,
        sandbox_id: str,
        sandbox_type: SandboxType,
        isolation_level: IsolationLevel,
        custom_config: Optional[Dict[str, Any]]
    ) -> SandboxConfig:
        """
        Cria configuração do sandbox
        
        Args:
            sandbox_id: ID do sandbox
            sandbox_type: Tipo de sandbox
            isolation_level: Nível de isolamento
            custom_config: Configuração customizada
            
        Returns:
            SandboxConfig: Configuração criada
        """
        # Configuração base
        base_config = self.default_configs[sandbox_type].copy()
        
        # Aplicar configuração customizada
        if custom_config:
            base_config.update(custom_config)
        
        # Ajustar limites baseado no nível de isolamento
        resource_limits = self._get_resource_limits(isolation_level)
        
        # Definir operações permitidas/bloqueadas
        allowed_ops, blocked_ops = self._get_operation_permissions(isolation_level)
        
        return SandboxConfig(
            sandbox_id=sandbox_id,
            sandbox_type=sandbox_type,
            isolation_level=isolation_level,
            resource_limits=resource_limits,
            timeout=base_config.get("timeout", 300),
            allowed_operations=allowed_ops,
            blocked_operations=blocked_ops,
            network_access=isolation_level in [IsolationLevel.LOW, IsolationLevel.MEDIUM],
            file_system_access=isolation_level == IsolationLevel.LOW
        )
    
    def _get_resource_limits(self, isolation_level: IsolationLevel) -> Dict[str, Any]:
        """
        Obtém limites de recursos baseado no nível de isolamento
        
        Args:
            isolation_level: Nível de isolamento
            
        Returns:
            Dict: Limites de recursos
        """
        limits = {
            IsolationLevel.LOW: {
                "memory": 512 * 1024 * 1024,  # 512MB
                "cpu": 0.8,
                "disk": 1024 * 1024 * 1024,  # 1GB
                "processes": 10,
                "file_operations": 500
            },
            IsolationLevel.MEDIUM: {
                "memory": 256 * 1024 * 1024,  # 256MB
                "cpu": 0.5,
                "disk": 512 * 1024 * 1024,   # 512MB
                "processes": 5,
                "file_operations": 200
            },
            IsolationLevel.HIGH: {
                "memory": 128 * 1024 * 1024,  # 128MB
                "cpu": 0.3,
                "disk": 256 * 1024 * 1024,   # 256MB
                "processes": 3,
                "file_operations": 50
            },
            IsolationLevel.MAXIMUM: {
                "memory": 64 * 1024 * 1024,   # 64MB
                "cpu": 0.1,
                "disk": 128 * 1024 * 1024,   # 128MB
                "processes": 1,
                "file_operations": 10
            }
        }
        
        return limits[isolation_level]
    
    def _get_operation_permissions(self, isolation_level: IsolationLevel) -> Tuple[List[str], List[str]]:
        """
        Obtém permissões de operações baseado no nível de isolamento
        
        Args:
            isolation_level: Nível de isolamento
            
        Returns:
            Tuple[List[str], List[str]]: Operações permitidas e bloqueadas
        """
        base_blocked = self.blocked_operations.copy()
        
        if isolation_level == IsolationLevel.LOW:
            allowed = ["file_read", "file_write", "network_request", "subprocess"]
            blocked = base_blocked
        elif isolation_level == IsolationLevel.MEDIUM:
            allowed = ["file_read", "network_request"]
            blocked = base_blocked + ["file_write", "subprocess"]
        elif isolation_level == IsolationLevel.HIGH:
            allowed = ["file_read"]
            blocked = base_blocked + ["file_write", "network_request", "subprocess"]
        else:  # MAXIMUM
            allowed = []
            blocked = base_blocked + ["file_read", "file_write", "network_request", "subprocess"]
        
        return allowed, blocked
    
    async def _create_docker_sandbox(self, config: SandboxConfig) -> None:
        """
        Cria sandbox Docker
        
        Args:
            config: Configuração do sandbox
        """
        if not self.docker_available:
            raise RuntimeError("Docker não está disponível")
        
        # Configurações do container
        container_config = {
            "image": self.default_configs[SandboxType.DOCKER]["image"],
            "mem_limit": config.resource_limits["memory"],
            "cpu_period": 100000,
            "cpu_quota": int(config.resource_limits["cpu"] * 100000),
            "network_mode": "none" if not config.network_access else "bridge",
            "read_only": True,
            "remove": True,
            "detach": True,
            "name": f"sandbox_{config.sandbox_id}"
        }
        
        # Criar container (será usado quando necessário)
        logger.debug(f"Configuração Docker preparada para {config.sandbox_id}")
    
    async def _create_venv_sandbox(self, config: SandboxConfig) -> None:
        """
        Cria sandbox com virtual environment
        
        Args:
            config: Configuração do sandbox
        """
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp(prefix=f"sandbox_{config.sandbox_id}_")
        
        # Criar virtual environment
        venv_path = Path(temp_dir) / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
        logger.debug(f"Virtual environment criado em {venv_path}")
    
    async def _create_process_sandbox(self, config: SandboxConfig) -> None:
        """
        Cria sandbox baseado em processo
        
        Args:
            config: Configuração do sandbox
        """
        # Configuração será aplicada durante a execução
        logger.debug(f"Sandbox de processo configurado: {config.sandbox_id}")
    
    async def _create_memory_sandbox(self, config: SandboxConfig) -> None:
        """
        Cria sandbox em memória
        
        Args:
            config: Configuração do sandbox
        """
        # Sandbox em memória - execução direta com limitações
        logger.debug(f"Sandbox em memória configurado: {config.sandbox_id}")
    
    async def _validate_evolution_code(self, code: str) -> bool:
        """
        Valida código de evolução antes da execução
        
        Args:
            code: Código a validar
            
        Returns:
            bool: True se válido
        """
        try:
            # Verificar sintaxe
            compile(code, '<evolution>', 'exec')
            
            # Verificar operações bloqueadas
            for blocked_op in self.blocked_operations:
                if blocked_op in code:
                    logger.warning(f"Operação bloqueada encontrada: {blocked_op}")
                    return False
            
            # Verificar tamanho do código
            if len(code) > 50000:  # 50KB máximo
                logger.warning("Código muito grande")
                return False
            
            return True
            
        except SyntaxError as e:
            logger.warning(f"Erro de sintaxe no código: {e}")
            return False
    
    async def _test_in_docker(
        self, 
        sandbox_id: str, 
        evolution_code: str, 
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executa teste em container Docker
        
        Args:
            sandbox_id: ID do sandbox
            evolution_code: Código a testar
            test_cases: Casos de teste
            
        Returns:
            Dict: Resultados do teste
        """
        if not self.docker_available:
            raise RuntimeError("Docker não disponível")
        
        config = self.sandbox_configs[sandbox_id]
        
        # Criar script de teste
        test_script = self._create_test_script(evolution_code, test_cases)
        
        # Executar container
        try:
            container = self.docker_client.containers.run(
                image=self.default_configs[SandboxType.DOCKER]["image"],
                command=["python", "-c", test_script],
                mem_limit=config.resource_limits["memory"],
                cpu_period=100000,
                cpu_quota=int(config.resource_limits["cpu"] * 100000),
                network_mode="none",
                remove=True,
                timeout=config.timeout
            )
            
            output = container.decode('utf-8')
            return {"success": True, "output": output, "container_logs": output}
            
        except docker.errors.ContainerError as e:
            return {"success": False, "error": str(e), "exit_code": e.exit_status}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_in_venv(
        self, 
        sandbox_id: str, 
        evolution_code: str, 
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executa teste em virtual environment
        
        Args:
            sandbox_id: ID do sandbox
            evolution_code: Código a testar
            test_cases: Casos de teste
            
        Returns:
            Dict: Resultados do teste
        """
        config = self.sandbox_configs[sandbox_id]
        
        # Criar script de teste
        test_script = self._create_test_script(evolution_code, test_cases)
        
        try:
            # Executar em processo separado com timeout
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-c", test_script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=config.timeout
            )
            
            return {
                "success": process.returncode == 0,
                "output": stdout.decode('utf-8'),
                "error": stderr.decode('utf-8'),
                "return_code": process.returncode
            }
            
        except asyncio.TimeoutError:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_in_process(
        self, 
        sandbox_id: str, 
        evolution_code: str, 
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executa teste em processo isolado
        
        Args:
            sandbox_id: ID do sandbox
            evolution_code: Código a testar
            test_cases: Casos de teste
            
        Returns:
            Dict: Resultados do teste
        """
        config = self.sandbox_configs[sandbox_id]
        
        try:
            # Executar com limitações de recursos
            results = []
            
            for test_case in test_cases:
                result = await self._execute_with_limits(
                    evolution_code, 
                    test_case, 
                    config.resource_limits
                )
                results.append(result)
            
            return {"success": True, "results": results}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_in_memory(
        self, 
        sandbox_id: str, 
        evolution_code: str, 
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executa teste em memória
        
        Args:
            sandbox_id: ID do sandbox
            evolution_code: Código a testar
            test_cases: Casos de teste
            
        Returns:
            Dict: Resultados do teste
        """
        config = self.sandbox_configs[sandbox_id]
        
        try:
            # Compilar código
            compiled_code = compile(evolution_code, '<evolution>', 'exec')
            
            # Executar em namespace isolado
            results = []
            
            for test_case in test_cases:
                namespace = {
                    '__builtins__': {},  # Namespace restrito
                    'test_input': test_case.get('input'),
                    'results': []
                }
                
                # Executar com timeout
                try:
                    exec(compiled_code, namespace)
                    results.append({
                        "success": True,
                        "output": namespace.get('results', []),
                        "test_case": test_case
                    })
                except Exception as e:
                    results.append({
                        "success": False,
                        "error": str(e),
                        "test_case": test_case
                    })
            
            return {"success": True, "results": results}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_test_script(self, evolution_code: str, test_cases: List[Dict[str, Any]]) -> str:
        """
        Cria script de teste
        
        Args:
            evolution_code: Código da evolução
            test_cases: Casos de teste
            
        Returns:
            str: Script de teste
        """
        script = f"""
import json
import sys

# Código da evolução
{evolution_code}

# Casos de teste
test_cases = {json.dumps(test_cases)}

results = []

for i, test_case in enumerate(test_cases):
    try:
        # Executar teste
        test_input = test_case.get('input', {{}})
        
        # Aqui seria executada a lógica específica do teste
        # Por simplicidade, assumimos que o código define uma função 'test_function'
        if 'test_function' in globals():
            result = test_function(test_input)
            results.append({{"test_case": i, "success": True, "result": result}})
        else:
            results.append({{"test_case": i, "success": False, "error": "test_function não encontrada"}})
            
    except Exception as e:
        results.append({{"test_case": i, "success": False, "error": str(e)}})

print(json.dumps(results))
"""
        return script
    
    async def _execute_with_limits(
        self, 
        code: str, 
        test_case: Dict[str, Any], 
        limits: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executa código com limitações de recursos
        
        Args:
            code: Código a executar
            test_case: Caso de teste
            limits: Limites de recursos
            
        Returns:
            Dict: Resultado da execução
        """
        try:
            # Implementação simplificada - em produção usaria cgroups ou similar
            compiled_code = compile(code, '<evolution>', 'exec')
            
            namespace = {
                '__builtins__': {},
                'test_input': test_case.get('input'),
                'result': None
            }
            
            exec(compiled_code, namespace)
            
            return {
                "success": True,
                "result": namespace.get('result'),
                "test_case": test_case
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test_case": test_case
            }
    
    async def _evaluate_test_results(
        self, 
        results: Dict[str, Any], 
        expected_outcomes: List[Dict[str, Any]]
    ) -> TestStatus:
        """
        Avalia resultados dos testes
        
        Args:
            results: Resultados obtidos
            expected_outcomes: Resultados esperados
            
        Returns:
            TestStatus: Status do teste
        """
        if not results.get("success", False):
            return TestStatus.FAILED
        
        # Comparar com resultados esperados
        test_results = results.get("results", [])
        
        if len(test_results) != len(expected_outcomes):
            return TestStatus.FAILED
        
        for i, (result, expected) in enumerate(zip(test_results, expected_outcomes)):
            if not result.get("success", False):
                return TestStatus.FAILED
            
            # Comparação simplificada - em produção seria mais sofisticada
            if result.get("result") != expected.get("expected_result"):
                return TestStatus.FAILED
        
        return TestStatus.PASSED
    
    async def _collect_resource_metrics(self, sandbox_id: str) -> Dict[str, Any]:
        """
        Coleta métricas de recursos do sandbox
        
        Args:
            sandbox_id: ID do sandbox
            
        Returns:
            Dict: Métricas coletadas
        """
        try:
            # Coletar métricas do sistema
            process = psutil.Process()
            
            return {
                "cpu_percent": process.cpu_percent(),
                "memory_info": process.memory_info()._asdict(),
                "io_counters": process.io_counters()._asdict() if hasattr(process, 'io_counters') else {},
                "num_threads": process.num_threads(),
                "create_time": process.create_time()
            }
            
        except Exception as e:
            logger.warning(f"Erro ao coletar métricas: {e}")
            return {}
    
    async def destroy_sandbox(self, sandbox_id: str) -> bool:
        """
        Destrói um sandbox
        
        Args:
            sandbox_id: ID do sandbox
            
        Returns:
            bool: True se destruído com sucesso
        """
        try:
            if sandbox_id not in self.active_sandboxes:
                return False
            
            config = self.sandbox_configs[sandbox_id]
            
            # Limpar recursos baseado no tipo
            if config.sandbox_type == SandboxType.DOCKER:
                await self._cleanup_docker_sandbox(sandbox_id)
            elif config.sandbox_type == SandboxType.VIRTUAL_ENV:
                await self._cleanup_venv_sandbox(sandbox_id)
            
            # Remover das estruturas de dados
            del self.active_sandboxes[sandbox_id]
            del self.sandbox_configs[sandbox_id]
            
            logger.info(f"Sandbox destruído: {sandbox_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao destruir sandbox {sandbox_id}: {e}")
            return False
    
    async def _cleanup_docker_sandbox(self, sandbox_id: str) -> None:
        """
        Limpa recursos do sandbox Docker
        
        Args:
            sandbox_id: ID do sandbox
        """
        if self.docker_available:
            try:
                container_name = f"sandbox_{sandbox_id}"
                containers = self.docker_client.containers.list(
                    all=True, 
                    filters={"name": container_name}
                )
                
                for container in containers:
                    container.remove(force=True)
                    
            except Exception as e:
                logger.warning(f"Erro ao limpar container Docker: {e}")
    
    async def _cleanup_venv_sandbox(self, sandbox_id: str) -> None:
        """
        Limpa recursos do sandbox virtual environment
        
        Args:
            sandbox_id: ID do sandbox
        """
        # Remover diretórios temporários
        temp_dirs = [d for d in Path(tempfile.gettempdir()).iterdir() 
                    if d.name.startswith(f"sandbox_{sandbox_id}_")]
        
        for temp_dir in temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Erro ao remover diretório temporário: {e}")
    
    def get_sandbox_status(self) -> Dict[str, Any]:
        """
        Retorna status dos sandboxes
        
        Returns:
            Dict: Status atual
        """
        return {
            "active_sandboxes": len(self.active_sandboxes),
            "completed_tests": len(self.completed_tests),
            "docker_available": self.docker_available,
            "security_limits": self.security_limits,
            "sandboxes": {
                sid: {
                    "type": info["config"].sandbox_type.value,
                    "isolation": info["config"].isolation_level.value,
                    "created_at": info["created_at"],
                    "tests_run": info["tests_run"],
                    "status": info["status"]
                }
                for sid, info in self.active_sandboxes.items()
            },
            "recent_tests": [
                {
                    "test_id": test.test_id,
                    "sandbox_id": test.sandbox_id,
                    "status": test.status.value,
                    "duration": test.duration,
                    "start_time": test.start_time
                }
                for test in list(self.completed_tests.values())[-10:]
            ]
        }
    
    async def cleanup_all_sandboxes(self) -> None:
        """
        Limpa todos os sandboxes ativos
        """
        sandbox_ids = list(self.active_sandboxes.keys())
        
        for sandbox_id in sandbox_ids:
            await self.destroy_sandbox(sandbox_id)
        
        logger.info("Todos os sandboxes foram limpos") 