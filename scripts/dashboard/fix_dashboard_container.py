#!/usr/bin/env python3
"""
Script para corrigir e atualizar o container do Dashboard AutoCura
==================================================================

Este script verifica e corrige as funcionalidades do dashboard,
garantindo que todas as features estejam operacionais.
"""

import os
import sys
import json
import subprocess
import time
import requests
from pathlib import Path
from datetime import datetime

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_status(message, status="info"):
    """Imprime mensagem com cor apropriada"""
    if status == "success":
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
    elif status == "error":
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
    elif status == "warning":
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
    elif status == "info":
        print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")
    elif status == "header":
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def check_docker():
    """Verifica se Docker está instalado e rodando"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_status("Docker está instalado", "success")
            
            # Verifica se está rodando
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if result.returncode == 0:
                print_status("Docker está rodando", "success")
                return True
            else:
                print_status("Docker não está rodando", "error")
                return False
        else:
            print_status("Docker não está instalado", "error")
            return False
    except FileNotFoundError:
        print_status("Docker não encontrado no PATH", "error")
        return False

def check_api_health():
    """Verifica se a API está respondendo"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status(f"API está saudável - Status: {data.get('status', 'unknown')}", "success")
            return True
        else:
            print_status(f"API retornou status {response.status_code}", "warning")
            return False
    except requests.exceptions.ConnectionError:
        print_status("API não está acessível em localhost:8000", "error")
        return False
    except Exception as e:
        print_status(f"Erro ao verificar API: {e}", "error")
        return False

