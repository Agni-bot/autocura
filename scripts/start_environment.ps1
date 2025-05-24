# Script para iniciar todo o ambiente do AutoCura

# Cores para output
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Red = [System.ConsoleColor]::Red

Write-Host "🚀 Iniciando ambiente do AutoCura..." -ForegroundColor $Green

# Criar diretórios necessários
Write-Host "📁 Criando diretórios..." -ForegroundColor $Yellow
New-Item -ItemType Directory -Force -Path "data/grafana"
New-Item -ItemType Directory -Force -Path "data/elasticsearch"
New-Item -ItemType Directory -Force -Path "data/redis"

# Iniciar containers
Write-Host "🐳 Iniciando containers..." -ForegroundColor $Yellow
docker-compose -f docker/docker-compose.testados.yml up -d

# Aguardar serviços estarem prontos
Write-Host "⏳ Aguardando serviços estarem prontos..." -ForegroundColor $Yellow
Start-Sleep -Seconds 30

# Verificar status dos containers
Write-Host "📡 Verificando status dos containers..." -ForegroundColor $Yellow
$containers = docker-compose -f docker/docker-compose.testados.yml ps --format json | ConvertFrom-Json

$allRunning = $true
foreach ($container in $containers) {
    if ($container.State -ne "running") {
        Write-Host "❌ Container $($container.Service) não está rodando" -ForegroundColor $Red
        $allRunning = $false
    } else {
        Write-Host "✅ Container $($container.Service) está rodando" -ForegroundColor $Green
    }
}

if (-not $allRunning) {
    Write-Host "❌ Alguns containers não estão rodando corretamente" -ForegroundColor $Red
    exit 1
}

# Configurar Grafana
Write-Host "📊 Configurando Grafana..." -ForegroundColor $Yellow
& .\scripts\setup_grafana.ps1

# Executar testes de integração
Write-Host "🧪 Executando testes de integração..." -ForegroundColor $Yellow
& .\scripts\run_tests.ps1

Write-Host "✨ Ambiente iniciado com sucesso!" -ForegroundColor $Green
Write-Host "🌐 Endpoints disponíveis:" -ForegroundColor $Yellow
Write-Host "   - Monitor: http://localhost:9090" -ForegroundColor $Yellow
Write-Host "   - Observador: http://localhost:8080" -ForegroundColor $Yellow
Write-Host "   - Prometheus: http://localhost:9091" -ForegroundColor $Yellow
Write-Host "   - Grafana: http://localhost:3000" -ForegroundColor $Yellow
Write-Host "   - Elasticsearch: http://localhost:9200" -ForegroundColor $Yellow 