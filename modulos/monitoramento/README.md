# Módulo de Monitoramento de Recursos

## Visão Geral

O módulo de monitoramento de recursos é responsável por coletar métricas detalhadas do sistema, calcular a equidade na distribuição de recursos e realizar ajustes automáticos quando necessário. Ele integra-se com a memória compartilhada do sistema e mantém logs estruturados para auditoria.

## Funcionalidades

### 1. Coleta de Métricas

- **CPU**
  - Uso total
  - Uso por core
  - Frequência atual
  - Limites configuráveis

- **Memória**
  - Uso total
  - Memória disponível
  - Uso de swap
  - Limites configuráveis

- **Disco**
  - Espaço total
  - Espaço usado
  - Espaço livre
  - Limites configuráveis

### 2. Cálculo de Equidade

- Distribuição de recursos entre processos
- Índice de equidade (0-1)
- Ajuste automático para manter equidade

### 3. Ajuste Automático

- **CPU**
  - Ajuste de prioridades de processos
  - Redução de carga em cores sobrecarregados

- **Memória**
  - Gerenciamento de swap
  - Liberação de cache
  - Ajuste de mapeamento de memória

- **Disco**
  - Limpeza de arquivos temporários
  - Gerenciamento de espaço livre

### 4. Integração

- Memória compartilhada
- Logs estruturados
- Histórico de métricas
- Alertas e notificações

## Configuração

O módulo é configurado através do arquivo `src/monitoramento/config.py`:

```python
CONFIG = {
    'intervalo_monitoramento': 30,  # segundos
    'intervalo_ajuste': 60,  # segundos
    
    'limites': {
        'cpu': {
            'total': 80,  # percentual
            'por_core': 90,  # percentual
            'frequencia_minima': 1000  # MHz
        },
        'memoria': {
            'percentual': 85,
            'swap_percentual': 80
        },
        'disco': {
            'percentual': 90,
            'espaco_livre_minimo': 1024 * 1024 * 1024  # 1GB
        },
        'equidade': 0.85
    }
}
```

## Uso

### Inicialização

```python
from src.monitoramento.recursos import MonitorRecursos

# Cria instância do monitor
monitor = MonitorRecursos()

# Inicia monitoramento
await monitor.iniciar_monitoramento()
```

### Métricas

```python
# Coleta métricas atuais
metricas = monitor.coletar_metricas()

# Acessa métricas específicas
cpu_total = metricas['cpu']['total']
memoria_percentual = metricas['memoria']['percentual']
disco_livre = metricas['disco']['livre']
equidade = metricas['equidade']
```

### Ajuste Manual

```python
# Ajusta recursos manualmente
await monitor.ajustar_recursos(metricas)
```

## Logs

Os logs são estruturados e incluem:

- Timestamp
- Nível (INFO, WARNING, ERROR)
- Métricas relevantes
- Ações tomadas
- Erros e exceções

Exemplo:
```
2024-07-01 10:00:00,123 - INFO - Métricas registradas - cpu: 45.2%, memoria: 60.1%, disco: 75.3%, equidade: 0.92
2024-07-01 10:00:30,456 - WARNING - Alerta: Métricas fora do limite - cpu: 85.5%, memoria: 88.2%, disco: 92.1%, equidade: 0.45
2024-07-01 10:00:30,789 - INFO - Iniciando ajuste de recursos
2024-07-01 10:00:31,123 - INFO - Ajuste de recursos concluído
```

## Testes

O módulo inclui testes automatizados em `tests/test_monitoramento.py`:

- Coleta de métricas
- Cálculo de equidade
- Verificação de limites
- Ajuste de recursos
- Monitoramento contínuo

## Integração com Memória Compartilhada

O módulo atualiza a memória compartilhada com:

- Última atualização
- Métricas atuais
- Histórico de ajustes
- Configurações ativas

## Próximos Passos

1. Implementar dashboard de monitoramento
2. Adicionar alertas por email/Slack
3. Integrar com ferramentas de APM
4. Implementar previsão de recursos
5. Adicionar suporte a containers 