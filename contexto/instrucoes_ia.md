# Instruções para IAs do Sistema AutoCura

## Introdução

Este documento fornece instruções específicas para outras IAs que irão trabalhar no sistema AutoCura. Ele detalha como entender o contexto atual, manter a consistência do desenvolvimento e seguir as diretrizes estabelecidas.

## Verificação Inicial

### 1. Arquivos Essenciais

Ao iniciar o trabalho no sistema, verifique os seguintes arquivos:

- `memoria_compartilhada.json`: Contém o estado atual do sistema
- `docs/sistema_registro_contexto.md`: Explica o sistema de registro de contexto
- `docs/contexto_sistema.md`: Detalha o contexto atual do desenvolvimento
- `config/config.yaml`: Configurações gerais do sistema

### 2. Estado Atual

Verifique o estado atual do sistema:

```python
from core.memoria.registrador_contexto import RegistradorContexto

registrador = RegistradorContexto()
estado = registrador.obter_estado_atual()
instrucoes = registrador.obter_instrucoes_pendentes()
eventos = registrador.obter_eventos_recentes()
```

## Fluxo de Trabalho

### 1. Início de Sessão

1. Carregue o contexto atual
2. Verifique instruções pendentes
3. Analise eventos recentes
4. Consulte a documentação relevante

### 2. Durante o Desenvolvimento

1. Registre todas as interações importantes
2. Mantenha as instruções atualizadas
3. Documente decisões técnicas
4. Siga as diretrizes de código

### 3. Finalização de Tarefas

1. Atualize o estado do sistema
2. Registre instruções para a próxima IA
3. Documente mudanças realizadas
4. Verifique consistência do contexto

## Diretrizes de Desenvolvimento

### 1. Código

- Siga o padrão de código estabelecido
- Mantenha a modularidade
- Documente funções e classes
- Implemente testes unitários

### 2. Documentação

- Atualize a documentação ao fazer mudanças
- Mantenha o histórico de decisões
- Documente APIs e interfaces
- Registre problemas e soluções

### 3. Integração

- Verifique compatibilidade com componentes existentes
- Teste integrações antes de finalizar
- Mantenha o sistema coeso
- Siga o padrão de arquitetura

## Registro de Contexto

### 1. Interações

```python
# Registrar interação com usuário
registrador.registrar_interacao(
    tipo="comando",
    conteudo="comando do usuário",
    resposta="resposta do sistema"
)
```

### 2. Instruções

```python
# Registrar instrução para próxima IA
registrador.registrar_instrucao(
    titulo="Título da instrução",
    descricao="Descrição detalhada",
    prioridade=1  # 1-5, sendo 1 a mais alta
)
```

### 3. Eventos

```python
# Registrar evento do sistema
registrador.registrar_evento(
    tipo="tipo_do_evento",
    descricao="descrição do evento"
)
```

## Manutenção do Contexto

### 1. Atualizações

- Mantenha o contexto atualizado
- Registre mudanças importantes
- Documente decisões técnicas
- Mantenha o histórico organizado

### 2. Verificações

- Verifique consistência do contexto
- Valide instruções pendentes
- Confirme estado do sistema
- Verifique integridade dos dados

## Boas Práticas

### 1. Comunicação

- Seja claro nas instruções
- Documente decisões importantes
- Mantenha o contexto organizado
- Registre problemas e soluções

### 2. Desenvolvimento

- Siga as diretrizes estabelecidas
- Mantenha a consistência do código
- Documente mudanças realizadas
- Teste alterações antes de finalizar

### 3. Integração

- Verifique compatibilidade
- Teste integrações
- Mantenha o sistema coeso
- Siga o padrão de arquitetura

## Troubleshooting

### 1. Problemas de Contexto

Se encontrar problemas com o contexto:

1. Verifique o arquivo `memoria_compartilhada.json`
2. Consulte o histórico de eventos
3. Verifique instruções pendentes
4. Consulte a documentação

### 2. Problemas de Integração

Se encontrar problemas de integração:

1. Verifique compatibilidade de versões
2. Teste componentes individualmente
3. Consulte a documentação de APIs
4. Verifique logs do sistema

## Considerações Finais

1. Mantenha o contexto atualizado
2. Siga as diretrizes estabelecidas
3. Documente mudanças importantes
4. Mantenha a consistência do sistema

## Recursos Adicionais

- `docs/`: Documentação completa do sistema
- `config/`: Arquivos de configuração
- `src/`: Código fonte do sistema
- `tests/`: Testes do sistema 