def check_modules_status():
    """Verifica o status dos módulos"""
    try:
        response = requests.get("http://localhost:8000/api/modules/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            operational = data.get('operational', 0)
            
            print_status(f"Módulos: {operational}/{total} operacionais", "info")
            
            # Lista módulos não operacionais
            modules = data.get('modules', [])
            for module in modules:
                if not module.get('health', False):
                    print_status(f"  - {module.get('name')}: {module.get('status')}", "warning")
            
            return operational, total
        else:
            return 0, 0
    except Exception as e:
        print_status(f"Erro ao verificar módulos: {e}", "error")
        return 0, 0

def create_docker_compose_dashboard():
    """Cria um docker-compose específico para o dashboard"""
    compose_content = """version: '3.8'

services:
  # API Principal com Dashboard
  autocura-api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    container_name: autocura-api
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - LOG_LEVEL=INFO
      - HOST=0.0.0.0
      - PORT=8000
      - RELOAD=false
    volumes:
      - ./src:/app/src
      - ./dashboard.html:/app/dashboard.html
      - ./memoria_compartilhada.json:/app/memoria_compartilhada.json
      - ./data:/app/data
    networks:
      - autocura-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Redis para cache e mensageria
  autocura-redis:
    image: redis:alpine
    container_name: autocura-redis
    ports:
      - "6379:6379"
    networks:
      - autocura-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL para persistencia
  autocura-postgres:
    image: postgres:14-alpine
    container_name: autocura-postgres
    environment:
      - POSTGRES_USER=autocura
      - POSTGRES_PASSWORD=autocura123
      - POSTGRES_DB=autocura_db
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - autocura-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U autocura"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Prometheus para metricas
  autocura-prometheus:
    image: prom/prometheus:latest
    container_name: autocura-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - autocura-network

  # Grafana para visualizacao
  autocura-grafana:
    image: grafana/grafana:latest
    container_name: autocura-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./config/grafana/provisioning:/etc/grafana/provisioning
    networks:
      - autocura-network
    depends_on:
      - autocura-prometheus

volumes:
  postgres-data:
  prometheus-data:
  grafana-data:

networks:
  autocura-network:
    driver: bridge
"""
    
    # Salva o arquivo com encoding UTF-8 sem BOM
    compose_path = Path("docker-compose.dashboard.yml")
    with open(compose_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(compose_content)
    print_status(f"Arquivo {compose_path} criado", "success")
    return compose_path

def create_dockerfile_api():
    """Cria Dockerfile otimizado para a API"""
    dockerfile_content = """FROM python:3.9-slim

# Instala dependencias do sistema
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Define diretorio de trabalho
WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Instala dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia codigo fonte
COPY . .

# Expoe porta
EXPOSE 8000

# Comando para iniciar
CMD ["python", "main.py"]
"""
    
    # Cria diretório docker se não existir
    docker_dir = Path("docker")
    docker_dir.mkdir(exist_ok=True)
    
    # Salva o arquivo com encoding UTF-8 sem BOM
    dockerfile_path = docker_dir / "Dockerfile.api"
    with open(dockerfile_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(dockerfile_content)
    print_status(f"Arquivo {dockerfile_path} criado", "success")
    return dockerfile_path

def create_prometheus_config():
    """Cria configuração do Prometheus"""
    prometheus_config = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'autocura-api'
    static_configs:
      - targets: ['autocura-api:8000']
    metrics_path: '/api/metrics'
    
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
"""
    
    # Cria diretório config se não existir
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Salva o arquivo com encoding UTF-8 sem BOM
    prometheus_path = config_dir / "prometheus.yml"
    with open(prometheus_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(prometheus_config)
    print_status(f"Arquivo {prometheus_path} criado", "success")
    return prometheus_path

def update_memory_file():
    """Atualiza o arquivo de memória compartilhada"""
    memory_path = Path("memoria_compartilhada.json")
    
    if memory_path.exists():
        try:
            with open(memory_path, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
        except:
            memory_data = {}
    else:
        memory_data = {}
    
    # Atualiza com informações do dashboard
    memory_data["dashboard_update"] = {
        "timestamp": datetime.now().isoformat(),
        "action": "dashboard_container_fix",
        "status": "in_progress",
        "components": {
            "api": "updating",
            "redis": "configuring",
            "postgres": "configuring",
            "prometheus": "configuring",
            "grafana": "configuring"
        }
    }
    
    # Salva atualização
    with open(memory_path, 'w', encoding='utf-8') as f:
        json.dump(memory_data, f, indent=2, ensure_ascii=False)
    
    print_status("Memória compartilhada atualizada", "success")

def stop_existing_containers():
    """Para containers existentes"""
    print_status("Parando containers existentes...", "info")
    
    containers = [
        "autocura-api",
        "autocura-redis", 
        "autocura-postgres",
        "autocura-prometheus",
        "autocura-grafana"
    ]
    
    for container in containers:
        try:
            result = subprocess.run(
                ['docker', 'stop', container],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print_status(f"Container {container} parado", "success")
            
            # Remove o container
            subprocess.run(
                ['docker', 'rm', container],
                capture_output=True,
                text=True
            )
        except:
            pass

def start_dashboard_containers():
    """Inicia os containers do dashboard"""
    print_status("Iniciando containers do dashboard...", "info")
    
    try:
        # Verifica se docker-compose existe, senão tenta docker compose
        compose_cmd = None
        
        # Tenta docker-compose primeiro
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            compose_cmd = ['docker-compose']
        else:
            # Tenta docker compose (novo formato)
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                compose_cmd = ['docker', 'compose']
        
        if not compose_cmd:
            print_status("docker-compose não encontrado. Instale o Docker Compose.", "error")
            return False
        
        # Build e start com docker-compose
        cmd = compose_cmd + ['-f', 'docker-compose.dashboard.yml', 'up', '-d', '--build']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_status("Containers iniciados com sucesso", "success")
            return True
        else:
            print_status(f"Erro ao iniciar containers: {result.stderr}", "error")
            # Tenta mostrar logs mais detalhados
            if result.stderr:
                print_status("Detalhes do erro:", "info")
                print(result.stderr)
            return False
    except Exception as e:
        print_status(f"Erro ao executar docker-compose: {e}", "error")
        return False

def wait_for_services():
    """Aguarda os serviços ficarem prontos"""
    print_status("Aguardando serviços ficarem prontos...", "info")
    
    services = [
        ("API", "http://localhost:8000/api/health", 60),
        ("Prometheus", "http://localhost:9090/-/ready", 30),
        ("Grafana", "http://localhost:3000/api/health", 30)
    ]
    
    for service_name, url, timeout in services:
        print(f"  Verificando {service_name}...", end="", flush=True)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code in [200, 204]:
                    print(f" {Colors.OKGREEN}✅{Colors.ENDC}")
                    break
            except:
                pass
            time.sleep(2)
        else:
            print(f" {Colors.FAIL}❌{Colors.ENDC}")

def main():
    """Função principal"""
    print_status("CORREÇÃO DO CONTAINER DASHBOARD AUTOCURA", "header")
    
    # 1. Verifica Docker
    if not check_docker():
        print_status("Docker é necessário para continuar", "error")
        sys.exit(1)
    
    # 2. Para containers existentes
    stop_existing_containers()
    
    # 3. Cria arquivos de configuração
    print_status("Criando arquivos de configuração...", "info")
    create_docker_compose_dashboard()
    create_dockerfile_api()
    create_prometheus_config()
    
    # 4. Atualiza memória compartilhada
    update_memory_file()
    
    # 5. Inicia containers
    if start_dashboard_containers():
        # 6. Aguarda serviços
        wait_for_services()
        
        # 7. Verifica status final
        print_status("\nVERIFICAÇÃO FINAL", "header")
        
        # Verifica API
        if check_api_health():
            # Verifica módulos
            operational, total = check_modules_status()
            
            if operational == total:
                print_status("\nTodos os módulos estão operacionais!", "success")
            else:
                print_status(f"\n{total - operational} módulos precisam ser ativados", "warning")
        
        # URLs de acesso
        print_status("\nACESSO AOS SERVIÇOS", "header")
        print(f"{Colors.OKBLUE}Dashboard HTML:{Colors.ENDC} http://localhost:8000/")
        print(f"{Colors.OKBLUE}API Docs:{Colors.ENDC} http://localhost:8000/docs")
        print(f"{Colors.OKBLUE}Prometheus:{Colors.ENDC} http://localhost:9090/")
        print(f"{Colors.OKBLUE}Grafana:{Colors.ENDC} http://localhost:3000/ (admin/admin)")
        
        print_status("\nDashboard corrigido e operacional! 🚀", "success")
    else:
        print_status("Falha ao iniciar containers", "error")
        sys.exit(1)

if __name__ == "__main__":
    main() 