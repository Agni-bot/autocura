# Cores para output
$VERDE = "`e[32m"
$AMARELO = "`e[33m"
$VERMELHO = "`e[31m"
$NC = "`e[0m"

Write-Host "$AMARELO Iniciando build e deploy dos módulos testados... $NC"

# Criar rede se não existir
docker network create autocura-network 2>$null

# Build da imagem base
Write-Host "$AMARELO Build da imagem base... $NC"
docker build -t autocura/base:latest -f docker/Dockerfile .

# Build dos módulos testados
Write-Host "$AMARELO Build dos módulos testados... $NC"

# Módulo de Monitoramento
Write-Host "$VERDE Build do módulo de Monitoramento... $NC"
docker build -t autocura/monitor:latest -f docker/Dockerfile.monitor .

# Módulo de Observabilidade
Write-Host "$VERDE Build do módulo de Observabilidade... $NC"
docker build -t autocura/observador:latest -f docker/Dockerfile.observador .

# Módulo de Validação Ética
Write-Host "$VERDE Build do módulo de Validação Ética... $NC"
docker build -t autocura/validador:latest -f docker/Dockerfile.validador .

# Módulo Guardião
Write-Host "$VERDE Build do módulo Guardião... $NC"
docker build -t autocura/guardiao:latest -f docker/Dockerfile.guardiao .

# Subir os containers
Write-Host "$AMARELO Subindo os containers... $NC"
docker-compose -f docker/docker-compose.testados.yml up -d

Write-Host "$VERDE Deploy concluído! $NC"
Write-Host "$AMARELO Verificando status dos containers... $NC"
docker-compose -f docker/docker-compose.testados.yml ps 