# Módulo de Observabilidade

## Visão Geral

O módulo de observabilidade fornece funcionalidades para coleta de métricas, armazenamento híbrido e auditoria ética do sistema. Ele inclui:

- Coleta de métricas do sistema, aplicação e componentes quânticos
- Armazenamento híbrido usando Redis e Prometheus
- Auditoria ética com métricas e alertas
- Visualização via Grafana

## Componentes

### Collectors

- `SystemCollector`: Coleta métricas do sistema operacional
- `ApplicationCollector`: Coleta métricas da aplicação
- `QuantumCollector`: Coleta métricas dos componentes quânticos

### Storage

- `HybridStorage`: Utiliza Redis para armazenamento temporário e Prometheus para métricas de longo prazo
  - Redis: Armazena métricas recentes e dados de alta frequência
  - Prometheus: Armazena métricas históricas e gera alertas

### Auditoria Ética

- `EthicalAuditor`: Monitora e valida decisões do sistema
  - Calcula score ético baseado em múltiplos fatores
  - Analisa transparência, justiça, privacidade e segurança
  - Gera recomendações baseadas na análise
  - Mantém histórico de decisões
  - Expõe métricas via Prometheus
  - Gera alertas baseados em thresholds

## Configuração

### Redis

```yaml
redis:
  host: localhost
  port: 6379
  db: 0
```

### Prometheus

```yaml
prometheus:
  host: localhost
  port: 9090
  scrape_interval: 15s
```

### Auditor Ético

```yaml
ethical_auditor:
  ethical_threshold: 0.8
  monitoring_interval: 300
  alert_threshold: 0.6
  max_decisions_history: 1000
  prometheus_port: 8000
```

## Uso

### Coleta de Métricas

```python
from modulos.observabilidade.collectors import SystemCollector, ApplicationCollector

# Coleta métricas do sistema
system_metrics = SystemCollector().collect()

# Coleta métricas da aplicação
app_metrics = ApplicationCollector().collect()
```

### Armazenamento

```python
from modulos.observabilidade.storage import HybridStorage

storage = HybridStorage()

# Armazena métricas
storage.store_metrics(system_metrics)
storage.store_metrics(app_metrics)

# Recupera métricas
metrics = storage.get_metrics(start_time="2024-03-19T00:00:00")
```

### Auditoria Ética

```python
from modulos.observabilidade.auditoria import EthicalAuditor

auditor = EthicalAuditor()

# Audita uma decisão
decision = auditor.audit_decision(
    decision_type="classificação",
    context={
        "reasoning": "Análise de padrões",
        "alternatives": ["A", "B", "C"],
        "stakeholders": ["usuários", "sistema"]
    },
    impact_analysis={
        "bias_analysis": {"bias_score": 0.1},
        "risk_assessment": {"risk_score": 0.2}
    }
)

# Recupera histórico
history = auditor.get_decisions_history(
    start_time="2024-03-19T00:00:00"
)
```

## Métricas Prometheus

O módulo expõe as seguintes métricas via Prometheus:

- `ethical_score`: Score ético atual (0-1)
- `transparency_score`: Score de transparência (0-1)
- `fairness_score`: Score de justiça (0-1)
- `privacy_score`: Score de privacidade (0-1)
- `safety_score`: Score de segurança (0-1)
- `ethical_decisions_total`: Total de decisões éticas
- `ethical_alerts_total`: Total de alertas éticos

## Alertas

O sistema gera alertas quando:

- Score ético fica abaixo de 0.6 por 5 minutos
- Taxa de alertas éticos está acima do normal
- Scores individuais (transparência, justiça, privacidade, segurança) ficam abaixo de 0.5 por 5 minutos

## Visualização

O dashboard Grafana "Ética" fornece visualizações para:

- Score ético ao longo do tempo
- Fatores de avaliação ética
- Taxa de decisões éticas
- Taxa de alertas éticos

## Atualizações Recentes

