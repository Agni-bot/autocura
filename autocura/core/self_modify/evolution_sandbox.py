"""
Sandbox de Evolução - Sistema Isolado para Testes
================================================

Sistema de sandbox Docker para testar evoluções de forma segura.
"""

import tempfile
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import subprocess
import os

logger = logging.getLogger(__name__)

class EvolutionSandbox:
    """Sandbox isolado para testes de evolução"""
    
    def __init__(self):
        self.container_name = "autocura-evolution-sandbox"
        self.docker_available = self._check_docker()
    
    def _check_docker(self) -> bool:
        """Verifica se Docker está disponível"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def test_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Testa código em ambiente isolado"""
        try:
            if not self.docker_available:
                return self._fallback_test(code)
            
            # Cria arquivo temporário
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Executa em container isolado
                cmd = [
                    'docker', 'run', '--rm',
                    '--memory=256m',
                    '--cpus=0.5',
                    '--network=none',
                    '-v', f'{temp_file}:/tmp/code.py:ro',
                    'python:3.11-slim',
                    'python', '/tmp/code.py'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None
                }
                
            finally:
                # Limpa arquivo temporário
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": None,
                "error": "Timeout: código execução muito longa"
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": f"Erro no sandbox: {str(e)}"
            }
    
    def _fallback_test(self, code: str) -> Dict[str, Any]:
        """Teste fallback sem Docker"""
        try:
            # Validação básica de sintaxe
            compile(code, '<string>', 'exec')
            
            return {
                "success": True,
                "output": "Sintaxe válida (teste simplificado - Docker não disponível)",
                "error": None
            }
            
        except SyntaxError as e:
            return {
                "success": False,
                "output": None,
                "error": f"Erro de sintaxe: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": f"Erro na validação: {str(e)}"
            }
