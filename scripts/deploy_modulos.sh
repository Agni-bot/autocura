#!/bin/bash

# Cores para output
VERDE='\033[0;32m'
AMARELO='\033[1;33m'
VERMELHO='\033[0;31m'
NC='\033[0m'

echo -e "${AMARELO}Iniciando build e deploy dos módulos testados...${NC}"

# Criar rede se não existir
docker network create autocura-network 2>/dev/null || true

# Build da imagem base
echo -e "${AMARELO}Build da imagem base...${NC}"
docker build -t autocura/base:latest -f docker/Dockerfile .

# Build dos módulos testados
echo -e "${AMARELO}Build dos módulos testados...${NC}"

# Módulo de Monitoramento
echo -e "${VERDE}Build do módulo de Monitoramento...${NC}"
docker build -t autocura/monitor:latest -f docker/Dockerfile.monitor .

# Módulo de Observabilidade
echo -e "${VERDE}Build do módulo de Observabilidade...${NC}"
docker build -t autocura/observador:latest -f docker/Dockerfile.observador .

# Módulo de Validação Ética
echo -e "${VERDE}Build do módulo de Validação Ética...${NC}"
docker build -t autocura/validador:latest -f docker/Dockerfile.validador .

# Módulo Guardião
echo -e "${VERDE}Build do módulo Guardião...${NC}"
docker build -t autocura/guardiao:latest -f docker/Dockerfile.guardiao .

# Subir os containers
echo -e "${AMARELO}Subindo os containers...${NC}"
docker-compose -f docker/docker-compose.yml up -d

echo -e "${VERDE}Deploy concluído!${NC}"
echo -e "${AMARELO}Verificando status dos containers...${NC}"
docker-compose -f docker/docker-compose.yml ps 