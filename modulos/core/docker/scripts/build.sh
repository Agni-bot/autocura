#!/bin/bash

# Construir imagem base
docker build -t autocura-base:latest -f docker/base/Dockerfile .

# Construir imagens dos serviços
docker build -t autocura-api:latest -f docker/services/api/Dockerfile .
docker build -t autocura-monitor:latest -f docker/services/monitor/Dockerfile .
docker build -t autocura-observador:latest -f docker/services/observador/Dockerfile .
docker build -t autocura-validador:latest -f docker/services/validador/Dockerfile .
docker build -t autocura-guardiao:latest -f docker/services/guardiao/Dockerfile .
docker build -t autocura-gerador:latest -f docker/services/gerador/Dockerfile .
docker build -t autocura-diagnostico:latest -f docker/services/diagnostico/Dockerfile .

# Construir imagem de testes
docker build -t autocura-tests:latest -f docker/tests/Dockerfile .

echo "Todas as imagens foram construídas com sucesso!" 