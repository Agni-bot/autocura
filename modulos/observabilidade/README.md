# Módulo de Observabilidade

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