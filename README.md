# AutoCura - Sistema de Autocura Cognitiva

## 📋 Visão Geral

O AutoCura é um sistema de autocura cognitiva que utiliza inteligência artificial para monitorar, validar e proteger operações em tempo real. O sistema é composto por módulos independentes que trabalham em conjunto para garantir a segurança e confiabilidade das operações.

## 🏗️ Arquitetura

O sistema é composto pelos seguintes módulos:

- **Monitor**: Responsável por coletar e analisar métricas do sistema
- **Observador**: Registra e analisa logs de operações
- **Validador**: Valida requisições e operações
- **Guardião**: Protege o sistema contra ameaças e anomalias

### Serviços de Suporte

- **Redis**: Cache e mensageria
- **Elasticsearch**: Armazenamento e busca de logs
- **Prometheus**: Coleta de métricas
- **Grafana**: Visualização de métricas e dashboards

## 🚀 Início Rápido

### Pré-requisitos

- Docker e Docker Compose
- PowerShell (Windows) ou Bash (Linux/Mac)
- Python 3.8+

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/autocura.git
cd autocura
```

2. Execute o script de inicialização:
```powershell
# Windows
.\scripts\start_environment.ps1

# Linux/Mac
./scripts/start_environment.sh
```

3. Acesse os endpoints:
- Monitor: http://localhost:9090
- Observador: http://localhost:8080
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3000
- Elasticsearch: http://localhost:9200

## 📊 Monitoramento

### Grafana Dashboard

O sistema inclui um dashboard predefinido no Grafana com as seguintes métricas:

- Taxa de validações
- Tempo de resposta (p50, p95)
- Taxa de erros
- Alertas ativos

Para acessar o dashboard:
1. Acesse http://localhost:3000
2. Use as credenciais padrão:
   - Usuário: admin
   - Senha: admin
3. O dashboard "AutoCura" estará disponível automaticamente

### Logs

Os logs podem ser acessados através do endpoint do Observador:
```bash
curl -H "Authorization: Bearer seu-token-jwt" http://localhost:8080/logs?limit=10&level=INFO
```

## 🧪 Testes

### Testes de Integração

Para executar os testes de integração:

```powershell
# Windows
.\scripts\run_tests.ps1

# Linux/Mac
./scripts/run_tests.sh
```

O script irá:
1. Verificar se todos os containers estão rodando
2. Executar os testes de integração
3. Gerar um relatório de cobertura

## 📚 Documentação

- [Documentação da API](docs/api.md)
- [Guia de Desenvolvimento](docs/desenvolvimento.md)
- [Arquitetura do Sistema](docs/arquitetura.md)

## 🔒 Segurança

- Todas as APIs requerem autenticação via token JWT
- Rate limiting: 100 requisições por minuto por IP
- Todas as comunicações são via HTTPS
- Logs são criptografados em repouso
- Métricas são anonimizadas

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 