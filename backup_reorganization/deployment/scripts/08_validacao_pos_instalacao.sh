#!/bin/bash
# Descrição: Etapa 08 - Validação Pós-Instalação
# Este script realiza verificações básicas para confirmar que a aplicação foi instalada e está funcionando.

set -e

LOG_PREFIX="[ETAPA 08]"
FLAG_FILE_DIR="/tmp"
PREVIOUS_FLAG="${FLAG_FILE_DIR}/.etapa_07_ok"
SUCCESS_FLAG="${FLAG_FILE_DIR}/.etapa_08_ok"

# Configurações de validação (ajuste conforme necessário)
APP_HEALTH_CHECK_URL="http://localhost:8080/health" # Exemplo de endpoint de health check
EXPECTED_HEALTH_RESPONSE_CONTAINS="OK" # Substring esperada na resposta do health check
SERVICE_NAME="meuapp"
LOG_DIR="/var/log/meuapp"
APP_LOG_FILE="${LOG_DIR}/${SERVICE_NAME}.log"

# Verificar se a etapa anterior foi concluída
echo "${LOG_PREFIX} Verificando conclusão da Etapa 07..."
if [ ! -f "${PREVIOUS_FLAG}" ]; then
    echo "${LOG_PREFIX} Erro: A Etapa 07 (inicializar_servicos) não foi concluída com sucesso." >&2
    echo "${LOG_PREFIX} Execute o script 07_inicializar_servicos.sh primeiro." >&2
    exit 1
fi
echo "${LOG_PREFIX} Etapa 07 concluída. Prosseguindo com a validação pós-instalação."

echo "${LOG_PREFIX} Iniciando validação pós-instalação..."

# 1. Verificar se o serviço principal está ativo (se gerenciado por systemd)
if pidof systemd &> /dev/null && sudo systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
    echo "${LOG_PREFIX} Verificando status do serviço ${SERVICE_NAME} via systemd..."
    if sudo systemctl is-active "${SERVICE_NAME}" &> /dev/null; then
        echo "${LOG_PREFIX} Serviço ${SERVICE_NAME} está ativo."
    else
        echo "${LOG_PREFIX} Erro: Serviço ${SERVICE_NAME} não está ativo." >&2
        sudo systemctl status "${SERVICE_NAME}" --no-pager || true
        exit 1
    fi
else
    echo "${LOG_PREFIX} Aviso: Não foi possível verificar o status do serviço ${SERVICE_NAME} via systemd (systemd não ativo ou serviço não encontrado)."
    echo "${LOG_PREFIX} A validação prosseguirá com outras checagens, mas o estado do serviço é incerto."
fi

# 2. Testar endpoint de health check da aplicação (se aplicável)
if [ -n "${APP_HEALTH_CHECK_URL}" ]; then
    echo "${LOG_PREFIX} Testando endpoint de health check: ${APP_HEALTH_CHECK_URL}"
    # Aguardar um pouco mais para garantir que a aplicação esteja totalmente operacional
    sleep 5 
    HEALTH_RESPONSE_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${APP_HEALTH_CHECK_URL}" || true)
    
    if [ "${HEALTH_RESPONSE_CODE}" -eq 200 ]; then
        echo "${LOG_PREFIX} Health check retornou HTTP 200 OK."
        if [ -n "${EXPECTED_HEALTH_RESPONSE_CONTAINS}" ]; then
            HEALTH_RESPONSE_BODY=$(curl -s "${APP_HEALTH_CHECK_URL}" || true)
            if echo "${HEALTH_RESPONSE_BODY}" | grep -q "${EXPECTED_HEALTH_RESPONSE_CONTAINS}"; then
                echo "${LOG_PREFIX} Resposta do health check contém o texto esperado: '${EXPECTED_HEALTH_RESPONSE_CONTAINS}'."
            else
                echo "${LOG_PREFIX} Erro: Resposta do health check não contém '${EXPECTED_HEALTH_RESPONSE_CONTAINS}'. Corpo da resposta:" >&2
                echo "${HEALTH_RESPONSE_BODY}" >&2
                exit 1
            fi
        fi
    else
        echo "${LOG_PREFIX} Erro: Health check falhou. Código HTTP retornado: ${HEALTH_RESPONSE_CODE} (Esperado: 200)" >&2
        # Tentar obter o corpo da resposta em caso de erro, se houver
        curl -s "${APP_HEALTH_CHECK_URL}" >&2 || true 
        exit 1
    fi
else
    echo "${LOG_PREFIX} Aviso: URL de health check não configurada (APP_HEALTH_CHECK_URL vazia). Pulando teste de endpoint."
fi

# 3. Verificar logs iniciais da aplicação por erros óbvios (exemplo básico)
if [ -f "${APP_LOG_FILE}" ]; then
    echo "${LOG_PREFIX} Verificando logs da aplicação em ${APP_LOG_FILE} por erros recentes..."
    # Procurar por palavras-chave de erro comuns nos últimos N minutos (ex: últimas 100 linhas)
    # Esta é uma verificação muito simples e pode precisar de refinamento.
    RECENT_LOGS=$(sudo tail -n 100 "${APP_LOG_FILE}" || true)
    if echo "${RECENT_LOGS}" | grep -E -i "(ERROR|FATAL|CRITICAL|Exception|Traceback)"; then 
        echo "${LOG_PREFIX} Aviso: Possíveis erros encontrados nos logs recentes da aplicação. Revise ${APP_LOG_FILE} manualmente." >&2
        echo "--- Início dos Logs Suspeitos ---" >&2
        echo "${RECENT_LOGS}" | grep -E -i "(ERROR|FATAL|CRITICAL|Exception|Traceback)" --color=always >&2
        echo "--- Fim dos Logs Suspeitos ---" >&2
        # Não sair com erro fatal, apenas avisar, pois a aplicação pode estar funcional apesar de alguns erros iniciais.
    else
        echo "${LOG_PREFIX} Nenhuma mensagem de erro óbvia encontrada nos logs recentes."
    fi
else 
    echo "${LOG_PREFIX} Aviso: Arquivo de log da aplicação (${APP_LOG_FILE}) não encontrado. Pulando verificação de logs."
fi

# 4. Executar um comando básico da aplicação que indique sucesso (se aplicável)
# Exemplo: se a aplicação tiver um CLI para verificar a versão ou status
# APP_CLI_COMMAND="/opt/meuapp/bin/meuapp-cli --version"
# if command -v "${APP_CLI_COMMAND% *}" &> /dev/null; then # Verifica se o comando base existe
#     echo "${LOG_PREFIX} Executando comando de validação da aplicação: ${APP_CLI_COMMAND}"
#     if sudo -u meuappuser ${APP_CLI_COMMAND}; then # Executar como usuário da app se necessário
#         echo "${LOG_PREFIX} Comando de validação da aplicação executado com sucesso."
#     else
#         echo "${LOG_PREFIX} Erro: Falha ao executar o comando de validação da aplicação." >&2
#         exit 1
#     fi
# else
#     echo "${LOG_PREFIX} Aviso: Comando CLI da aplicação não configurado ou não encontrado. Pulando esta validação."
# fi
echo "${LOG_PREFIX} (Simulado) Comando de validação específico da aplicação seria executado aqui."

# Criar flag de sucesso para esta etapa
touch "${SUCCESS_FLAG}"
echo "${LOG_PREFIX} Validação pós-instalação concluída com sucesso."
echo "${LOG_PREFIX} Flag de sucesso criada em: ${SUCCESS_FLAG}"

exit 0

