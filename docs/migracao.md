# Guia de Migração

Este documento descreve o processo de migração para a nova estrutura modular do sistema.

## 1. Estrutura de Módulos

### 1.1 Módulo Ético-Operacional

A estrutura do módulo ético foi reorganizada em submodules:

```
etica/
├── circuitos-morais/     # Novos pilares éticos
├── decisao-hibrida/      # Sistema de decisão híbrida
├── auditoria/            # Sistema de auditoria
├── governanca/           # Governança adaptativa
├── fluxo-autonomia/      # Controle de autonomia
├── validadores-eticos/   # Validadores éticos
├── priorizacao-financeira/ # Priorização financeira
└── registro-decisoes/    # Registro de decisões
```

#### Migração de Código Existente

1. Mover código de validação ética para `validadores-eticos/`
2. Mover código de auditoria para `auditoria/`
3. Mover código de governança para `governanca/`
4. Mover código de registro para `registro-decisoes/`

### 1.2 Módulo de Monitoramento

O módulo de monitoramento foi consolidado com observabilidade:

```
monitoramento/
├── coletores/           # Coletores de métricas
├── processadores/       # Processamento de dados
├── storage/            # Armazenamento
└── api/                # APIs de acesso
```

#### Migração de Código Existente

1. Mover coletores para `coletores/`
2. Mover processadores para `processadores/`
3. Mover storage para `storage/`
4. Mover APIs para `api/`

## 2. Atualização de Dependências

### 2.1 Requirements

Atualizar `requirements.txt` com novas dependências:

```bash
# Atualizar dependências
pip install -r requirements.txt

# Atualizar dependências de desenvolvimento
pip install -r requirements-test.txt
```

### 2.2 Docker

Atualizar Dockerfiles e docker-compose:

```bash
# Reconstruir imagens
./build-images.sh

# Atualizar containers
docker-compose up -d
```

## 3. Testes

### 3.1 Atualização de Testes

1. Mover testes para a nova estrutura
2. Atualizar imports nos testes
3. Adicionar novos testes de integração

```bash
# Executar testes
pytest

# Gerar relatório de cobertura
pytest --cov=modulos
```

### 3.2 Testes de Integração

Adicionar testes de integração entre módulos:

```python
# tests/integration/test_etica_monitoramento.py
async def test_etica_monitoramento():
    # Teste de integração entre ética e monitoramento
    pass
```

## 4. Documentação

### 4.1 Atualização de Documentação

1. Atualizar READMEs dos módulos
2. Atualizar documentação de API
3. Atualizar guias de desenvolvimento

### 4.2 Novos Documentos

1. Criar documentação para novos módulos
2. Atualizar diagramas de arquitetura
3. Atualizar guias de contribuição

## 5. Checklist de Migração

- [ ] Atualizar estrutura de diretórios
- [ ] Migrar código existente
- [ ] Atualizar dependências
- [ ] Atualizar Docker
- [ ] Atualizar testes
- [ ] Atualizar documentação
- [ ] Executar testes de integração
- [ ] Validar em ambiente de desenvolvimento
- [ ] Fazer deploy em produção

## 6. Suporte

Para suporte durante a migração:

1. Abrir issue no GitHub
2. Consultar documentação em `docs/`
3. Contatar equipe de desenvolvimento 