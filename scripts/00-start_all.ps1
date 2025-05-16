# Script para inicializar todo o Sistema de Autocura Cognitiva no Kubernetes local (Kind)
<<<<<<< HEAD
# Versão: 2.0.2
=======
# Versão: 2.0.5
>>>>>>> origin/main
# Última atualização: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# Configuração de codificação
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Configurações globais
$BASE_DIR = Split-Path $PSScriptRoot -Parent
$LOG_DIR = Join-Path $PSScriptRoot "logs"
$LOG_FILE = Join-Path $LOG_DIR "startup_$(Get-Date -Format 'yyyyMMdd_HHmm').log"
$MAX_RETRIES = 3
$TIMEOUT_SECONDS = 300
$REGISTRY = "localhost:5000"
$TAG = "latest"
$NAMESPACE = "autocura"
<<<<<<< HEAD

# Funções utilitárias
function Write-LogInfo {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[INFO] $Message"
    Add-Content -Path $LOG_FILE -Value "[$timestamp] [INFO] $Message"
}

function Write-LogError {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[ERRO] $Message" -ForegroundColor Red
    Add-Content -Path $LOG_FILE -Value "[$timestamp] [ERRO] $Message"
    return 1
=======
$SERVICES = @("will", "monitoramento", "diagnostico", "gerador", "observabilidade", "executor-acoes")
$PROMETHEUS_OPERATOR_VERSION = "v0.73.0"

# Funções utilitárias
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-LogInfo {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-ColorOutput Green "[INFO] $Message"
    Add-Content -Path $LOG_FILE -Value "[$timestamp] [INFO] $Message"
}

function Write-LogWarn {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-ColorOutput Yellow "[WARN] $Message"
    Add-Content -Path $LOG_FILE -Value "[$timestamp] [WARN] $Message"
}

function Write-LogError {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-ColorOutput Red "[ERRO] $Message"
    Add-Content -Path $LOG_FILE -Value "[$timestamp] [ERRO] $Message"
>>>>>>> origin/main
}

# Criar diretório de logs se não existir
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR | Out-Null
}

Write-LogInfo "Iniciando script de inicialização do Sistema de Autocura Cognitiva"
Write-LogInfo "Logs serão salvos em: $LOG_FILE"

# 1. Verificar pré-requisitos
function Check-Prerequisites {
<<<<<<< HEAD
=======
    $result = 0
>>>>>>> origin/main
    Write-LogInfo "Verificando pré-requisitos..."

    # Verificar Docker
    try {
<<<<<<< HEAD
        $dockerVersion = docker --version
        Write-LogInfo "Versão do Docker: $dockerVersion"
    }
    catch {
        return Write-LogError "Docker não está instalado"
    }
=======
        $dockerVersion = docker --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-LogError "Falha ao executar 'docker --version'"
            return 1
        }
        Write-LogInfo "Versão do Docker: $dockerVersion"
    }
    catch {
        Write-LogError "Falha ao executar 'docker --version'"
        return 1
    }
    Write-LogInfo "Passou docker --version"
>>>>>>> origin/main

    # Verificar se Docker está rodando
    $retryCount = 0
    while ($retryCount -lt $MAX_RETRIES) {
        try {
<<<<<<< HEAD
            docker info | Out-Null
=======
            $dockerInfo = docker info 2>&1
            if ($LASTEXITCODE -ne 0) {
                throw "Docker não está rodando"
            }
>>>>>>> origin/main
            break
        }
        catch {
            $retryCount++
            if ($retryCount -lt $MAX_RETRIES) {
                Write-LogInfo "Aguardando Docker iniciar (tentativa $retryCount de $MAX_RETRIES)..."
                Start-Sleep -Seconds 5
            }
            else {
<<<<<<< HEAD
                return Write-LogError "Docker Desktop não está rodando"
            }
        }
    }

    # Verificar Kind
    try {
        kind --version | Out-Null
    }
    catch {
        return Write-LogError "Kind não está instalado"
    }

    # Verificar kubectl
    try {
        $kubectlVersion = kubectl version --client
        Write-LogInfo "Versão do kubectl: $kubectlVersion"
    }
    catch {
        return Write-LogError "kubectl não está instalado"
    }

