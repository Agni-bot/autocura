# Estrutura Organizada do Sistema AutoCura

## 📁 Visão Geral da Organização

O projeto foi reorganizado seguindo as melhores práticas de desenvolvimento, com uma estrutura modular clara e bem definida.

## 🗂️ Estrutura de Diretórios

```
autocura/
├── src/                        # Código fonte principal
│   ├── core/                   # Núcleo do sistema
│   ├── services/               # Serviços especializados
│   ├── monitoring/             # Monitoramento avançado
│   └── seguranca/              # Módulos de segurança
│
├── scripts/                    # Scripts utilitários
│   ├── dashboard/              # Scripts do dashboard
│   │   ├── run_dashboard_simple.py
│   │   └── fix_dashboard_container.py
│   ├── tests/                  # Scripts de teste
│   │   ├── test_*.py
│   │   ├── casos_uso_especificos.py
│   │   └── debug_test.py
│   ├── demos/                  # Demonstrações
│   │   ├── demo_*.py
│   │   └── api_sugestoes.py
│   └── *.bat                   # Scripts batch Windows
│
├── deployment/                 # Arquivos de deployment
│   └── docker/                 # Configurações Docker
│       └── docker-compose.dashboard.yml
│
├── docs/                       # Documentação
│   ├── relatorios/             # Relatórios do sistema
│   │   ├── relatorio_*.md
│   │   ├── analise_*.md
│   │   └── RELATORIO_*.md
│   ├── SOLUCAO_CONTAINER_DASHBOARD.md
│   ├── INTEGRACAO_COMPLETA_DASHBOARD.md
│   └── implementacao_producao.md
│
├── config/                     # Configurações
│   └── prometheus.yml          # Config do Prometheus
│
├── tests/                      # Testes unitários/integração
├── modulos/                    # Módulos independentes (Etapa 2)
├── reports/                    # Relatórios de testes
│   ├── coverage.xml
│   └── .coverage
│
├── assets/                     # Recursos estáticos
│   └── teste_api.html
│
├── data/                       # Dados do sistema
├── logs/                       # Logs do sistema
├── contexto/                   # Sistema de registro de contexto
│
├── main.py                     # Entrada principal da aplicação
├── dashboard.html              # Interface do dashboard
├── memoria_compartilhada.json  # Estado do sistema
├── requirements.txt            # Dependências Python
└── README.md                   # Documentação principal
```

## 🚀 Como Executar

### Dashboard Simples (Sem Docker)
```bash
python scripts\dashboard\run_dashboard_simple.py
```

### Dashboard com Docker
```bash
python scripts\dashboard\fix_dashboard_container.py
```

### Executar Testes
```bash
# Todos os testes
pytest scripts/tests/

# Teste específico
python scripts/tests/test_auto_modification_simple.py
```

### Executar Demonstrações
```bash
python scripts/demos/demo_dashboard_integrado.py
```

## 📝 Arquivos Importantes na Raiz

Apenas arquivos essenciais foram mantidos na raiz:

- **main.py**: Ponto de entrada principal do sistema
- **dashboard.html**: Interface web do dashboard
- **memoria_compartilhada.json**: Estado persistente do sistema
- **requirements.txt**: Dependências do projeto
- **README.md**: Documentação principal

## 🔧 Scripts Organizados

### `/scripts/dashboard/`
- `run_dashboard_simple.py`: Executa o dashboard sem Docker
- `fix_dashboard_container.py`: Corrige e executa com Docker

### `/scripts/tests/`
- Todos os arquivos de teste (`test_*.py`)
- Casos de uso específicos
- Scripts de debug

### `/scripts/demos/`
- Demonstrações do sistema
- APIs de exemplo
- Interfaces de aprovação

## 📚 Documentação Organizada

### `/docs/`
- Documentação técnica principal
- Guias de implementação
- Soluções de problemas

### `/docs/relatorios/`
- Relatórios de análise
- Relatórios de implementação
- Status do sistema

## 🐳 Deployment

### `/deployment/docker/`
- `docker-compose.dashboard.yml`: Configuração completa do dashboard
- Futuros arquivos de deployment

## ✅ Benefícios da Nova Organização

1. **Clareza**: Estrutura intuitiva e fácil de navegar
2. **Modularidade**: Componentes bem separados
3. **Manutenibilidade**: Fácil localização de arquivos
4. **Escalabilidade**: Preparado para crescimento
5. **Profissionalismo**: Segue padrões da indústria

## 🎯 Próximos Passos

1. Continuar movendo componentes para estrutura modular
2. Implementar CI/CD baseado na nova estrutura
3. Atualizar imports nos arquivos conforme necessário
4. Criar scripts de automação para tarefas comuns

---

**Última Atualização**: 27/01/2025 