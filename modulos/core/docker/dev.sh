#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Função para exibir mensagens
print_message() {
    echo -e "${GREEN}[DEV]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

# Verifica se o Docker está instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verifica se o Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Função para construir a imagem
build_image() {
    print_message "Construindo imagem Docker..."
    docker-compose build
}

# Função para iniciar os containers
start_containers() {
    print_message "Iniciando containers..."
    docker-compose up -d
}

# Função para parar os containers
stop_containers() {
    print_message "Parando containers..."
    docker-compose down
}

# Função para mostrar logs
show_logs() {
    print_message "Mostrando logs..."
    docker-compose logs -f
}

# Função para executar testes
run_tests() {
    print_message "Executando testes..."
    docker-compose exec core python -m pytest tests/ -v
}

# Função para executar linting
run_lint() {
    print_message "Executando linting..."
    docker-compose exec core flake8 .
}

# Função para mostrar ajuda
show_help() {
    echo "Uso: ./dev.sh [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  build    - Constrói a imagem Docker"
    echo "  start    - Inicia os containers"
    echo "  stop     - Para os containers"
    echo "  logs     - Mostra os logs"
    echo "  test     - Executa os testes"
    echo "  lint     - Executa o linting"
    echo "  help     - Mostra esta mensagem de ajuda"
}

# Processa os argumentos
case "$1" in
    build)
        build_image
        ;;
    start)
        start_containers
        ;;
    stop)
        stop_containers
        ;;
    logs)
        show_logs
        ;;
    test)
        run_tests
        ;;
    lint)
        run_lint
        ;;
    help|*)
        show_help
        ;;
esac 