=======
                Write-LogError "Falha ao executar 'docker info'"
                return 1
            }
        }
    }
    Write-LogInfo "Passou docker info"

    # Verificar Kind
    try {
        $kindVersion = kind --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-LogError "Falha ao executar 'kind --version'"
            return 1
        }
        Write-LogInfo "Versão do Kind: $kindVersion"
    }
    catch {
        Write-LogError "Falha ao executar 'kind --version'"
        return 1
    }
    Write-LogInfo "Passou kind --version"

    # Verificar kubectl
    try {
        $kubectlVersion = kubectl version --client 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-LogError "Falha ao executar 'kubectl version --client'"
            return 1
        }
        Write-LogInfo "Versão do kubectl: $kubectlVersion"
    }
    catch {
        Write-LogError "Falha ao executar 'kubectl version --client'"
        return 1
    }
    Write-LogInfo "Passou kubectl version --client"

    # Verificar portas
    $port30000 = Get-NetTCPConnection -LocalPort 30000 -ErrorAction SilentlyContinue
    $port30001 = Get-NetTCPConnection -LocalPort 30001 -ErrorAction SilentlyContinue
    $port5000 = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue

    if ($port30000) {
        Write-LogWarn "Porta 30000 já está em uso (isso é apenas um aviso, o script continuará)"
    }
    if ($port30001) {
        Write-LogWarn "Porta 30001 já está em uso (isso é apenas um aviso, o script continuará)"
    }
    if ($port5000) {
        Write-LogWarn "Porta 5000 já está em uso (isso é apenas um aviso, o script continuará)"
    }
    Write-LogInfo "Passou verificação de portas"

    Write-LogInfo "Todos os pré-requisitos foram verificados com sucesso!"
>>>>>>> origin/main
    return 0
}

