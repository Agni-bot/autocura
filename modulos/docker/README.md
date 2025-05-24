# Módulo Docker

## Descrição
Módulo responsável por gerenciar a containerização e orquestração do sistema, garantindo consistência e portabilidade entre ambientes.

## Estrutura
```
docker/
├── images/                # Imagens Docker
│   ├── base/             # Imagem base
│   ├── dev/              # Imagem de desenvolvimento
│   └── prod/             # Imagem de produção
├── compose/              # Arquivos docker-compose
│   ├── dev/              # Compose de desenvolvimento
│   └── prod/             # Compose de produção
├── scripts/              # Scripts de automação
└── config/               # Configurações Docker
```

## Funcionalidades

### Imagens
- Imagem base do sistema
- Imagem de desenvolvimento
- Imagem de produção
- Multi-stage builds

### Compose
- Orquestração de serviços
- Configuração de redes
- Gerenciamento de volumes
- Variáveis de ambiente

### Scripts
- Build de imagens
- Push para registry
- Deploy de containers
- Limpeza de recursos

### Configuração
- Dockerfiles
- .dockerignore
- Configurações de rede
- Configurações de volume

## Configuração

1. Instale as dependências:
```bash
# Instale o Docker
curl -fsSL https://get.docker.com | sh

# Instale o Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.5.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Execute os testes:
```bash
# Testa a imagem
docker build -t sistema-teste .

# Testa o compose
docker-compose -f compose/dev/docker-compose.yml up -d
```

## Uso

```bash
# Build da imagem
./scripts/build.sh

# Inicia os containers
./scripts/start.sh

# Para os containers
./scripts/stop.sh

# Limpa recursos
./scripts/clean.sh
```

## Contribuição

1. Siga a estrutura modular
2. Adicione testes
3. Atualize a documentação
4. Envie um pull request

## Licença

Este módulo está sob a licença MIT. 