# Sistema de Registro Automático de Contexto

## Visão Geral

O Sistema de Registro Automático de Contexto é um componente essencial do AutoCura que mantém um registro detalhado de todas as interações, instruções e eventos do sistema. Este sistema garante que o contexto seja preservado entre diferentes sessões e que outras IAs possam entender facilmente o estado atual do desenvolvimento.

## Componentes Principais

### 1. RegistradorContexto

Localizado em `src/core/memoria/registrador_contexto.py`, este é o componente principal que gerencia o registro automático de contexto. Ele oferece as seguintes funcionalidades:

- Registro de interações
- Registro de instruções para outras IAs
- Registro de eventos do sistema
- Gerenciamento de instruções pendentes
- Exportação de contexto

### 2. GerenciadorMemoria

Localizado em `src/core/memoria/gerenciador_memoria.py`, este componente trabalha em conjunto com o RegistradorContexto para manter o estado do sistema atualizado.

## Como Funciona

### Registro Automático

O sistema registra automaticamente:

1. **Interações**: Todas as interações entre o usuário e o sistema
2. **Instruções**: Comandos e diretrizes para outras IAs
3. **Eventos**: Ações e mudanças de estado do sistema
4. **Erros**: Falhas e exceções que ocorrem

### Estrutura do Contexto

O contexto é armazenado em `memoria_compartilhada.json` com a seguinte estrutura:

```json
{
    "ultima_atualizacao": "timestamp",
    "estado_atual": {
        "configuracoes": {},
        "estrutura_diretorios": {},
        "acoes_recentes": [],
        "contexto_atual": {
            "tarefa": "string",
            "status": "string",
            "proximos_passos": []
        }
    },
    "historico_interacoes": [],
    "instrucoes_pendentes": [],
    "eventos_recentes": []
}
```

## Uso no Sistema

### Inicialização

O sistema é inicializado automaticamente no `main.py`:

```python
self.registrador = RegistradorContexto()
```

### Registro de Eventos

Eventos são registrados automaticamente em pontos críticos do sistema:

```python
self.registrador.registrar_evento(
    "tipo_evento",
    "descricao_do_evento"
)
```

### Instruções para Outras IAs

Instruções são registradas para guiar outras IAs:

```python
self.registrador.registrar_instrucao(
    "titulo",
    "descricao",
    prioridade=1
)
```

## Verificação de Contexto

### Via Código

```python
# Obter estado atual
estado = self.registrador.obter_estado_atual()

# Verificar instruções pendentes
instrucoes = self.registrador.obter_instrucoes_pendentes()

# Verificar eventos recentes
eventos = self.registrador.obter_eventos_recentes()
```

### Via Arquivo

O arquivo `memoria_compartilhada.json` pode ser consultado diretamente para verificar o contexto atual.

## Boas Práticas

1. **Registro Consistente**: Sempre registre eventos importantes
2. **Instruções Claras**: Forneça instruções detalhadas para outras IAs
3. **Priorização**: Use o sistema de prioridades para instruções
4. **Verificação Regular**: Consulte o contexto antes de iniciar novas tarefas

## Integração com Outras IAs

Para que outras IAs possam entender o contexto:

1. Compartilhe o arquivo `memoria_compartilhada.json`
2. Forneça acesso à documentação do sistema
3. Mantenha as instruções atualizadas
4. Registre todas as decisões importantes

## Manutenção

### Limpeza de Histórico

```python
# Limpar histórico antigo
self.registrador.limpar_historico()
```

### Exportação de Contexto

```python
# Exportar contexto para arquivo
self.registrador.exportar_contexto("caminho/arquivo.json")
```

## Considerações Importantes

1. O sistema mantém um registro completo de todas as interações
2. As instruções são priorizadas para guiar outras IAs
3. O contexto é atualizado automaticamente
4. O histórico é mantido para referência futura

## Troubleshooting

### Problemas Comuns

1. **Arquivo de Memória Corrompido**
   - Solução: O sistema criará um novo arquivo automaticamente

2. **Instruções Desatualizadas**
   - Solução: Marque como concluídas e registre novas instruções

3. **Contexto Inconsistente**
   - Solução: Verifique o histórico de eventos e atualize o contexto

## Próximos Passos

1. Implementar sistema de backup do contexto
2. Adicionar suporte para múltiplos formatos de exportação
3. Desenvolver interface visual para consulta do contexto
4. Implementar sistema de notificações para mudanças importantes 