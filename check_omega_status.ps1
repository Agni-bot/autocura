# Script para verificar status dos servicos Omega

Write-Host "Verificando status dos servicos Omega..." -ForegroundColor Green
Write-Host ""

# Verificar containers
Write-Host "Containers rodando:" -ForegroundColor Cyan
docker ps --filter "name=autocura" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host ""
Write-Host "Testando endpoints internos via Docker:" -ForegroundColor Cyan

# Testar Monitor de Consciencia
Write-Host "`nMonitor de Consciencia (porta 9002):" -ForegroundColor Yellow
docker exec autocura-api curl -s http://consciousness-monitor:9002/health | ConvertFrom-Json | ConvertTo-Json

# Testar Motor de Evolucao
Write-Host "`nMotor de Evolucao (porta 9003):" -ForegroundColor Yellow
docker exec autocura-api curl -s http://evolution-engine:9003/health | ConvertFrom-Json | ConvertTo-Json

# Testar Orquestrador
Write-Host "`nOrquestrador de Integracao (porta 9004):" -ForegroundColor Yellow
docker exec autocura-api curl -s http://integration-orchestrator:9004/health | ConvertFrom-Json | ConvertTo-Json

# Testar API principal
Write-Host "`nAPI Principal (porta 8000):" -ForegroundColor Yellow
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json

# Verificar metricas de consciencia
Write-Host "`nMetricas de Consciencia:" -ForegroundColor Cyan
docker exec autocura-api curl -s http://consciousness-monitor:9002/metrics | ConvertFrom-Json | ConvertTo-Json

Write-Host ""
Write-Host "Status completo verificado!" -ForegroundColor Green 