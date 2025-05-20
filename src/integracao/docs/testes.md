# Guia de Testes

Este documento descreve as práticas de testes implementadas no módulo de integração.

## 🧪 Testes Unitários

### Estrutura

```python
import pytest
from unittest.mock import Mock, patch

class TestMessageProcessor:
    @pytest.fixture
    def processor(self):
        return MessageProcessor()

    def test_process_message_success(self, processor):
        message = Mock(id="msg_123", protocol="http")
        result = processor.process(message)
        assert result.status == "success"
        assert result.processing_time_ms > 0

    def test_process_message_error(self, processor):
        message = Mock(id="msg_123", protocol="invalid")
        with pytest.raises(InvalidProtocolError):
            processor.process(message)
```

### Cobertura

```python
# pytest.ini
[pytest]
addopts = --cov=src --cov-report=html --cov-report=term-missing
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## 🔄 Testes de Integração

### Setup

```python
import pytest
from fastapi.testclient import TestClient
from app import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_db():
    # Setup test database
    db = TestDatabase()
    yield db
    # Teardown
    db.cleanup()
```

### Casos de Teste

```python
def test_message_flow(client, test_db):
    # Enviar mensagem
    response = client.post(
        "/messages",
        json={"protocol": "http", "content": "test"}
    )
    assert response.status_code == 200
    message_id = response.json()["id"]

    # Verificar processamento
    response = client.get(f"/messages/{message_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
```

## 🚀 Testes de Performance

### Locust

```python
from locust import HttpUser, task, between

class MessageUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def send_message(self):
        self.client.post(
            "/messages",
            json={"protocol": "http", "content": "test"}
        )

    @task
    def get_message(self):
        self.client.get("/messages/msg_123")
```

### JMeter

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Message Flow Test">
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Message Thread Group">
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">100</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">10</stringProp>
        <stringProp name="ThreadGroup.ramp_time">1</stringProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Send Message">
          <stringProp name="HTTPSampler.path">/messages</stringProp>
          <stringProp name="HTTPSampler.method">POST</stringProp>
        </HTTPSamplerProxy>
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```

## 🔒 Testes de Segurança

### OWASP ZAP

```python
from zapv2 import ZAPv2

def test_security():
    zap = ZAPv2(apikey='your-api-key')
    
    # Iniciar varredura
    zap.spider.scan('http://localhost:8000')
    zap.ascan.scan('http://localhost:8000')
    
    # Verificar resultados
    alerts = zap.core.alerts()
    assert len(alerts) == 0
```

### Bandit

```ini
# .bandit
[bandit]
exclude_dirs = tests,venv
skips = B101,B105
```

## 📊 Testes de Carga

### K6

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '1m', target: 20 },
    { duration: '30s', target: 0 },
  ],
};

export default function() {
  let res = http.post('http://localhost:8000/messages', {
    protocol: 'http',
    content: 'test'
  });
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
  
  sleep(1);
}
```

## 🔄 Testes de Regressão

### Testes Automatizados

```python
def test_regression():
    # Setup
    db = TestDatabase()
    processor = MessageProcessor(db)
    
    # Testar funcionalidades existentes
    test_cases = [
        {"protocol": "http", "expected": "success"},
        {"protocol": "grpc", "expected": "success"},
        {"protocol": "invalid", "expected": "error"},
    ]
    
    for case in test_cases:
        result = processor.process(Message(**case))
        assert result.status == case["expected"]
```

## 📝 Relatórios

### Cobertura

```python
# coverage.py
[run]
source = src
omit = 
    */tests/*
    */venv/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
```

### JUnit

```xml
<?xml version="1.0" encoding="utf-8"?>
<testsuites>
  <testsuite name="MessageProcessor" tests="10" failures="0" errors="0" skipped="0">
    <testcase classname="MessageProcessor" name="test_process_message_success" time="0.1"/>
    <testcase classname="MessageProcessor" name="test_process_message_error" time="0.1"/>
  </testsuite>
</testsuites>
```

## 🔄 CI/CD

### GitHub Actions

```yaml
name: Tests

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
```

## 📚 Referências

- [pytest](https://docs.pytest.org/)
- [Locust](https://docs.locust.io/)
- [JMeter](https://jmeter.apache.org/usermanual/)
- [OWASP ZAP](https://www.zaproxy.org/docs/)
- [K6](https://k6.io/docs/)
- [Bandit](https://bandit.readthedocs.io/) 