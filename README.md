# AutoCura

Sistema de autocura e monitoramento inteligente.

## Estrutura do Projeto

```
autocura/
├── src/                    # Código fonte
├── tests/                  # Testes e configurações de teste
├── config/                 # Configurações
│   ├── monitoring/        # Configurações de monitoramento
│   └── kubernetes/        # Configurações do Kubernetes
├── deploy/                # Scripts de deploy
├── docker/               # Arquivos Docker
├── docs/                 # Documentação
├── reports/             # Relatórios (cobertura, testes)
├── scripts/             # Scripts utilitários
└── assets/              # Recursos estáticos
```

## Requisitos

- Python 3.10+
- Docker
- Kubernetes (opcional)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/autocura.git
cd autocura
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

## Executando os Testes

```bash
pytest
```

## Executando com Docker

1. Construa as imagens:
```bash
# Linux/Mac
./docker/build.sh

# Windows
.\docker\build.ps1
```

2. Inicie os serviços:
```bash
docker-compose up -d
```

3. Inicie o monitoramento:
```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

## Monitoramento

O sistema inclui:
- Prometheus para métricas
- Grafana para visualização
- Loki para logs
- Alertmanager para alertas

Acesse:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Autores
- Seu Nome (@seu-usuario)

## Agradecimentos
- [LangChain](https://github.com/hwchase17/langchain)
- [Groq](https://groq.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)

# Sistema de Monitoramento de Recursos

Este módulo implementa um sistema de monitoramento de recursos para o sistema de autocura, fornecendo métricas em tempo real e ajustes automáticos.

## Funcionalidades

- Monitoramento contínuo de recursos do sistema (CPU, memória, disco)
- Coleta de métricas via Prometheus
- Alertas configuráveis via email e Slack
- Ajuste automático de recursos
- Integração com sistema de autocura
- Histórico de métricas e alertas

## Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Configuração

O sistema é configurado através do arquivo `src/monitoramento/config.py`. Principais configurações:

- Intervalo de monitoramento
- Limites de recursos
- Configurações de alertas
- Parâmetros de ajuste automático

## Uso

Para iniciar o monitoramento:

```bash
python src/monitoramento/executar_monitoramento.py
```

O sistema irá:
1. Iniciar o servidor Prometheus na porta 9090
2. Começar a coletar métricas
3. Enviar alertas quando necessário
4. Realizar ajustes automáticos

## Métricas Prometheus

O sistema expõe as seguintes métricas:

### Contadores
- `autocura_ajustes_total`: Total de ajustes realizados
- `autocura_alertas_total`: Total de alertas gerados

### Gauges
- `autocura_cpu_usage`: Uso de CPU por core
- `autocura_memory_usage`: Uso de memória (RAM e swap)
- `autocura_disk_usage`: Uso de disco por partição
- `autocura_equidade`: Índice de equidade na distribuição

### Histogramas
- `autocura_ajuste_duration_seconds`: Duração dos ajustes

## Alertas

O sistema envia alertas quando:

- Uso de CPU excede limite configurado
- Uso de memória excede limite configurado
- Uso de disco excede limite configurado
- Índice de equidade cai abaixo do limite

Alertas são enviados via:
- Email (SMTP)
- Slack (Webhook)

## Integração com Autocura

O monitoramento se integra com o sistema de autocura através de:

1. Métricas em tempo real
2. Ajustes automáticos de recursos
3. Histórico de métricas e alertas
4. Memória compartilhada

## Logs

Logs são salvos em:
- `logs/monitoramento.log`: Log geral do sistema
- `logs/dependencias.log`: Log de dependências

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes. 