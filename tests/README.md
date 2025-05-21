# Testes do Sistema de Autocura

Este diretório contém os testes automatizados do sistema de autocura. Os testes são organizados em diferentes categorias e seguem as melhores práticas de desenvolvimento.

## 📁 Estrutura de Diretórios

```
tests/
├── unit/              # Testes unitários
│   ├── core/         # Testes dos módulos core
│   ├── autocura/     # Testes dos módulos de autocura
│   ├── etica/        # Testes dos módulos éticos
│   └── ...
├── integration/       # Testes de integração
│   ├── api/          # Testes de API
│   ├── database/     # Testes de banco de dados
│   └── ...
└── e2e/              # Testes end-to-end
    └── scenarios/    # Cenários de teste
```

## 🚀 Executando os Testes

### Pré-requisitos

1. Instale as dependências de teste:
```bash
pip install -r requirements-test.txt
```

2. Configure o ambiente:
```bash
cp .env.example .env.test
# Edite .env.test com as configurações de teste
```

### Execução

1. **Executar todos os testes**:
```bash
python scripts/run_tests.py
```

2. **Executar testes específicos**:
```bash
# Testes unitários
python scripts/run_tests.py tests/unit/

# Testes de integração
python scripts/run_tests.py tests/integration/

# Testes end-to-end
python scripts/run_tests.py tests/e2e/
```

3. **Executar com marcadores**:
```bash
# Testes assíncronos
python scripts/run_tests.py -m async

# Testes de banco de dados
python scripts/run_tests.py -m database

# Testes de API
python scripts/run_tests.py -m api
```

## 📊 Relatórios

Os relatórios são gerados automaticamente após a execução dos testes:

- **Relatório HTML**: `test-results/report.html`
- **Relatório JUnit**: `test-results/junit.xml`
- **Cobertura de Código**: `htmlcov/index.html`
- **Relatório Markdown**: `test-results/test_report.md`

## 🎯 Cobertura de Código

A cobertura mínima de código é de 80%. Para verificar a cobertura:

```bash
python scripts/run_tests.py --cov-report=term-missing
```

## 🔍 Marcadores de Teste

- `@pytest.mark.unit`: Testes unitários
- `@pytest.mark.integration`: Testes de integração
- `@pytest.mark.e2e`: Testes end-to-end
- `@pytest.mark.slow`: Testes que demoram mais
- `@pytest.mark.async`: Testes assíncronos
- `@pytest.mark.memory`: Testes de memória
- `@pytest.mark.database`: Testes de banco de dados
- `@pytest.mark.api`: Testes de API
- `@pytest.mark.security`: Testes de segurança
- `@pytest.mark.performance`: Testes de performance

## 📝 Escrevendo Testes

### Estrutura Básica

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def fixture_exemplo():
    """Fixture de exemplo."""
    return {
        "dado": "valor"
    }

@pytest.mark.asyncio
async def test_exemplo(fixture_exemplo):
    """Teste de exemplo."""
    # Arrange
    valor = fixture_exemplo["dado"]
    
    # Act
    resultado = await funcao_teste(valor)
    
    # Assert
    assert resultado == valor_esperado
```

### Boas Práticas

1. **Nomenclatura**:
   - Arquivos: `test_*.py`
   - Funções: `test_*`
   - Classes: `Test*`

2. **Organização**:
   - Um arquivo por módulo testado
   - Testes relacionados agrupados
   - Fixtures compartilhadas no `conftest.py`

3. **Asserts**:
   - Use asserts específicos
   - Verifique exceções quando apropriado
   - Teste casos de erro

4. **Mocks**:
   - Use mocks para dependências externas
   - Evite mocks desnecessários
   - Documente o comportamento esperado

## 🔧 Configuração

O arquivo `pytest.ini` contém as configurações principais:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts = 
    --verbose
    --tb=long
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=80
```

## 🛠️ Utilitários

### Fixtures Comuns

- `config_teste`: Configurações de teste
- `mock_api`: Mock da API
- `mock_db`: Mock do banco de dados
- `mock_redis`: Mock do Redis
- `dados_teste`: Dados de exemplo
- `monitoramento`: Instância do monitoramento
- `temp_dir`: Diretório temporário
- `log_captura`: Captura de logs
- `mock_env`: Variáveis de ambiente
- `mock_time`: Mock de tempo

### Helpers

- `assert_dict_contains`: Verifica se dicionário contém chaves
- `assert_list_contains`: Verifica se lista contém itens
- `assert_async_raises`: Verifica exceções assíncronas
- `assert_log_contains`: Verifica mensagens de log

## 🔐 Segurança

1. **Dados Sensíveis**:
   - Use variáveis de ambiente
   - Não comite credenciais
   - Use mocks para serviços externos

2. **Ambiente de Teste**:
   - Isolado do ambiente de produção
   - Dados de teste anônimos
   - Limpeza após execução

## 📈 Monitoramento

Os testes são monitorados através de:

- Métricas de cobertura
- Tempo de execução
- Taxa de falhas
- Tendências de performance

## 🤝 Contribuindo

1. Siga o padrão de código
2. Adicione testes para novas funcionalidades
3. Mantenha a cobertura acima de 80%
4. Documente mudanças significativas
5. Atualize este README quando necessário 