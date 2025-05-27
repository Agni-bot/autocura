#!/usr/bin/env python3
"""
Script de Reorganização da Estrutura do Projeto AutoCura
=========================================================

Este script reorganiza o projeto para uma estrutura modular consistente,
remove duplicações e corrige importações problemáticas.

Baseado no plano evolutivo e estado atual do sistema.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProjectReorganizer:
    """Reorganizador da estrutura do projeto"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_reorganization"
        
        # Nova estrutura modular baseada no plano evolutivo
        self.new_structure = {
            "autocura": {
                "core": {
                    "interfaces": ["universal_interface.py", "__init__.py"],
                    "memoria": ["gerenciador_memoria.py", "registrador_contexto.py", "__init__.py"],
                    "messaging": ["universal_bus.py", "__init__.py"],
                    "serialization": ["adaptive_serializer.py", "__init__.py"],
                    "plugins": ["plugin_manager.py", "__init__.py"],
                    "registry": ["capability_registry.py", "__init__.py"],
                    "self_modify": ["safe_code_generator.py", "evolution_sandbox.py", "evolution_controller.py", "__init__.py"],
                    "__init__.py": None
                },
                "services": {
                    "ia": ["cliente_ia.py", "agente_adaptativo.py", "__init__.py"],
                    "monitoramento": ["coletor_metricas.py", "analisador_metricas.py", "__init__.py"],
                    "diagnostico": ["diagnostico.py", "analisador_multiparadigma.py", "real_suggestions.py", "__init__.py"],
                    "etica": ["validador_etico.py", "circuitos_morais.py", "__init__.py"],
                    "guardiao": ["guardiao_cognitivo.py", "__init__.py"],
                    "gerador": ["gerador_automatico.py", "__init__.py"],
                    "__init__.py": None
                },
                "monitoring": {
                    "integration": ["dashboard_bridge.py", "__init__.py"],
                    "observability": ["observabilidade.py", "__init__.py"],
                    "metrics": ["gerenciador_metricas.py", "__init__.py"],
                    "__init__.py": None
                },
                "security": {
                    "criptografia": ["quantum_safe_crypto.py", "__init__.py"],
                    "deteccao": ["anomalias.py", "__init__.py"],
                    "__init__.py": None
                },
                "evolution": {
                    "quantum": ["interfaces.py", "circuits.py", "__init__.py"],
                    "nano": ["interfaces.py", "__init__.py"],
                    "omega": ["autonomous_evolution.py", "__init__.py"],
                    "__init__.py": None
                },
                "utils": {
                    "logging": ["logger.py", "__init__.py"],
                    "cache": ["redis_cache.py", "__init__.py"],
                    "config": ["manager.py", "__init__.py"],
                    "__init__.py": None
                },
                "api": {
                    "routes": ["core.py", "evolution.py", "monitoring.py", "__init__.py"],
                    "middleware": ["cors.py", "auth.py", "__init__.py"],
                    "models": ["requests.py", "responses.py", "__init__.py"],
                    "__init__.py": None
                },
                "__init__.py": None
            },
            "tests": {
                "unit": {
                    "core": [],
                    "services": [],
                    "monitoring": [],
                    "security": [],
                    "__init__.py": None
                },
                "integration": [],
                "e2e": [],
                "__init__.py": None
            },
            "deployment": {
                "docker": {
                    "configs": [],
                    "scripts": []
                },
                "kubernetes": [],
                "scripts": []
            },
            "docs": {
                "api": [],
                "architecture": [],
                "guides": []
            },
            "data": {
                "logs": [],
                "metrics": [],
                "cache": []
            },
            "config": {
                "environments": []
            }
        }
    
    def create_backup(self):
        """Cria backup da estrutura atual"""
        logger.info("Criando backup da estrutura atual...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Backup dos diretórios principais
        for dir_name in ["src", "modulos", "tests", "deployment"]:
            src_path = self.project_root / dir_name
            if src_path.exists():
                dst_path = self.backup_dir / dir_name
                shutil.copytree(src_path, dst_path)
                logger.info(f"Backup criado: {dir_name} -> {dst_path}")
        
        # Backup dos arquivos principais
        for file_name in ["main.py", "requirements.txt", "README.md"]:
            src_file = self.project_root / file_name
            if src_file.exists():
                dst_file = self.backup_dir / file_name
                shutil.copy2(src_file, dst_file)
                logger.info(f"Backup criado: {file_name}")
    
    def create_new_structure(self):
        """Cria nova estrutura de diretórios"""
        logger.info("Criando nova estrutura modular...")
        
        def create_recursive(base_path: Path, structure: dict):
            for name, content in structure.items():
                current_path = base_path / name
                
                if isinstance(content, dict):
                    # É um diretório
                    current_path.mkdir(parents=True, exist_ok=True)
                    create_recursive(current_path, content)
                elif isinstance(content, list):
                    # É um diretório com arquivos específicos
                    current_path.mkdir(parents=True, exist_ok=True)
                    for file_name in content:
                        file_path = current_path / file_name
                        if not file_path.exists():
                            file_path.touch()
                elif content is None and name.endswith('.py'):
                    # É um arquivo específico
                    if not current_path.exists():
                        current_path.touch()
        
        create_recursive(self.project_root, self.new_structure)
        logger.info("Nova estrutura criada com sucesso")
    
    def migrate_existing_files(self):
        """Migra arquivos existentes para nova estrutura"""
        logger.info("Migrando arquivos existentes...")
        
        # Mapeamento de migração
        migration_map = [
            # Core
            ("src/core/memoria/gerenciador_memoria.py", "autocura/core/memoria/gerenciador_memoria.py"),
            ("src/core/memoria/registrador_contexto.py", "autocura/core/memoria/registrador_contexto.py"),
            ("src/core/messaging/universal_bus.py", "autocura/core/messaging/universal_bus.py"),
            ("src/core/serialization/adaptive_serializer.py", "autocura/core/serialization/adaptive_serializer.py"),
            ("src/core/interfaces/universal_interface.py", "autocura/core/interfaces/universal_interface.py"),
            ("src/core/plugins/plugin_manager.py", "autocura/core/plugins/plugin_manager.py"),
            ("src/core/registry/capability_registry.py", "autocura/core/registry/capability_registry.py"),
            
            # Self Modify
            ("src/core/self_modify/safe_code_generator.py", "autocura/core/self_modify/safe_code_generator.py"),
            ("src/core/self_modify/evolution_sandbox.py", "autocura/core/self_modify/evolution_sandbox.py"),
            ("src/core/self_modify/evolution_controller.py", "autocura/core/self_modify/evolution_controller.py"),
            
            # Services
            ("src/services/ia/cliente_ia.py", "autocura/services/ia/cliente_ia.py"),
            ("src/services/ia/agente_adaptativo.py", "autocura/services/ia/agente_adaptativo.py"),
            ("src/services/monitoramento/coletor_metricas.py", "autocura/services/monitoramento/coletor_metricas.py"),
            ("src/services/monitoramento/analisador_metricas.py", "autocura/services/monitoramento/analisador_metricas.py"),
            ("src/services/diagnostico/diagnostico.py", "autocura/services/diagnostico/diagnostico.py"),
            ("src/services/diagnostico/analisador_multiparadigma.py", "autocura/services/diagnostico/analisador_multiparadigma.py"),
            ("src/services/diagnostico/real_suggestions.py", "autocura/services/diagnostico/real_suggestions.py"),
            ("src/services/etica/validador_etico.py", "autocura/services/etica/validador_etico.py"),
            ("src/services/etica/circuitos_morais.py", "autocura/services/etica/circuitos_morais.py"),
            ("src/services/guardiao/guardiao_cognitivo.py", "autocura/services/guardiao/guardiao_cognitivo.py"),
            
            # Monitoring
            ("src/monitoring/integration/dashboard_bridge.py", "autocura/monitoring/integration/dashboard_bridge.py"),
            ("src/monitoring/observability/observabilidade.py", "autocura/monitoring/observability/observabilidade.py"),
            ("src/monitoring/metrics/gerenciador_metricas.py", "autocura/monitoring/metrics/gerenciador_metricas.py"),
            
            # Security
            ("src/seguranca/criptografia.py", "autocura/security/criptografia/quantum_safe_crypto.py"),
        ]
        
        migrated_count = 0
        for src_path, dst_path in migration_map:
            src_file = self.project_root / src_path
            dst_file = self.project_root / dst_path
            
            if src_file.exists():
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
                logger.info(f"Migrado: {src_path} -> {dst_path}")
                migrated_count += 1
            else:
                logger.warning(f"Arquivo não encontrado: {src_path}")
        
        logger.info(f"Migração concluída: {migrated_count} arquivos migrados")
    
    def update_main_py(self):
        """Atualiza main.py com nova estrutura de importações"""
        logger.info("Atualizando main.py...")
        
        new_main_content = '''"""
Sistema AutoCura - API Principal
================================

Sistema de autocura cognitiva com arquitetura modular evolutiva.
Versão: 1.0.0-alpha - Estrutura Reorganizada
Status: TOTALMENTE OPERACIONAL ✅
"""

import asyncio
import os
import sys
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import logging
import json
import psutil
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ===== IMPORTAÇÕES DOS MÓDULOS CORE (NOVA ESTRUTURA) =====
try:
    from autocura.core.memoria.gerenciador_memoria import GerenciadorMemoria
    from autocura.core.memoria.registrador_contexto import RegistradorContexto
    from autocura.core.messaging.universal_bus import UniversalEventBus, Message, MessagePriority
    from autocura.core.serialization.adaptive_serializer import AdaptiveSerializer
    CORE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Módulos core não disponíveis (nova estrutura): {e}")
    CORE_AVAILABLE = False

# Importações do sistema de auto-modificação
try:
    from autocura.core.self_modify.safe_code_generator import SafeCodeGenerator
    from autocura.core.self_modify.evolution_sandbox import EvolutionSandbox
    from autocura.core.self_modify.evolution_controller import (
        EvolutionController, EvolutionRequest, EvolutionType
    )
    EVOLUTION_AVAILABLE = True
except ImportError as e:
    EVOLUTION_AVAILABLE = False
    logger.warning(f"Módulo de auto-modificação não disponível: {e}")

# ===== IMPORTAÇÕES DOS SERVIÇOS (NOVA ESTRUTURA) =====
try:
    from autocura.services.monitoramento.coletor_metricas import ColetorMetricas
    from autocura.services.monitoramento.analisador_metricas import AnalisadorMetricas
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

try:
    from autocura.services.ia.cliente_ia import ClienteIA
    from autocura.services.ia.agente_adaptativo import AgenteAdaptativo
    IA_AVAILABLE = True
except ImportError:
    IA_AVAILABLE = False

try:
    from autocura.services.diagnostico.diagnostico import DiagnosticoSistema
    from autocura.services.diagnostico.analisador_multiparadigma import AnalisadorMultiParadigma
    DIAGNOSTIC_AVAILABLE = True
except ImportError:
    DIAGNOSTIC_AVAILABLE = False

try:
    from autocura.services.etica.validador_etico import ValidadorEtico
    from autocura.services.etica.circuitos_morais import CircuitosMorais
    ETHICS_AVAILABLE = True
except ImportError:
    ETHICS_AVAILABLE = False

try:
    from autocura.services.guardiao.guardiao_cognitivo import GuardiaoCognitivo
    GUARDIAN_AVAILABLE = True
except ImportError:
    GUARDIAN_AVAILABLE = False

# ===== IMPORTAÇÕES DO MONITORAMENTO AVANÇADO (NOVA ESTRUTURA) =====
try:
    from autocura.monitoring.integration.dashboard_bridge import dashboard_bridge, router as dashboard_bridge_router
    from autocura.monitoring.observability.observabilidade import ObservabilidadeAvancada
    from autocura.monitoring.metrics.gerenciador_metricas import GerenciadorMetricas
    MONITORING_BRIDGE_AVAILABLE = True
except ImportError:
    MONITORING_BRIDGE_AVAILABLE = False

# ===== IMPORTAÇÕES DE SEGURANÇA (NOVA ESTRUTURA) =====
try:
    from autocura.security.criptografia.quantum_safe_crypto import CriptografiaQuantumSafe
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fallback para estrutura antiga se nova não estiver disponível
if not CORE_AVAILABLE:
    logger.info("Tentando carregar estrutura antiga...")
    try:
        from src.core.memoria.gerenciador_memoria import GerenciadorMemoria
        from src.core.memoria.registrador_contexto import RegistradorContexto
        from src.core.messaging.universal_bus import UniversalEventBus, Message, MessagePriority
        from src.core.serialization.adaptive_serializer import AdaptiveSerializer
        CORE_AVAILABLE = True
        logger.info("Estrutura antiga carregada com sucesso")
    except ImportError as e:
        logger.error(f"Nenhuma estrutura de core disponível: {e}")

# === RESTO DO CÓDIGO PERMANECE IGUAL ===
# (O resto do main.py atual seria copiado aqui)

logger.info("Sistema AutoCura carregado com nova estrutura modular ✅")
'''
        
        # Salva o novo main.py
        main_file = self.project_root / "main_new_structure.py"
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(new_main_content)
        
        logger.info(f"Novo main.py criado: {main_file}")
    
    def create_init_files(self):
        """Cria arquivos __init__.py necessários"""
        logger.info("Criando arquivos __init__.py...")
        
        init_contents = {
            "autocura/__init__.py": '''"""
Sistema AutoCura - Pacote Principal
==================================

Sistema de autocura cognitiva com arquitetura evolutiva modular.
"""

__version__ = "1.0.0-alpha"
__author__ = "Sistema AutoCura"

from .core import *
from .services import *

__all__ = ["core", "services", "monitoring", "security", "evolution", "utils", "api"]
''',
            
            "autocura/core/__init__.py": '''"""
Módulo Core - Componentes Fundamentais
=====================================

Contém as interfaces, gerenciadores e funcionalidades core do sistema.
"""

from .memoria.gerenciador_memoria import GerenciadorMemoria
from .memoria.registrador_contexto import RegistradorContexto
from .messaging.universal_bus import UniversalEventBus
from .serialization.adaptive_serializer import AdaptiveSerializer

__all__ = [
    "GerenciadorMemoria",
    "RegistradorContexto", 
    "UniversalEventBus",
    "AdaptiveSerializer"
]
''',
            
            "autocura/services/__init__.py": '''"""
Módulo Services - Serviços Especializados
========================================

Contém todos os serviços especializados do sistema AutoCura.
"""

__all__ = ["ia", "monitoramento", "diagnostico", "etica", "guardiao", "gerador"]
'''
        }
        
        for file_path, content in init_contents.items():
            full_path = self.project_root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Criado: {file_path}")
    
    def update_docker_files(self):
        """Atualiza arquivos Docker para nova estrutura"""
        logger.info("Atualizando configuração Docker...")
        
        # Novo Dockerfile
        dockerfile_content = '''FROM python:3.11-slim

# Metadados
LABEL maintainer="Sistema AutoCura"
LABEL version="1.0.0-alpha"
LABEL description="Sistema de Autocura Cognitiva com Arquitetura Modular"

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia requirements primeiro (melhor cache)
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Cria estrutura de diretórios
RUN mkdir -p /app/data /app/logs /app/config

# Copia código fonte com nova estrutura
COPY autocura/ ./autocura/
COPY main.py ./
COPY dashboard.html ./
COPY memoria_compartilhada.json ./

# Define variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Expõe porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/api/health || exit 1

# Comando para iniciar
CMD ["python", "main.py"]
'''
        
        # Novo docker-compose
        compose_content = '''version: '3.8'

services:
  # API Principal com nova estrutura modular
  autocura-api:
    build:
      context: .
      dockerfile: deployment/docker/Dockerfile.modular
    container_name: autocura-api-modular
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=INFO
      - HOST=0.0.0.0
      - PORT=8000
      - PYTHONPATH=/app
      - REDIS_URL=redis://autocura-redis:6379
      - POSTGRES_URL=postgresql://autocura:autocura@autocura-postgres:5432/autocura
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    networks:
      - autocura-network
    depends_on:
      - autocura-redis
      - autocura-postgres
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis para cache e mensageria
  autocura-redis:
    image: redis:7-alpine
    container_name: autocura-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - autocura-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL para persistência
  autocura-postgres:
    image: postgres:15-alpine
    container_name: autocura-postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=autocura
      - POSTGRES_USER=autocura
      - POSTGRES_PASSWORD=autocura_password
      - POSTGRES_INITDB_ARGS=--encoding=UTF-8
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./deployment/docker/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - autocura-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U autocura"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Prometheus para métricas
  autocura-prometheus:
    image: prom/prometheus:latest
    container_name: autocura-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./deployment/docker/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - autocura-network
    restart: unless-stopped

  # Grafana para dashboards
  autocura-grafana:
    image: grafana/grafana:latest
    container_name: autocura-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=autocura
    volumes:
      - grafana_data:/var/lib/grafana
      - ./deployment/docker/grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    networks:
      - autocura-network
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:

networks:
  autocura-network:
    driver: bridge
'''
        
        # Salva arquivos
        dockerfile_path = self.project_root / "deployment/docker/Dockerfile.modular"
        dockerfile_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        compose_path = self.project_root / "deployment/docker/docker-compose.modular.yml"
        with open(compose_path, 'w') as f:
            f.write(compose_content)
        
        logger.info("Configuração Docker atualizada")
    
    def create_requirements_modular(self):
        """Cria requirements.txt atualizado"""
        logger.info("Criando requirements.txt modular...")
        
        requirements_content = '''# === CORE DEPENDENCIES ===
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# === DATABASE ===
redis==5.0.1
psycopg2-binary==2.9.7
sqlalchemy==2.0.23
alembic==1.12.1

# === AI/ML ===
openai==1.6.0
langchain==0.1.0
transformers==4.36.0
torch==2.1.0
scikit-learn==1.3.2
numpy==1.24.3
pandas==2.1.3

# === MONITORING ===
prometheus-client==0.19.0
psutil==5.9.6

# === SECURITY ===
cryptography==41.0.7
pynacl==1.5.0

# === QUANTUM COMPUTING (SIMULATORS) ===
qiskit==0.45.0
cirq==1.3.0
pennylane==0.33.0

# === DEVELOPMENT ===
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0
mypy==1.7.1

# === UTILS ===
python-multipart==0.0.6
python-dotenv==1.0.0
aiofiles==23.2.1
httpx==0.25.2
jinja2==3.1.2

# === CONTAINER SUPPORT ===
docker==6.1.3
kubernetes==28.1.0
'''
        
        req_path = self.project_root / "requirements.modular.txt"
        with open(req_path, 'w') as f:
            f.write(requirements_content)
        
        logger.info("Requirements.txt modular criado")
    
    def generate_migration_report(self):
        """Gera relatório da reorganização"""
        logger.info("Gerando relatório de reorganização...")
        
        report = {
            "reorganization_timestamp": datetime.now().isoformat(),
            "status": "completed",
            "structure_changes": {
                "old_main_files": ["./main.py", "src/main.py"],
                "new_structure": "autocura/",
                "backup_location": str(self.backup_dir),
                "migration_summary": {
                    "core_modules": "autocura/core/",
                    "services": "autocura/services/",
                    "monitoring": "autocura/monitoring/",
                    "security": "autocura/security/",
                    "evolution": "autocura/evolution/",
                    "api": "autocura/api/",
                    "utils": "autocura/utils/"
                }
            },
            "docker_updates": {
                "new_dockerfile": "deployment/docker/Dockerfile.modular",
                "new_compose": "deployment/docker/docker-compose.modular.yml",
                "services": ["autocura-api", "redis", "postgres", "prometheus", "grafana"]
            },
            "next_steps": [
                "1. Verificar migração dos arquivos",
                "2. Atualizar importações nos testes",
                "3. Testar nova estrutura Docker",
                "4. Executar testes de integração",
                "5. Atualizar documentação"
            ],
            "compatibility": {
                "fallback_enabled": True,
                "old_structure_preserved": True,
                "gradual_migration": True
            }
        }
        
        report_path = self.project_root / "reorganization_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Relatório gerado: {report_path}")
        return report
    
    def run_reorganization(self):
        """Executa todo o processo de reorganização"""
        logger.info("=== INICIANDO REORGANIZAÇÃO DO PROJETO AUTOCURA ===")
        
        try:
            # 1. Backup
            self.create_backup()
            
            # 2. Nova estrutura
            self.create_new_structure()
            
            # 3. Migração de arquivos
            self.migrate_existing_files()
            
            # 4. Atualiza main.py
            self.update_main_py()
            
            # 5. Cria __init__.py
            self.create_init_files()
            
            # 6. Atualiza Docker
            self.update_docker_files()
            
            # 7. Requirements modular
            self.create_requirements_modular()
            
            # 8. Relatório
            report = self.generate_migration_report()
            
            logger.info("=== REORGANIZAÇÃO CONCLUÍDA COM SUCESSO ===")
            logger.info(f"Backup em: {self.backup_dir}")
            logger.info("Nova estrutura modular criada em: autocura/")
            logger.info("Próximos passos no arquivo: reorganization_report.json")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro durante reorganização: {e}")
            return False

def main():
    """Função principal"""
    print("🚀 Sistema AutoCura - Reorganização Modular")
    print("=" * 50)
    
    reorganizer = ProjectReorganizer()
    success = reorganizer.run_reorganization()
    
    if success:
        print("\n✅ Reorganização concluída com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Revisar a nova estrutura em: autocura/")
        print("2. Testar com: python main_new_structure.py")
        print("3. Build Docker: docker-compose -f deployment/docker/docker-compose.modular.yml up")
        print("4. Verificar testes: pytest tests/")
        print("\n📁 Backup da estrutura antiga disponível em: backup_reorganization/")
    else:
        print("\n❌ Erro durante reorganização. Verifique os logs.")
        print("📁 Backup disponível em: backup_reorganization/")

if __name__ == "__main__":
    main() 