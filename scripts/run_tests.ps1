# Script para executar testes de integração do AutoCura

# Cores para output
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Red = [System.ConsoleColor]::Red

Write-Host "🚀 Iniciando testes de integração do AutoCura..." -ForegroundColor $Green

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

# Instalar dependências de teste
Write-Host "📦 Instalando dependências de teste..." -ForegroundColor $Yellow
pip install pytest pytest-asyncio requests

# Executar testes
Write-Host "🧪 Executando testes de integração..." -ForegroundColor $Green
pytest tests/test_integracao.py -v

# Verificar resultados
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Todos os testes passaram!" -ForegroundColor $Green
} else {
    Write-Host "❌ Alguns testes falharam. Verifique os logs acima." -ForegroundColor $Red
}

# Gerar relatório de cobertura
Write-Host "📊 Gerando relatório de cobertura..." -ForegroundColor $Yellow
pytest tests/test_integracao.py --cov=modulos --cov-report=html

Write-Host "📝 Relatório de cobertura gerado em htmlcov/index.html" -ForegroundColor $Green 