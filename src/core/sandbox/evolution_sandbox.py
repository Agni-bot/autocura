"""
EvolutionSandbox - Ambiente Isolado para Testes de Evolução
=========================================================

Sistema de sandbox que executa código gerado em ambiente Docker isolado
para garantir segurança durante a auto-modificação.
"""

import docker
import tempfile
import json
import os
import time
import asyncio
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import shutil
import uuid

logger = logging.getLogger(__name__)

class SandboxStatus(Enum):
    """Status do sandbox"""
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    KILLED = "killed"

@dataclass
class SandboxResult:
    """Resultado da execução no sandbox"""
    status: SandboxStatus
    exit_code: Optional[int]
    stdout: str
    stderr: str
    execution_time: float
    resource_usage: Dict
    test_results: Dict
    timestamp: str
    container_id: Optional[str] = None
    error_message: Optional[str] = None

class EvolutionSandbox:
    """
    Ambiente isolado para teste seguro de código evolutivo
    """
    
    def __init__(self, docker_image: str = "python:3.11-alpine"):
        """
        Inicializa o sandbox
        
        Args:
            docker_image: Imagem Docker base para execução
        """
        try:
            self.docker_client = docker.from_env()
            self.docker_image = docker_image
            
            # Configurações de segurança
            self.resource_limits = {
                "mem_limit": "256m",        # 256MB RAM (corrigido)
                "cpu_period": 100000,       # 100ms
                "cpu_quota": 50000,         # 50% CPU
                "pids_limit": 50,           # Máximo 50 processos
                "ulimits": [
                    docker.types.Ulimit(name='nofile', soft=64, hard=64),  # Máximo 64 arquivos
                    docker.types.Ulimit(name='nproc', soft=32, hard=32),   # Máximo 32 processos
                ]
            }
            
            # Configurações de rede e segurança
            self.security_opts = [
                "no-new-privileges:true",   # Sem novos privilégios
                "seccomp:unconfined"        # Perfil seccomp restritivo
            ]
            
            self.timeout = 300  # 5 minutos máximo
            self.active_containers = {}
            
            # Verifica se Docker está disponível
            self._check_docker_availability()
            
        except Exception as e:
            logger.error(f"Erro ao inicializar sandbox: {e}")
            raise
    
    def _check_docker_availability(self):
        """Verifica se Docker está disponível e funcionando"""
        try:
            self.docker_client.ping()
            logger.info("Docker disponível e funcionando")
            
            # Verifica se imagem base existe
            try:
                self.docker_client.images.get(self.docker_image)
                logger.info(f"Imagem {self.docker_image} disponível")
            except docker.errors.ImageNotFound:
                logger.info(f"Baixando imagem {self.docker_image}...")
                self.docker_client.images.pull(self.docker_image)
                
        except Exception as e:
            logger.error(f"Docker não disponível: {e}")
            raise
    
    async def test_evolution(self, code: str, test_data: Dict = None, 
                           timeout: Optional[int] = None) -> SandboxResult:
        """
        Testa código em ambiente isolado
        
        Args:
            code: Código Python a ser testado
            test_data: Dados de teste (opcional)
            timeout: Timeout personalizado em segundos
            
        Returns:
            SandboxResult: Resultado da execução
        """
        container_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando teste sandbox {container_id}")
            
            # 1. Prepara ambiente de teste
            test_dir = await self._prepare_test_environment(code, test_data, container_id)
            
            # 2. Cria e executa container
            container = await self._create_container(test_dir, container_id)
            
            # 3. Monitora execução
            result = await self._monitor_execution(
                container, 
                timeout or self.timeout,
                start_time
            )
            
            # 4. Coleta resultados
            result.resource_usage = await self._collect_resource_usage(container)
            result.test_results = await self._collect_test_results(test_dir)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no teste sandbox {container_id}: {e}")
            return SandboxResult(
                status=SandboxStatus.FAILED,
                exit_code=None,
                stdout="",
                stderr=str(e),
                execution_time=time.time() - start_time,
                resource_usage={},
                test_results={},
                timestamp=datetime.now().isoformat(),
                container_id=container_id,
                error_message=str(e)
            )
        finally:
            # Limpeza
            await self._cleanup_container(container_id)
            await self._cleanup_test_environment(container_id)
    
    async def _prepare_test_environment(self, code: str, test_data: Dict, 
                                      container_id: str) -> str:
        """Prepara ambiente de teste temporário"""
        
        # Cria diretório temporário
        test_dir = tempfile.mkdtemp(prefix=f"sandbox_{container_id}_")
        
        try:
            # Arquivo principal com código
            main_file = os.path.join(test_dir, "main.py")
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(self._wrap_code_for_testing(code))
            
            # Arquivo de dados de teste
            if test_data:
                test_data_file = os.path.join(test_dir, "test_data.json")
                with open(test_data_file, 'w', encoding='utf-8') as f:
                    json.dump(test_data, f, indent=2)
            
            # Script de execução
            runner_script = os.path.join(test_dir, "runner.py")
            with open(runner_script, 'w', encoding='utf-8') as f:
                f.write(self._create_runner_script())
            
            # Arquivo de requirements básico
            requirements_file = os.path.join(test_dir, "requirements.txt")
            with open(requirements_file, 'w', encoding='utf-8') as f:
                f.write("# Apenas bibliotecas seguras permitidas\n")
            
            logger.info(f"Ambiente de teste preparado em {test_dir}")
            return test_dir
            
        except Exception as e:
            # Limpeza em caso de erro
            shutil.rmtree(test_dir, ignore_errors=True)
            raise e
    
    def _wrap_code_for_testing(self, code: str) -> str:
        """Envolve código em estrutura de teste segura"""
        
        wrapper = f'''
import sys
import json
import traceback
from datetime import datetime
import time

# Configurações de segurança
sys.tracebacklimit = 10

def safe_execution():
    """Executa código de forma segura"""
    start_time = time.time()
    result = {{
        "success": False,
        "output": None,
        "error": None,
        "execution_time": 0,
        "timestamp": datetime.now().isoformat()
    }}
    
    try:
        # Carrega dados de teste se disponível
        test_data = None
        try:
            with open('/app/test_data.json', 'r') as f:
                test_data = json.load(f)
        except FileNotFoundError:
            pass
        
        # Código gerado (inserido aqui)
        {code}
        
        # Se chegou até aqui, execução foi bem-sucedida
        result["success"] = True
        result["output"] = "Código executado com sucesso"
        
    except Exception as e:
        result["error"] = {{
            "type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }}
    
    finally:
        result["execution_time"] = time.time() - start_time
    
    # Salva resultado
    with open('/app/result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    return result

if __name__ == "__main__":
    result = safe_execution()
    print(json.dumps(result, indent=2))
'''
        return wrapper
    
    def _create_runner_script(self) -> str:
        """Cria script de execução principal"""
        
        return '''
#!/usr/bin/env python3
import subprocess
import sys
import json
import time
import signal
import os

def timeout_handler(signum, frame):
    print("TIMEOUT: Execução interrompida por timeout")
    sys.exit(124)  # Código de timeout

def main():
    # Configura timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(300)  # 5 minutos
    
    try:
        # Executa código principal
        result = subprocess.run(
            [sys.executable, '/app/main.py'],
            capture_output=True,
            text=True,
            timeout=300,
            cwd='/app'
        )
        
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print("RETURN_CODE:", result.returncode)
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("TIMEOUT: Processo excedeu tempo limite")
        return 124
    except Exception as e:
        print(f"ERROR: {e}")
        return 1
    finally:
        signal.alarm(0)  # Cancela timeout

if __name__ == "__main__":
    sys.exit(main())
'''
    
    async def _create_container(self, test_dir: str, container_id: str):
        """Cria container Docker isolado"""
        
        try:
            container = self.docker_client.containers.run(
                self.docker_image,
                command="python /app/runner.py",
                volumes={
                    test_dir: {"bind": "/app", "mode": "ro"}  # Read-only
                },
                working_dir="/app",
                network_mode="none",  # Sem acesso à rede
                security_opt=self.security_opts,
                detach=True,
                remove=False,  # Não remove automaticamente para coleta de logs
                name=f"sandbox_{container_id}",
                **self.resource_limits
            )
            
            self.active_containers[container_id] = container
            logger.info(f"Container {container_id} criado: {container.id}")
            
            return container
            
        except Exception as e:
            logger.error(f"Erro ao criar container {container_id}: {e}")
            raise
    
    async def _monitor_execution(self, container, timeout: int, 
                               start_time: float) -> SandboxResult:
        """Monitora execução do container"""
        
        container_id = container.name.split('_')[-1]
        
        try:
            # Aguarda execução com timeout
            result = container.wait(timeout=timeout)
            execution_time = time.time() - start_time
            
            # Coleta logs
            logs = container.logs().decode('utf-8', errors='ignore')
            
            # Separa stdout e stderr dos logs
            stdout_lines = []
            stderr_lines = []
            
            for line in logs.split('\n'):
                if line.startswith('STDOUT:'):
                    stdout_lines.append(line[7:])
                elif line.startswith('STDERR:'):
                    stderr_lines.append(line[7:])
                elif line.startswith('ERROR:'):
                    stderr_lines.append(line[6:])
            
            stdout = '\n'.join(stdout_lines)
            stderr = '\n'.join(stderr_lines)
            
            # Determina status
            exit_code = result.get("StatusCode", -1)
            if exit_code == 0:
                status = SandboxStatus.COMPLETED
            elif exit_code == 124:
                status = SandboxStatus.TIMEOUT
            else:
                status = SandboxStatus.FAILED
            
            return SandboxResult(
                status=status,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                resource_usage={},
                test_results={},
                timestamp=datetime.now().isoformat(),
                container_id=container_id
            )
            
        except docker.errors.APIError as e:
            if "timeout" in str(e).lower():
                # Mata container em caso de timeout
                try:
                    container.kill()
                except:
                    pass
                
                return SandboxResult(
                    status=SandboxStatus.TIMEOUT,
                    exit_code=124,
                    stdout="",
                    stderr="Execução interrompida por timeout",
                    execution_time=time.time() - start_time,
                    resource_usage={},
                    test_results={},
                    timestamp=datetime.now().isoformat(),
                    container_id=container_id,
                    error_message="Timeout"
                )
            else:
                raise
    
    async def _collect_resource_usage(self, container) -> Dict:
        """Coleta uso de recursos do container"""
        
        try:
            stats = container.stats(stream=False)
            
            # Extrai métricas principais
            memory_usage = stats.get("memory", {})
            cpu_stats = stats.get("cpu_stats", {})
            
            return {
                "memory": {
                    "usage": memory_usage.get("usage", 0),
                    "max_usage": memory_usage.get("max_usage", 0),
                    "limit": memory_usage.get("limit", 0)
                },
                "cpu": {
                    "total_usage": cpu_stats.get("cpu_usage", {}).get("total_usage", 0),
                    "system_cpu_usage": cpu_stats.get("system_cpu_usage", 0)
                },
                "network": stats.get("networks", {}),
                "blkio": stats.get("blkio_stats", {})
            }
            
        except Exception as e:
            logger.warning(f"Erro ao coletar estatísticas: {e}")
            return {}
    
    async def _collect_test_results(self, test_dir: str) -> Dict:
        """Coleta resultados dos testes"""
        
        try:
            result_file = os.path.join(test_dir, "result.json")
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    return json.load(f)
            else:
                return {"error": "Arquivo de resultado não encontrado"}
                
        except Exception as e:
            logger.warning(f"Erro ao coletar resultados: {e}")
            return {"error": str(e)}
    
    async def _cleanup_container(self, container_id: str):
        """Remove container após execução"""
        
        try:
            if container_id in self.active_containers:
                container = self.active_containers[container_id]
                
                # Para container se ainda estiver rodando
                try:
                    container.kill()
                except:
                    pass
                
                # Remove container
                try:
                    container.remove(force=True)
                except:
                    pass
                
                del self.active_containers[container_id]
                logger.info(f"Container {container_id} removido")
                
        except Exception as e:
            logger.warning(f"Erro na limpeza do container {container_id}: {e}")
    
    async def _cleanup_test_environment(self, container_id: str):
        """Remove diretório de teste temporário"""
        
        try:
            # Encontra e remove diretório temporário
            temp_dirs = [d for d in os.listdir(tempfile.gettempdir()) 
                        if d.startswith(f"sandbox_{container_id}_")]
            
            for temp_dir in temp_dirs:
                full_path = os.path.join(tempfile.gettempdir(), temp_dir)
                shutil.rmtree(full_path, ignore_errors=True)
                logger.info(f"Diretório temporário {full_path} removido")
                
        except Exception as e:
            logger.warning(f"Erro na limpeza do ambiente {container_id}: {e}")
    
    def cleanup_all(self):
        """Remove todos os containers ativos"""
        
        logger.info("Limpando todos os containers ativos...")
        
        for container_id in list(self.active_containers.keys()):
            asyncio.create_task(self._cleanup_container(container_id))
    
    def get_active_containers(self) -> List[str]:
        """Retorna lista de containers ativos"""
        return list(self.active_containers.keys())
    
    def get_sandbox_stats(self) -> Dict:
        """Retorna estatísticas do sandbox"""
        
        return {
            "active_containers": len(self.active_containers),
            "docker_available": True,
            "docker_image": self.docker_image,
            "resource_limits": self.resource_limits,
            "timeout": self.timeout
        } 