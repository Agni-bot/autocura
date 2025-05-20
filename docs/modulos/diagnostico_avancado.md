# Módulo de Diagnóstico Avançado

## Visão Geral

O módulo de Diagnóstico Avançado é responsável por realizar análises preditivas e correlações de eventos no sistema, utilizando técnicas de machine learning e análise estatística para identificar padrões, anomalias e tendências.

## Funcionalidades Principais

### 1. Detecção de Anomalias
- Utiliza o algoritmo Isolation Forest para identificar comportamentos anômalos
- Analisa múltiplas métricas do sistema simultaneamente
- Adapta-se dinamicamente aos padrões do sistema

### 2. Análise de Correlação
- Identifica relações entre diferentes métricas do sistema
- Calcula lags temporais entre eventos correlacionados
- Ajuda a entender cadeias causais de problemas

### 3. Predição de Métricas
- Realiza previsões de valores futuros para métricas importantes
- Calcula níveis de confiança para as predições
- Identifica tendências de crescimento ou degradação

## Métricas Monitoradas

### Sistema
- CPU (percentual de uso, carga)
- Memória (percentual de uso, memória utilizada)
- Disco (percentual de uso, I/O)
- Rede (bytes, pacotes)

### Aplicação
- Latência
- Taxa de erros
- Número de requisições

## Configuração

O módulo é configurado através do arquivo `config/diagnostico_avancado.json`:

```json
{
    "configuracoes": {
        "intervalo_analise": 300,
        "janela_historico": 86400,
        "min_amostras": 100,
        "threshold_anomalia": 0.95
    },
    "metricas": {
        "cpu": ["percent", "load"],
        "memoria": ["percent", "used"],
        "disco": ["percent", "io"],
        "rede": ["bytes", "packets"],
        "aplicacao": ["latencia", "erros", "requisicoes"]
    },
    "correlacao": {
        "min_correlacao": 0.7,
        "max_lag": 300,
        "janela_analise": 3600
    },
    "predicao": {
        "horizonte": 3600,
        "intervalo_predicao": 300,
        "min_confianca": 0.8
    }
}
```

## Uso

```python
from src.core.diagnostico_avancado import DiagnosticoAvancado
from src.memoria.gerenciador_memoria import GerenciadorMemoria
from src.core.logger import Logger
from src.core.cache import Cache

# Inicializa dependências
gerenciador_memoria = GerenciadorMemoria()
logger = Logger()
cache = Cache()

# Cria instância do diagnóstico
diagnostico = DiagnosticoAvancado(
    gerenciador_memoria,
    logger,
    cache
)

# Inicia o sistema
diagnostico.iniciar()

# Obtém resultados
resultados = diagnostico.obter_resultados()

# Para o sistema
diagnostico.parar()
```

## Resultados

O módulo gera dois tipos principais de resultados:

### 1. Correlações
```json
{
    "cpu-memoria": {
        "correlacao": 0.8,
        "lag": 0
    }
}
```

### 2. Predições
```json
{
    "cpu": {
        "valores": [50, 55, 60],
        "confianca": 0.9,
        "tendencia": 0.1
    }
}
```

## Integração

O módulo se integra com:

- Sistema de Cache para armazenamento de métricas
- Sistema de Logging para registro de eventos
- Gerenciador de Memória para persistência de dados
- Sistema de Notificações para alertas

## Testes

Os testes unitários estão disponíveis em `tests/test_diagnostico_avancado.py` e cobrem:

- Inicialização e configuração
- Coleta de dados históricos
- Extração de features
- Cálculo de correlações
- Predição de valores
- Registro de resultados

## Dependências

- numpy >= 1.21.0
- scikit-learn >= 1.0.0
- pandas >= 1.3.0

## Contribuição

Para contribuir com o módulo:

1. Siga as convenções de código do projeto
2. Adicione testes para novas funcionalidades
3. Atualize a documentação
4. Verifique a cobertura de testes
5. Submeta um pull request

## Próximos Passos

1. Implementar mais algoritmos de detecção de anomalias
2. Adicionar suporte a séries temporais
3. Melhorar a precisão das predições
4. Otimizar o processamento de dados
5. Expandir as métricas monitoradas 