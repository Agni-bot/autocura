#!/bin/bash

# Cores para output
VERDE='\033[0;32m'
VERMELHO='\033[0;31m'
AMARELO='\033[1;33m'
AZUL='\033[0;34m'
NC='\033[0m'

echo -e "${AMARELO}Listando backups do módulo de diagnóstico avançado...${NC}\n"

# Diretório de backups
BACKUP_DIR="backup/diagnostico_avancado"

# Verifica se o diretório existe
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${VERMELHO}Erro: Diretório de backups não encontrado: $BACKUP_DIR${NC}"
    exit 1
fi

# Verifica se existem backups
BACKUPS=$(ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null)
if [ -z "$BACKUPS" ]; then
    echo -e "${AMARELO}Nenhum backup encontrado no diretório: $BACKUP_DIR${NC}"
    exit 0
fi

# Função para obter informações do backup
obter_info_backup() {
    local backup_file="$1"
    local temp_dir="$BACKUP_DIR/temp_info"
    
    # Cria diretório temporário
    mkdir -p "$temp_dir"
    
    # Extrai apenas o arquivo de configuração
    tar -xzf "$backup_file" -C "$temp_dir" config.json 2>/dev/null
    
    # Obtém informações do arquivo
    local size=$(du -h "$backup_file" | cut -f1)
    local date=$(stat -c "%y" "$backup_file" | cut -d' ' -f1)
    local time=$(stat -c "%y" "$backup_file" | cut -d' ' -f2 | cut -d'.' -f1)
    
    # Limpa diretório temporário
    rm -rf "$temp_dir"
    
    echo "$size|$date|$time"
}

# Cabeçalho da tabela
printf "${AZUL}%-40s %-10s %-12s %-10s${NC}\n" "Backup" "Tamanho" "Data" "Hora"
echo "----------------------------------------------------------------------"

# Lista os backups
for backup in $BACKUPS; do
    filename=$(basename "$backup")
    info=$(obter_info_backup "$backup")
    size=$(echo "$info" | cut -d'|' -f1)
    date=$(echo "$info" | cut -d'|' -f2)
    time=$(echo "$info" | cut -d'|' -f3)
    
    printf "%-40s %-10s %-12s %-10s\n" "$filename" "$size" "$date" "$time"
done

echo -e "\n${VERDE}Total de backups encontrados: $(echo "$BACKUPS" | wc -l)${NC}"
echo -e "\nPara restaurar um backup, use:"
echo -e "${AMARELO}./scripts/restaurar_diagnostico_avancado.sh <arquivo_backup>${NC}" 