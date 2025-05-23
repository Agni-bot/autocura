#!/bin/bash
# Descrição: Etapa 07 - Inicializar Serviços da Aplicação
# Este script configura e inicia os serviços ou daemons da aplicação.

set -e

LOG_PREFIX="[ETAPA 07]"
FLAG_FILE_DIR="/tmp"
PREVIOUS_FLAG="${FLAG_FILE_DIR}/.etapa_06_ok"
SUCCESS_FLAG="${FLAG_FILE_DIR}/.etapa_07_ok"

# Configurações do serviço (ajuste conforme necessário)
SERVICE_NAME="meuapp"
SERVICE_FILE_SOURCE="/opt/meuapp/src/config/${SERVICE_NAME}.service" # Localização do arquivo .service no pacote da app
SERVICE_FILE_DESTINATION="/etc/systemd/system/${SERVICE_NAME}.service"

# Verificar se a etapa anterior foi concluída
echo "${LOG_PREFIX} Verificando conclusão da Etapa 06..."
if [ ! -f "${PREVIOUS_FLAG}" ]; then
    echo "${LOG_PREFIX} Erro: A Etapa 06 (configurar_aplicacao) não foi concluída com sucesso." >&2
    echo "${LOG_PREFIX} Execute o script 06_configurar_aplicacao.sh primeiro." >&2
    exit 1
fi
echo "${LOG_PREFIX} Etapa 06 concluída. Prosseguindo com a inicialização dos serviços."

echo "${LOG_PREFIX} Iniciando configuração e inicialização do serviço ${SERVICE_NAME}..."

# Verificar se systemd está em uso
if ! pidof systemd &> /dev/null; then
    echo "${LOG_PREFIX} Aviso: systemd não parece ser o sistema de init. Este script é otimizado para systemd."
    echo "${LOG_PREFIX} Você pode precisar adaptar para SysVinit, Upstart, ou outro sistema de init."
    # Poderia tentar uma abordagem genérica ou sair, dependendo da complexidade.
    # Para este exemplo, vamos focar em systemd mas não sair com erro fatal imediatamente.
    # Contudo, as operações de systemctl falharão.
fi

# 1. Copiar arquivo de unit do systemd (se existir e não for igual)
echo "${LOG_PREFIX} Verificando arquivo de unit do serviço: ${SERVICE_FILE_SOURCE}"
if [ ! -f "${SERVICE_FILE_SOURCE}" ]; then
    echo "${LOG_PREFIX} Aviso: Arquivo de unit do serviço '${SERVICE_FILE_SOURCE}' não encontrado. Pulando cópia."
    echo "${LOG_PREFIX} O serviço pode precisar ser configurado manualmente ou já existir."
else
    NEEDS_COPY=true
    if [ -f "${SERVICE_FILE_DESTINATION}" ]; then
        echo "${LOG_PREFIX} Arquivo de unit de destino '${SERVICE_FILE_DESTINATION}' já existe."
        # Opcional: verificar se são diferentes antes de copiar
        if cmp -s "${SERVICE_FILE_SOURCE}" "${SERVICE_FILE_DESTINATION}"; then
            echo "${LOG_PREFIX} Arquivo de unit de destino é idêntico ao de origem. Nenhuma cópia necessária."
            NEEDS_COPY=false
        else
            echo "${LOG_PREFIX} Arquivo de unit de destino difere do de origem. Fazendo backup e substituindo..."
            sudo cp "${SERVICE_FILE_DESTINATION}" "${SERVICE_FILE_DESTINATION}.bak_$(date +%Y%m%d%H%M%S)"
        fi
    fi

    if [ "${NEEDS_COPY}" = true ]; then
        echo "${LOG_PREFIX} Copiando arquivo de unit '${SERVICE_FILE_SOURCE}' para '${SERVICE_FILE_DESTINATION}'..."
        if sudo cp "${SERVICE_FILE_SOURCE}" "${SERVICE_FILE_DESTINATION}"; then
            echo "${LOG_PREFIX} Arquivo de unit copiado com sucesso."
            sudo chmod 644 "${SERVICE_FILE_DESTINATION}" # Permissões padrão para arquivos de unit
        else
            echo "${LOG_PREFIX} Erro: Falha ao copiar o arquivo de unit do serviço." >&2
            exit 1
        fi
    fi
