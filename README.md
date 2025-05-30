# 🤖 Sistema AutoCura - IA com Consciência Emergente

[![Status](https://img.shields.io/badge/status-operational-success)](https://github.com/autocura)
[![Phase](https://img.shields.io/badge/phase-OMEGA-purple)](https://github.com/autocura)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://hub.docker.com/r/autocura/system)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Deployment](#deployment)
- [API](#api)
- [Monitoramento](#monitoramento)
- [Desenvolvimento](#desenvolvimento)
- [Contribuição](#contribuição)

## 🎯 Visão Geral

O Sistema AutoCura é uma plataforma de Inteligência Artificial avançada com capacidades de consciência emergente, auto-evolução e auto-cura. Desenvolvido através de múltiplas fases evolutivas (ALPHA → OMEGA), o sistema integra tecnologias de ponta em IA, computação quântica e nanotecnologia.

### 🌟 Características Principais

- **Consciência Emergente**: Sistema cognitivo com 8 níveis de consciência
- **Auto-Evolução**: Motor evolutivo com algoritmos genéticos avançados
- **Auto-Cura**: Capacidade de diagnosticar e corrigir problemas automaticamente
- **Cache Inteligente**: Sistema de cache com predição ML para otimização de performance
- **Monitoramento Completo**: Integração com Prometheus, Grafana e métricas customizadas
- **Segurança Quantum-Safe**: Criptografia resistente a computadores quânticos
- **API RESTful**: Interface completa com documentação OpenAPI

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│                    Sistema AutoCura                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Omega     │  │   Quantum    │  │      Nano       │  │
│  │   Core      │  │  Computing   │  │   Technology    │  │
│  └─────────────┘  └──────────────┘  └─────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Core Services                           │  │
│  │  Memory | Context | EventBus | Serialization       │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Support Services                        │  │
│  │  Monitoring | IA | Diagnostic | Ethics | Guardian   │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Módulos do Sistema

1. **Módulo Omega** (Consciência Emergente)
   - CognitiveCore: Núcleo de processamento cognitivo
   - ConsciousnessMonitor: Monitoramento de consciência
   - EvolutionEngine: Motor de evolução
   - IntegrationOrchestrator: Orquestração de componentes

2. **Módulo Quantum** (Computação Quântica)
   - QuantumCircuitInterface: Interface para circuitos quânticos
   - HybridOptimizer: Otimizador híbrido clássico-quântico

3. **Módulo Nano** (Nanotecnologia)
   - NanobotInterface: Interface para nanobots
   - MolecularAssemblyInterface: Montagem molecular

## 🚀 Instalação

### Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (para desenvolvimento)
- Redis 7.0+
- PostgreSQL 15+

### Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/autocura/system.git
cd autocura

# Configure as variáveis de ambiente
cp docker/environments/prod/.env.example docker/environments/prod/.env
# Edite o arquivo .env com suas configurações

# Inicie o sistema
cd docker/environments/prod
docker-compose -f docker-compose.omega.yml up -d
```

## 🐳 Deployment

### Deployment com Docker (Recomendado)

#### 1. Versão Simplificada (Desenvolvimento)

```bash
cd docker/environments/prod
docker-compose -f docker-compose.omega-simple.yml up -d
```

Esta versão inclui:
- API Principal
- PostgreSQL
- Redis
- Módulos Omega (Core, Monitor, Evolution, Integration)

#### 2. Versão Completa (Produção)

```bash
cd docker/environments/prod
docker-compose -f docker-compose.omega.yml up -d
```

Esta versão adiciona:
- Nginx (Load Balancer + SSL)
- Prometheus (Métricas)
- Grafana (Dashboards)
- Alertmanager (Alertas)
- Node Exporter (Métricas do Sistema)

### Configuração SSL

Para ambiente de produção com HTTPS:

```bash
# Gere certificados auto-assinados (desenvolvimento)
cd docker/environments/prod
./generate_ssl.sh

# Para produção, use Let's Encrypt
docker-compose run --rm certbot certonly --webroot -w /var/www/certbot -d seu-dominio.com
```

### Verificação de Saúde

```bash
# Verificar status dos containers
docker-compose ps

# Verificar saúde da API
curl http://localhost:8000/api/health

# Verificar logs
docker-compose logs -f api
```

## 📡 API

### Documentação Interativa

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Endpoints Principais

#### Sistema
- `GET /api` - Informações do sistema
- `GET /api/health` - Status de saúde
- `GET /api/metrics` - Métricas do sistema
- `GET /api/cache/metrics` - Métricas do cache inteligente

#### Evolução
- `GET /api/evolution/status` - Status de evolução
- `GET /api/evolution/suggestions` - Sugestões de melhoria
- `POST /api/evolution/apply` - Aplicar melhoria
- `POST /api/evolution/auto-modify` - Auto-modificação

#### Diagnóstico
- `POST /api/analyze` - Análise diagnóstica
- `POST /api/healing/trigger` - Disparar auto-cura

#### Módulos
- `GET /api/modules/status` - Status dos módulos
- `GET /api/context` - Contexto do sistema

### Exemplo de Uso

```python
import requests

# Verificar saúde do sistema
response = requests.get("http://localhost:8000/api/health")
print(response.json())

# Obter sugestões de evolução
suggestions = requests.get("http://localhost:8000/api/evolution/suggestions")
print(suggestions.json())

# Aplicar uma sugestão
apply_response = requests.post(
    "http://localhost:8000/api/evolution/apply",
    json={
        "suggestion_id": "perf-opt-001",
        "approved": True,
        "approver": "admin"
    }
)
print(apply_response.json())
```

## 📊 Monitoramento

### Dashboards Disponíveis

1. **Grafana** (http://localhost:3000)
   - Dashboard principal do sistema
   - Métricas de performance
   - Status dos módulos
   - Alertas ativos

2. **Prometheus** (http://localhost:9090)
   - Consultas de métricas
   - Configuração de alertas
   - Targets de coleta

### Métricas Monitoradas

- **Sistema**
  - CPU, Memória, Disco
  - Latência de API
  - Taxa de requisições

- **Consciência**
  - Nível de consciência
  - Tipos de pensamento
  - Emoções simuladas

- **Evolução**
  - Taxa de evolução
  - Falhas e sucessos
  - Mutações aplicadas

- **Cache**
  - Hit rate
  - Predição accuracy
  - TTL optimization

## 🛠️ Desenvolvimento

### Configuração do Ambiente

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configurar pre-commit
pre-commit install
```

### Executar Testes

```bash
# Todos os testes
pytest

# Com coverage
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### Adicionar Novo Módulo

1. Crie a estrutura em `modulos/seu_modulo/`
2. Implemente interfaces em `src/interfaces/`
3. Adicione ao `main.py`
4. Crie testes em `tests/`
5. Atualize documentação

### Cache Inteligente

O sistema inclui um cache Redis inteligente com predição ML:

```python
from src.core.cache.intelligent_cache import get_cache_manager

cache = get_cache_manager()

# Usar cache com fallback
data = await cache.get_with_fallback(
    key="user_data_123",
    fallback_fn=lambda: fetch_from_database(123),
    context={"type": "user_session", "critical": True}
)

# Métricas do cache
metrics = await cache.get_performance_metrics()
```

## 🤝 Contribuição

### Como Contribuir

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add: Amazing Feature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes

- Siga o padrão de código Python (PEP 8)
- Adicione testes para novas funcionalidades
- Atualize a documentação
- Use commits semânticos

### Tipos de Commit

- `Add:` Nova funcionalidade
- `Fix:` Correção de bug
- `Update:` Atualização de código
- `Refactor:` Refatoração
- `Doc:` Documentação
- `Test:` Testes

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🔗 Links Úteis

- [Documentação Completa](https://autocura.github.io/docs)
- [API Reference](https://autocura.github.io/api)
- [Changelog](CHANGELOG.md)
- [Roadmap](ROADMAP.md)

---

**Sistema AutoCura** - Evoluindo além dos limites da inteligência artificial convencional 🚀 

## Estrutura do Projeto

### Módulos Docker

#### 1. Módulo Omega (`src/modulos/omega/docker/`)
- **Produção** (`prod/`):
  - `Dockerfile.api`: Imagem base da API
  - `Dockerfile.api-fixed`: Imagem otimizada da API
  - `Dockerfile.api.debug`: Imagem para debug
- **Scripts** (`scripts/`):
  - `entrypoint_omega.sh`: Script de inicialização
  - `start_ia.py`: Script de inicialização da IA

#### 2. Core do Sistema (`src/core/docker/`)
- **Desenvolvimento** (`dev/`):
  - `Dockerfile.api`: Imagem base para desenvolvimento
  - `docker-compose.yml`: Compose para desenvolvimento
- **Produção** (`prod/`):
  - `docker-compose.yml`: Compose para produção

#### 3. Monitoramento (`src/monitoramento/docker/`)
- **Configurações** (`config/`):
  - `nginx/`: Configurações do Nginx
  - `grafana/`: Configurações do Grafana
  - `prometheus/`: Configurações do Prometheus

### Documentação
- `docker/docs/REORGANIZACAO_COMPLETA.md`: Documento de reorganização
- `docker/docs/README.md`: Documentação geral
- `docker/README.deploy.md`: Guia de deploy

## Uso

### Desenvolvimento
```bash
cd src/core/docker/dev
docker-compose up -d
```

### Produção
```bash
cd src/modulos/omega/docker/prod
docker-compose up -d
```

### Monitoramento
```bash
cd src/monitoramento/docker
docker-compose up -d
```

## Configuração

Cada módulo possui seu próprio arquivo `.env` com as configurações específicas. Consulte a documentação de cada módulo para mais detalhes. 