# 2. Configurar ambiente
function Setup-Environment {
<<<<<<< HEAD
    Write-LogInfo "Configurando ambiente..."

=======
    Write-LogInfo "[DEBUG] Entrando em Setup-Environment..."
    Write-LogInfo "Configurando ambiente..."

    # Verificar e criar namespace se não existir
    if (-not (kubectl get namespace $NAMESPACE 2>$null)) {
        Write-LogInfo "Criando namespace $NAMESPACE..."
        kubectl create namespace $NAMESPACE
        if ($LASTEXITCODE -ne 0) {
            Write-LogError "[DEBUG] Falha ao criar namespace $NAMESPACE"
            return 1
        }
        Write-LogInfo "[DEBUG] Namespace $NAMESPACE criado com sucesso"
    }

>>>>>>> origin/main
    # Verificar e iniciar registry local
    $registryRunning = $false
    $containers = docker ps --format "{{.Names}}"
    if ($containers -match "registry") {
        $registryRunning = $true
    }

    if (-not $registryRunning) {
        Write-LogInfo "Iniciando registry local..."
        try {
            docker run -d -p 5000:5000 --restart=always --name registry registry:2
<<<<<<< HEAD
        }
        catch {
            return Write-LogError "Falha ao iniciar registry local"
=======
            if ($LASTEXITCODE -ne 0) {
                Write-LogError "[DEBUG] Falha ao iniciar registry local"
                return 1
            }
            Write-LogInfo "[DEBUG] Registry local iniciado com sucesso"
        }
        catch {
            Write-LogError "[DEBUG] Exceção ao iniciar registry local"
            return 1
>>>>>>> origin/main
        }
    }
    else {
        Write-LogInfo "Registry local já está rodando"
    }

<<<<<<< HEAD
    # Garantir que o registry está conectado à rede kind
    $kindNetwork = docker network ls --filter "name=kind" --format "{{.Name}}"
    if ($kindNetwork) {
        $registryInKind = docker network inspect kind | Select-String "registry"
        if (-not $registryInKind) {
            Write-LogInfo "Conectando o registry à rede kind..."
            docker network connect kind registry
        }
    }

    # Verificar se o arquivo setup-kind.ps1 existe
    $setupKindPath = Join-Path $PSScriptRoot "kind-config\setup-kind.ps1"
    if (-not (Test-Path $setupKindPath)) {
        return Write-LogError "Arquivo setup-kind.ps1 não encontrado em $setupKindPath"
    }

    # Configurar cluster Kind
    try {
        Set-Location (Join-Path $PSScriptRoot "kind-config")
        & .\setup-kind.ps1
        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao configurar cluster Kind"
        }
    }
    catch {
        Set-Location $BASE_DIR
        return Write-LogError "Falha ao configurar cluster Kind: $_"
=======
    # Criar uma rede Docker para o kind e o registry se não existir
    $kindNetwork = docker network ls --filter "name=kind" --format "{{.Name}}"
    if (-not $kindNetwork) {
        Write-LogInfo "Criando rede Docker 'kind'..."
        docker network create kind
        if ($LASTEXITCODE -ne 0) {
            Write-LogError "[DEBUG] Falha ao criar rede Docker 'kind'"
            return 1
        }
        Write-LogInfo "[DEBUG] Rede Docker 'kind' criada com sucesso"
    }

    # Garantir que o registry está conectado à rede kind
    $registryInKind = docker network inspect kind | Select-String "registry"
    if (-not $registryInKind) {
        Write-LogInfo "Conectando o registry à rede kind..."
        docker network connect kind registry
        if ($LASTEXITCODE -ne 0) {
            Write-LogError "[DEBUG] Falha ao conectar registry à rede kind"
            return 1
        }
        Write-LogInfo "[DEBUG] Registry conectado à rede kind com sucesso"
    }

    # Verificar se o cluster já existe e excluí-lo
    $existingClusters = kind get clusters
    if ($existingClusters -contains "autocura") {
        Write-LogInfo "Cluster 'autocura' já existe. Excluindo..."
        kind delete cluster --name autocura
        if ($LASTEXITCODE -ne 0) {
            Write-LogError "[DEBUG] Falha ao excluir cluster 'autocura'"
            return 1
        }
        Write-LogInfo "[DEBUG] Cluster 'autocura' excluído com sucesso"
    }

    # Criar cluster kind com a configuração personalizada
    Write-LogInfo "Criando cluster kind 'autocura'..."
    try {
        Set-Location (Join-Path $PSScriptRoot "kind-config")
        kind create cluster --config kind-config.yaml
        if ($LASTEXITCODE -ne 0) {
            Write-LogError "[DEBUG] Falha ao criar cluster Kind"
            Set-Location $BASE_DIR
            return 1
        }
        Write-LogInfo "[DEBUG] Cluster kind 'autocura' criado com sucesso"
    }
    catch {
        Set-Location $BASE_DIR
        Write-LogError "[DEBUG] Exceção ao criar cluster Kind"
        return 1
>>>>>>> origin/main
    }
    finally {
        Set-Location $BASE_DIR
    }

<<<<<<< HEAD
=======
    # Verificar se o cluster foi criado com sucesso
    $clusters = kind get clusters
    if (-not ($clusters -contains "autocura")) {
        Write-LogError "[DEBUG] Cluster 'autocura' não foi criado com sucesso"
        return 1
    }

    # Configurar kubectl para usar o contexto do kind
    kubectl cluster-info --context kind-autocura
    if ($LASTEXITCODE -ne 0) {
        Write-LogError "[DEBUG] Falha ao configurar contexto do kubectl"
        return 1
    }
    Write-LogInfo "[DEBUG] Contexto do kubectl configurado"

    # Aplicar recursos base
    Write-LogInfo "Aplicando recursos base do Kubernetes..."
    kubectl apply -k "kubernetes\base"
    if ($LASTEXITCODE -ne 0) {
        Write-LogError "[DEBUG] Falha ao aplicar kubernetes\base"
        return 1
    }
    Write-LogInfo "[DEBUG] kubernetes\base aplicado com sucesso"

    # Instalar CRDs do Prometheus Operator
    Write-LogInfo "Instalando CRDs do Prometheus Operator..."
    kubectl apply -f kubernetes/crds/monitoring.coreos.com_alertmanagers.yaml
    if ($LASTEXITCODE -ne 0) {
        Write-LogError "[DEBUG] Falha ao aplicar CRD alertmanagers"
        return 1
    }
    kubectl apply -f kubernetes/crds/monitoring.coreos.com_prometheuses.yaml
    if ($LASTEXITCODE -ne 0) {
        Write-LogError "[DEBUG] Falha ao aplicar CRD prometheuses"
        return 1
    }
    kubectl apply -f kubernetes/crds/monitoring.coreos.com_servicemonitors.yaml
    if ($LASTEXITCODE -ne 0) {
        Write-LogError "[DEBUG] Falha ao aplicar CRD servicemonitors"
        return 1
    }
    kubectl apply -f kubernetes/crds/monitoring.coreos.com_podmonitors.yaml
    if ($LASTEXITCODE -ne 0) {
        Write-LogError "[DEBUG] Falha ao aplicar CRD podmonitors"
        return 1
    }
    kubectl apply -f kubernetes/crds/monitoring.coreos.com_prometheusrules.yaml
    if ($LASTEXITCODE -ne 0) {
        Write-LogError "[DEBUG] Falha ao aplicar CRD prometheusrules"
        return 1
    }
    Write-LogInfo "[DEBUG] CRDs do Prometheus Operator aplicados com sucesso"

    # Aplicar recursos de monitoring
    Write-LogInfo "Aplicando recursos de monitoring..."
    kubectl apply -k "kubernetes\monitoring"
    if ($LASTEXITCODE -ne 0) {
        Write-LogError "[DEBUG] Falha ao aplicar kubernetes\monitoring"
        return 1
    }
    Write-LogInfo "[DEBUG] kubernetes\monitoring aplicado com sucesso"

    Write-LogInfo "[DEBUG] Saindo de Setup-Environment."
>>>>>>> origin/main
    return 0
}

