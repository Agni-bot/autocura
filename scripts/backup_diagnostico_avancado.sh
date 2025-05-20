#!/bin/bash

# Cores para output
VERDE='\033[0;32m'
VERMELHO='\033[0;31m'
AMARELO='\033[1;33m'
NC='\033[0m'

echo -e "${AMARELO}Iniciando backup dos dados do módulo de diagnóstico avançado...${NC}\n"

# Verifica se o ambiente virtual está ativado
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${VERMELHO}Erro: Ambiente virtual não está ativado${NC}"
    echo "Por favor, ative o ambiente virtual antes de executar o backup"
    exit 1
fi

# Cria diretório de backup se não existir
BACKUP_DIR="backup/diagnostico_avancado"
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${AMARELO}Criando diretório de backup...${NC}"
    mkdir -p "$BACKUP_DIR"
fi

# Gera timestamp para o backup
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"

# Cria diretório do backup
mkdir -p "$BACKUP_PATH"

# Função para fazer backup do cache
backup_cache() {
    echo -e "${AMARELO}Fazendo backup do cache...${NC}"
    python -c "
from src.core.cache import Cache
import json
import os

# Inicializa cache
cache = Cache()

# Obtém dados do diagnóstico avançado
dados = cache.obter('diagnostico_avancado', 'ultimo')

# Salva dados
if dados:
    with open('$BACKUP_PATH/cache.json', 'w') as f:
        json.dump(dados, f, indent=2)
    print('Cache backup realizado com sucesso!')
else:
    print('Nenhum dado de cache encontrado')
"
}

# Função para fazer backup dos logs
backup_logs() {
    echo -e "${AMARELO}Fazendo backup dos logs...${NC}"
    if [ -f "logs/diagnostico_avancado.log" ]; then
        cp "logs/diagnostico_avancado.log" "$BACKUP_PATH/logs.log"
        echo "Logs backup realizados com sucesso!"
    else
        echo "Nenhum arquivo de log encontrado"
    fi
}

# Função para fazer backup das métricas
backup_metricas() {
    echo -e "${AMARELO}Fazendo backup das métricas...${NC}"
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

# Obtém métricas
metricas = cache.obter('metricas', 'historico')

# Salva métricas
if metricas:
    with open('$BACKUP_PATH/metricas.json', 'w') as f:
        json.dump(metricas, f, indent=2)
    print('Métricas backup realizadas com sucesso!')
else:
    print('Nenhuma métrica encontrada')
"
}

# Função para fazer backup da configuração
backup_config() {
    echo -e "${AMARELO}Fazendo backup da configuração...${NC}"
    if [ -f "config/diagnostico_avancado.json" ]; then
        cp "config/diagnostico_avancado.json" "$BACKUP_PATH/config.json"
        echo "Configuração backup realizada com sucesso!"
    else
        echo "Nenhum arquivo de configuração encontrado"
    fi
}

# Função para compactar backup
compactar_backup() {
    echo -e "${AMARELO}Compactando backup...${NC}"
    cd "$BACKUP_DIR"
    tar -czf "backup_$TIMESTAMP.tar.gz" "backup_$TIMESTAMP"
    rm -rf "backup_$TIMESTAMP"
    cd - > /dev/null
    echo "Backup compactado com sucesso!"
}

# Executa backup
echo -e "${AMARELO}Iniciando processo de backup...${NC}\n"

# Faz backup do cache
backup_cache

# Faz backup dos logs
backup_logs

# Faz backup das métricas
backup_metricas

# Faz backup da configuração
backup_config

# Compacta backup
compactar_backup

echo -e "\n${VERDE}✓ Backup concluído com sucesso!${NC}"
echo -e "Arquivo de backup: ${AMARELO}$BACKUP_DIR/backup_$TIMESTAMP.tar.gz${NC}" 