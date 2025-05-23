# Dependências

Este documento lista todas as dependências utilizadas pelo módulo de integração.

## 📦 Dependências Principais

### FastAPI e Dependências

```toml
[tool.poetry.dependencies]
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
python-multipart = "^0.0.6"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
pydantic = {extras = ["email"], version = "^2.4.2"}
pydantic-settings = "^2.0.3"
```

### Banco de Dados

```toml
[tool.poetry.dependencies]
sqlalchemy = "^2.0.23"
alembic = "^1.12.1"
psycopg2-binary = "^2.9.9"
redis = "^5.0.1"
```

### Mensageria

```toml
[tool.poetry.dependencies]
kafka-python = "^2.0.2"
aiokafka = "^0.8.1"
```

### Monitoramento

```toml
[tool.poetry.dependencies]
prometheus-client = "^0.17.1"
opentelemetry-api = "^1.21.0"
opentelemetry-sdk = "^1.21.0"
opentelemetry-instrumentation-fastapi = "^0.42b0"
opentelemetry-exporter-otlp = "^1.21.0"
```

### Cache

```toml
[tool.poetry.dependencies]
cachetools = "^5.3.2"
```

### Segurança

```toml
[tool.poetry.dependencies]
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
```

## 🧪 Dependências de Desenvolvimento

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
black = "^23.10.1"
isort = "^5.12.0"
flake8 = "^6.1.0"
mypy = "^1.6.1"
```

## 📚 Dependências de Documentação

```toml
[tool.poetry.group.docs.dependencies]
mkdocs = "^1.5.3"
mkdocs-material = "^9.4.14"
mkdocstrings = {extras = ["python"], version = "^0.23.0"}
```

## 🔧 Dependências de Testes

```toml
[tool.poetry.group.test.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
pytest-mock = "^3.12.0"
pytest-env = "^1.1.3"
```

## 📊 Dependências de Análise

```toml
[tool.poetry.group.analysis.dependencies]
bandit = "^1.7.5"
safety = "^2.3.5"
```

## 🔍 Versões Mínimas

| Dependência | Versão Mínima | Versão Atual |
|-------------|---------------|--------------|
| Python | 3.9 | 3.11 |
| FastAPI | 0.104.0 | 0.104.0 |
| SQLAlchemy | 2.0.23 | 2.0.23 |
| Redis | 5.0.1 | 5.0.1 |
| Kafka | 2.0.2 | 2.0.2 |
| Prometheus | 0.17.1 | 0.17.1 |
| OpenTelemetry | 1.21.0 | 1.21.0 |

## 📝 Arquivo pyproject.toml Completo

```toml
[tool.poetry]
name = "autocura-integracao"
version = "0.1.0"
description = "Módulo de integração do sistema de autocura"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.9"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
python-multipart = "^0.0.6"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
pydantic = {extras = ["email"], version = "^2.4.2"}
pydantic-settings = "^2.0.3"
sqlalchemy = "^2.0.23"
alembic = "^1.12.1"
psycopg2-binary = "^2.9.9"
redis = "^5.0.1"
kafka-python = "^2.0.2"
aiokafka = "^0.8.1"
prometheus-client = "^0.17.1"
opentelemetry-api = "^1.21.0"
opentelemetry-sdk = "^1.21.0"
opentelemetry-instrumentation-fastapi = "^0.42b0"
opentelemetry-exporter-otlp = "^1.21.0"
cachetools = "^5.3.2"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
black = "^23.10.1"
isort = "^5.12.0"
flake8 = "^6.1.0"
mypy = "^1.6.1"

[tool.poetry.group.docs.dependencies]
mkdocs = "^1.5.3"
mkdocs-material = "^9.4.14"
mkdocstrings = {extras = ["python"], version = "^0.23.0"}

[tool.poetry.group.test.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
pytest-mock = "^3.12.0"
pytest-env = "^1.1.3"

[tool.poetry.group.analysis.dependencies]
bandit = "^1.7.5"
safety = "^2.3.5"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --cov=src --cov-report=term-missing"
```

## 🔄 Atualização de Dependências

Para atualizar as dependências, execute:

```bash
# Atualizar todas as dependências
poetry update

# Atualizar uma dependência específica
poetry update fastapi

# Verificar vulnerabilidades
poetry run safety check

# Verificar problemas de segurança
poetry run bandit -r src/
```

## 📚 Referências

- [Poetry Documentation](https://python-poetry.org/docs/)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [Kafka Python Client](https://kafka-python.readthedocs.io/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/) 