#!/bin/bash

# Script de automação para o sistema Autocura
# Uso: ./autocura.sh <ação> [ambiente]

set -e

ACTION=${1:-install}
ENVIRONMENT=${2:-dev}

function write_status() {
    echo -e "\n[Autocura] $1"
}

function install_dependencies() {
    write_status "Instalando dependências..."
    python3 -m pip install --upgrade pip
    pip install -e ".[dev,monitoring,security]"
}

function run_tests() {
    write_status "Executando testes..."
    pytest --cov=src tests/ --cov-report=term-missing
}

function run_linting() {
    write_status "Executando verificações de código..."
    black . --check
    flake8 .
    isort . --check-only
    mypy src/
}

function build_project() {
    write_status "Construindo projeto..."
    docker-compose build
}

function clean_project() {
    write_status "Limpando arquivos temporários..."
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type f -name ".coverage" -delete
    find . -type d -name "htmlcov" -exec rm -rf {} +
    find . -type d -name ".mypy_cache" -exec rm -rf {} +
    find . -type d -name ".ruff_cache" -exec rm -rf {} +
}

function start_monitoring() {
    write_status "Iniciando monitoramento..."
    docker-compose up -d prometheus grafana
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:3000  # Grafana
        open http://localhost:9090  # Prometheus
    else
        xdg-open http://localhost:3000  # Grafana
        xdg-open http://localhost:9090  # Prometheus
    fi
}

function backup_data() {
    write_status "Realizando backup..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backup/$timestamp"
    mkdir -p "$backup_dir"
    
    cp -r config data logs "$backup_dir"
    
    tar -czf "$backup_dir.tar.gz" -C "$backup_dir" .
    rm -rf "$backup_dir"
}

function restore_data() {
    if [ -z "$1" ]; then
        echo "Erro: Arquivo de backup não especificado"
        exit 1
    fi
    
    write_status "Restaurando backup..."
    mkdir -p restore_temp
    tar -xzf "$1" -C restore_temp
    cp -r restore_temp/* .
    rm -rf restore_temp
}

# Execução principal
case $ACTION in
    install)
        install_dependencies
        ;;
    test)
        run_tests
        ;;
    lint)
        run_linting
        ;;
    build)
        build_project
        ;;
    clean)
        clean_project
        ;;
    monitor)
        start_monitoring
        ;;
    backup)
        backup_data
        ;;
    restore)
        restore_data "$2"
        ;;
    *)
        echo "Ação desconhecida: $ACTION"
        echo "Uso: $0 <ação> [ambiente]"
        echo "Ações disponíveis: install, test, lint, build, clean, monitor, backup, restore"
        exit 1
        ;;
esac 