# 3. Build e push de imagens
function Build-And-Push-Images {
    Write-LogInfo "Iniciando build e push de imagens..."

<<<<<<< HEAD
    $services = @("monitoramento", "diagnostico", "gerador", "observabilidade", "portal")

    foreach ($service in $services) {
=======
    foreach ($service in $SERVICES) {
>>>>>>> origin/main
        Write-LogInfo "Buildando imagem do $service..."
        
        $serviceDir = Join-Path $BASE_DIR "src\$service"
        if (-not (Test-Path $serviceDir)) {
<<<<<<< HEAD
            return Write-LogError "Diretório do serviço $service não encontrado em $serviceDir"
=======
            return 1
>>>>>>> origin/main
        }
        
        Set-Location $serviceDir
        
<<<<<<< HEAD
=======
        # Verificar qual Dockerfile usar
        $dockerfile = "Dockerfile.$service"
        if (-not (Test-Path $dockerfile)) {
            $dockerfile = "Dockerfile"
        }
        
>>>>>>> origin/main
        # Build da imagem
        $retryCount = 0
        while ($retryCount -lt $MAX_RETRIES) {
            try {
<<<<<<< HEAD
                if (Test-Path "Dockerfile.$service") {
                    docker build -t "$REGISTRY/autocura/$service`:$TAG" -f "Dockerfile.$service" .
                }
                else {
                    docker build -t "$REGISTRY/autocura/$service`:$TAG" -f Dockerfile .
                }
=======
                docker build -t "$REGISTRY/$service`:$TAG" -f $dockerfile .
>>>>>>> origin/main
                break
            }
            catch {
                $retryCount++
                if ($retryCount -lt $MAX_RETRIES) {
                    Write-LogInfo "Tentando build novamente (tentativa $retryCount de $MAX_RETRIES)..."
                    Start-Sleep -Seconds 5
                }
                else {
                    Set-Location $BASE_DIR
<<<<<<< HEAD
                    return Write-LogError "Falha ao buildar imagem do $service"
=======
                    return 1
>>>>>>> origin/main
                }
            }
        }

        # Push da imagem
        $retryCount = 0
        while ($retryCount -lt $MAX_RETRIES) {
            try {
<<<<<<< HEAD
                docker push "$REGISTRY/autocura/$service`:$TAG"
=======
                docker push "$REGISTRY/$service`:$TAG"
>>>>>>> origin/main
                break
            }
            catch {
                $retryCount++
                if ($retryCount -lt $MAX_RETRIES) {
                    Write-LogInfo "Tentando push novamente (tentativa $retryCount de $MAX_RETRIES)..."
                    Start-Sleep -Seconds 5
                }
                else {
                    Set-Location $BASE_DIR
<<<<<<< HEAD
                    return Write-LogError "Falha ao enviar imagem do $service"
=======
                    return 1
>>>>>>> origin/main
                }
            }
        }
    }

    Set-Location $BASE_DIR
    return 0
}

# 4. Aplicar recursos Kubernetes
function Apply-Kubernetes-Resources {
    Write-LogInfo "Aplicando recursos Kubernetes..."

    # Limpar deployments antigos
    Write-LogInfo "Limpando deployments antigos..."
    kubectl delete deployment --all -n $NAMESPACE

    # Aplicar recursos na ordem correta
    Set-Location $BASE_DIR

    # Aplicar recursos do ambiente de desenvolvimento
    Write-LogInfo "Aplicando recursos do ambiente de desenvolvimento..."
    kubectl apply -k "kubernetes\environments\development"

<<<<<<< HEAD
=======
    # Verificar status dos deployments
    foreach ($service in $SERVICES) {
        Write-LogInfo "Verificando status do deployment $service..."
        kubectl rollout status deployment/$service -n $NAMESPACE --timeout=300s
        if ($LASTEXITCODE -ne 0) {
            return 1
        }
    }

>>>>>>> origin/main
    return 0
}

# 4.1 Verificar RBAC
function Verify-RBAC {
    Write-LogInfo "Verificando configurações RBAC..."
    
    # Verificar ServiceAccounts
    $serviceAccounts = kubectl get serviceaccount -n $NAMESPACE
<<<<<<< HEAD
    if (-not ($serviceAccounts -match "diagnostico|gerador|observabilidade|monitoramento")) {
        return Write-LogError "Falha na verificação dos ServiceAccounts"
=======
    if (-not ($serviceAccounts -match "diagnostico|gerador|monitoramento")) {
        return 1
>>>>>>> origin/main
    }
    
    # Verificar Roles
    $roles = kubectl get role -n $NAMESPACE
<<<<<<< HEAD
    if (-not ($roles -match "diagnostico|gerador|observabilidade|monitoramento")) {
        return Write-LogError "Falha na verificação das Roles"
=======
    if (-not ($roles -match "diagnostico|gerador|monitoramento")) {
        return 1
>>>>>>> origin/main
    }
    
    # Verificar RoleBindings
    $roleBindings = kubectl get rolebinding -n $NAMESPACE
<<<<<<< HEAD
    if (-not ($roleBindings -match "diagnostico|gerador|observabilidade|monitoramento")) {
        return Write-LogError "Falha na verificação dos RoleBindings"
=======
    if (-not ($roleBindings -match "diagnostico|gerador|monitoramento")) {
        return 1
>>>>>>> origin/main
    }
    
    Write-LogInfo "Verificação RBAC concluída com sucesso"
    return 0
}

# 5. Verificar status final
function Check-Final-Status {
    Write-LogInfo "Verificando status final..."

    $podsReady = $false
    $maxAttempts = 30
    $attempt = 0

    while ($attempt -lt $maxAttempts) {
        $attempt++
        $pods = kubectl get pods -n $NAMESPACE --no-headers
        if ($pods -match "Running") {
            $podsReady = $true
            break
        }
        else {
            if ($attempt -lt $maxAttempts) {
                Write-LogInfo "Aguardando pods ficarem prontos (tentativa $attempt de $maxAttempts)..."
                Start-Sleep -Seconds 10
            }
        }
    }

    if (-not $podsReady) {
<<<<<<< HEAD
        return Write-LogError "Falha ao verificar status dos pods"
=======
        return 1
>>>>>>> origin/main
    }

    Write-LogInfo "Todos os pods estão rodando!"
    return 0
}

# Função principal
function Main {
<<<<<<< HEAD
    # Verificar pré-requisitos
    if (Check-Prerequisites -ne 0) {
        exit 1
    }

    # Configurar ambiente
    if (Setup-Environment -ne 0) {
        exit 1
    }

    # Build e push de imagens
    if (Build-And-Push-Images -ne 0) {
        exit 1
    }

    # Aplicar recursos Kubernetes
    if (Apply-Kubernetes-Resources -ne 0) {
        exit 1
    }

    # 4.1 Verificar RBAC
    if (Verify-RBAC -ne 0) {
        exit 1
    }

    # 5. Verificar status final
    if (Check-Final-Status -ne 0) {
        exit 1
    }

    Write-LogInfo "=== Sistema de Autocura Cognitiva inicializado com sucesso! ==="
    Write-LogInfo "Agora você pode executar 'build-images.ps1' para construir as imagens e"
    Write-LogInfo "em seguida 'kubectl apply -k kubernetes\environments\development' para implantar o sistema."
=======
    Write-LogInfo "[DEBUG] Início da função Main"
    # Verificar pré-requisitos
    Write-LogInfo "[DEBUG] Chamando Check-Prerequisites"
    $ret = (Check-Prerequisites | Select-Object -Last 1)
    Write-LogInfo "[DEBUG] Retorno de Check-Prerequisites: $ret"
    if ($ret -ne 0) {
        Write-LogError "[DEBUG] Falha em Check-Prerequisites"
        return
    }
    Write-LogInfo "[DEBUG] Check-Prerequisites OK"

    # Configurar ambiente
    Write-LogInfo "[DEBUG] Chamando Setup-Environment"
    $ret = (Setup-Environment | Select-Object -Last 1)
    Write-LogInfo "[DEBUG] Retorno de Setup-Environment: $ret"
    if ($ret -ne 0) {
        Write-LogError "[DEBUG] Falha em Setup-Environment"
        return
    }
    Write-LogInfo "[DEBUG] Setup-Environment OK"

    # Build e push de imagens
    Write-LogInfo "[DEBUG] Chamando Build-And-Push-Images"
    $ret = (Build-And-Push-Images | Select-Object -Last 1)
    if ($ret -ne 0) {
        Write-LogError "[DEBUG] Falha em Build-And-Push-Images"
        return
    }
    Write-LogInfo "[DEBUG] Build-And-Push-Images OK"

    # Aplicar recursos Kubernetes
    Write-LogInfo "[DEBUG] Chamando Apply-Kubernetes-Resources"
    $ret = (Apply-Kubernetes-Resources | Select-Object -Last 1)
    if ($ret -ne 0) {
        Write-LogError "[DEBUG] Falha em Apply-Kubernetes-Resources"
        return
    }
    Write-LogInfo "[DEBUG] Apply-Kubernetes-Resources OK"

    # 4.1 Verificar RBAC
    Write-LogInfo "[DEBUG] Chamando Verify-RBAC"
    $ret = (Verify-RBAC | Select-Object -Last 1)
    if ($ret -ne 0) {
        Write-LogError "[DEBUG] Falha em Verify-RBAC"
        return
    }
    Write-LogInfo "[DEBUG] Verify-RBAC OK"

    # 5. Verificar status final
    Write-LogInfo "[DEBUG] Chamando Check-Final-Status"
    $ret = (Check-Final-Status | Select-Object -Last 1)
    if ($ret -ne 0) {
        Write-LogError "[DEBUG] Falha em Check-Final-Status"
        return
    }
    Write-LogInfo "[DEBUG] Check-Final-Status OK"

    Write-LogInfo "=== Sistema de Autocura Cognitiva inicializado com sucesso! ==="
>>>>>>> origin/main
}

# Executar função principal
Main 