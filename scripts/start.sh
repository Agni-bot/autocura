#!/bin/bash

# Cria diretórios necessários
mkdir -p logs data config/prometheus config/grafana/provisioning/datasources config/grafana/provisioning/dashboards

# Inicia os containers
docker-compose up -d

# Aguarda os serviços iniciarem
echo "Aguardando serviços iniciarem..."
sleep 10

# Verifica se os serviços estão rodando
echo "Verificando status dos serviços..."
docker-compose ps

echo "Sistema iniciado com sucesso!"
echo "Acesse:"
echo "- Grafana: http://localhost:3000 (usuário: admin, senha: admin)"
echo "- Prometheus: http://localhost:9090" 