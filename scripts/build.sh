#!/bin/bash

# Script para construir todas as imagens Docker do Sistema Autocura Cognitiva
# Este script constrói as imagens e as carrega no cluster kind local

set -e

echo "=== Construindo imagens Docker para o Sistema Autocura Cognitiva ==="

# Verificar se o Docker está instalado e em execução
if ! command -v docker &> /dev/null; then
    echo "Docker não está instalado. Por favor, instale o Docker antes de continuar." >&2
    exit 1
fi
if ! docker info &> /dev/null; then
    echo "Docker daemon não está em execução ou não está acessível." >&2
    echo "Por favor, inicie o Docker e certifique-se de que o usuário atual tem permissão para usá-lo." >&2
    echo "Dica para usuários WSL: Verifique a integração do Docker Desktop com sua distribuição WSL." >&2
    exit 1
fi

# Diretório base do projeto
BASE_DIR=$(pwd)
REGISTRY="localhost:5000"
TAG="dev"

# Função para verificar se um diretório existe
check_directory() {
    local dir=$1
    if [ ! -d "$dir" ]; then
        echo "Erro: Diretório '$dir' não encontrado!" >&2
        return 1
    fi
    return 0
}

# Função para verificar se um Dockerfile existe
check_dockerfile() {
    local dir=$1
    if [ ! -f "$dir/Dockerfile" ]; then
        echo "Erro: Dockerfile não encontrado em '$dir'!" >&2
        return 1
    fi
    return 0
}

# Função para construir e carregar uma imagem
build_and_load() {
    local component=$1
    local dir=$2
    local image_name="${REGISTRY}/autocura-cognitiva/${component}:${TAG}"
    
    echo "Verificando diretório para ${component}..."
    if ! check_directory "${BASE_DIR}/${dir}"; then
        echo "Pulando construção de ${component} devido a erro no diretório."
        return 1
    fi
    
    echo "Verificando Dockerfile para ${component}..."
    if ! check_dockerfile "${BASE_DIR}/${dir}"; then
        echo "Pulando construção de ${component} devido a erro no Dockerfile."
        return 1
    fi
    
    echo "Construindo imagem: ${image_name}"
    cd "${BASE_DIR}/${dir}"
    
    # Verificar se todos os arquivos necessários existem
    if [ -f "go.mod" ] && [ -f "go.sum" ]; then
        echo "Arquivos go.mod e go.sum encontrados."
    fi
    
    if [ -d "api" ]; then
        echo "Diretório api encontrado."
    fi
    
    if [ -d "controller" ]; then
        echo "Diretório controller encontrado."
    fi
    
    docker build -t "${image_name}" .
    
    echo "Enviando imagem para o registro local: ${image_name}"
    docker push "${image_name}"
    
    echo "Imagem ${image_name} construída e enviada com sucesso!"
    echo ""
}

# Verificar se o registro local está em execução
if ! docker ps | grep -q registry:2; then
    echo "Iniciando registro Docker local na porta 5000..."
    if docker run -d -p 5000:5000 --restart=always --name registry registry:2; then
        echo "Registro local iniciado!"
    else
        echo "Falha ao iniciar o registro Docker local. Verifique as permissões e a disponibilidade da porta 5000." >&2
        exit 1
    fi
else
    echo "Registro local já está em execução."
fi

# Construir imagens dos componentes principais
echo "Construindo imagens dos componentes principais..."
build_and_load "monitoramento" "src/monitoramento"
build_and_load "diagnostico" "src/diagnostico"
build_and_load "gerador-acoes" "src/geradorAcoes"
build_and_load "observabilidade" "src/observabilidade"

# Construir imagens dos operadores
echo "Construindo imagens dos operadores..."
build_and_load "healing-operator" "kubernetes/operators/HealingOperator"
build_and_load "rollback-operator" "kubernetes/operators/RollbackOperator"

echo "=== Todas as imagens foram construídas e enviadas com sucesso! ==="

