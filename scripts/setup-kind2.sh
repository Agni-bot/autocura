#!/bin/bash

# Script para configurar um ambiente Kubernetes local usando kind
# para o Sistema Autocura Cognitiva

set -e

echo "=== Configurando ambiente Kubernetes local com kind ==="

# --- Verificações de Pré-requisitos ---
echo "[SETUP] Verificando pré-requisitos..."

# Verificar se o kind está instalado
if ! command -v kind &> /dev/null; then
    echo "[ERRO] kind não está instalado. Por favor, instale-o seguindo as instruções em:" >&2
    echo "https://kind.sigs.k8s.io/docs/user/quick-start/#installation" >&2
    exit 1
fi
echo "[INFO] kind encontrado: $(kind version)"

# Verificar se o kubectl está instalado
if ! command -v kubectl &> /dev/null; then
    echo "[ERRO] kubectl não está instalado. Por favor, instale-o seguindo as instruções em:" >&2
    echo "https://kubernetes.io/docs/tasks/tools/install-kubectl/" >&2
    exit 1
fi
echo "[INFO] kubectl encontrado: $(kubectl version --client --short)"

# Verificar se o Docker está instalado e em execução
if ! command -v docker &> /dev/null; then
    echo "[ERRO] Docker não está instalado. Por favor, instale o Docker antes de continuar." >&2
    exit 1
fi
if ! docker info &> /dev/null; then
    echo "[ERRO] Docker daemon não está em execução ou não está acessível." >&2
    echo "Por favor, inicie o Docker e certifique-se de que o usuário atual tem permissão para usá-lo." >&2
    echo "Dica para usuários WSL: Verifique a integração do Docker Desktop com sua distribuição WSL nas configurações do Docker Desktop." >&2
    exit 1
fi
echo "[INFO] Docker encontrado: $(docker version --format \'{{.Server.Version}}\')"

# --- Configuração do Cluster Kind ---
CLUSTER_NAME="autocura-cognitiva"
KIND_CONFIG_FILE="kind-config.yaml"
AUTOCURA_NAMESPACE="autocura-ns"

# Criar arquivo de configuração do kind
cat > "${KIND_CONFIG_FILE}" << EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: ${CLUSTER_NAME}
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
  - containerPort: 30000 # Exemplo de NodePort para serviços
    hostPort: 30000
    protocol: TCP
  - containerPort: 30001 # Exemplo de NodePort para serviços
    hostPort: 30001
    protocol: TCP
containerdConfigPatches:
- |-
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."localhost:5000"]
    endpoint = ["http://kind-registry:5000"]
EOF

# Verificar se o cluster já existe
if kind get clusters | grep -q "${CLUSTER_NAME}"; then
    echo "[WARN] Cluster '${CLUSTER_NAME}' já existe. Deseja excluí-lo e criar um novo? (s/n)"
    read -r resposta
    if [[ "$resposta" =~ ^[Ss]$ ]]; then
        echo "[INFO] Excluindo cluster existente '${CLUSTER_NAME}'..."
        kind delete cluster --name "${CLUSTER_NAME}"
    else
        echo "[INFO] Mantendo cluster existente. Verificando configuração do registro..."
        # Garantir que o registro esteja conectado se o cluster for mantido
        if docker ps --filter name=kind-registry --filter status=running | grep -q kind-registry; then
            if ! docker network inspect kind | grep -q "kind-registry"; then
                 echo "[INFO] Conectando o registro 'kind-registry' à rede 'kind'..."
                 docker network connect kind kind-registry || echo "[WARN] Falha ao conectar o registro à rede kind. Pode já estar conectado."
            fi
        fi
        echo "[INFO] Configuração do cluster existente verificada."
        rm -f "${KIND_CONFIG_FILE}"
        exit 0
    fi
fi

# --- Configuração do Registro Docker Local para Kind ---
REGISTRY_NAME="kind-registry"
REGISTRY_PORT="5000"

