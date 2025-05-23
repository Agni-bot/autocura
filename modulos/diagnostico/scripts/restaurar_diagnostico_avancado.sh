#!/bin/bash

# Cores para output
VERDE='\033[0;32m'
VERMELHO='\033[0;31m'
AMARELO='\033[1;33m'
NC='\033[0m'

echo -e "${AMARELO}Iniciando restauração de backup do módulo de diagnóstico avançado...${NC}\n"

# Verifica se o ambiente virtual está ativado
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${VERMELHO}Erro: Ambiente virtual não está ativado${NC}"
    echo "Por favor, ative o ambiente virtual antes de executar a restauração"
    exit 1
fi

# Verifica se foi fornecido um arquivo de backup
if [ -z "$1" ]; then
    echo -e "${VERMELHO}Erro: Nenhum arquivo de backup especificado${NC}"
    echo "Uso: $0 <arquivo_backup>"
    echo "Exemplo: $0 backup/diagnostico_avancado/backup_20240315_123456.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"
BACKUP_DIR="backup/diagnostico_avancado"
TEMP_DIR="$BACKUP_DIR/temp_restore"

# Verifica se o arquivo de backup existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${VERMELHO}Erro: Arquivo de backup não encontrado: $BACKUP_FILE${NC}"
    exit 1
fi

# Cria diretório temporário para restauração
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi
mkdir -p "$TEMP_DIR"

# Função para extrair backup
extrair_backup() {
    echo -e "${AMARELO}Extraindo arquivo de backup...${NC}"
    tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
    if [ $? -eq 0 ]; then
        echo "Backup extraído com sucesso!"
    else
        echo -e "${VERMELHO}Erro ao extrair backup${NC}"
        exit 1
    fi
}

# Função para restaurar cache
restaurar_cache() {
    echo -e "${AMARELO}Restaurando cache...${NC}"
    if [ -f "$TEMP_DIR/cache.json" ]; then
        python -c "
from src.core.cache import Cache
import json

# Inicializa cache
cache = Cache()

# Carrega dados do backup
with open('$TEMP_DIR/cache.json', 'r') as f:
    dados = json.load(f)

# Restaura dados
if dados:
    cache.definir('diagnostico_avancado', 'ultimo', dados)
    print('Cache restaurado com sucesso!')
else:
    print('Nenhum dado de cache para restaurar')
"
    else
        echo "Nenhum arquivo de cache encontrado no backup"
    fi
}

# Função para restaurar logs
restaurar_logs() {
    echo -e "${AMARELO}Restaurando logs...${NC}"
    if [ -f "$TEMP_DIR/logs.log" ]; then
        # Cria diretório de logs se não existir
        mkdir -p "logs"
        cp "$TEMP_DIR/logs.log" "logs/diagnostico_avancado.log"
        echo "Logs restaurados com sucesso!"
    else
        echo "Nenhum arquivo de log encontrado no backup"
    fi
}

# Função para restaurar métricas
restaurar_metricas() {
    echo -e "${AMARELO}Restaurando métricas...${NC}"
    if [ -f "$TEMP_DIR/metricas.json" ]; then
        python -c "
from src.core.diagnostico_avancado import DiagnosticoAvancado
from src.memoria.gerenciador_memoria import GerenciadorMemoria
from src.core.logger import Logger
from src.core.cache import Cache
import json

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

# Carrega métricas do backup
with open('$TEMP_DIR/metricas.json', 'r') as f:
    metricas = json.load(f)

# Restaura métricas
if metricas:
    cache.definir('metricas', 'historico', metricas)
    print('Métricas restauradas com sucesso!')
else:
    print('Nenhuma métrica para restaurar')
"
    else
        echo "Nenhum arquivo de métricas encontrado no backup"
    fi
}

# Função para restaurar configuração
restaurar_config() {
    echo -e "${AMARELO}Restaurando configuração...${NC}"
    if [ -f "$TEMP_DIR/config.json" ]; then
        # Cria diretório de configuração se não existir
        mkdir -p "config"
        cp "$TEMP_DIR/config.json" "config/diagnostico_avancado.json"
        echo "Configuração restaurada com sucesso!"
    else
        echo "Nenhum arquivo de configuração encontrado no backup"
    fi
}

# Função para limpar arquivos temporários
limpar_temp() {
    echo -e "${AMARELO}Limpando arquivos temporários...${NC}"
    rm -rf "$TEMP_DIR"
    echo "Limpeza concluída!"
}

# Executa restauração
echo -e "${AMARELO}Iniciando processo de restauração...${NC}\n"

# Extrai backup
extrair_backup

# Restaura cache
restaurar_cache

# Restaura logs
restaurar_logs

# Restaura métricas
restaurar_metricas

# Restaura configuração
restaurar_config

# Limpa arquivos temporários
limpar_temp

echo -e "\n${VERDE}✓ Restauração concluída com sucesso!${NC}" 