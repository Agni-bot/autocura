"""
Fixtures específicas para testes end-to-end do sistema de autocura.

Este módulo contém fixtures que são específicas para testes e2e,
como configuração do ambiente completo, serviços externos, etc.
"""

import pytest
from typing import Generator
import docker
from pathlib import Path
import sys
import yaml
import time
import os

# Adiciona o diretório src ao PYTHONPATH
src_path = str(Path(__file__).parent.parent.parent / "src")
sys.path.append(src_path)

def load_e2e_config() -> dict:
    """Carrega configurações específicas para testes e2e."""
    config_path = Path(__file__).parent.parent.parent / "config" / "test" / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def e2e_config():
    """Fixture que fornece configurações para testes e2e."""
    return load_e2e_config()

@pytest.fixture(scope="session")
def docker_compose():
    """Fixture que gerencia o ambiente Docker Compose para testes e2e."""
    import subprocess
    
    # Inicia o ambiente
    subprocess.run(["docker-compose", "-f", "docker-compose.test.yml", "up", "-d"])
    
    # Aguarda os serviços estarem prontos
    time.sleep(10)
    
    yield
    
    # Para o ambiente
    subprocess.run(["docker-compose", "-f", "docker-compose.test.yml", "down"])

@pytest.fixture(scope="session")
def e2e_services(e2e_config):
    """Fixture que fornece URLs dos serviços para testes e2e."""
    return {
        "api_url": f"http://{e2e_config['api']['host']}:{e2e_config['api']['port']}",
        "grafana_url": f"http://localhost:{e2e_config['monitoring']['grafana']['port']}",
        "prometheus_url": f"http://localhost:{e2e_config['monitoring']['prometheus']['port']}",
        "loki_url": f"http://localhost:{e2e_config['monitoring']['loki']['port']}"
    }

@pytest.fixture(scope="function")
def clean_e2e_env(e2e_config):
    """Fixture que limpa o ambiente e2e antes e depois de cada teste."""
    # Setup
    test_files = [
        e2e_config["memory"]["path"],
        e2e_config["logging"]["file"]
    ]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
    
    yield
    
    # Teardown
    for file in test_files:
        if os.path.exists(file):
            os.remove(file) 