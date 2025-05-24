# 📦 Guia de Migração do Sistema AutoCura

Este documento descreve o processo detalhado de migração para a nova estrutura modular do Sistema AutoCura, garantindo uma transição suave e segura.

## 🏗️ 1. Estrutura de Módulos

### 1.1 Módulo Ético-Operacional

A estrutura do módulo ético foi reorganizada em submodules para melhor separação de responsabilidades:

```
etica/
├── circuitos-morais/     # Pilares éticos e validações
│   ├── validadores/      # Validadores de regras éticas
│   ├── regras/          # Definições de regras
│   └── testes/          # Testes de conformidade
├── decisao-hibrida/      # Sistema de decisão híbrida
│   ├── algoritmos/      # Algoritmos de decisão
│   ├── interface/       # Interface humana
│   └── integracao/      # Integração com outros módulos
├── auditoria/            # Sistema de auditoria
│   ├── coletores/       # Coletores de eventos
│   ├── analisadores/    # Análise de conformidade
│   └── relatorios/      # Geração de relatórios
├── governanca/           # Governança adaptativa
│   ├── politicas/       # Políticas de governança
│   ├── simulacoes/      # Simulações de impacto
│   └── dashboard/       # Interface de monitoramento
├── fluxo-autonomia/      # Controle de autonomia
│   ├── niveis/          # Definição de níveis
│   ├── transicoes/      # Controle de transições
│   └── monitoramento/   # Monitoramento de autonomia
├── validadores-eticos/   # Validadores éticos
│   ├── regras/          # Regras de validação
│   ├── testes/          # Testes de validação
│   └── relatorios/      # Relatórios de validação
├── priorizacao-financeira/ # Priorização financeira
│   ├── algoritmos/      # Algoritmos de priorização
│   ├── metricas/        # Métricas de impacto
│   └── dashboard/       # Interface de monitoramento
└── registro-decisoes/    # Registro de decisões
    ├── blockchain/      # Integração com blockchain
    ├── storage/         # Armazenamento de decisões
    └── api/            # APIs de acesso
```

#### Migração de Código Existente

1. **Validadores Éticos**
   - Mover código de validação para `validadores-eticos/`
   - Atualizar imports e dependências
   - Adicionar novos testes

2. **Auditoria**
   - Mover código de auditoria para `auditoria/`
   - Configurar novos coletores
   - Atualizar formatos de relatório

3. **Governança**
   - Mover código de governança para `governanca/`
   - Atualizar políticas
   - Configurar novos dashboards

4. **Registro**
   - Mover código de registro para `registro-decisoes/`
   - Configurar blockchain
   - Atualizar APIs

### 1.2 Módulo de Monitoramento

O módulo de monitoramento foi consolidado com observabilidade:

```
monitoramento/
├── coletores/           # Coletores de métricas
│   ├── prometheus/     # Métricas do Prometheus
│   ├── logs/          # Coleta de logs
│   └── eventos/       # Eventos do sistema
├── processadores/       # Processamento de dados
│   ├── agregadores/   # Agregação de métricas
│   ├── correlacionadores/ # Correlação de eventos
│   └── alertas/       # Geração de alertas
├── storage/            # Armazenamento
│   ├── timeseries/    # Séries temporais
│   ├── logs/          # Armazenamento de logs
│   └── eventos/       # Eventos processados
└── api/                # APIs de acesso
    ├── rest/          # APIs REST
    ├── graphql/       # APIs GraphQL
    └── websocket/     # WebSockets
```

#### Migração de Código Existente

1. **Coletores**
   - Mover coletores para `coletores/`
   - Configurar novos formatos
   - Atualizar endpoints

2. **Processadores**
   - Mover processadores para `processadores/`
   - Atualizar algoritmos
   - Configurar novos alertas

3. **Storage**
   - Mover storage para `storage/`
   - Configurar novos formatos
   - Migrar dados existentes

4. **APIs**
   - Mover APIs para `api/`
   - Atualizar documentação
   - Configurar novos endpoints

## 📦 2. Atualização de Dependências

### 2.1 Requirements

Atualizar arquivos de dependências:

