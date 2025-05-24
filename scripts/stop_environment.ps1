# Script para parar o ambiente do AutoCura

# Cores para output
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Red = [System.ConsoleColor]::Red

Write-Host "🛑 Parando ambiente do AutoCura..." -ForegroundColor $Yellow

# Parar containers
Write-Host "🐳 Parando containers..." -ForegroundColor $Yellow
docker-compose -f docker/docker-compose.testados.yml down

# Verificar se todos os containers foram parados
$containers = docker ps --filter "name=autocura" --format "{{.Names}}"
if ($containers) {
    Write-Host "❌ Alguns containers ainda estão rodando:" -ForegroundColor $Red
    $containers | ForEach-Object { Write-Host "   - $_" -ForegroundColor $Red }
    
    # Forçar parada dos containers restantes
    Write-Host "🔄 Forçando parada dos containers restantes..." -ForegroundColor $Yellow
    $containers | ForEach-Object { docker stop $_ }
}

# Limpar volumes (opcional)
$cleanVolumes = Read-Host "Deseja remover os volumes? (s/N)"
if ($cleanVolumes -eq "s") {
    Write-Host "🧹 Removendo volumes..." -ForegroundColor $Yellow
    docker volume rm autocura_redis_data autocura_es_data
}

Write-Host "✨ Ambiente parado com sucesso!" -ForegroundColor $Green 