# Script de Deploy do AutoCura para Kubernetes
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("staging", "production", "dev")]
    [string]$Environment = "staging",
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun,
    
    [Parameter(Mandatory=$false)]
    [switch]$BuildImages,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipPreChecks
)

# Cores para output
$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host "🚀 AutoCura - Deploy para Kubernetes" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar pré-requisitos
if (-not $SkipPreChecks) {
    Write-Host "📋 Verificando pré-requisitos..." -ForegroundColor Yellow
    
    # Verificar Docker
    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "❌ Docker não encontrado! Por favor, instale o Docker Desktop."
        exit 1
    }
    
    # Verificar kubectl
    if (!(Get-Command kubectl -ErrorAction SilentlyContinue)) {
        Write-Error "❌ kubectl não encontrado! Por favor, instale o kubectl."
        exit 1
    }
    
    # Verificar se Kubernetes está rodando
    try {
        kubectl cluster-info | Out-Null
        Write-Host "✅ Kubernetes está rodando" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Kubernetes não está acessível. Ativando no Docker Desktop..." -ForegroundColor Yellow
        Write-Host "Por favor, ative o Kubernetes no Docker Desktop e execute novamente." -ForegroundColor Red
        exit 1
    }
}

# 2. Definir namespace baseado no ambiente
$namespace = "autocura-$Environment"
Write-Host ""
Write-Host "🎯 Ambiente: $Environment" -ForegroundColor Magenta
Write-Host "📦 Namespace: $namespace" -ForegroundColor Magenta
Write-Host ""

# 3. Build das imagens Docker (se solicitado)
if ($BuildImages) {
    Write-Host "🔨 Construindo imagens Docker..." -ForegroundColor Yellow
    
    # API Principal
    Write-Host "  - Construindo autocura/api..." -ForegroundColor Cyan
    docker build -t autocura/api:latest -f docker/environments/prod/Dockerfile.api .
    
    # Omega Core
    Write-Host "  - Construindo autocura/omega-core..." -ForegroundColor Cyan
    docker build -t autocura/omega-core:latest -f Dockerfile.omega . --build-arg SERVICE=omega-core
    
    # Consciousness Monitor
    Write-Host "  - Construindo autocura/consciousness-monitor..." -ForegroundColor Cyan
    docker build -t autocura/consciousness-monitor:latest -f Dockerfile.omega . --build-arg SERVICE=consciousness-monitor
    
    # Evolution Engine
    Write-Host "  - Construindo autocura/evolution-engine..." -ForegroundColor Cyan
    docker build -t autocura/evolution-engine:latest -f Dockerfile.omega . --build-arg SERVICE=evolution-engine
    
    # Integration Orchestrator
    Write-Host "  - Construindo autocura/integration-orchestrator..." -ForegroundColor Cyan
    docker build -t autocura/integration-orchestrator:latest -f Dockerfile.omega . --build-arg SERVICE=integration-orchestrator
    
    Write-Host "✅ Imagens construídas com sucesso!" -ForegroundColor Green
    Write-Host ""
}

# 4. Criar namespace se não existir
Write-Host "📁 Criando namespace..." -ForegroundColor Yellow
if ($DryRun) {
    kubectl create namespace $namespace --dry-run=client -o yaml
} else {
    kubectl create namespace $namespace --dry-run=client -o yaml | kubectl apply -f -
}

# 5. Aplicar configurações base
Write-Host ""
Write-Host "⚙️  Aplicando configurações..." -ForegroundColor Yellow

$baseDir = "deployment/kubernetes"
$applyCommand = if ($DryRun) { "apply --dry-run=client" } else { "apply" }

# Ordem de aplicação
$deployOrder = @(
    "base/namespace.yaml",
    "base/configmap.yaml",
    "base/secrets.yaml",
    "storage/postgres-pvc.yaml",
    "databases/postgres-deployment.yaml",
    "databases/redis-deployment.yaml",
    "apps/api-deployment.yaml",
    "apps/omega-deployments.yaml",
    "monitoring/prometheus-grafana.yaml",
    "ingress/nginx-ingress.yaml"
)

