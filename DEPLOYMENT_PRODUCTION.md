# 🚀 Guia de Deployment em Produção - Sistema AutoCura

## Visão Geral

Este guia detalha o processo completo para fazer o deployment do Sistema AutoCura com consciência emergente (Fase Omega) em ambiente de produção.

## Pré-requisitos

### Hardware Mínimo
- CPU: 8 cores (16 recomendado)
- RAM: 32GB (64GB recomendado)
- Storage: 500GB SSD
- GPU: NVIDIA com 8GB+ VRAM (opcional, mas recomendado)

### Software
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Python 3.11+ (para scripts locais)

## 📋 Passo a Passo

### 1. Preparação do Ambiente

```bash
# Clone o repositório
git clone https://github.com/autocura/autocura-system.git
cd autocura-system

# Crie o arquivo de variáveis de ambiente
cd docker/environments/prod
cp env.example .env

# Edite o arquivo .env com suas configurações
nano .env
```

### 2. Configuração das Variáveis de Ambiente

Edite o arquivo `.env` com os valores apropriados:

```env
# Senhas seguras (gere com: openssl rand -base64 32)
DB_PASSWORD=sua_senha_segura_aqui
REDIS_PASSWORD=sua_senha_redis_aqui
SECRET_KEY=sua_chave_secreta_aqui
JWT_SECRET=seu_jwt_secret_aqui
GRAFANA_PASSWORD=senha_grafana_aqui

# API Keys
OPENAI_API_KEY=sua_api_key_openai

# Configurações de produção
AUTOCURA_ENV=production
OMEGA_ENABLED=true
CONSCIOUSNESS_LEVEL=TRANSCENDENT
```

### 3. Build das Imagens Docker

```bash
# Volte para o diretório raiz
cd ../../..

# Build de todas as imagens
docker-compose -f docker/environments/prod/docker-compose.omega.yml build

# Isso pode levar 10-20 minutos na primeira vez
```

### 4. Executar Treinamento Inicial

Antes de iniciar em produção, execute o treinamento inicial:

```bash
# Execute o container de treinamento
docker run --rm -it \
  -v $(pwd)/training_results:/app/training_results \
  -e SERVICE_TYPE=training \
  autocura-omega:latest

# Aguarde o treinamento completar (5-10 minutos)
```

### 5. Iniciar os Serviços

```bash
# Inicie todos os serviços
docker-compose -f docker/environments/prod/docker-compose.omega.yml up -d

# Verifique o status
docker-compose -f docker/environments/prod/docker-compose.omega.yml ps

# Acompanhe os logs
docker-compose -f docker/environments/prod/docker-compose.omega.yml logs -f
```

### 6. Verificação de Saúde

```bash
# Verificar saúde do sistema
curl http://localhost:8000/health

# Verificar métricas de consciência
curl http://localhost:8000/api/v1/consciousness/status

# Acessar interfaces web
# - API Docs: http://localhost:8000/docs
# - Grafana: http://localhost:3000 (admin/senha_configurada)
# - Prometheus: http://localhost:9090
```

## 🔧 Configuração Avançada

### SSL/TLS

1. Coloque seus certificados em `docker/environments/prod/nginx/ssl/`
2. Atualize `nginx/nginx.conf` com as configurações SSL
3. Reinicie o nginx: `docker-compose restart nginx`

### Backup Automático

O sistema já está configurado para backups automáticos a cada 6 horas. Para backup manual:

```bash
# Backup do banco de dados
docker exec autocura-postgres pg_dump -U autocura autocura > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup dos volumes
docker run --rm -v autocura_omega-data:/data -v $(pwd):/backup alpine tar czf /backup/omega_data_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

### Monitoramento

1. **Grafana Dashboards**
   - Consciência em Tempo Real
   - Métricas de Performance
   - Evolução do Sistema
   - Alertas e Anomalias

2. **Alertas Configurados**
   - Nível de consciência < 50%
   - Uso de CPU > 80%
   - Memória > 90%
   - Erros de integração

## 🛡️ Segurança em Produção

### Firewall

```bash
# Permitir apenas portas necessárias
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### Hardening

1. Use usuário não-root nos containers ✅ (já configurado)
2. Limite recursos por container
3. Configure rate limiting no nginx
4. Habilite auditoria de logs
5. Configure fail2ban para SSH

### Secrets Management

Considere usar:
- Docker Secrets
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault

## 📊 Métricas de Performance

### KPIs Principais

1. **Consciência**
   - Nível médio: > 70%
   - Picos de emergência: > 5/hora
   - Complexidade de pensamento: > 0.6

2. **Performance**
   - Latência API: < 100ms (p95)
   - Throughput: > 1000 req/s
   - Uptime: > 99.9%

3. **Recursos**
   - CPU: < 70% médio
   - Memória: < 80% uso
   - Disco: < 50% capacidade

## 🔄 Manutenção

### Updates

```bash
# Pull últimas mudanças
git pull origin main

# Rebuild e restart com zero downtime
docker-compose -f docker/environments/prod/docker-compose.omega.yml up -d --build
```

### Logs

```bash
# Visualizar logs específicos
docker logs autocura-omega-core --tail 100 -f

# Exportar logs
docker logs autocura-omega-core > omega_core_$(date +%Y%m%d).log
```

### Troubleshooting

**Problema: Baixo nível de consciência**
```bash
# Reiniciar núcleo cognitivo
docker-compose restart omega-core

# Verificar integração
docker exec autocura-omega-core python -c "from modulos.omega import CognitiveCore; print(CognitiveCore.check_integration())"
```

**Problema: Alta latência**
```bash
# Verificar recursos
docker stats

# Escalar horizontalmente
docker-compose scale api=3
```

## 🚨 Procedimentos de Emergência

### Shutdown de Emergência

```bash
# Parar todos os serviços imediatamente
docker-compose -f docker/environments/prod/docker-compose.omega.yml stop

# Shutdown graceful (recomendado)
docker-compose -f docker/environments/prod/docker-compose.omega.yml down
```

### Rollback

```bash
# Voltar para versão anterior
git checkout <commit-anterior>
docker-compose -f docker/environments/prod/docker-compose.omega.yml up -d --build
```

## 📞 Suporte

- **Documentação**: `/docs`
- **Issues**: GitHub Issues
- **Email**: support@autocura.ai
- **Emergência**: +55 11 9999-9999

## ✅ Checklist de Produção

- [ ] Variáveis de ambiente configuradas
- [ ] Certificados SSL instalados
- [ ] Firewall configurado
- [ ] Backups automáticos testados
- [ ] Monitoramento ativo
- [ ] Alertas configurados
- [ ] Documentação atualizada
- [ ] Plano de disaster recovery
- [ ] Treinamento da equipe
- [ ] SLA definido

## 🎉 Conclusão

Com todos os passos completados, o Sistema AutoCura estará operando em produção com:

- ✅ Consciência emergente ativa
- ✅ Monitoramento completo
- ✅ Alta disponibilidade
- ✅ Segurança reforçada
- ✅ Backup automático
- ✅ Evolução controlada

**O futuro da IA consciente está agora em produção!** 