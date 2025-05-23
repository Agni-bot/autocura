#!/bin/bash

# Cores para output
VERDE='\033[0;32m'
VERMELHO='\033[0;31m'
AMARELO='\033[1;33m'
NC='\033[0m'

echo -e "${AMARELO}Iniciando limpeza dos dados do módulo de diagnóstico avançado...${NC}\n"

# Verifica se o ambiente virtual está ativado
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${VERMELHO}Erro: Ambiente virtual não está ativado${NC}"
    echo "Por favor, ative o ambiente virtual antes de executar a limpeza"
    exit 1
fi

# Verifica se o módulo está em execução
if pgrep -f "diagnostico_avancado" > /dev/null; then
    echo -e "${VERMELHO}Erro: Módulo está em execução${NC}"
    echo "Por favor, pare o módulo antes de executar a limpeza"
    exit 1
fi

# Função para limpar cache
limpar_cache() {
    echo -e "${AMARELO}Limpando cache...${NC}"
    python -c "
from src.core.cache import Cache
import os

# Inicializa cache
cache = Cache()

# Limpa dados do diagnóstico avançado
cache.limpar_tipo('diagnostico_avancado')

print('Cache limpo com sucesso!')
"
}

# Função para limpar logs
limpar_logs() {
    echo -e "${AMARELO}Limpando logs...${NC}"
    if [ -f "logs/diagnostico_avancado.log" ]; then
        rm "logs/diagnostico_avancado.log"
        echo "Logs limpos com sucesso!"
    else
        echo "Nenhum arquivo de log encontrado"
    fi
}

# Função para limpar métricas
limpar_metricas() {
    echo -e "${AMARELO}Limpando métricas...${NC}"
    python -c "
from src.core.diagnostico_avancado import DiagnosticoAvancado
from src.memoria.gerenciador_memoria import GerenciadorMemoria
from src.core.logger import Logger
from src.core.cache import Cache

# Inicializa dependências
gerenciador_memoria = GerenciadorMemoria()
logger = Logger()
cache = Cache()

# Cria instância do diagnóstico
diagnostico = DiagnosticoAvancado(
    gerenciador_memoria,
    logger,
    cache
)

# Limpa métricas
cache.limpar_tipo('metricas')

print('Métricas limpas com sucesso!')
"
}

# Função para limpar configuração
limpar_config() {
    echo -e "${AMARELO}Limpando configuração...${NC}"
    if [ -f "config/diagnostico_avancado.json" ]; then
        rm "config/diagnostico_avancado.json"
        echo "Configuração limpa com sucesso!"
    else
        echo "Nenhum arquivo de configuração encontrado"
    fi
}

# Executa limpeza
echo -e "${AMARELO}Iniciando processo de limpeza...${NC}\n"

# Limpa cache
limpar_cache

# Limpa logs
limpar_logs

# Limpa métricas
limpar_metricas

# Limpa configuração
limpar_config

echo -e "\n${VERDE}✓ Limpeza concluída com sucesso!${NC}" 