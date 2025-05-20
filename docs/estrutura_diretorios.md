# Estrutura de Diretórios do Sistema Autocura

## Visão Geral

```
autocura/
├── config/                 # Configurações do sistema
├── docs/                   # Documentação
├── grafana/               # Configurações do Grafana
├── kubernetes/            # Manifestos Kubernetes
├── logs/                  # Logs do sistema
├── memoria/              # Armazenamento persistente
├── prometheus/           # Configurações do Prometheus
├── scripts/              # Scripts utilitários
├── src/                  # Código fonte
│   ├── core/             # Núcleo do sistema
│   ├── etica/            # Módulo de validação ética
│   ├── gerador/          # Gerador de ações
│   ├── guardiao/         # Guardião cognitivo
│   ├── kubernetes/       # Orquestração Kubernetes
│   ├── memoria/          # Gerenciamento de memória
│   ├── monitoramento/    # Monitoramento do sistema
│   ├── observabilidade/  # Observabilidade 4D
│   └── portal/           # Interface web
├── tests/                # Testes automatizados
└── verificar/            # Scripts de verificação
```

## Descrição dos Diretórios

### `/config`
Contém arquivos de configuração do sistema:
- `config.yaml`: Configurações globais
- `logging.yaml`: Configurações de logging
- `security.yaml`: Configurações de segurança

### `/docs`
Documentação do sistema:
- Arquitetura
- Guias de uso
- Documentação técnica
- Manuais de operação

### `/grafana`
Configurações do Grafana:
- Dashboards
- Datasources
- Provisioning

### `/kubernetes`
Manifestos Kubernetes:
- Deployments
- Services
- ConfigMaps
- PersistentVolumeClaims

### `/logs`
Armazenamento de logs:
- Logs de aplicação
- Logs de sistema
- Logs de auditoria

### `/memoria`
Armazenamento persistente:
- Banco de dados SQLite
- Cache
- Backups

### `/prometheus`
Configurações do Prometheus:
- Rules
- Alerts
- Scrape configs

### `/scripts`
Scripts utilitários:
- Deploy
- Backup
- Manutenção
- Monitoramento

### `/src`
Código fonte do sistema:

#### `/src/core`
Núcleo do sistema:
- Configurações base
- Utilitários comuns
- Interfaces base

#### `/src/etica`
Módulo de validação ética:
- Validação de decisões
- Políticas éticas
- Relatórios de conformidade

#### `/src/gerador`
Gerador de ações:
- Geração de planos
- Priorização
- Execução

#### `/src/guardiao`
Guardião cognitivo:
- Monitoramento de saúde
- Protocolos de emergência
- Salvaguardas

#### `/src/kubernetes`
Orquestração Kubernetes:
- Gerenciamento de cluster
- Auto-scaling
- Auto-healing

#### `/src/memoria`
Gerenciamento de memória:
- Armazenamento
- Recuperação
- Cache

#### `/src/monitoramento`
Monitoramento do sistema:
- Coleta de métricas
- Detecção de anomalias
- Alertas

#### `/src/observabilidade`
Observabilidade 4D:
- Dashboard
- Visualização
- Projeções

#### `/src/portal`
Interface web:
- API REST
- Interface gráfica
- Documentação interativa

### `/tests`
Testes automatizados:
- Testes unitários
- Testes de integração
- Testes de sistema

### `/verificar`
Scripts de verificação:
- Validação de configuração
- Verificação de saúde
- Diagnóstico

## Convenções de Nomenclatura

- Diretórios: snake_case
- Arquivos Python: snake_case
- Classes: PascalCase
- Funções/Métodos: snake_case
- Variáveis: snake_case
- Constantes: UPPER_SNAKE_CASE 