if true; then
    echo "[INFO] Usando registro Docker existente na porta 5000."
        echo "[INFO] Registro local '${REGISTRY_NAME}' iniciado."
    else
        echo "[ERRO] Falha ao iniciar o registro Docker local '${REGISTRY_NAME}'. Verifique as permissões e a disponibilidade da porta." >&2
        exit 1
    fi
else
    echo "[INFO] Registro local '${REGISTRY_NAME}' já está em execução."
fi

# Criar uma rede Docker para o kind se não existir
if ! docker network ls | grep -q "kind"; then
    echo "[INFO] Criando rede Docker 'kind'..."
    docker network create kind
fi

# Conectar o registro à rede kind
if ! docker network inspect kind | grep -q "${REGISTRY_NAME}"; then
    echo "[INFO] Conectando o registro '${REGISTRY_NAME}' à rede 'kind'..."
    docker network connect kind "${REGISTRY_NAME}" || echo "[WARN] Falha ao conectar o registro à rede kind. Pode já estar conectado."
fi

# --- Criação do Cluster Kind ---
echo "[INFO] Criando cluster kind '${CLUSTER_NAME}' com a configuração de registro..."
kind create cluster --config "${KIND_CONFIG_FILE}"

# Verificar se o cluster foi criado com sucesso
if ! kind get clusters | grep -q "${CLUSTER_NAME}"; then
    echo "[ERRO] Falha ao criar o cluster kind '${CLUSTER_NAME}'." >&2
    exit 1
fi
echo "[INFO] Cluster kind '${CLUSTER_NAME}' criado com sucesso!"

# Configurar kubectl para usar o contexto do kind
kubectl cluster-info --context "kind-${CLUSTER_NAME}"

# --- Criação de Namespace e Quotas (Exemplo) ---
echo "[INFO] Configurando namespace e quotas para Autocura..."

# Criar namespace se não existir
if ! kubectl get namespace "${AUTOCURA_NAMESPACE}" &> /dev/null; then
    echo "[INFO] Criando namespace '${AUTOCURA_NAMESPACE}'..."
    kubectl create namespace "${AUTOCURA_NAMESPACE}"
else
    echo "[INFO] Namespace '${AUTOCURA_NAMESPACE}' já existe."
fi

# Aplicar ResourceQuota (exemplo)
cat <<EOF | kubectl apply -n "${AUTOCURA_NAMESPACE}" -f -
apiVersion: v1
kind: ResourceQuota
metadata:
  name: autocura-quota
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 2Gi
    limits.cpu: "4"
    limits.memory: 4Gi
    pods: "20"
    services: "10"
EOF
echo "[INFO] ResourceQuota 'autocura-quota' aplicada ao namespace '${AUTOCURA_NAMESPACE}'."

# Aplicar LimitRange (exemplo)
cat <<EOF | kubectl apply -n "${AUTOCURA_NAMESPACE}" -f -
apiVersion: v1
kind: LimitRange
metadata:
  name: autocura-limits
spec:
  limits:
  - default:
      memory: "512Mi"
      cpu: "500m"
    defaultRequest:
      memory: "256Mi"
      cpu: "250m"
    type: Container
EOF
echo "[INFO] LimitRange 'autocura-limits' aplicado ao namespace '${AUTOCURA_NAMESPACE}'."

# Limpar arquivo de configuração temporário
rm -f "${KIND_CONFIG_FILE}"

echo "
=== Ambiente Kubernetes local configurado com sucesso! ===
Cluster: ${CLUSTER_NAME}
Namespace: ${AUTOCURA_NAMESPACE}

Próximos passos sugeridos:
1. Execute './build.sh' para construir as imagens Docker do projeto.
2. Implante os componentes no namespace '${AUTOCURA_NAMESPACE}', por exemplo:
   kubectl apply -k kubernetes/environments/development -n ${AUTOCURA_NAMESPACE}
   (Ajuste o caminho do kustomize conforme sua estrutura)
"

