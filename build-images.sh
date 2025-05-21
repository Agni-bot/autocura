#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Iniciando build das imagens Docker...${NC}"

# Build da imagem base
echo -e "\n${YELLOW}Construindo imagem base...${NC}"
docker build -t autocura-base:latest -f Dockerfile.base .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Imagem base construída com sucesso!${NC}"
else
    echo -e "${RED}Falha ao construir imagem base${NC}"
    exit 1
fi

# Build das imagens dos serviços
services=("api" "monitor" "diagnostico" "gerador" "guardiao" "validador" "observador")

for service in "${services[@]}"; do
    echo -e "\n${YELLOW}Construindo imagem do serviço $service...${NC}"
    docker build -t autocura-$service:latest -f Dockerfile.$service .
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Imagem do serviço $service construída com sucesso!${NC}"
    else
        echo -e "${RED}Falha ao construir imagem do serviço $service${NC}"
        exit 1
    fi
done

echo -e "\n${GREEN}Todas as imagens foram construídas com sucesso!${NC}" 