```bash
# Atualizar dependências principais
pip install -r requirements.txt

# Atualizar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Atualizar dependências de teste
pip install -r requirements-test.txt

# Atualizar dependências de documentação
pip install -r requirements-docs.txt
```

### 2.2 Docker

Atualizar configurações Docker:

```bash
# Reconstruir imagens
./scripts/build-images.sh

# Atualizar containers
docker-compose up -d

# Verificar logs
docker-compose logs -f
```

## 🧪 3. Testes

### 3.1 Atualização de Testes

1. **Testes Unitários**
   - Mover testes para nova estrutura
   - Atualizar imports
   - Adicionar novos casos de teste

2. **Testes de Integração**
   - Criar novos testes de integração
   - Configurar ambiente de teste
   - Adicionar mocks necessários

```bash
# Executar testes unitários
pytest tests/unit

# Executar testes de integração
pytest tests/integration

# Gerar relatório de cobertura
pytest --cov=modulos --cov-report=html
```

### 3.2 Testes de Integração

Exemplo de teste de integração:

```python
# tests/integration/test_etica_monitoramento.py
import pytest
from modulos.etica import CircuitosMorais
from modulos.monitoramento import SistemaMonitoramento

async def test_etica_monitoramento():
    # Configurar ambiente
    circuitos = CircuitosMorais()
    monitor = SistemaMonitoramento()
    
    # Testar integração
    resultado = await circuitos.validar_acao({
        "tipo": "operacao_critica",
        "parametros": {...}
    })
    
    # Verificar monitoramento
    eventos = await monitor.buscar_eventos(
        tipo="validacao_etica",
        periodo="ultima_hora"
    )
    
    assert len(eventos) > 0
    assert eventos[0].status == "aprovado"
```

## 📚 4. Documentação

### 4.1 Atualização de Documentação

1. **READMEs**
   - Atualizar READMEs dos módulos
   - Adicionar novos exemplos
   - Atualizar diagramas

2. **APIs**
   - Atualizar documentação OpenAPI
   - Adicionar novos endpoints
   - Atualizar exemplos

3. **Guias**
   - Atualizar guias de desenvolvimento
   - Adicionar novos tutoriais
   - Atualizar troubleshooting

### 4.2 Novos Documentos

1. **Arquitetura**
   - Criar novos diagramas
   - Atualizar documentação técnica
   - Adicionar novos fluxos

2. **Contribuição**
   - Atualizar guias de contribuição
   - Adicionar novos templates
   - Atualizar processos

## ✅ 5. Checklist de Migração

### 5.1 Preparação
- [ ] Backup do código atual
- [ ] Backup dos dados
- [ ] Criação de branch de migração
- [ ] Configuração de ambiente de teste

### 5.2 Implementação
- [ ] Atualizar estrutura de diretórios
- [ ] Migrar código existente
- [ ] Atualizar dependências
- [ ] Atualizar Docker
- [ ] Atualizar testes
- [ ] Atualizar documentação

### 5.3 Validação
- [ ] Executar testes unitários
- [ ] Executar testes de integração
- [ ] Validar em ambiente de desenvolvimento
- [ ] Testar em ambiente de staging
- [ ] Fazer deploy em produção

### 5.4 Monitoramento
- [ ] Configurar novos dashboards
- [ ] Configurar novos alertas
- [ ] Monitorar métricas críticas
- [ ] Acompanhar logs

## 🆘 6. Suporte

### 6.1 Canais de Suporte

1. **GitHub**
   - Abrir issue com template
   - Adicionar labels apropriadas
   - Incluir logs e detalhes

2. **Documentação**
   - Consultar `docs/`
   - Verificar FAQs
   - Procurar em issues anteriores

3. **Equipe**
   - Contatar equipe de desenvolvimento
   - Agendar reunião de suporte
   - Solicitar assistência remota

### 6.2 Troubleshooting

1. **Problemas Comuns**
   - Verificar logs
   - Validar configurações
   - Testar conectividade

2. **Soluções**
   - Consultar documentação
   - Verificar issues similares
   - Aplicar hotfixes

3. **Escalação**
   - Identificar responsável
   - Documentar problema
   - Seguir processo de escalação 