fi

# 2. Recarregar o daemon do systemd
# Só faz sentido se um arquivo de unit foi copiado/modificado ou se systemd está presente.
if [ -f "${SERVICE_FILE_DESTINATION}" ] && pidof systemd &> /dev/null; then # Verifica se o arquivo de destino existe
    echo "${LOG_PREFIX} Recarregando daemon do systemd..."
    if sudo systemctl daemon-reload; then
        echo "${LOG_PREFIX} Daemon do systemd recarregado com sucesso."
    else
        echo "${LOG_PREFIX} Erro: Falha ao recarregar o daemon do systemd." >&2
        exit 1
    fi
else
    echo "${LOG_PREFIX} Pulando recarregamento do systemd (arquivo de unit não gerenciado por este script ou systemd não ativo)."
fi

# 3. Habilitar o serviço para iniciar no boot (se systemd estiver ativo e o serviço existir)
if pidof systemd &> /dev/null && sudo systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
    echo "${LOG_PREFIX} Verificando se o serviço ${SERVICE_NAME} está habilitado..."
    if sudo systemctl is-enabled "${SERVICE_NAME}" &> /dev/null; then
        echo "${LOG_PREFIX} Serviço ${SERVICE_NAME} já está habilitado."
    else
        echo "${LOG_PREFIX} Habilitando serviço ${SERVICE_NAME} para iniciar no boot..."
        if sudo systemctl enable "${SERVICE_NAME}"; then
            echo "${LOG_PREFIX} Serviço ${SERVICE_NAME} habilitado com sucesso."
        else
            echo "${LOG_PREFIX} Erro: Falha ao habilitar o serviço ${SERVICE_NAME}." >&2
            # Não necessariamente um erro fatal, a aplicação pode ser iniciada manualmente.
        fi
    fi
else
    echo "${LOG_PREFIX} Pulando habilitação do serviço (systemd não ativo ou serviço ${SERVICE_NAME} não encontrado)."
fi

# 4. Iniciar/Reiniciar o serviço (se systemd estiver ativo e o serviço existir)
if pidof systemd &> /dev/null && sudo systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
    echo "${LOG_PREFIX} Tentando iniciar/reiniciar o serviço ${SERVICE_NAME}..."
    # Usar restart para garantir que está usando a config mais recente, ou start se for a primeira vez.
    # `systemctl try-restart` é mais seguro se não souber o estado.
    # `systemctl restart` irá iniciar se não estiver rodando.
    if sudo systemctl restart "${SERVICE_NAME}"; then
        echo "${LOG_PREFIX} Comando de restart para o serviço ${SERVICE_NAME} enviado com sucesso."
        # Dar um tempo para o serviço iniciar antes de verificar o status
        echo "${LOG_PREFIX} Aguardando alguns segundos para o serviço iniciar..."
        sleep 5

        echo "${LOG_PREFIX} Verificando status do serviço ${SERVICE_NAME}..."
        if sudo systemctl is-active "${SERVICE_NAME}" &> /dev/null; then
            echo "${LOG_PREFIX} Serviço ${SERVICE_NAME} está ativo e rodando."
        else
            echo "${LOG_PREFIX} Erro: Serviço ${SERVICE_NAME} não está ativo após tentativa de início/restart." >&2
            sudo systemctl status "${SERVICE_NAME}" --no-pager || true # Mostrar mais detalhes do erro
            exit 1
        fi
    else
        echo "${LOG_PREFIX} Erro: Falha ao enviar comando de restart para o serviço ${SERVICE_NAME}." >&2
        sudo systemctl status "${SERVICE_NAME}" --no-pager || true
        exit 1
    fi
else
    echo "${LOG_PREFIX} Pulando início/restart do serviço (systemd não ativo ou serviço ${SERVICE_NAME} não encontrado)."
    echo "${LOG_PREFIX} Se este serviço for gerenciado por outro sistema (ex: init.d, supervisord), inicie-o manualmente."
fi

# Criar flag de sucesso para esta etapa
touch "${SUCCESS_FLAG}"
echo "${LOG_PREFIX} Inicialização de serviços concluída."
echo "${LOG_PREFIX} Flag de sucesso criada em: ${SUCCESS_FLAG}"

exit 0

