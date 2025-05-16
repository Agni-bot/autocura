#!/bin/bash
# Descrição: Etapa 10 - Inicia o Servidor Frontend do Autocura
# Este script inicia o servidor Flask que hospeda o painel de controle do Autocura.

echo "[ETAPA 10] Iniciando o Servidor Frontend do Autocura..."

# Variáveis de Configuração
AUTOCURA_PROJECT_DIR="/home/ubuntu/Autocura_project/Autocura"
FRONTEND_DIR="${AUTOCURA_PROJECT_DIR}/frontend"
FRONTEND_SERVER_SCRIPT="frontend_server.py"
PYTHON_EXEC="python3"
LOG_FILE="/var/log/autocura_frontend_startup.log"
FLAG_PREVIOUS_STEP="/home/ubuntu/.etapa_09_ok"
FLAG_CURRENT_STEP="/home/ubuntu/.etapa_10_ok"

# Função para registrar logs
log_message() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a "${LOG_FILE}"
}

# Tratamento de Erros
set -e

log_message "-------------------------------------------------"
log_message "Iniciando script 10_iniciar_frontend.sh"

# 1. Verificar se a etapa anterior foi concluída
if [ ! -f "${FLAG_PREVIOUS_STEP}" ]; then
    log_message "Erro: A Etapa 09 (Limpeza da Instalação) não foi concluída com sucesso."
    log_message "Por favor, execute o script 09_limpeza_instalacao.sh antes de continuar."
    exit 1
fi
log_message "Verificação da Etapa 09: OK."

# 2. Verificar se o diretório do frontend existe
if [ ! -d "${FRONTEND_DIR}" ]; then
    log_message "Erro: Diretório do frontend '${FRONTEND_DIR}' não encontrado."
    exit 1
fi
log_message "Diretório do frontend encontrado: ${FRONTEND_DIR}"

# 3. Verificar se o script do servidor Flask existe
if [ ! -f "${FRONTEND_DIR}/${FRONTEND_SERVER_SCRIPT}" ]; then
    log_message "Erro: Script do servidor Flask '${FRONTEND_SERVER_SCRIPT}' não encontrado em '${FRONTEND_DIR}'."
    exit 1
fi
log_message "Script do servidor Flask encontrado: ${FRONTEND_DIR}/${FRONTEND_SERVER_SCRIPT}"

# 4. Verificar se o Python 3 está instalado
if ! command -v ${PYTHON_EXEC} &> /dev/null; then
    log_message "Erro: ${PYTHON_EXEC} não encontrado. Por favor, instale o Python 3."
    log_message "Considere adicionar a instalação do Flask e outras dependências Python no script 02_instalar_dependencias.sh"
    exit 1
fi
log_message "Python 3 encontrado: $(command -v ${PYTHON_EXEC})"

# 5. (Opcional) Verificar se Flask está instalado
# Esta é uma verificação simples. Um ambiente virtual e requirements.txt seria mais robusto.
if ! ${PYTHON_EXEC} -c "import flask" &> /dev/null; then
    log_message "Aviso: Módulo Flask do Python não encontrado. Tentando instalar..."
    log_message "Recomendação: Adicionar 'pip3 install Flask' ao script 02_instalar_dependencias.sh ou usar um requirements.txt dedicado."
    # Tentativa de instalação (requer pip3 e permissões)
    if command -v pip3 &> /dev/null; then
        pip3 install Flask
        if ! ${PYTHON_EXEC} -c "import flask" &> /dev/null; then
            log_message "Erro: Falha ao instalar o Flask. Por favor, instale manualmente."
            exit 1
        fi
        log_message "Flask instalado com sucesso via pip3."
    else
        log_message "Erro: pip3 não encontrado. Não foi possível instalar o Flask automaticamente."
        exit 1
    fi
fi
log_message "Módulo Flask do Python: OK."

# 6. Navegar para o diretório do frontend e iniciar o servidor
cd "${FRONTEND_DIR}"
log_message "Navegado para o diretório: $(pwd)"

log_message "Iniciando o servidor Flask (${FRONTEND_SERVER_SCRIPT})..."
log_message "O servidor será iniciado em segundo plano. Logs do Flask serão direcionados para o console e/ou seu próprio sistema de log."

# Iniciar o servidor Flask em segundo plano
# nohup ${PYTHON_EXEC} ${FRONTEND_SERVER_SCRIPT} > /var/log/autocura_flask.log 2>&1 &
# FLASK_PID=$!

# Para este ambiente, vamos iniciar em primeiro plano e o usuário pode colocar em bg se desejar.
# Ou, se for um serviço, usar systemd (como no meuapp.service)

# Informar ao usuário como acessar
# Obter o IP da máquina (pode variar dependendo do ambiente)
IP_ADDRESS=$(hostname -I | awk '{print $1}')
if [ -z "${IP_ADDRESS}" ]; then
    IP_ADDRESS="localhost" # Fallback para localhost
fi

log_message "=================================================================="
log_message "Servidor Frontend Autocura (Flask) está sendo iniciado."
log_message "Para acessar o painel, abra seu navegador e vá para:"
log_message "http://${IP_ADDRESS}:8080  OU  http://localhost:8080"
log_message "=================================================================="
log_message "Pressione Ctrl+C para parar o servidor se estiver rodando em primeiro plano."

# Criar flag de sucesso para esta etapa
touch "${FLAG_CURRENT_STEP}"
log_message "Etapa 10 concluída com sucesso. Flag ${FLAG_CURRENT_STEP} criada."

# Executar o servidor Flask em primeiro plano
# O usuário pode optar por rodar em background manualmente (ex: com nohup ... &)
${PYTHON_EXEC} ${FRONTEND_SERVER_SCRIPT}

log_message "Servidor Flask encerrado."

exit 0

