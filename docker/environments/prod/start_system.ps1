# Script de Inicialização - Sistema AutoCura Omega
# Inicia todos os serviços em ordem correta

Write-Host "🚀 Iniciando Sistema AutoCura - Fase Omega" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se .env existe
if (-not (Test-Path ".env")) {
    Write-Host "❌ Arquivo .env não encontrado!" -ForegroundColor Red
    Write-Host "Execute primeiro: .\setup_security.ps1" -ForegroundColor Yellow
    exit 1
}

# Verificar se Docker está rodando
try {
    docker version | Out-Null
} catch {
    Write-Host "❌ Docker não está rodando!" -ForegroundColor Red
    Write-Host "Por favor, inicie o Docker Desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Docker está rodando" -ForegroundColor Green
Write-Host ""

# Parar containers antigos se existirem
Write-Host "🛑 Parando containers antigos..." -ForegroundColor Yellow
docker-compose -f docker-compose.omega.yml down 2>$null

Write-Host ""
Write-Host "🏗️ Construindo imagens (pode levar alguns minutos)..." -ForegroundColor Yellow
$buildResult = docker-compose -f docker-compose.omega.yml build 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao construir imagens!" -ForegroundColor Red
    Write-Host $buildResult -ForegroundColor Red
    exit 1
}

Write-Host "✅ Imagens construídas com sucesso!" -ForegroundColor Green
Write-Host ""

# Iniciar serviços base primeiro (banco de dados e cache)
Write-Host "🗄️ Iniciando serviços de dados..." -ForegroundColor Yellow
docker-compose -f docker-compose.omega.yml up -d postgres redis

# Aguardar serviços estarem prontos
Write-Host "⏳ Aguardando banco de dados..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar se PostgreSQL está pronto
$pgReady = $false
$attempts = 0
while (-not $pgReady -and $attempts -lt 30) {
    $pgCheck = docker exec autocura-postgres pg_isready -U autocura 2>&1
    if ($LASTEXITCODE -eq 0) {
        $pgReady = $true
        Write-Host "✅ PostgreSQL está pronto!" -ForegroundColor Green
    } else {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
        $attempts++
    }
}

if (-not $pgReady) {
    Write-Host ""
    Write-Host "❌ PostgreSQL não iniciou corretamente!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🧠 Iniciando núcleo cognitivo e serviços..." -ForegroundColor Yellow
docker-compose -f docker-compose.omega.yml up -d

Write-Host ""
Write-Host "⏳ Aguardando todos os serviços iniciarem..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verificar status
Write-Host ""
Write-Host "📊 Status dos containers:" -ForegroundColor Yellow
docker-compose -f docker-compose.omega.yml ps

Write-Host ""
Write-Host "🔍 Verificando saúde do sistema..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Executar verificação de saúde
if (Test-Path ".\health_check.ps1") {
    Write-Host ""
    & .\health_check.ps1
} else {
    Write-Host "⚠️ Script de verificação de saúde não encontrado" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🎉 Sistema AutoCura iniciado!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "📡 Acesse os serviços:" -ForegroundColor Cyan
Write-Host "  - API REST: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - Grafana: http://localhost:3000 (admin/senha do .env)" -ForegroundColor White
Write-Host "  - Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host ""
Write-Host "📋 Comandos úteis:" -ForegroundColor Cyan
Write-Host "  - Ver logs: docker-compose -f docker-compose.omega.yml logs -f" -ForegroundColor White
Write-Host "  - Parar sistema: docker-compose -f docker-compose.omega.yml down" -ForegroundColor White
Write-Host "  - Ver status: docker-compose -f docker-compose.omega.yml ps" -ForegroundColor White
Write-Host "" 