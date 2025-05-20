#!/bin/bash

# Cores para output
VERDE='\033[0;32m'
VERMELHO='\033[0;31m'
AMARELO='\033[1;33m'
AZUL='\033[0;34m'
NC='\033[0m'

echo -e "${AMARELO}Iniciando monitoramento do módulo de diagnóstico avançado...${NC}\n"

# Verifica se o ambiente virtual está ativado
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${VERMELHO}Erro: Ambiente virtual não está ativado${NC}"
    echo "Por favor, ative o ambiente virtual antes de executar o monitoramento"
    exit 1
fi

# Verifica se o arquivo de configuração existe
if [ ! -f "config/diagnostico_avancado.json" ]; then
    echo -e "${VERMELHO}Erro: Arquivo de configuração não encontrado${NC}"
    echo "Por favor, crie o arquivo config/diagnostico_avancado.json"
    exit 1
fi

# Função para limpar a tela
limpar_tela() {
    clear
    echo -e "${AMARELO}Monitoramento do módulo de diagnóstico avançado${NC}\n"
}

# Função para exibir métricas
exibir_metricas() {
    echo -e "${AZUL}Métricas do Sistema:${NC}"
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

# Obtém resultados
resultados = diagnostico.obter_resultados()

# Exibe métricas
if resultados:
    print('\nCorrelações:')
    for metrica, dados in resultados.get('correlacoes', {}).items():
        print(f'  {metrica}:')
        print(f'    Correlação: {dados["correlacao"]:.2f}')
        print(f'    Lag: {dados["lag"]}s')
    
    print('\nPredições:')
    for metrica, dados in resultados.get('predicoes', {}).items():
        print(f'  {metrica}:')
        print(f'    Valores: {dados["valores"]}')
        print(f'    Confiança: {dados["confianca"]:.2f}')
        print(f'    Tendência: {dados["tendencia"]:.2f}')
else:
    print('Nenhum resultado disponível')
"
}

# Função para exibir logs
exibir_logs() {
    echo -e "\n${AZUL}Últimos Logs:${NC}"
    tail -n 10 logs/diagnostico_avancado.log
}

# Função para exibir status
exibir_status() {
    echo -e "\n${AZUL}Status do Sistema:${NC}"
    if pgrep -f "diagnostico_avancado" > /dev/null; then
        echo -e "${VERDE}✓ Módulo em execução${NC}"
    else
        echo -e "${VERMELHO}✗ Módulo parado${NC}"
    fi
}

# Loop principal
while true; do
    limpar_tela
    exibir_status
    exibir_metricas
    exibir_logs
    
    echo -e "\n${AMARELO}Pressione Ctrl+C para sair${NC}"
    sleep 5
done 