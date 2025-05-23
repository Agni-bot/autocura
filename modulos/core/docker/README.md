# Estrutura Docker do Projeto

Este diretório contém todos os arquivos Docker necessários para construir e executar os diferentes serviços do projeto.

## Estrutura de Diretórios

```
docker/
├── base/                 # Imagem base comum a todos os serviços
├── services/            # Dockerfiles específicos para cada serviço
│   ├── api/            # Serviço de API
│   ├── monitor/        # Serviço de monitoramento
│   ├── observador/     # Serviço observador
│   ├── validador/      # Serviço validador
│   ├── guardiao/       # Serviço guardião
│   ├── gerador/        # Serviço gerador
│   └── diagnostico/    # Serviço de diagnóstico
└── tests/              # Dockerfile para testes
```

## Imagens Docker

### Base (`docker/base/Dockerfile`)
- Imagem base Python 3.10
- Instala dependências comuns
- Configura ambiente básico

### Serviços
Cada serviço tem seu próprio Dockerfile com configurações específicas:
- `api`: Serviço de API REST
- `monitor`: Monitoramento do sistema
- `observador`: Observação de eventos
- `validador`: Validação de dados
- `guardiao`: Proteção do sistema
- `gerador`: Geração de conteúdo
- `diagnostico`: Diagnóstico do sistema

### Testes (`docker/tests/Dockerfile`)
- Configuração específica para execução de testes
- Inclui ferramentas de cobertura e relatórios

## Scripts de Build

- `build.sh`: Script para Linux/Mac
- `build.ps1`: Script para Windows

## Como Usar

1. Construir as imagens:
   ```bash
   # Linux/Mac
   ./docker/build.sh
   
   # Windows
   .\docker\build.ps1
   ```

2. Executar os serviços:
   ```bash
   docker-compose up -d
   ```

3. Executar os testes:
   ```bash
   docker-compose run tests
   ```

4. Monitoramento:
   ```bash
   docker-compose -f docker-compose.monitoring.yml up -d
   ```

## Variáveis de Ambiente

Cada serviço pode ser configurado através de variáveis de ambiente no `docker-compose.yml`:

- `REDIS_HOST`: Host do Redis
- `REDIS_PORT`: Porta do Redis
- `SERVICE_NAME`: Nome do serviço
- `*_INTERVAL`: Intervalos específicos para cada serviço

## Volumes

- `redis_data`: Dados do Redis
- `prometheus_data`: Dados do Prometheus
- `grafana_data`: Dados do Grafana

## Redes

- `monitoring-network`: Rede para serviços de monitoramento 