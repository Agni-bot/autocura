# Rebuild e Deploy da API AutoCura no Kubernetes
Write-Host "AutoCura - Rebuild e Deploy da API" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker nao encontrado!"
    exit 1
}

# Verificar kubectl
if (!(Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Error "kubectl nao encontrado!"
    exit 1
}

# Variaveis
$namespace = "autocura-staging"
$imageName = "autocura/api:latest"
$deploymentName = "autocura-api"

Write-Host "Namespace: $namespace" -ForegroundColor Magenta
Write-Host "Imagem: $imageName" -ForegroundColor Magenta
Write-Host ""

# Verificar msgpack no requirements.txt
Write-Host "Verificando dependencias..." -ForegroundColor Yellow
$requirements = Get-Content "requirements.txt"
if ($requirements -match "msgpack") {
    Write-Host "msgpack encontrado no requirements.txt" -ForegroundColor Green
}

# Build da imagem Docker
Write-Host ""
Write-Host "Construindo imagem Docker..." -ForegroundColor Yellow
docker build -t $imageName -f docker/environments/prod/Dockerfile.api .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Imagem construida com sucesso!" -ForegroundColor Green
} else {
    Write-Error "Falha ao construir imagem!"
    exit 1
}

# Verificar deployment
Write-Host ""
Write-Host "Verificando deployment..." -ForegroundColor Yellow
$deploymentExists = kubectl get deployment $deploymentName -n $namespace 2>$null

if ($deploymentExists) {
    Write-Host "Deployment encontrado" -ForegroundColor Green
    
    # Listar pods atuais
    Write-Host ""
    Write-Host "Pods atuais:" -ForegroundColor Yellow
    kubectl get pods -n $namespace -l app=autocura-api
    
    # Restart dos pods
    Write-Host ""
    Write-Host "Reiniciando pods..." -ForegroundColor Yellow
    kubectl rollout restart deployment/$deploymentName -n $namespace
    
    # Aguardar rollout
    Write-Host "Aguardando rollout..." -ForegroundColor Yellow
    kubectl rollout status deployment/$deploymentName -n $namespace --timeout=300s
}

# Status final
Write-Host ""
Write-Host "Status dos pods:" -ForegroundColor Yellow
kubectl get pods -n $namespace -l app=autocura-api

Write-Host ""
Write-Host "Processo concluido!" -ForegroundColor Green
Write-Host ""
Write-Host "Para verificar logs:" -ForegroundColor Yellow
Write-Host "kubectl logs -n $namespace -l app=autocura-api -f" -ForegroundColor White
Write-Host ""
Write-Host "Para port-forward:" -ForegroundColor Yellow
Write-Host "kubectl port-forward -n $namespace service/autocura-api-service 8000:8000" -ForegroundColor White 