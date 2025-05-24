# Documentação de Testes

## Visão Geral

Este documento descreve a estrutura, configuração e execução dos testes automatizados do sistema de autocura.

## Estrutura de Testes

```
tests/
├── unit/           # Testes unitários
├── integration/    # Testes de integração
├── e2e/           # Testes end-to-end
├── fixtures/      # Fixtures compartilhadas
└── data/          # Dados de teste
```

## Configuração

### Arquivos de Configuração

- `config/testes.yaml`: Configurações gerais dos testes
- `config/prometheus/testes.yml`: Configurações do Prometheus
- `config/grafana/provisioning/dashboards/testes.json`: Dashboard do Grafana

### Variáveis de Ambiente

```bash
# Configurações de Teste
TEST_DB_NAME=autocura_test
TEST_REDIS_DB=1
COVERAGE_THRESHOLD=80

# Configurações de Monitoramento
PROMETHEUS_PORT=9091
GRAFANA_PORT=3001
LOKI_PORT=3101
```

## Execução de Testes

### Execução Local

```bash
# Executar todos os testes
python scripts/run_tests_monitored.py

# Executar testes específicos
pytest tests/unit/test_seu_caso.py -v

# Executar com cobertura
pytest --cov=src --cov-report=html
```

### Execução no CI/CD

Os testes são executados automaticamente no GitHub Actions quando:
- Um push é feito para as branches `main` ou `develop`
- Um pull request é aberto para as branches `main` ou `develop`

## Monitoramento

### Métricas Coletadas

- Total de testes executados
- Testes passados/falhados
- Tempo de execução
- Cobertura de código

### Alertas

- Cobertura abaixo de 80%
- Testes falhando
- Tempo de execução alto
- Múltiplas falhas consecutivas

### Dashboards

O dashboard do Grafana (`http://localhost:3000/d/testes`) mostra:
- Gráfico de tempo de execução
- Estatísticas de testes
- Cobertura de código

## Relatórios

### Relatórios Gerados

- `coverage/`: Relatório de cobertura em HTML
- `test-results.xml`: Relatório JUnit
- `logs/testes.log`: Logs de execução

### Acesso aos Relatórios

- Relatórios de cobertura: `coverage/index.html`
- Relatórios de teste: `test-results.xml`
- Logs: `logs/testes.log`

## Boas Práticas

1. **Organização**
   - Mantenha os testes organizados por tipo
   - Use fixtures para setup/teardown
   - Documente casos de teste complexos

2. **Cobertura**
   - Mantenha cobertura acima de 80%
   - Teste casos de borda
   - Inclua testes negativos

3. **Performance**
   - Execute testes em paralelo
   - Use mocks quando apropriado
   - Mantenha testes rápidos

4. **Manutenção**
   - Atualize testes ao modificar código
   - Revise periodicamente
   - Remova testes obsoletos

## Troubleshooting

### Problemas Comuns

1. **Testes Falhando**
   - Verifique logs em `logs/testes.log`
   - Consulte relatórios de cobertura
   - Verifique configurações em `config/testes.yaml`

2. **Cobertura Baixa**
   - Execute `coverage report` para detalhes
   - Verifique exclusões em `config/testes.yaml`
   - Adicione testes para código não coberto

3. **Performance**
   - Use `pytest --durations=10` para identificar testes lentos
   - Verifique configurações de paralelismo
   - Otimize fixtures e setup

### Comandos Úteis

```bash
# Limpar cache de testes
pytest --cache-clear

# Ver testes mais lentos
pytest --durations=10

# Executar com debug
pytest -v --pdb

# Gerar relatório detalhado
pytest --html=report.html
```

## Contribuição

1. Siga o padrão de nomenclatura
2. Documente novos testes
3. Mantenha cobertura alta
4. Execute testes localmente antes de commitar

## Suporte

Para suporte adicional:
- Consulte a documentação em `docs/`
- Abra uma issue no GitHub
- Entre em contato com a equipe de desenvolvimento 

## Status Atual dos Testes (21/05/2025)

### Resumo da Execução
- Total de testes executados: 349
- Testes passados: 9
- Testes falharam: 3 (última execução parou após 3 falhas)
- Cobertura total: 14.49% (abaixo do threshold de 80%)

### Situação por Módulo
- **Guardião Cognitivo**: Todos os testes de integração passaram após correções recentes nos endpoints e mocks.
- **Monitoramento**: Testes básicos passaram, mas cobertura ainda baixa.
- **Dependências**: Falhas em testes de persistência e verificação de compatibilidade de Python (espera Python <= 3.13).
- **Sistema Completo**: Falha em teste de processamento por ausência de log esperado.

### Principais Falhas Atuais
- `test_fluxo_completo_autocura`: Falha na verificação de compatibilidade do Python.
- `test_historico_persistencia`: Persistência do histórico de dependências duplicando registros.
- `test_fluxo_completo_processamento`: Log "Iniciando processamento" não capturado.

### Próximos Passos
- Corrigir lógica de verificação de versão do Python no módulo de dependências.
- Revisar persistência do histórico para evitar duplicidade.
- Garantir que logs relevantes sejam emitidos e capturados nos testes de sistema completo.
- Aumentar cobertura de testes unitários e integração para todos os módulos.

### Histórico de Evolução
- **21/05/2025**: Corrigidos todos os testes do Guardião Cognitivo. Falhas remanescentes isoladas em dependências e sistema completo.
- **20/05/2025**: Ajustes no monitoramento e início da padronização dos testes de integração.

---
> **Este status será atualizado a cada ciclo de correção relevante. Consulte esta seção para acompanhar a evolução dos testes e priorizar correções.** 