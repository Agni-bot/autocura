#!/bin/bash

# Cria a rede docker se não existir
if ! docker network ls | grep -q autocura-net; then
  echo "Criando rede Docker autocura-net..."
  docker network create autocura-net
else
  echo "Rede Docker autocura-net já existe."
fi

# Para e remove containers antigos, se existirem
for svc in observabilidade monitoramento diagnostico gerador-acoes; do
  if docker ps -a --format '{{.Names}}' | grep -q "^$svc$"; then
    echo "Removendo container antigo: $svc"
    docker stop $svc
    docker rm $svc
  fi
done

# Sobe o serviço de monitoramento
echo "Subindo monitoramento..."
docker run -d --name monitoramento --network autocura-net -p 8081:8081 localhost:5000/autocura-cognitiva/monitoramento:dev

# Sobe o serviço de diagnóstico
echo "Subindo diagnostico..."
docker run -d --name diagnostico --network autocura-net -p 5002:5002 localhost:5000/autocura-cognitiva/diagnostico:dev

# Sobe o serviço de gerador de ações
echo "Subindo gerador-acoes..."
docker run -d --name gerador-acoes --network autocura-net -p 5003:5003 localhost:5000/autocura-cognitiva/gerador-acoes:dev

# Sobe o serviço de observabilidade
# (Ajusta as variáveis de ambiente para apontar para os nomes dos containers)
echo "Subindo observabilidade..."
docker run -d --name observabilidade --network autocura-net -p 8080:8080 \
  -e MONITORAMENTO_URL=http://monitoramento:8081 \
  -e DIAGNOSTICO_URL=http://diagnostico:5002 \
  -e GERADOR_URL=http://gerador-acoes:5003 \
  localhost:5000/autocura-cognitiva/observabilidade:dev

echo "Todos os serviços do autocura foram iniciados!"
echo "Acesse o painel em: http://localhost:8080" 