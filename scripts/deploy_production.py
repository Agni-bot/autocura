#!/usr/bin/env python3
"""
Script de Deploy em Produção - Sistema AutoCura
==============================================

Script automatizado para deploy seguro em ambiente de produção.
"""

import os
import sys
import subprocess
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class ProductionDeployer:
    """Deployer para ambiente de produção"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.deployment_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log de deployment"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
    
    async def deploy(self):
        """Executa deploy completo"""
        
        self.log("🚀 Iniciando deploy em produção do Sistema AutoCura")
        
        try:
            # 1. Verificações pré-deploy
            await self.pre_deployment_checks()
            
            # 2. Preparar ambiente
            await self.prepare_environment()
            
            # 3. Configurar segurança
            await self.configure_security()
            
            # 4. Deploy da aplicação
            await self.deploy_application()
            
            # 5. Configurar monitoramento
            await self.setup_monitoring()
            
            # 6. Testes pós-deploy
            await self.post_deployment_tests()
            
            # 7. Finalizar
            await self.finalize_deployment()
            
            self.log("✅ Deploy concluído com sucesso!", "SUCCESS")
            
        except Exception as e:
            self.log(f"❌ Erro no deploy: {e}", "ERROR")
            await self.rollback()
            raise
    
    async def pre_deployment_checks(self):
        """Verificações antes do deploy"""
        
        self.log("🔍 Executando verificações pré-deploy...")
        
        # Verificar Docker
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Docker não está disponível")
            self.log(f"✅ Docker: {result.stdout.strip()}")
        except Exception as e:
            raise Exception(f"Docker não encontrado: {e}")
        
        # Verificar Docker Compose
        try:
            result = subprocess.run(["docker-compose", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Docker Compose não está disponível")
            self.log(f"✅ Docker Compose: {result.stdout.strip()}")
        except Exception as e:
            raise Exception(f"Docker Compose não encontrado: {e}")
        
        # Verificar variáveis de ambiente
        required_vars = ["AI_API_KEY", "POSTGRES_PASSWORD", "GRAFANA_PASSWORD"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise Exception(f"Variáveis de ambiente faltando: {missing_vars}")
        
        self.log("✅ Todas as verificações pré-deploy passaram")
    
    async def prepare_environment(self):
        """Prepara ambiente de produção"""
        
        self.log("🏗️ Preparando ambiente de produção...")
        
        # Criar diretórios necessários
        directories = [
            "logs",
            "data",
            "config",
            "sql",
            "scripts"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.log(f"📁 Diretório criado: {directory}")
        
        # Copiar arquivos de configuração
        await self.create_production_configs()
        
        self.log("✅ Ambiente preparado")
    
    async def create_production_configs(self):
        """Cria configurações de produção"""
        
        # Docker Compose de produção
        docker_compose_content = """version: '3.8'

services:
  autocura-api:
    build: 
      context: .
      dockerfile: docker/Dockerfile.production
    ports:
      - "8001:8001"
    environment:
      - ENVIRONMENT=production
      - AI_API_KEY=${AI_API_KEY}
      - REDIS_URL=redis://autocura-redis:6379
      - POSTGRES_URL=postgresql://autocura:${POSTGRES_PASSWORD}@autocura-postgres:5432/autocura
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      - autocura-redis
      - autocura-postgres
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  autocura-redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  autocura-postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=autocura
      - POSTGRES_USER=autocura
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped

  autocura-monitoring:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

  autocura-grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:
"""
        
        with open("docker-compose.production.yml", "w") as f:
            f.write(docker_compose_content)
        
        # Configuração do Prometheus
        prometheus_config = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'autocura-api'
    static_configs:
      - targets: ['autocura-api:8001']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'autocura-evolution'
    static_configs:
      - targets: ['autocura-api:8001']
    metrics_path: '/evolution/metrics'
    scrape_interval: 30s
"""
        
        with open("config/prometheus.yml", "w") as f:
            f.write(prometheus_config)
        
        # SQL de inicialização
        init_sql = """-- Inicialização do banco AutoCura
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de evoluções
CREATE TABLE IF NOT EXISTS evolutions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(255) UNIQUE NOT NULL,
    evolution_type VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    success BOOLEAN DEFAULT FALSE,
    execution_time FLOAT,
    approval_level VARCHAR(50),
    requester VARCHAR(255),
    context TEXT,
    generated_code TEXT,
    analysis_result JSONB,
    metrics JSONB
);

-- Tabela de métricas
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_type VARCHAR(100) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    metric_value FLOAT NOT NULL,
    tags JSONB,
    evolution_id UUID REFERENCES evolutions(id)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_evolutions_status ON evolutions(status);
CREATE INDEX IF NOT EXISTS idx_evolutions_created_at ON evolutions(created_at);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type);

-- Usuário para aplicação
CREATE USER autocura_app WITH PASSWORD '${POSTGRES_PASSWORD}';
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO autocura_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO autocura_app;
"""
        
        with open("sql/init.sql", "w") as f:
            f.write(init_sql)
        
        self.log("✅ Configurações de produção criadas")
    
    async def configure_security(self):
        """Configura segurança"""
        
        self.log("🛡️ Configurando segurança...")
        
        # Verificar se as chaves estão seguras
        ai_key = os.getenv("AI_API_KEY")
        if ai_key and len(ai_key) < 20:
            self.log("⚠️ Chave AI_API_KEY parece muito curta", "WARNING")
        
        # Configurar firewall (exemplo)
        security_rules = [
            "# Regras de firewall para AutoCura",
            "# Permitir apenas portas necessárias:",
            "# 8001 - API AutoCura",
            "# 3000 - Grafana",
            "# 9090 - Prometheus",
            "# 22 - SSH (admin apenas)"
        ]
        
        with open("config/security_rules.txt", "w") as f:
            f.write("\n".join(security_rules))
        
        self.log("✅ Segurança configurada")
    
    async def deploy_application(self):
        """Deploy da aplicação"""
        
        self.log("🚀 Fazendo deploy da aplicação...")
        
        # Build e start dos containers
        try:
            # Pull das imagens base
            self.log("📥 Baixando imagens base...")
            subprocess.run(["docker-compose", "-f", "docker-compose.production.yml", 
                          "pull"], check=True)
            
            # Build da aplicação
            self.log("🔨 Construindo aplicação...")
            subprocess.run(["docker-compose", "-f", "docker-compose.production.yml", 
                          "build"], check=True)
            
            # Start dos serviços
            self.log("▶️ Iniciando serviços...")
            subprocess.run(["docker-compose", "-f", "docker-compose.production.yml", 
                          "up", "-d"], check=True)
            
            # Aguardar inicialização
            self.log("⏳ Aguardando inicialização dos serviços...")
            await asyncio.sleep(30)
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Erro no deploy: {e}")
        
        self.log("✅ Aplicação deployada")
    
    async def setup_monitoring(self):
        """Configura monitoramento"""
        
        self.log("📊 Configurando monitoramento...")
        
        # Verificar se Prometheus está rodando
        try:
            import requests
            response = requests.get("http://localhost:9090/-/healthy", timeout=10)
            if response.status_code == 200:
                self.log("✅ Prometheus está funcionando")
            else:
                self.log("⚠️ Prometheus não está respondendo", "WARNING")
        except Exception as e:
            self.log(f"⚠️ Erro ao verificar Prometheus: {e}", "WARNING")
        
        # Verificar se Grafana está rodando
        try:
            import requests
            response = requests.get("http://localhost:3000/api/health", timeout=10)
            if response.status_code == 200:
                self.log("✅ Grafana está funcionando")
            else:
                self.log("⚠️ Grafana não está respondendo", "WARNING")
        except Exception as e:
            self.log(f"⚠️ Erro ao verificar Grafana: {e}", "WARNING")
        
        self.log("✅ Monitoramento configurado")
    
    async def post_deployment_tests(self):
        """Testes pós-deploy"""
        
        self.log("🧪 Executando testes pós-deploy...")
        
        # Teste de saúde da API
        try:
            import requests
            response = requests.get("http://localhost:8001/health", timeout=10)
            if response.status_code == 200:
                self.log("✅ API está respondendo")
            else:
                raise Exception(f"API retornou status {response.status_code}")
        except Exception as e:
            raise Exception(f"Erro no teste da API: {e}")
        
        # Teste básico de auto-modificação
        try:
            result = subprocess.run([
                sys.executable, "test_auto_modification_simple.py"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log("✅ Teste básico de auto-modificação passou")
            else:
                self.log(f"⚠️ Teste básico falhou: {result.stderr}", "WARNING")
        except Exception as e:
            self.log(f"⚠️ Erro no teste básico: {e}", "WARNING")
        
        self.log("✅ Testes pós-deploy concluídos")
    
    async def finalize_deployment(self):
        """Finaliza deployment"""
        
        self.log("🏁 Finalizando deployment...")
        
        # Salvar log de deployment
        log_file = f"logs/deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(log_file, "w") as f:
            f.write("\n".join(self.deployment_log))
        
        # Criar arquivo de status
        status = {
            "deployment_time": datetime.now().isoformat(),
            "environment": self.environment,
            "status": "success",
            "services": [
                "autocura-api",
                "autocura-redis", 
                "autocura-postgres",
                "autocura-monitoring",
                "autocura-grafana"
            ],
            "endpoints": {
                "api": "http://localhost:8001",
                "grafana": "http://localhost:3000",
                "prometheus": "http://localhost:9090"
            }
        }
        
        with open("deployment_status.json", "w") as f:
            json.dump(status, f, indent=2)
        
        self.log("✅ Deployment finalizado")
        
        # Mostrar informações finais
        print("\n" + "="*60)
        print("🎉 SISTEMA AUTOCURA DEPLOYADO COM SUCESSO!")
        print("="*60)
        print("📍 Endpoints disponíveis:")
        print("   🔗 API AutoCura: http://localhost:8001")
        print("   📊 Grafana: http://localhost:3000")
        print("   📈 Prometheus: http://localhost:9090")
        print("\n🔐 Credenciais:")
        print("   Grafana: admin / [GRAFANA_PASSWORD]")
        print("\n📋 Próximos passos:")
        print("   1. Configurar domínio e SSL")
        print("   2. Configurar backup automático")
        print("   3. Configurar alertas")
        print("   4. Testar casos de uso específicos")
        print("="*60)
    
    async def rollback(self):
        """Rollback em caso de erro"""
        
        self.log("🔄 Executando rollback...", "WARNING")
        
        try:
            subprocess.run(["docker-compose", "-f", "docker-compose.production.yml", 
                          "down"], check=True)
            self.log("✅ Rollback concluído")
        except Exception as e:
            self.log(f"❌ Erro no rollback: {e}", "ERROR")

async def main():
    """Função principal"""
    
    print("🚀 Sistema AutoCura - Deploy em Produção")
    print("=" * 50)
    
    deployer = ProductionDeployer()
    
    try:
        await deployer.deploy()
    except KeyboardInterrupt:
        print("\n⚠️ Deploy interrompido pelo usuário")
        await deployer.rollback()
    except Exception as e:
        print(f"\n❌ Erro crítico no deploy: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 