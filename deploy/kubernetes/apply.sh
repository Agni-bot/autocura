#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Iniciando deploy do Autocura no Kubernetes...${NC}"

# Criar namespace de monitoramento
echo -e "${YELLOW}Criando namespace de monitoramento...${NC}"
kubectl apply -f monitoring/namespace.yaml

# Aplicar configurações de monitoramento
echo -e "${YELLOW}Aplicando configurações de monitoramento...${NC}"
kubectl apply -f monitoring/prometheus-config.yaml
kubectl apply -f monitoring/grafana-dashboard.yaml

# Aplicar configurações base
echo -e "${YELLOW}Aplicando configurações base...${NC}"
kubectl apply -f base/namespace.yaml

# Aplicar configurações de produção
echo -e "${YELLOW}Aplicando configurações de produção...${NC}"
kubectl apply -k production/

# Verificar status
echo -e "${YELLOW}Verificando status do deploy...${NC}"
kubectl get pods -n autocura
kubectl get pods -n monitoring

# Verificar logs
echo -e "${YELLOW}Verificando logs dos pods...${NC}"
kubectl logs -n autocura -l app=autocura --tail=50

echo -e "${GREEN}Deploy concluído!${NC}"
echo -e "${YELLOW}Para verificar o status do sistema, execute:${NC}"
echo "kubectl get pods -n autocura"
echo "kubectl get pods -n monitoring"
echo "kubectl get services -n autocura"
echo "kubectl get services -n monitoring" 