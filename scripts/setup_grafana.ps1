# Script para configurar o Grafana e importar o dashboard do AutoCura

# Cores para output
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Red = [System.ConsoleColor]::Red

Write-Host "🚀 Configurando Grafana para o AutoCura..." -ForegroundColor $Green

# Verificar se o Grafana está rodando
Write-Host "📡 Verificando status do Grafana..." -ForegroundColor $Yellow
$grafanaStatus = docker ps --filter "name=grafana" --format "{{.Status}}"

if (-not $grafanaStatus) {
    Write-Host "❌ Grafana não está rodando. Iniciando..." -ForegroundColor $Yellow
    
    # Criar diretório para dados do Grafana
    New-Item -ItemType Directory -Force -Path "data/grafana"
    
    # Iniciar Grafana
    docker run -d `
        --name grafana `
        -p 3000:3000 `
        -v "${PWD}/data/grafana:/var/lib/grafana" `
        -v "${PWD}/config/prometheus/dashboards:/etc/grafana/provisioning/dashboards" `
        grafana/grafana:latest
        
    Start-Sleep -Seconds 10
}

# Configurar fonte de dados do Prometheus
Write-Host "⚙️ Configurando fonte de dados do Prometheus..." -ForegroundColor $Yellow

$prometheusConfig = @{
    name = "Prometheus"
    type = "prometheus"
    access = "proxy"
    url = "http://prometheus:9090"
    isDefault = $true
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
}

# Aguardar API do Grafana estar disponível
$maxAttempts = 30
$attempt = 0
$success = $false

while (-not $success -and $attempt -lt $maxAttempts) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:3000/api/health" -Method Get
        if ($response.status -eq "ok") {
            $success = $true
        }
    } catch {
        $attempt++
        Start-Sleep -Seconds 1
    }
}

if (-not $success) {
    Write-Host "❌ Não foi possível conectar ao Grafana" -ForegroundColor $Red
    exit 1
}

# Criar fonte de dados
$response = Invoke-RestMethod `
    -Uri "http://localhost:3000/api/datasources" `
    -Method Post `
    -Headers $headers `
    -Body $prometheusConfig `
    -ContentType "application/json"

Write-Host "✅ Fonte de dados configurada com ID: $($response.id)" -ForegroundColor $Green

# Importar dashboard
Write-Host "📊 Importando dashboard..." -ForegroundColor $Yellow

$dashboardJson = Get-Content -Path "config/prometheus/dashboards/autocura.json" -Raw
$dashboardConfig = @{
    dashboard = $dashboardJson | ConvertFrom-Json
    overwrite = $true
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:3000/api/dashboards/db" `
    -Method Post `
    -Headers $headers `
    -Body $dashboardConfig `
    -ContentType "application/json"

Write-Host "✅ Dashboard importado com sucesso!" -ForegroundColor $Green
Write-Host "🌐 Acesse o Grafana em: http://localhost:3000" -ForegroundColor $Green
Write-Host "👤 Credenciais padrão:" -ForegroundColor $Yellow
Write-Host "   Usuário: admin" -ForegroundColor $Yellow
Write-Host "   Senha: admin" -ForegroundColor $Yellow 