foreach ($file in $deployOrder) {
    $filePath = Join-Path $baseDir $file
    if (Test-Path $filePath) {
        Write-Host "  - Aplicando $file..." -ForegroundColor Cyan
        
        # Substituir namespace no arquivo temporariamente
        $content = Get-Content $filePath -Raw
        $content = $content -replace "namespace: autocura-staging", "namespace: $namespace"
        
        # Aplicar via pipe
        if ($DryRun) {
            $content | kubectl apply -n $namespace --dry-run=client -f -
        } else {
            $content | kubectl apply -n $namespace -f -
        }
    } else {
        Write-Host "  ⚠️  Arquivo não encontrado: $filePath" -ForegroundColor Yellow
    }
}

# 6. Aguardar pods ficarem prontos (se não for dry-run)
if (-not $DryRun) {
    Write-Host ""
    Write-Host "⏳ Aguardando pods ficarem prontos..." -ForegroundColor Yellow
    
    # Aguardar PostgreSQL
    Write-Host "  - Aguardando PostgreSQL..." -ForegroundColor Cyan
    kubectl wait --for=condition=ready pod -l app=postgres -n $namespace --timeout=120s
    
    # Aguardar Redis
    Write-Host "  - Aguardando Redis..." -ForegroundColor Cyan
    kubectl wait --for=condition=ready pod -l app=redis -n $namespace --timeout=60s
    
    # Aguardar API
    Write-Host "  - Aguardando API..." -ForegroundColor Cyan
    kubectl wait --for=condition=ready pod -l app=autocura-api -n $namespace --timeout=120s
    
    Write-Host "✅ Todos os pods principais estão prontos!" -ForegroundColor Green
}

# 7. Mostrar status
Write-Host ""
Write-Host "📊 Status do Deploy:" -ForegroundColor Yellow
kubectl get all -n $namespace

# 8. Mostrar URLs de acesso
Write-Host ""
Write-Host "🌐 URLs de Acesso:" -ForegroundColor Yellow
Write-Host "  - API Principal: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - Consciousness Monitor: http://localhost:9002" -ForegroundColor Cyan
Write-Host "  - Evolution Engine: http://localhost:9003" -ForegroundColor Cyan
Write-Host "  - Integration Orchestrator: http://localhost:9004" -ForegroundColor Cyan
Write-Host "  - Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host "  - Grafana: http://localhost:3000" -ForegroundColor Cyan

# 9. Configurar port-forward para acesso local
if (-not $DryRun) {
    Write-Host ""
    Write-Host "🔌 Deseja configurar port-forward para acesso local? (S/N)" -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -eq "S" -or $response -eq "s") {
        Write-Host "Configurando port-forward..." -ForegroundColor Cyan
        
        # Criar script de port-forward
        $portForwardScript = @"
# Port-forward para serviços do AutoCura
Write-Host "Iniciando port-forward para AutoCura..." -ForegroundColor Green

# API
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward -n $namespace service/autocura-api-service 8000:8000"

# Grafana
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward -n $namespace service/grafana-service 3000:3000"

# Prometheus
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward -n $namespace service/prometheus-service 9090:9090"

Write-Host "Port-forward iniciado! Pressione qualquer tecla para parar..."
Read-Host
"@
        
        $portForwardScript | Out-File -FilePath "port-forward-autocura.ps1" -Encoding UTF8
        Write-Host "✅ Script de port-forward criado: port-forward-autocura.ps1" -ForegroundColor Green
        
        # Executar port-forward
        & .\port-forward-autocura.ps1
    }
}

Write-Host ""
Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host ""

# 10. Instruções finais
Write-Host "📝 Próximos passos:" -ForegroundColor Yellow
Write-Host "  1. Verificar logs: kubectl logs -n $namespace -l app=autocura-api" -ForegroundColor White
Write-Host "  2. Acessar dashboard: kubectl port-forward -n $namespace service/autocura-api-service 8000:8000" -ForegroundColor White
Write-Host "  3. Monitorar métricas: kubectl port-forward -n $namespace service/grafana-service 3000:3000" -ForegroundColor White
Write-Host "" 