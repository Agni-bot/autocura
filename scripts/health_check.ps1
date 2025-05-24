# Script para verificar a saúde do sistema AutoCura

# Cores para output
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Red = [System.ConsoleColor]::Red

# Função para verificar endpoint
function Test-Endpoint {
    param (
        [string]$Url,
        [string]$Service
    )
    
    try {
        $response = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 5
        if ($response.status -eq "ok") {
            Write-Host "✅ $Service está saudável" -ForegroundColor $Green
            return $true
        } else {
            Write-Host "❌ $Service retornou status não esperado" -ForegroundColor $Red
            return $false
        }
    } catch {
        Write-Host "❌ $Service não está respondendo: $_" -ForegroundColor $Red
        return $false
    }
}

# Função para verificar métricas
function Test-Metrics {
    param (
        [string]$Service
    )
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:9090/metrics" -Method Get -TimeoutSec 5
        if ($response -match $Service) {
            Write-Host "✅ Métricas do $Service estão sendo coletadas" -ForegroundColor $Green
            return $true
        } else {
            Write-Host "❌ Métricas do $Service não encontradas" -ForegroundColor $Red
            return $false
        }
    } catch {
        Write-Host "❌ Não foi possível acessar métricas: $_" -ForegroundColor $Red
        return $false
    }
}

# Função para verificar logs
function Test-Logs {
    param (
        [string]$Service
    )
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8080/logs?limit=1&service=$Service" -Method Get -TimeoutSec 5
        if ($response.logs.Count -gt 0) {
            Write-Host "✅ Logs do $Service estão sendo gerados" -ForegroundColor $Green
            return $true
        } else {
            Write-Host "❌ Nenhum log encontrado para $Service" -ForegroundColor $Red
            return $false
        }
    } catch {
        Write-Host "❌ Não foi possível acessar logs: $_" -ForegroundColor $Red
        return $false
    }
}

Write-Host "🔍 Iniciando verificação de saúde do sistema..." -ForegroundColor $Yellow

# Verificar containers
Write-Host "`n📡 Verificando containers..." -ForegroundColor $Yellow
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

# Verificar endpoints
Write-Host "`n🌐 Verificando endpoints..." -ForegroundColor $Yellow

$endpoints = @(
    @{Url = "http://localhost:9090/health"; Service = "Monitor"},
    @{Url = "http://localhost:8080/health"; Service = "Observador"},
    @{Url = "http://localhost:8080/health"; Service = "Validador"},
    @{Url = "http://localhost:8080/health"; Service = "Guardião"}
)

$allHealthy = $true
foreach ($endpoint in $endpoints) {
    if (-not (Test-Endpoint -Url $endpoint.Url -Service $endpoint.Service)) {
        $allHealthy = $false
    }
}

# Verificar métricas
Write-Host "`n📊 Verificando métricas..." -ForegroundColor $Yellow

$services = @("monitor", "observador", "validador", "guardiao")
$allMetrics = $true
foreach ($service in $services) {
    if (-not (Test-Metrics -Service $service)) {
        $allMetrics = $false
    }
}

# Verificar logs
Write-Host "`n📝 Verificando logs..." -ForegroundColor $Yellow

$allLogs = $true
foreach ($service in $services) {
    if (-not (Test-Logs -Service $service)) {
        $allLogs = $false
    }
}

# Gerar relatório
Write-Host "`n📋 Relatório de Saúde do Sistema" -ForegroundColor $Yellow
Write-Host "----------------------------------------" -ForegroundColor $Yellow

if ($allRunning -and $allHealthy -and $allMetrics -and $allLogs) {
    Write-Host "✅ Sistema está saudável" -ForegroundColor $Green
} else {
    Write-Host "❌ Sistema apresenta problemas" -ForegroundColor $Red
    if (-not $allRunning) { Write-Host "   - Containers não estão todos rodando" -ForegroundColor $Red }
    if (-not $allHealthy) { Write-Host "   - Endpoints não estão todos saudáveis" -ForegroundColor $Red }
    if (-not $allMetrics) { Write-Host "   - Métricas não estão sendo coletadas corretamente" -ForegroundColor $Red }
    if (-not $allLogs) { Write-Host "   - Logs não estão sendo gerados corretamente" -ForegroundColor $Red }
}

# Verificar recursos
Write-Host "`n💻 Recursos do Sistema" -ForegroundColor $Yellow
Write-Host "----------------------------------------" -ForegroundColor $Yellow

# CPU
$cpu = Get-Counter '\Processor(_Total)\% Processor Time' | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue
Write-Host "CPU: $cpu% utilizado" -ForegroundColor $(if ($cpu -gt 80) { $Red } elseif ($cpu -gt 60) { $Yellow } else { $Green })

# Memória
$memory = Get-Counter '\Memory\% Committed Bytes In Use' | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue
Write-Host "Memória: $memory% utilizada" -ForegroundColor $(if ($memory -gt 80) { $Red } elseif ($memory -gt 60) { $Yellow } else { $Green })

# Disco
$disk = Get-Counter '\LogicalDisk(_Total)\% Free Space' | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue
Write-Host "Disco: $disk% livre" -ForegroundColor $(if ($disk -lt 20) { $Red } elseif ($disk -lt 40) { $Yellow } else { $Green }) 