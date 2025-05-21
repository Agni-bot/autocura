# Sistema de Automação de Testes

Este módulo implementa um sistema automatizado para execução e gerenciamento de testes do sistema de autocura.

## 🎯 Funcionalidades

- Execução automática de testes unitários e de integração
- Geração de relatórios detalhados em Markdown
- Monitoramento de cobertura de código
- Configuração flexível via YAML
- Sistema de logging completo
- Suporte a notificações (email e Slack)
- Execução paralela de testes
- Retry automático de testes falhos

## 📋 Pré-requisitos

- Python 3.8+
- pytest
- pytest-cov
- pytest-timeout
- pyyaml

## 🚀 Como Usar

1. Configure o ambiente:

```bash
pip install -r requirements.txt
```

2. Ajuste as configurações em `config_testes.yaml` conforme necessário

3. Execute os testes:

```bash
python -m src.orquestrador.executar_testes
```

## ⚙️ Configuração

O arquivo `config_testes.yaml` permite configurar:

- Cobertura mínima de código
- Timeout para testes
- Configurações de logging
- Formato e localização dos relatórios
- Notificações (email/Slack)
- Variáveis de ambiente
- Execução paralela

## 📊 Relatórios

Os relatórios são gerados em Markdown e incluem:

- Status de cada teste
- Cobertura de código
- Métricas de performance
- Logs de erro
- Timestamp de execução

## 🔄 CI/CD

Para integrar com CI/CD, adicione ao seu pipeline:

```yaml
- name: Executar Testes
  run: |
    python -m src.orquestrador.executar_testes
```

## 🛠️ Desenvolvimento

### Estrutura de Arquivos

```
src/orquestrador/
├── automatizador_testes.py    # Classe principal de automação
├── config_testes.yaml         # Configurações
├── executar_testes.py         # Script de execução
└── README_TESTES.md          # Esta documentação
```

### Adicionando Novos Testes

1. Crie seus testes em `tests/` ou `tests/integration/`
2. Siga o padrão de nomenclatura `test_*.py`
3. Use fixtures do pytest quando necessário
4. Documente casos de teste complexos

## 📝 Logs

Os logs são salvos em `logs/testes.log` e incluem:

- Início/fim de execução
- Status de cada teste
- Erros e exceções
- Métricas de performance

## 🔍 Monitoramento

O sistema gera métricas que podem ser integradas com:

- Prometheus
- Grafana
- ELK Stack
- Datadog

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Crie um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes. 