# Cria o namespace autocura se não existir
kubectl create namespace autocura --dry-run=client -o yaml | kubectl apply -f -

# Instala CRDs do Prometheus Operator (necessário para Alertmanager, ServiceMonitor, etc.)
kubectl apply -f https://github.com/prometheus-operator/prometheus-operator/releases/latest/download/bundle.yaml

# Aguarda alguns segundos para os CRDs serem registrados
Start-Sleep -Seconds 10

Write-Host "Aplicando todos os manifests dos componentes..."

kubectl apply -k kubernetes/components

if ($LASTEXITCODE -eq 0) {
    Write-Host "Todos os componentes foram aplicados com sucesso!"
} else {
    Write-Host "Ocorreu um erro ao aplicar os componentes." -ForegroundColor Red
} 