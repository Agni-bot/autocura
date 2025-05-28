# Script de Verificação de Saúde - Sistema AutoCura
# Verifica se todos os componentes estão funcionando corretamente

Write-Host "🏥 Verificação de Saúde - Sistema AutoCura" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Função para verificar container
function Check-Container {
    param(
        [string]$containerName,
        [string]$displayName
    )
    
    $container = docker ps --filter "name=$containerName" --format "table {{.Names}}\t{{.Status}}" | Select-String $containerName
    
    if ($container) {
        Write-Host "✅ $displayName está rodando" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ $displayName não está rodando" -ForegroundColor Red
        return $false
    }
}

# Função para verificar porta
function Check-Port {
    param(
        [int]$port,
        [string]$service
    )
    
    $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue -InformationLevel Quiet
    
    if ($connection) {
        Write-Host "✅ Porta $port ($service) está acessível" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Porta $port ($service) não está acessível" -ForegroundColor Red
        return $false
    }
}

# Função para verificar URL
function Check-URL {
    param(
        [string]$url,
        [string]$service
    )
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $service está respondendo em $url" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "❌ $service não está respondendo em $url" -ForegroundColor Red
        return $false
    }
}

Write-Host "1️⃣ Verificando Containers Docker..." -ForegroundColor Yellow
Write-Host ""

$containers = @(
    @{Name="autocura-omega-core"; Display="Núcleo Cognitivo Omega"},
    @{Name="autocura-api"; Display="API REST"},
    @{Name="autocura-postgres"; Display="PostgreSQL"},
    @{Name="autocura-redis"; Display="Redis Cache"},
    @{Name="autocura-consciousness-monitor"; Display="Monitor de Consciência"},
    @{Name="autocura-integration-orchestrator"; Display="Orquestrador de Integração"},
    @{Name="autocura-evolution-engine"; Display="Motor de Evolução"},
    @{Name="autocura-nginx"; Display="Nginx Proxy"},
    @{Name="autocura-prometheus"; Display="Prometheus"},
    @{Name="autocura-grafana"; Display="Grafana"}
)

$runningContainers = 0
foreach ($container in $containers) {
    if (Check-Container -containerName $container.Name -displayName $container.Display) {
        $runningContainers++
    }
}

Write-Host ""
Write-Host "Containers rodando: $runningContainers/$($containers.Count)" -ForegroundColor $(if ($runningContainers -eq $containers.Count) { "Green" } else { "Yellow" })

Write-Host ""
Write-Host "2️⃣ Verificando Portas..." -ForegroundColor Yellow
Write-Host ""

$ports = @(
    @{Port=80; Service="HTTP (Nginx)"},
    @{Port=8000; Service="API REST"},
    @{Port=3000; Service="Grafana"},
    @{Port=9090; Service="Prometheus"}
)

$openPorts = 0
foreach ($port in $ports) {
    if (Check-Port -port $port.Port -service $port.Service) {
        $openPorts++
    }
}

Write-Host ""
Write-Host "3️⃣ Verificando Serviços..." -ForegroundColor Yellow
Write-Host ""

$services = @(
    @{URL="http://localhost:8000/health"; Service="API Health Check"},
    @{URL="http://localhost:8000/docs"; Service="API Documentation"},
    @{URL="http://localhost:3000"; Service="Grafana Dashboard"},
    @{URL="http://localhost:9090"; Service="Prometheus Metrics"}
)

$activeServices = 0
foreach ($service in $services) {
    if (Check-URL -url $service.URL -service $service.Service) {
        $activeServices++
    }
}

Write-Host ""
Write-Host "4️⃣ Verificando Logs Recentes..." -ForegroundColor Yellow
Write-Host ""

# Verificar logs do núcleo cognitivo
$logs = docker logs autocura-omega-core --tail 5 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "📋 Últimas linhas do log do Núcleo Cognitivo:" -ForegroundColor Cyan
    Write-Host $logs -ForegroundColor Gray
} else {
    Write-Host "⚠️ Não foi possível acessar logs do Núcleo Cognitivo" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "📊 RESUMO DA VERIFICAÇÃO" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

$totalChecks = $containers.Count + $ports.Count + $services.Count
$passedChecks = $runningContainers + $openPorts + $activeServices
$healthPercentage = [math]::Round(($passedChecks / $totalChecks) * 100, 2)

Write-Host "Total de verificações: $totalChecks" -ForegroundColor White
Write-Host "Verificações bem-sucedidas: $passedChecks" -ForegroundColor $(if ($passedChecks -eq $totalChecks) { "Green" } else { "Yellow" })
Write-Host "Saúde do sistema: $healthPercentage%" -ForegroundColor $(if ($healthPercentage -ge 80) { "Green" } elseif ($healthPercentage -ge 50) { "Yellow" } else { "Red" })

if ($healthPercentage -eq 100) {
    Write-Host ""
    Write-Host "🎉 Sistema AutoCura está 100% operacional!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Acesse:" -ForegroundColor Cyan
    Write-Host "  📡 API: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  📊 Grafana: http://localhost:3000" -ForegroundColor White
    Write-Host "  📈 Prometheus: http://localhost:9090" -ForegroundColor White
} elseif ($healthPercentage -ge 50) {
    Write-Host ""
    Write-Host "⚠️ Sistema parcialmente operacional" -ForegroundColor Yellow
    Write-Host "Execute 'docker-compose -f docker-compose.omega.yml ps' para mais detalhes" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Sistema com problemas críticos" -ForegroundColor Red
    Write-Host "Execute 'docker-compose -f docker-compose.omega.yml logs' para diagnosticar" -ForegroundColor White
} 