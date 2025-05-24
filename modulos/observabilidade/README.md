# Módulo de Observabilidade

## Atualizações Recentes

- **Dependências**: Atualizadas para versões mais recentes, garantindo compatibilidade entre pacotes.
- **Estrutura de Pacotes**: Adicionados arquivos `__init__.py` em todos os diretórios necessários para reconhecimento como pacotes Python.
- **Imports**: Ajustados para formato absoluto nos testes, garantindo execução correta.
- **Testes**: 
  - Testes de coletores passaram com sucesso.
  - Testes de storage apresentam falhas devido à ausência do serviço Redis e duplicidade de métricas no Prometheus.
  - Recomenda-se iniciar o Redis localmente e isolar o registro do Prometheus entre testes.

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