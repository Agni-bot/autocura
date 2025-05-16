# Guia de Autoaperfeiçoamento

## Visão Geral

O sistema de autoaperfeiçoamento do Autocura Cognitiva é responsável por analisar padrões de anomalias, sugerir automações e implementar melhorias contínuas no sistema. Este guia descreve o funcionamento deste processo e como interagir com ele através do portal.

## Fluxo de Autoaperfeiçoamento

### 1. Detecção de Padrões

O sistema monitora continuamente:
- Frequência de anomalias
- Tipos de anomalias
- Ações executadas
- Resultados das ações

#### Exemplo de Padrão Detectado
```json
{
    "pattern_id": "pat_123",
    "detected_at": "2024-05-02T12:00:00Z",
    "anomalies": [
        {
            "id": "anom_1",
            "type": "cpu_high",
            "timestamp": "2024-05-02T11:00:00Z"
        },
        {
            "id": "anom_2",
            "type": "cpu_high",
            "timestamp": "2024-05-02T11:30:00Z"
        }
    ],
    "frequency": 2,
    "time_window": "1h",
    "confidence": 0.95
}
```

### 2. Geração de Sugestões

Quando um padrão é detectado, o sistema gera sugestões de automação:

#### Estrutura de Sugestão
```json
{
    "id": "sug_123",
    "pattern_id": "pat_123",
    "created_at": "2024-05-02T12:00:00Z",
    "type": "automation",
    "description": "Auto-escalar CPU quando uso > 80%",
    "action": {
        "type": "scale_up",
        "parameters": {
            "resource": "cpu",
            "amount": 2
        }
    },
    "confidence": 0.95,
    "status": "pending"
}
```

### 3. Aprovação e Implementação

1. **Revisão da Sugestão**
   - Analisar histórico de anomalias
   - Verificar impacto potencial
   - Avaliar confiança da sugestão

2. **Aprovação/Rejeição**
   - Aprovar para criar regra de automação
   - Rejeitar para ignorar sugestão
   - Modificar parâmetros antes de aprovar

3. **Implementação**
   - Criação de regra de automação
   - Configuração de notificações
   - Ativação do monitoramento

### 4. Monitoramento e Ajuste

#### Métricas de Acompanhamento
```python
# Exemplo de métricas
automation_suggestions_total = Counter(
    'autocura_automation_suggestions_total',
    'Total de sugestões de automação'
)

automation_success_rate = Gauge(
    'autocura_automation_success_rate',
    'Taxa de sucesso das automações'
)

automation_execution_time = Histogram(
    'autocura_automation_execution_seconds',
    'Tempo de execução das automações'
)
```

## Interface do Portal

### 1. Sugestões

#### Listagem
- Filtros por status, tipo, confiança
- Ordenação por data, confiança
- Visualização de detalhes

#### Ações
- Aprovar sugestão
- Rejeitar sugestão
- Modificar parâmetros
- Ver histórico

### 2. Regras de Automação

#### Gerenciamento
- Listar regras ativas
- Ativar/desativar regras
- Editar parâmetros
- Visualizar histórico

#### Monitoramento
- Taxa de sucesso
- Tempo de execução
- Impacto no sistema
- Alertas e notificações

## Exemplos de Uso

### 1. Aprovar Sugestão de Automação

```python
# Exemplo de código para aprovar sugestão
def approve_suggestion(suggestion_id: str, parameters: dict = None):
    """
    Aprova uma sugestão de automação.
    
    Args:
        suggestion_id: ID da sugestão
        parameters: Parâmetros opcionais para modificar
    """
    # Buscar sugestão
    suggestion = get_suggestion(suggestion_id)
    
    # Validar sugestão
    if not suggestion or suggestion.status != 'pending':
        raise ValueError('Sugestão inválida ou já processada')
    
    # Criar regra de automação
    rule = create_automation_rule(
        name=f"Auto-{suggestion.type}",
        condition=suggestion.pattern,
        action=suggestion.action,
        parameters=parameters or suggestion.action.parameters
    )
    
    # Atualizar status da sugestão
    update_suggestion_status(suggestion_id, 'approved', rule.id)
    
    return rule
```

### 2. Monitorar Efetividade

```python
# Exemplo de código para monitorar efetividade
def monitor_automation_effectiveness(rule_id: str):
    """
    Monitora a efetividade de uma regra de automação.
    
    Args:
        rule_id: ID da regra
    """
    # Coletar métricas
    executions = get_rule_executions(rule_id)
    success_rate = calculate_success_rate(executions)
    avg_time = calculate_average_time(executions)
    
    # Atualizar métricas
    automation_success_rate.labels(rule_id=rule_id).set(success_rate)
    automation_execution_time.labels(rule_id=rule_id).observe(avg_time)
    
    # Gerar relatório
    return {
        'rule_id': rule_id,
        'success_rate': success_rate,
        'avg_execution_time': avg_time,
        'total_executions': len(executions)
    }
```

## Troubleshooting

### 1. Problemas Comuns

1. **Sugestões não são geradas**
   - Verificar coleta de anomalias
   - Verificar thresholds de detecção
   - Verificar processamento de padrões

2. **Automações não são efetivas**
   - Verificar parâmetros da regra
   - Analisar histórico de execuções
   - Ajustar thresholds

3. **Falsos positivos**
   - Ajustar sensibilidade da detecção
   - Revisar padrões de anomalia
   - Implementar filtros adicionais

### 2. Procedimentos de Resolução

1. **Investigação**
   - Coletar logs e métricas
   - Analisar padrões de falha
   - Identificar causa raiz

2. **Ajuste**
   - Modificar parâmetros
   - Atualizar regras
   - Implementar correções

3. **Validação**
   - Monitorar resultados
   - Verificar efetividade
   - Documentar mudanças

## Próximos Passos

1. Implementar mais tipos de padrões
2. Melhorar algoritmos de detecção
3. Expandir tipos de automação
4. Adicionar mais métricas
5. Otimizar performance 