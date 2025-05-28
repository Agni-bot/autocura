# Script para reconstruir containers Omega com correcoes

Write-Host "Reconstruindo containers Omega com correcoes..." -ForegroundColor Green
Write-Host ""

# Parar containers existentes
Write-Host "Parando containers existentes..." -ForegroundColor Yellow
docker-compose -f docker/environments/prod/docker-compose.omega-complete.yml down

# Limpar imagens antigas
Write-Host "Limpando imagens antigas..." -ForegroundColor Yellow
docker rmi prod-omega-core:latest prod-consciousness-monitor:latest prod-evolution-engine:latest prod-integration-orchestrator:latest -f 2>$null

# Reconstruir imagens
Write-Host "Reconstruindo imagens..." -ForegroundColor Yellow
docker-compose -f docker/environments/prod/docker-compose.omega-complete.yml build --no-cache omega-core consciousness-monitor evolution-engine integration-orchestrator

# Iniciar containers
Write-Host "Iniciando containers..." -ForegroundColor Yellow
docker-compose -f docker/environments/prod/docker-compose.omega-complete.yml up -d

# Aguardar inicializacao
Write-Host "Aguardando inicializacao dos servicos..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Verificar status
Write-Host ""
Write-Host "Status dos containers:" -ForegroundColor Cyan
docker-compose -f docker/environments/prod/docker-compose.omega-complete.yml ps

# Verificar logs dos servicos Omega
Write-Host ""
Write-Host "Logs dos servicos Omega:" -ForegroundColor Cyan

Write-Host "`n--- Omega Core ---" -ForegroundColor Yellow
docker logs autocura-omega-core --tail 20

Write-Host "`n--- Consciousness Monitor ---" -ForegroundColor Yellow
docker logs autocura-consciousness-monitor --tail 20

Write-Host "`n--- Evolution Engine ---" -ForegroundColor Yellow
docker logs autocura-evolution-engine --tail 20

Write-Host "`n--- Integration Orchestrator ---" -ForegroundColor Yellow
docker logs autocura-integration-orchestrator --tail 20

# Testar endpoints
Write-Host ""
Write-Host "Testando endpoints dos servicos:" -ForegroundColor Cyan

# Funcao para testar endpoint
function Test-Endpoint {
    param($url, $service)
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "OK $service" -ForegroundColor Green
        } else {
            Write-Host "AVISO $service : Status $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "ERRO $service : $_" -ForegroundColor Red
    }
}

# Testar cada servico
Test-Endpoint "http://localhost:9002/health" "Monitor de Consciencia"
Test-Endpoint "http://localhost:9003/health" "Motor de Evolucao"
Test-Endpoint "http://localhost:9004/health" "Orquestrador de Integracao"

Write-Host ""
Write-Host "Reconstrucao concluida!" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "   1. Verificar logs para erros: docker logs [container-name]" -ForegroundColor White
Write-Host "   2. Acessar dashboards:" -ForegroundColor White
Write-Host "      - API Principal: http://localhost:8000/docs" -ForegroundColor White
Write-Host "      - Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "      - Grafana: http://localhost:3000" -ForegroundColor White
Write-Host "   3. Monitorar metricas de consciencia emergente" -ForegroundColor White 