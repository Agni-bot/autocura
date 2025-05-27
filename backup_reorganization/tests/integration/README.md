# Testes de Integração

Este diretório contém os testes de integração do sistema de autocura. Testes de integração são responsáveis por testar a interação entre diferentes componentes do sistema.

## Estrutura

- `test_*.py`: Arquivos de teste de integração
- `conftest.py`: Configurações e fixtures específicas para testes de integração

## Convenções

1. Nome dos arquivos: `test_[componente]_integration.py`
2. Nome das classes: `Test[Componente]Integration`
3. Nome dos métodos: `test_[cenario]_integration`

## Integrações Testadas

- API com banco de dados
- Monitoramento com Prometheus
- Logs com Loki
- Cache com Redis
- Kubernetes com orquestrador
- Camada de integração com serviços externos
- Fluxo de autonomia entre componentes
- Diagnóstico avançado com múltiplos componentes

## Ambiente de Teste

Os testes de integração utilizam containers Docker para simular o ambiente de produção:

- Redis
- PostgreSQL
- Prometheus
- Outros serviços necessários

## Executando os Testes

```bash
# Executar todos os testes de integração
pytest tests/integration/

# Executar um teste específico
pytest tests/integration/test_[componente]_integration.py

# Executar com cobertura
pytest tests/integration/ --cov=src --cov-report=term-missing
``` 