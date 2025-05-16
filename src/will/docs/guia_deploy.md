# Guia de Deploy - Sistema Will

## 1. Pré-requisitos

### 1.1 Requisitos do Sistema
- Docker instalado (versão 20.10 ou superior)
- Docker Compose (opcional, para ambientes mais complexos)
- Git (para clonar o repositório)
- Acesso à internet para download de imagens Docker

### 1.2 Portas Necessárias
- 5000: API Will (HTTP)
- 5001: API Will (HTTPS, se configurado)

## 2. Processo de Deploy

### 2.1 Preparação do Ambiente

1. **Clone do Repositório**
   ```bash
   git clone <repositório>
   cd <diretório>
   ```

2. **Configuração de Variáveis de Ambiente**
   - Crie um arquivo `.env` na raiz do projeto
   - Configure as variáveis necessárias:
     ```
     FLASK_ENV=production
     FLASK_APP=app.py
     GEMINI_API_KEY=sua_chave_api
     ```

### 2.2 Build da Imagem Docker

1. **Build da Imagem**
   ```bash
   docker build --no-cache -t will:latest -f src/will/inst/Dockerfile .
   ```

2. **Verificação da Imagem**
   ```bash
   docker images | grep will
   ```

### 2.3 Execução do Container

1. **Modo de Produção**
   ```bash
   docker run -d \
     --name will-api \
     -p 5000:5000 \
     --env-file .env \
     will:latest
   ```

2. **Modo de Desenvolvimento**
   ```bash
   docker run -d \
     --name will-api-dev \
     -p 5000:5000 \
     -v $(pwd)/src/will/inst:/app \
     --env-file .env \
     will:latest
   ```

### 2.4 Verificação do Deploy

1. **Verificar Logs**
   ```bash
   docker logs will-api
   ```

2. **Testar Endpoints**
   ```bash
   curl http://localhost:5000/api/will/status
   ```

## 3. Configuração de Produção

### 3.1 Configuração de Proxy Reverso (Nginx)

1. **Instalação do Nginx**
   ```bash
   sudo apt-get update
   sudo apt-get install nginx
   ```

2. **Configuração do Virtual Host**
   ```nginx
   server {
       listen 80;
       server_name seu-dominio.com;

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### 3.2 Configuração de SSL (HTTPS)

1. **Instalação do Certbot**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   ```

2. **Obtenção do Certificado**
   ```bash
   sudo certbot --nginx -d seu-dominio.com
   ```

## 4. Monitoramento

### 4.1 Configuração de Logs

1. **Logs do Container**
   ```bash
   docker logs -f will-api
   ```

2. **Logs do Sistema**
   ```bash
   journalctl -u docker.service
   ```

### 4.2 Métricas de Performance

1. **Monitoramento do Container**
   ```bash
   docker stats will-api
   ```

2. **Monitoramento do Sistema**
   ```bash
   top
   ```

## 5. Manutenção

### 5.1 Atualizações

1. **Atualização da Imagem**
   ```bash
   docker pull will:latest
   docker stop will-api
   docker rm will-api
   docker run -d --name will-api -p 5000:5000 will:latest
   ```

2. **Rollback**
   ```bash
   docker stop will-api
   docker rm will-api
   docker run -d --name will-api -p 5000:5000 will:previous
   ```

### 5.2 Backup

1. **Backup de Dados**
   ```bash
   docker cp will-api:/app/data ./backup
   ```

2. **Backup de Configurações**
   ```bash
   cp .env ./backup/env_$(date +%Y%m%d)
   ```

## 6. Troubleshooting

### 6.1 Problemas Comuns

1. **Container não inicia**
   - Verificar logs: `docker logs will-api`
   - Verificar configurações: `docker inspect will-api`

2. **API não responde**
   - Verificar status do container: `docker ps`
   - Testar conectividade: `curl localhost:5000/api/will/status`

### 6.2 Soluções

1. **Reiniciar Container**
   ```bash
   docker restart will-api
   ```

2. **Reconstruir Imagem**
   ```bash
   docker build --no-cache -t will:latest -f src/will/inst/Dockerfile .
   ```

## 7. Segurança

### 7.1 Boas Práticas

1. **Atualizações Regulares**
   - Manter Docker atualizado
   - Atualizar dependências do projeto
   - Aplicar patches de segurança

2. **Configurações de Segurança**
   - Usar HTTPS em produção
   - Implementar rate limiting
   - Configurar firewall

### 7.2 Checklist de Segurança

- [ ] SSL/TLS configurado
- [ ] Firewall ativo
- [ ] Logs de segurança monitorados
- [ ] Backups regulares
- [ ] Atualizações de segurança aplicadas

## 8. Conclusão

Este guia fornece as instruções necessárias para deploy e manutenção do Sistema Will em ambiente de produção. Mantenha a documentação atualizada conforme novas funcionalidades são implementadas ou configurações são alteradas. 