- Implementação de métricas Prometheus para auditoria ética
- Configuração de alertas baseados em thresholds
- Dashboard Grafana para visualização de métricas éticas
- Correção no tratamento de timestamps
- Isolamento de métricas Prometheus
- Redis operacional via Docker
- Testes automatizados passando

## Próximos Passos

- Integração com sistema de logs
- Expansão dos critérios de avaliação ética
- Documentação de casos de uso
- Implementação de dashboards adicionais
- Integração com sistemas de notificação

## Troubleshooting

### Timestamps

Se encontrar erros com timestamps, verifique se:
- O formato está em ISO 8601
- A conversão para float está correta
- O timezone está configurado adequadamente

### Redis

Se o Redis não estiver respondendo:
- Verifique se o container está rodando
- Confirme as credenciais de acesso
- Verifique a conexão na porta correta

### Prometheus

Se as métricas não estiverem aparecendo:
- Verifique se o servidor está rodando
- Confirme a configuração de scrape
- Verifique os logs do Prometheus

### Auditoria Ética

Se os scores estiverem inconsistentes:
- Verifique os thresholds configurados
- Confirme os pesos dos fatores
- Analise o contexto e impacto das decisões

## Atualização - Progresso de Maio/2025

- Redis operacional via Docker (`redis-test`)
- Correção do tratamento de timestamps ISO no método `get_metrics` (`HybridStorage`)
- Isolamento de métricas Prometheus por instância, evitando duplicidade em testes
- Inclusão do método `clear_metrics()` para reset de métricas entre execuções
- Todos os testes automatizados do módulo de observabilidade passaram com sucesso (`pytest`)

### Troubleshooting
- Se ocorrer erro de conversão de timestamp, garantir que o campo `timestamp` está em formato ISO e usar `datetime.fromisoformat()` para conversão.
- Recomenda-se sempre limpar as métricas Prometheus entre execuções de teste usando `clear_metrics()`.

### Próximos passos sugeridos
- Automatizar limpeza do Redis entre execuções de testes (fixture)
- Documentar exemplos de integração com Prometheus externo

## Requisitos de Ambiente

- Redis ativo em `localhost:6379` para testes integrais.
- Prometheus configurado para evitar duplicidade de métricas.

## Próximos Passos

- Iniciar o serviço Redis localmente.
- Ajustar os testes do Prometheus para isolar o registro global.
- Atualizar a documentação conforme evolução do projeto.

## Descrição
Módulo responsável pela coleta, processamento e análise de métricas, logs e traces do sistema para garantir visibilidade e monitoramento efetivo.

## Estrutura
```
observabilidade/
├── src/                    # Código fonte
│   ├── metricas/          # Coleta de métricas
│   ├── logs/              # Processamento de logs
│   ├── traces/            # Rastreamento distribuído
│   └── api/               # API de observabilidade
├── tests/                 # Testes
├── config/               # Configurações
├── docker/              # Dockerfiles
├── README.md           # Documentação
└── __init__.py         # Inicialização
```

## Funcionalidades

### Métricas
- Coleta de métricas do sistema
- Agregação de dados
- Alertas e thresholds

### Logs
- Coleta de logs
- Processamento e indexação
- Busca e análise

### Traces
- Rastreamento distribuído
- Análise de performance
- Mapeamento de dependências

### API
- Endpoints de métricas
- Endpoints de logs
- Endpoints de traces

## Configuração

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Execute os testes:
```bash
pytest tests/
```

## Uso

```python
from observabilidade import Observabilidade

# Inicializa o sistema de observabilidade
obs = Observabilidade()

# Coleta métricas
metricas = obs.coletar_metricas()

# Processa logs
logs = obs.processar_logs()

# Rastreia operações
trace = obs.iniciar_trace("operacao")
# ... executa operação ...
obs.finalizar_trace(trace)
```

## Contribuição

1. Siga a estrutura modular
2. Adicione testes
3. Atualize a documentação
4. Envie um pull request

## Licença

Este módulo está sob a licença MIT. 