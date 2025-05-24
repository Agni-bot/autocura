# Verificação Inicial do Sistema AutoCura

## Instruções para IAs

Ao iniciar uma nova sessão de chat, a IA deve seguir estas etapas para entender o contexto atual do sistema:

### 1. Verificar Arquivos Essenciais

```python
# Código para verificar o contexto
from core.memoria.registrador_contexto import RegistradorContexto

# Inicializar registrador
registrador = RegistradorContexto()

# Verificar estado atual
estado = registrador.obter_estado_atual()
print("Estado atual:", estado)

# Verificar instruções pendentes
instrucoes = registrador.obter_instrucoes_pendentes()
print("Instruções pendentes:", instrucoes)

# Verificar eventos recentes
eventos = registrador.obter_eventos_recentes()
print("Eventos recentes:", eventos)
```

### 2. Arquivos a Verificar

1. `contexto/memoria_compartilhada.json`
   - Estado atual do sistema
   - Histórico de interações
   - Instruções pendentes

2. `contexto/contexto_sistema.md`
   - Fase atual de desenvolvimento
   - Componentes implementados
   - Próximos passos

3. `contexto/sistema_registro_contexto.md`
   - Funcionamento do sistema de registro
   - Estrutura do contexto
   - Boas práticas

4. `contexto/instrucoes_ia.md`
   - Diretrizes para desenvolvimento
   - Fluxo de trabalho
   - Padrões a seguir

### 3. Checklist de Verificação

- [ ] Carregar e analisar `memoria_compartilhada.json`
- [ ] Verificar fase atual de desenvolvimento
- [ ] Identificar instruções pendentes
- [ ] Analisar eventos recentes
- [ ] Entender próximos passos
- [ ] Verificar documentação relevante

### 4. Resposta Inicial

Após a verificação, a IA deve:

1. Confirmar que analisou o contexto
2. Resumir o estado atual do sistema
3. Identificar instruções pendentes
4. Propor próximos passos

### 5. Exemplo de Resposta

```
Analisei o contexto do sistema AutoCura:

Estado Atual:
- Fase: ALPHA
- Versão: 0.1.0
- Status: Em desenvolvimento inicial

Instruções Pendentes:
1. [Prioridade 1] Verificar estado de inicialização
2. [Prioridade 2] Monitorar execução do sistema

Próximos Passos:
1. Implementar sistema de testes
2. Completar documentação
3. Implementar sistema de backup

Como posso ajudar no desenvolvimento do sistema?
```

## Manutenção do Contexto

### 1. Durante a Sessão

- Registrar todas as interações importantes
- Atualizar instruções pendentes
- Documentar decisões técnicas
- Manter histórico de eventos

### 2. Ao Finalizar

- Atualizar estado do sistema
- Registrar instruções para próxima IA
- Documentar mudanças realizadas
- Verificar consistência do contexto

## Troubleshooting

Se encontrar problemas ao verificar o contexto:

1. Verificar se os arquivos existem
2. Tentar recriar arquivos corrompidos
3. Consultar documentação
4. Registrar problema no log de eventos 