# Módulo Core

Este é o módulo central do sistema de Inteligência Artificial, responsável por fornecer funcionalidades essenciais como gerenciamento de eventos, middleware de comunicação e sistema de logging.

## 🏗️ Estrutura do Módulo

```
modulos/core/
├── docker/                 # Configurações Docker
│   ├── Dockerfile         # Configuração da imagem
│   ├── docker-compose.yml # Orquestração de containers
│   ├── .dockerignore     # Arquivos ignorados no build
│   └── dev.sh            # Script de desenvolvimento
├── src/                   # Código fonte
│   ├── events.py         # Sistema de eventos
│   ├── middleware.py     # Middleware de comunicação
│   └── logging.py        # Sistema de logging
├── tests/                # Testes automatizados
│   ├── test_events.py    # Testes do sistema de eventos
│   ├── test_middleware.py # Testes do middleware
│   └── test_logging.py   # Testes do sistema de logging
├── config/               # Configurações
│   └── config.py         # Configurações do módulo
└── README.md            # Esta documentação
```

## 🚀 Funcionalidades

### Sistema de Eventos
- Publicação e assinatura de eventos
- Histórico de eventos
- Tratamento de erros em handlers
- Filtragem por tópicos

### Middleware de Comunicação
- Registro de módulos
- Comunicação entre módulos
- Broadcast de mensagens
- Handlers de mensagens
- Tratamento de erros

### Sistema de Logging
- Logs estruturados em JSON
- Diferentes níveis de log
- Rotação de logs
- Filtragem por nível
- Formatação personalizada

## 🛠️ Desenvolvimento

### Pré-requisitos
- Docker
- Docker Compose
- Python 3.9+

### Configuração do Ambiente

1. Clone o repositório
2. Navegue até o diretório do módulo core:
   ```bash
   cd modulos/core
   ```

3. Use o script de desenvolvimento:
   ```bash
   # Construir a imagem
   ./docker/dev.sh build

   # Iniciar os containers
   ./docker/dev.sh start

   # Executar testes
   ./docker/dev.sh test

   # Ver logs
   ./docker/dev.sh logs

   # Parar containers
   ./docker/dev.sh stop
   ```

### Variáveis de Ambiente

O módulo pode ser configurado através das seguintes variáveis de ambiente:

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| ENVIRONMENT | Ambiente (development/production) | development |
| DEBUG | Modo debug | true |
| LOG_LEVEL | Nível de log | DEBUG |
| CORE_HOST | Host do servidor | 0.0.0.0 |
| CORE_PORT | Porta do servidor | 8000 |
| CORE_WORKERS | Número de workers | 2 |
| LOG_FORMAT | Formato dos logs | json |
| LOG_FILE_PATH | Caminho do arquivo de log | /app/logs/app.log |
| LOG_MAX_SIZE | Tamanho máximo do log (MB) | 100 |
| LOG_BACKUP_COUNT | Número de backups | 5 |
| EVENT_HISTORY_SIZE | Tamanho do histórico de eventos | 1000 |
| EVENT_PROCESSING_TIMEOUT | Timeout de processamento (s) | 5.0 |
| MIDDLEWARE_TIMEOUT | Timeout do middleware (s) | 10.0 |
| MIDDLEWARE_RETRY_ATTEMPTS | Tentativas de retry | 3 |
| MIDDLEWARE_RETRY_DELAY | Delay entre retries (s) | 1.0 |

## 🧪 Testes

Os testes são executados automaticamente ao iniciar o container em modo de desenvolvimento. Para executar os testes manualmente:

```bash
./docker/dev.sh test
```

## 📝 Logs

Os logs são armazenados em `/app/logs/app.log` dentro do container e são persistidos através de um volume Docker. Para visualizar os logs:

```bash
./docker/dev.sh logs
```

## 🔒 Segurança

- Todas as comunicações são feitas através de canais seguros
- Logs sensíveis são mascarados automaticamente
- Validação de entrada em todos os endpoints
- Rate limiting implementado
- Sanitização de dados

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](../LICENSE) para detalhes.

