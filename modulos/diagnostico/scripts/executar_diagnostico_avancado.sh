#!/bin/bash

# Cores para output
VERDE='\033[0;32m'
VERMELHO='\033[0;31m'
AMARELO='\033[1;33m'
NC='\033[0m'

echo -e "${AMARELO}Iniciando módulo de diagnóstico avançado...${NC}\n"

# Verifica se o ambiente virtual está ativado
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${VERMELHO}Erro: Ambiente virtual não está ativado${NC}"
    echo "Por favor, ative o ambiente virtual antes de executar o módulo"
    exit 1
fi

# Verifica se o arquivo de configuração existe
if [ ! -f "config/diagnostico_avancado.json" ]; then
    echo -e "${VERMELHO}Erro: Arquivo de configuração não encontrado${NC}"
    echo "Por favor, crie o arquivo config/diagnostico_avancado.json"
    exit 1
fi

# Verifica se os diretórios necessários existem
for dir in "logs" "cache"; do
    if [ ! -d "$dir" ]; then
        echo -e "${AMARELO}Criando diretório $dir...${NC}"
        mkdir -p "$dir"
    fi
done

# Executa o módulo
echo -e "\n${AMARELO}Executando módulo de diagnóstico avançado...${NC}"
python -c "
from src.core.diagnostico_avancado import DiagnosticoAvancado
from src.memoria.gerenciador_memoria import GerenciadorMemoria
from src.core.logger import Logger
from src.core.cache import Cache
import time

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

try:
    # Inicia o sistema
    diagnostico.iniciar()
    print('Módulo iniciado com sucesso!')
    
    # Mantém o script rodando
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print('\nParando o módulo...')
    diagnostico.parar()
    print('Módulo parado com sucesso!')
"

# Verifica resultado da execução
if [ $? -eq 0 ]; then
    echo -e "\n${VERDE}✓ Módulo executado com sucesso!${NC}"
else
    echo -e "\n${VERMELHO}✗ Erro ao executar o módulo${NC}"
    exit 1
fi 