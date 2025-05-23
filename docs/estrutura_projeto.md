# Estrutura do Projeto

## 1. Diretórios Principais

### 1.1 Módulos (`modulos/`)
- `core/`: Módulo central com interfaces comuns
- `monitoramento/`: Monitoramento e observabilidade
- `diagnostico/`: Diagnóstico e análise
- `gerador-acoes/`: Geração de ações
- `integracao/`: Integração com sistemas externos
- `guardiao-cognitivo/`: Guardião cognitivo
- `etica/`: Módulos ético-operacionais

### 1.2 Compartilhado (`shared/`)
- `api/`: APIs compartilhadas
- `events/`: Sistema de eventos
- `utils/`: Utilitários comuns

### 1.3 Testes (`tests/`)
- `integration/`: Testes de integração
- `e2e/`: Testes end-to-end
- `unit/`: Testes unitários (migrados para seus módulos)

### 1.4 Deployment (`deployment/`)
- `scripts/`: Scripts de instalação
- `build/`: Scripts de build
- `config/`: Configurações de deployment

## 2. Scripts

### 2.1 Scripts Principais
- `autocura.sh`/`autocura.ps1`: Script principal
- `run_tests_*.py`: Scripts de teste
- `monitor_dependencias.py`: Monitoramento de dependências

### 2.2 Scripts por Módulo
- `modulos/diagnostico/scripts/`: Scripts específicos de diagnóstico
- `deployment/scripts/`: Scripts de instalação
- `deployment/build/`: Scripts de build

## 3. Resultados de Teste

### 3.1 Arquivos Mantidos
- `report.html`: Relatório de cobertura
- `junit.xml`: Resultados em formato JUnit
- `assets/`: Recursos de teste

## 4. Migração

Para migrar para a nova estrutura:

1. Executar script de reorganização:
```bash
python scripts/reorganizar_estrutura.py
```

2. Atualizar imports:
```bash
python scripts/update_imports.py
```

3. Validar estrutura:
```bash
python scripts/validar_estrutura.py
```

## 5. Convenções

### 5.1 Nomenclatura
- Módulos: snake_case
- Classes: PascalCase
- Funções: snake_case
- Variáveis: snake_case
- Constantes: UPPER_CASE

### 5.2 Organização
- Cada módulo tem sua própria estrutura de testes
- Scripts específicos ficam em seus módulos
- Scripts gerais ficam na raiz
- Documentação em `docs/`

## 6. Manutenção

### 6.1 Limpeza Regular
- Remover resultados antigos de teste
- Limpar caches
- Atualizar documentação

### 6.2 Atualizações
- Manter dependências atualizadas
- Seguir guia de migração
- Validar após mudanças 