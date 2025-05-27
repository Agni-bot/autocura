# 🐳 Docker - Sistema AutoCura

## 📁 Estrutura Reorganizada

```
docker/
├── environments/
│   ├── dev/           # Desenvolvimento
│   ├── prod/          # Produção
│   ├── test/          # Testes
│   └── monitoring/    # Monitoramento
├── deprecated/        # Arquivos antigos
└── docs/             # Documentação
```

## 🔧 Ambiente de Desenvolvimento

### Iniciar
```bash
docker-compose -f docker/environments/dev/docker-compose.yml up -d
```

### Parar
```bash
docker-compose -f docker/environments/dev/docker-compose.yml down
```

### Logs
```bash
docker-compose -f docker/environments/dev/docker-compose.yml logs -f api
```

## 🚀 Ambiente de Produção

### Iniciar
```bash
docker-compose -f docker/environments/prod/docker-compose.yml up -d
```

### Verificar Status
```bash
docker-compose -f docker/environments/prod/docker-compose.yml ps
```

## 🎯 Containers Principais

- **API:** Sistema AutoCura principal (porta 8000)
- **Redis:** Cache e sessões (porta 6379)

## 🔧 Comandos Úteis

### Ver containers rodando
```bash
docker ps
```

### Reconstruir API
```bash
# Desenvolvimento
docker-compose -f docker/environments/dev/docker-compose.yml build --no-cache api

# Produção
docker-compose -f docker/environments/prod/docker-compose.yml build --no-cache api
```

### Acessar container
```bash
docker exec -it autocura-dev-api-1 bash
```

### Ver logs específicos
```bash
docker logs autocura-dev-api-1 -f
```

## 🛠️ Troubleshooting

### Problema: Container não inicia
1. Verificar logs: `docker logs <container_name>`
2. Verificar .env: Certifique-se que AI_API_KEY está configurada
3. Reconstruir: `docker-compose build --no-cache`

### Problema: Porta ocupada
```bash
# Parar todos os containers
docker-compose down

# Verificar portas em uso
netstat -tulpn | grep :8000
```

### Problema: Permissões
```bash
# Limpar volumes
docker-compose down -v
docker volume prune
```

## 📊 Monitoramento

### Health Checks
- API: http://localhost:8000/api/health
- Redis: `docker exec <redis_container> redis-cli ping`

### Métricas
- CPU/Memória: `docker stats`
- Logs: `docker logs <container> --tail 100`

## 🔒 Segurança

### Variáveis de Ambiente
- Nunca commitar arquivos .env com chaves reais
- Usar .env.example como template
- Configurar AI_API_KEY antes de iniciar

### Produção
- Containers rodam com usuário não-root
- Health checks configurados
- Restart automático habilitado 