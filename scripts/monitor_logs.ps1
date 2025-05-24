# Script para monitorar logs em tempo real do AutoCura

# Cores para output
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Red = [System.ConsoleColor]::Red
$Blue = [System.ConsoleColor]::Blue
$Magenta = [System.ConsoleColor]::Magenta

# Função para monitorar logs de um serviço
function Monitor-Logs {
    param (
        [string]$Service,
        [System.ConsoleColor]$Color
    )
    
    Write-Host "📝 Monitorando logs do $Service..." -ForegroundColor $Color
    docker-compose -f docker/docker-compose.testados.yml logs -f $Service
}

# Verificar se os containers estão rodando
Write-Host "📡 Verificando status dos containers..." -ForegroundColor $Yellow
$containers = docker-compose -f docker/docker-compose.testados.yml ps --format json | ConvertFrom-Json

$allRunning = $true
foreach ($container in $containers) {
    if ($container.State -ne "running") {
        Write-Host "❌ Container $($container.Service) não está rodando" -ForegroundColor $Red
        $allRunning = $false
    }
}

if (-not $allRunning) {
    Write-Host "❌ Alguns containers não estão rodando. Iniciando..." -ForegroundColor $Yellow
    docker-compose -f docker/docker-compose.testados.yml up -d
    Start-Sleep -Seconds 10
}

# Iniciar monitoramento em paralelo
Write-Host "🚀 Iniciando monitoramento de logs..." -ForegroundColor $Green

$jobs = @()

# Monitor
$jobs += Start-Job -ScriptBlock {
    param($Service, $Color)
    docker-compose -f docker/docker-compose.testados.yml logs -f $Service
} -ArgumentList "monitor", $Green

# Observador
$jobs += Start-Job -ScriptBlock {
    param($Service, $Color)
    docker-compose -f docker/docker-compose.testados.yml logs -f $Service
} -ArgumentList "observador", $Blue

# Validador
$jobs += Start-Job -ScriptBlock {
    param($Service, $Color)
    docker-compose -f docker/docker-compose.testados.yml logs -f $Service
} -ArgumentList "validador", $Yellow

# Guardião
$jobs += Start-Job -ScriptBlock {
    param($Service, $Color)
    docker-compose -f docker/docker-compose.testados.yml logs -f $Service
} -ArgumentList "guardiao", $Magenta

Write-Host "✨ Monitoramento iniciado. Pressione Ctrl+C para parar." -ForegroundColor $Green

try {
    # Aguardar jobs
    $jobs | Wait-Job
} finally {
    # Limpar jobs
    $jobs | Remove-Job
} 