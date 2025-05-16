#!/bin/bash
# Descrição: Executável de Exemplo para MeuApp

echo "[MeuApp Executable] Iniciando MeuApp..."

CONFIG_FILE="${CONFIG_PATH:-/etc/meuapp/meuapp.conf}"
LOG_FILE_DEFAULT="/var/log/meuapp/meuapp_executable.log"

if [ -f "${CONFIG_FILE}" ]; then
    echo "[MeuApp Executable] Lendo configuração de: ${CONFIG_FILE}" | tee -a "${LOG_FILE_DEFAULT}"
    # Exemplo de leitura de uma configuração específica
    LISTEN_PORT=$(grep -E '^listen_port\s*=' "${CONFIG_FILE}" | cut -d'=' -f2 | tr -d '[:space:]')
    echo "[MeuApp Executable] Configuração 'listen_port' encontrada: ${LISTEN_PORT:-N/A}" | tee -a "${LOG_FILE_DEFAULT}"
else
    echo "[MeuApp Executable] Aviso: Arquivo de configuração '${CONFIG_FILE}' não encontrado. Usando padrões." | tee -a "${LOG_FILE_DEFAULT}"
fi

echo "[MeuApp Executable] MeuApp está em execução (simulado). PID: $$" | tee -a "${LOG_FILE_DEFAULT}"
echo "[MeuApp Executable] Pressione Ctrl+C para parar." | tee -a "${LOG_FILE_DEFAULT}"

# Loop infinito para simular um serviço em execução
# Em um aplicativo real, este seria o loop principal do aplicativo ou um processo daemon.
while true; do
    echo "[MeuApp Executable] Heartbeat - $(date)" >> "${LOG_FILE_DEFAULT}"
    sleep 60
done

echo "[MeuApp Executable] MeuApp encerrado." | tee -a "${LOG_FILE_DEFAULT}"
exit 0

