# Script para configurar um ambiente Kubernetes local usando kind no Windows
# para o Sistema Autocura Cognitiva

Write-Host "=== Configurando ambiente Kubernetes local com kind ==="

# Verificar se o kind está instalado
try {
    $kindVersion = kind version
    Write-Host "kind versão: $kindVersion"
} catch {
    Write-Host "kind não está instalado. Por favor, instale-o seguindo as instruções em:"
    Write-Host "https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    exit 1
}

# Verificar se o kubectl está instalado
try {
    $kubectlVersion = kubectl version --client
    Write-Host "kubectl versão: $kubectlVersion"
} catch {
    Write-Host "kubectl não está instalado. Por favor, instale-o seguindo as instruções em:"
    Write-Host "https://kubernetes.io/docs/tasks/tools/install-kubectl/"
    exit 1
}

# Verificar se o Docker está instalado e em execução
try {
    $dockerInfo = docker info
    Write-Host "Docker está em execução"
} catch {
    Write-Host "Docker não está instalado ou não está em execução."
    Write-Host "Por favor, instale o Docker Desktop e inicie-o antes de continuar."
    exit 1
}

# Verificar portas
$port30000 = Get-NetTCPConnection -LocalPort 30000 -ErrorAction SilentlyContinue
$port30001 = Get-NetTCPConnection -LocalPort 30001 -ErrorAction SilentlyContinue
$port5000 = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue

if ($port30000) {
    Write-Host "Porta 30000 já está em uso"
}
if ($port30001) {
    Write-Host "Porta 30001 já está em uso"
}
if ($port5000) {
    Write-Host "Porta 5000 já está em uso"
}

# Verificar se o cluster já existe e excluí-lo
$existingClusters = kind get clusters
if ($existingClusters -contains "autocura") {
    Write-Host "Cluster 'autocura' já existe. Excluindo..."
    kind delete cluster --name autocura
}

# Iniciar o registro local se ainda não estiver em execução
$registry = docker ps --filter "name=registry" --format "{{.Names}}"
if (-not $registry) {
    Write-Host "Iniciando registro Docker local na porta 5000..."
    docker run -d -p 5000:5000 --restart=always --name registry registry:2
} else {
    Write-Host "Registro local já está em execução."
}

# Criar uma rede Docker para o kind e o registro se não existir
$kindNetwork = docker network ls --filter "name=kind" --format "{{.Name}}"
if (-not $kindNetwork) {
    Write-Host "Criando rede Docker 'kind'..."
    docker network create kind
}

# Conectar o registro à rede kind
$registryInKind = docker network inspect kind | Select-String "registry"
if (-not $registryInKind) {
    Write-Host "Conectando o registro à rede kind..."
    docker network connect kind registry
}

# Criar cluster kind com a configuração personalizada
Write-Host "Criando cluster kind 'autocura'..."
kind create cluster --config kind-config.yaml

# Verificar se o cluster foi criado com sucesso
$clusters = kind get clusters
if (-not ($clusters -contains "autocura")) {
    Write-Host "Falha ao criar o cluster kind."
    exit 1
}

Write-Host "Cluster kind 'autocura' criado com sucesso!"

# Configurar kubectl para usar o contexto do kind
kubectl cluster-info --context kind-autocura

# Voltar ao diretório raiz do projeto
Set-Location (Split-Path $PSScriptRoot -Parent)

# Aplicar recursos base
Write-Host "Aplicando recursos base do Kubernetes..."
kubectl apply -k ../kubernetes/base

# Versão do Prometheus Operator
$PROMETHEUS_OPERATOR_VERSION = "v0.73.0"

# Instalar CRDs do Prometheus Operator (apenas os necessários)
Write-Host "Instalando CRDs do Prometheus Operator..."
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/v0.65.1/example/prometheus-operator-crd/monitoring.coreos.com_alertmanagers.yaml
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/v0.65.1/example/prometheus-operator-crd/monitoring.coreos.com_prometheuses.yaml
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/v0.65.1/example/prometheus-operator-crd/monitoring.coreos.com_servicemonitors.yaml
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/v0.65.1/example/prometheus-operator-crd/monitoring.coreos.com_podmonitors.yaml
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/v0.65.1/example/prometheus-operator-crd/monitoring.coreos.com_prometheusrules.yaml

# Aplicar recursos de monitoring
Write-Host "Aplicando recursos de monitoring..."
kubectl apply -k ../kubernetes/monitoring

Write-Host "=== Ambiente Kubernetes local configurado com sucesso! ==="
Write-Host "Agora você pode executar 'build.ps1' para construir as imagens e"
Write-Host "em seguida 'kubectl apply -k kubernetes\environments\development' para implantar o sistema." 