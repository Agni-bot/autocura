#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Função para verificar se um comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar dependências
echo -e "${YELLOW}Verificando dependências...${NC}"
for cmd in docker docker-compose; do
    if ! command_exists $cmd; then
        echo -e "${RED}Erro: $cmd não está instalado${NC}"
        exit 1
    fi
done

# Criar diretórios necessários
echo -e "${YELLOW}Criando diretórios...${NC}"
mkdir -p logs coverage test-reports

# Iniciar serviços
echo -e "${YELLOW}Iniciando serviços...${NC}"
docker-compose -f docker-compose.monitoring.yml up -d

# Verificar se os serviços estão rodando
echo -e "${YELLOW}Verificando serviços...${NC}"
for service in prometheus grafana alertmanager; do
    if ! docker-compose -f docker-compose.monitoring.yml ps | grep -q "$service.*Up"; then
        echo -e "${RED}Erro: Serviço $service não está rodando${NC}"
        exit 1
    fi
done

# Configurar Prometheus
echo -e "${YELLOW}Configurando Prometheus...${NC}"
docker-compose -f docker-compose.monitoring.yml exec prometheus promtool check config /etc/prometheus/prometheus.yml

# Configurar AlertManager
echo -e "${YELLOW}Configurando AlertManager...${NC}"
docker-compose -f docker-compose.monitoring.yml exec alertmanager amtool check-config /etc/alertmanager/alertmanager.yml

# Verificar endpoints
echo -e "${YELLOW}Verificando endpoints...${NC}"
for port in 9090 3000 9093; do
    if ! curl -s "http://localhost:$port" > /dev/null; then
        echo -e "${RED}Erro: Endpoint na porta $port não está respondendo${NC}"
        exit 1
    fi
done

# Mostrar URLs
echo -e "${GREEN}Serviços iniciados com sucesso!${NC}"
echo -e "Prometheus: http://localhost:9090"
echo -e "Grafana: http://localhost:3000"
echo -e "AlertManager: http://localhost:9093"

# Iniciar testes monitorados
echo -e "${YELLOW}Iniciando testes monitorados...${NC}"
python scripts/run_tests_monitored.py

# Verificar resultados
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Testes executados com sucesso!${NC}"
else
    echo -e "${RED}Erro na execução dos testes${NC}"
    exit 1
fi

echo -e "${GREEN}Ambiente de monitoramento configurado e rodando!${NC}"
echo -e "Para parar os serviços, execute: docker-compose -f docker-compose.monitoring.yml down" 