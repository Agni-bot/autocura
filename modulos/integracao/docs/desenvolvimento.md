# Guia de Desenvolvimento

Este documento descreve as práticas e padrões de desenvolvimento do módulo de integração.

## 🛠️ Ambiente de Desenvolvimento

### Requisitos

- Python 3.9+
- Docker
- Docker Compose
- Git
- VS Code (recomendado)

### Configuração

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/autocura.git
cd autocura
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Inicie os serviços:
```bash
docker-compose up -d
```

## 📝 Padrões de Código

### Estrutura de Diretórios

```
src/
  ├── integracao/
  │   ├── __init__.py
  │   ├── api/
  │   │   ├── __init__.py
  │   │   ├── routes.py
  │   │   └── models.py
  │   ├── core/
  │   │   ├── __init__.py
  │   │   ├── gateway.py
  │   │   └── processor.py
  │   ├── adapters/
  │   │   ├── __init__.py
  │   │   ├── http.py
  │   │   └── websocket.py
  │   └── utils/
  │       ├── __init__.py
  │       ├── logging.py
  │       └── metrics.py
  ├── tests/
  │   ├── __init__.py
  │   ├── conftest.py
  │   └── test_gateway.py
  └── docs/
      ├── api.md
      ├── arquitetura.md
      └── desenvolvimento.md
```

### Convenções

1. **Nomes de Arquivos**
   - Use snake_case para nomes de arquivos
   - Sufixo `_test.py` para arquivos de teste
   - Sufixo `_config.py` para arquivos de configuração

2. **Nomes de Classes**
   - Use PascalCase
   - Nomes descritivos e autoexplicativos
   - Evite abreviações

3. **Nomes de Funções/Métodos**
   - Use snake_case
   - Verbos para ações
   - Nomes descritivos

4. **Nomes de Variáveis**
   - Use snake_case
   - Nomes descritivos
   - Evite abreviações

5. **Docstrings**
   - Use docstrings em todas as classes e funções
   - Formato Google Style
   - Documente parâmetros e retornos

### Exemplo

```python
class MessageProcessor:
    """Processa mensagens recebidas pelo gateway.
    
    Esta classe é responsável por processar mensagens recebidas
    pelo gateway e encaminhá-las para os handlers apropriados.
    
    Args:
        broker (MessageBroker): Broker de mensagens
        config (ProcessorConfig): Configuração do processador
        
    Attributes:
        handlers (Dict[str, Handler]): Mapeamento de tipos para handlers
    """
    
    def __init__(self, broker: MessageBroker, config: ProcessorConfig):
        self.broker = broker
        self.config = config
        self.handlers = {}
        
    async def process(self, message: Message) -> ProcessResult:
        """Processa uma mensagem.
        
        Args:
            message (Message): Mensagem a ser processada
            
        Returns:
            ProcessResult: Resultado do processamento
            
        Raises:
            HandlerNotFound: Se não houver handler para o tipo da mensagem
            ProcessingError: Se ocorrer erro no processamento
        """
        handler = self.get_handler(message.type)
        if not handler:
            raise HandlerNotFound(message.type)
            
        try:
            result = await handler.handle(message)
            await self.broker.publish(result)
            return result
        except Exception as e:
            raise ProcessingError(f"Erro ao processar mensagem: {e}")
```

## 🧪 Testes

### Unitários

```python
import pytest
from unittest.mock import Mock, patch

class TestMessageProcessor:
    @pytest.fixture
    def processor(self):
        broker = Mock()
        config = Mock()
        return MessageProcessor(broker, config)
        
    def test_process_success(self, processor):
        message = Mock(type="test")
        handler = Mock()
        processor.handlers["test"] = handler
        
        result = processor.process(message)
        
        handler.handle.assert_called_once_with(message)
        assert result == handler.handle.return_value
        
    def test_process_handler_not_found(self, processor):
        message = Mock(type="invalid")
        
        with pytest.raises(HandlerNotFound):
            processor.process(message)
```

### Integração

```python
import pytest
from fastapi.testclient import TestClient
from app import app

@pytest.fixture
def client():
    return TestClient(app)
    
def test_message_flow(client):
    # Enviar mensagem
    response = client.post(
        "/messages",
        json={"type": "test", "content": "test"}
    )
    assert response.status_code == 200
    message_id = response.json()["id"]
    
    # Verificar processamento
    response = client.get(f"/messages/{message_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
```

## 🔄 CI/CD

### GitHub Actions

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
        
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
        
    - name: Run linters
      run: |
        flake8 src tests
        black --check src tests
        isort --check-only src tests
```

## 📚 Documentação

### Docstrings

```python
def process_message(message: Message) -> ProcessResult:
    """Processa uma mensagem.
    
    Esta função processa uma mensagem recebida, validando seu conteúdo
    e encaminhando para o handler apropriado.
    
    Args:
        message (Message): Mensagem a ser processada
            
    Returns:
        ProcessResult: Resultado do processamento
            
    Raises:
        ValidationError: Se a mensagem for inválida
        ProcessingError: Se ocorrer erro no processamento
        
    Examples:
        >>> message = Message(type="test", content="test")
        >>> result = process_message(message)
        >>> print(result.status)
        "processed"
    """
    pass
```

### README

```markdown
# Módulo de Integração

## Descrição

Este módulo é responsável por gerenciar a comunicação entre os diferentes
componentes do sistema de autocura.

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

```python
from integracao import Gateway

gateway = Gateway(config)
await gateway.start()
```

## Desenvolvimento

```bash
# Instalar dependências
pip install -r requirements-dev.txt

# Executar testes
pytest

# Executar linters
flake8
black
isort
```

## Licença

MIT
```

## 🔍 Debugging

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def process_message(message: Message):
    logger.debug("Iniciando processamento: %s", message.id)
    try:
        result = do_process(message)
        logger.info("Mensagem processada: %s", message.id)
        return result
    except Exception as e:
        logger.error("Erro ao processar mensagem: %s", e, exc_info=True)
        raise
```

### VS Code

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

## 📚 Referências

- [Python Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Flake8 Documentation](https://flake8.pycqa.org/) 