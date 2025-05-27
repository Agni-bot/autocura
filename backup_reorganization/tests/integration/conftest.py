"""
Fixtures específicas para testes de integração do sistema de autocura.

Este módulo contém fixtures que são específicas para testes de integração,
como configuração de serviços externos, banco de dados, etc.
"""

import pytest
from typing import Generator
import docker
from pathlib import Path
import sys

# Adiciona o diretório src ao PYTHONPATH
src_path = str(Path(__file__).parent.parent.parent / "src")
sys.path.append(src_path)

@pytest.fixture(scope="session")
def docker_client():
    """Fixture que fornece um cliente Docker para testes de integração."""
    return docker.from_env()

@pytest.fixture(scope="session")
def test_containers(docker_client):
    """Fixture que inicia os containers necessários para os testes de integração."""
    containers = []
    
    # Inicia os containers necessários
    services = [
        {"name": "redis", "image": "redis:latest", "ports": {"6379/tcp": 6379}},
        {"name": "postgres", "image": "postgres:latest", "ports": {"5432/tcp": 5432}},
        {"name": "prometheus", "image": "prom/prometheus:latest", "ports": {"9090/tcp": 9090}}
    ]
    
    for service in services:
        container = docker_client.containers.run(
            service["image"],
            name=f"test_{service['name']}",
            ports=service["ports"],
            detach=True
        )
        containers.append(container)
    
    yield containers
    
    # Limpa os containers após os testes
    for container in containers:
        container.stop()
        container.remove()

@pytest.fixture(scope="session")
def test_services(test_containers):
    """Fixture que fornece URLs dos serviços para testes de integração."""
    return {
        "redis_url": "redis://localhost:6379/0",
        "postgres_url": "postgresql://test:test@localhost:5432/test_db",
        "prometheus_url": "http://localhost:9090"
    } 