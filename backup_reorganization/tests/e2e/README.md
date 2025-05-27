# Testes End-to-End (E2E)

Este diretório contém os testes end-to-end do sistema de autocura. Testes E2E são responsáveis por testar o sistema completo, simulando o uso real pelos usuários.

## Estrutura

- `test_*.py`: Arquivos de teste E2E
- `conftest.py`: Configurações e fixtures específicas para testes E2E

## Convenções

1. Nome dos arquivos: `test_[fluxo]_e2e.py`
2. Nome das classes: `Test[Fluxo]E2E`
3. Nome dos métodos: `test_[cenario]_e2e`

## Fluxos Testados

- Fluxo completo de autocura
- Monitoramento crítico
- Diagnóstico crítico
- Ações críticas
- Execução de monitoramento
- Alocação de recursos
- Métricas do sistema

## Ambiente de Teste

Os testes E2E utilizam Docker Compose para simular o ambiente completo de produção:

- API
- Banco de dados
- Cache
- Monitoramento (Prometheus, Grafana, Loki)
- Alertmanager
- Outros serviços necessários

## Executando os Testes

```bash
# Executar todos os testes E2E
pytest tests/e2e/

# Executar um teste específico
pytest tests/e2e/test_[fluxo]_e2e.py

# Executar com cobertura
pytest tests/e2e/ --cov=src --cov-report=term-missing
```

## Observações

- Os testes E2E são mais lentos que os outros tipos de teste
- Requerem mais recursos do sistema
- Devem ser executados em um ambiente limpo
- Podem ser executados em paralelo com `-n auto` 