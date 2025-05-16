#!/bin/bash
# Descrição: Etapa 05 - Baixar e Preparar Artefatos da Aplicação
# Este script simula o download e extração dos artefatos da aplicação,
# garantindo que os arquivos de configuração template estejam disponíveis.

set -e

LOG_PREFIX="[ETAPA 05]"
FLAG_FILE_DIR="/tmp"
PREVIOUS_FLAG="${FLAG_FILE_DIR}/.etapa_04_ok"
SUCCESS_FLAG="${FLAG_FILE_DIR}/.etapa_05_ok"

# Configurações (ajuste conforme necessário)
BASE_INSTALL_DIR="/opt/meuapp"
# DOWNLOAD_DIR é onde o código/binários da aplicação residiriam.
# Para este exemplo, será /opt/meuapp/src
DOWNLOAD_DIR="${BASE_INSTALL_DIR}/src"
# APP_CONFIG_SOURCE_DIR é onde os templates de config estão no "pacote" simulado
APP_CONFIG_SOURCE_DIR="/mnt/c/Users/filip/OneDrive/Área de Trabalho/autocura/app_package_placeholders/config"
APP_CONFIG_TARGET_SUBDIR="config" # Subdiretório dentro de DOWNLOAD_DIR para os configs

# Usuário e grupo da aplicação (para definir propriedade dos arquivos)
APP_USER="meuappuser"
APP_GROUP="meuappgroup"

# Verificar se a etapa anterior foi concluída
echo "${LOG_PREFIX} Verificando conclusão da Etapa 04..."
if [ ! -f "${PREVIOUS_FLAG}" ]; then
    echo "${LOG_PREFIX} Erro: A Etapa 04 (criar_diretorios) não foi concluída com sucesso." >&2
    echo "${LOG_PREFIX} Execute o script 04_criar_diretorios.sh primeiro." >&2
    exit 1
fi
echo "${LOG_PREFIX} Etapa 04 concluída. Prosseguindo com a preparação dos artefatos da aplicação."

# Garantir que o diretório de "download/extração" principal exista
# Este diretório (DOWNLOAD_DIR) deve ter sido criado e ter permissões definidas na Etapa 04 se for o mesmo que BASE_INSTALL_DIR
# Se for um subdiretório como /opt/meuapp/src, precisa ser criado aqui ou na Etapa 04.
echo "${LOG_PREFIX} Verificando/Criando diretório de artefatos da aplicação: ${DOWNLOAD_DIR}"
if [ ! -d "${DOWNLOAD_DIR}" ]; then
    if sudo mkdir -p "${DOWNLOAD_DIR}"; then
        echo "${LOG_PREFIX} Diretório de artefatos da aplicação '${DOWNLOAD_DIR}' criado."
        sudo chown "${APP_USER}:${APP_GROUP}" "${DOWNLOAD_DIR}"
        sudo chmod 770 "${DOWNLOAD_DIR}" # Ajuste conforme necessário
    else
        echo "${LOG_PREFIX} Erro: Falha ao criar o diretório de artefatos da aplicação '${DOWNLOAD_DIR}'." >&2
        exit 1
    fi
else
    echo "${LOG_PREFIX} Diretório de artefatos da aplicação '${DOWNLOAD_DIR}' já existe."
fi

# 1. Simular "Download e Extração" - Copiando arquivos de configuração placeholder
# Em um cenário real, aqui você baixaria um .tar.gz ou .zip e o extrairia.
# A extração resultaria nos arquivos da aplicação, incluindo os templates de configuração.

TARGET_CONFIG_DIR="${DOWNLOAD_DIR}/${APP_CONFIG_TARGET_SUBDIR}"
echo "${LOG_PREFIX} Verificando/Criando diretório de configuração da aplicação em ${TARGET_CONFIG_DIR}..."
if sudo mkdir -p "${TARGET_CONFIG_DIR}"; then
    echo "${LOG_PREFIX} Diretório de configuração da aplicação '${TARGET_CONFIG_DIR}' criado/verificado."
    sudo chown "${APP_USER}:${APP_GROUP}" "${TARGET_CONFIG_DIR}"
    sudo chmod 770 "${TARGET_CONFIG_DIR}" # Ajuste conforme necessário
else
    echo "${LOG_PREFIX} Erro: Falha ao criar o diretório de configuração da aplicação '${TARGET_CONFIG_DIR}'." >&2
    exit 1
fi

CONFIG_TEMPLATE_SOURCE_FILE="${APP_CONFIG_SOURCE_DIR}/meuapp.conf.template"
CONFIG_TEMPLATE_DEST_FILE="${TARGET_CONFIG_DIR}/meuapp.conf.template"
SERVICE_TEMPLATE_SOURCE_FILE="${APP_CONFIG_SOURCE_DIR}/meuapp.service"
SERVICE_TEMPLATE_DEST_FILE="${TARGET_CONFIG_DIR}/meuapp.service"

echo "${LOG_PREFIX} Copiando arquivo de configuração template para ${CONFIG_TEMPLATE_DEST_FILE}..."
if sudo cp "${CONFIG_TEMPLATE_SOURCE_FILE}" "${CONFIG_TEMPLATE_DEST_FILE}"; then
    echo "${LOG_PREFIX} Arquivo '${CONFIG_TEMPLATE_DEST_FILE}' copiado com sucesso."
    sudo chown "${APP_USER}:${APP_GROUP}" "${CONFIG_TEMPLATE_DEST_FILE}"
    sudo chmod 660 "${CONFIG_TEMPLATE_DEST_FILE}" # User/Group rw, Other ---
else
    echo "${LOG_PREFIX} Erro: Falha ao copiar '${CONFIG_TEMPLATE_SOURCE_FILE}' para '${CONFIG_TEMPLATE_DEST_FILE}'." >&2
    exit 1
fi

echo "${LOG_PREFIX} Copiando arquivo de serviço template para ${SERVICE_TEMPLATE_DEST_FILE}..."
if sudo cp "${SERVICE_TEMPLATE_SOURCE_FILE}" "${SERVICE_TEMPLATE_DEST_FILE}"; then
    echo "${LOG_PREFIX} Arquivo '${SERVICE_TEMPLATE_DEST_FILE}' copiado com sucesso."
    sudo chown "${APP_USER}:${APP_GROUP}" "${SERVICE_TEMPLATE_DEST_FILE}"
    sudo chmod 660 "${SERVICE_TEMPLATE_DEST_FILE}" # User/Group rw, Other ---
else
    echo "${LOG_PREFIX} Erro: Falha ao copiar '${SERVICE_TEMPLATE_SOURCE_FILE}' para '${SERVICE_TEMPLATE_DEST_FILE}'." >&2
    exit 1
fi

echo "${LOG_PREFIX} Simulação de download e extração de artefatos (com foco nos arquivos de configuração) concluída."

# 2. Definir Propriedade de todo o diretório de artefatos (reafirmar, se necessário)
echo "${LOG_PREFIX} (Reafirmando) Definindo proprietário '${APP_USER}:${APP_GROUP}' para o conteúdo de '${DOWNLOAD_DIR}'..."
if sudo chown -R "${APP_USER}:${APP_GROUP}" "${DOWNLOAD_DIR}"; then
    echo "${LOG_PREFIX} Proprietário definido com sucesso para o conteúdo de '${DOWNLOAD_DIR}'."
else
    echo "${LOG_PREFIX} Erro: Falha ao definir proprietário para o conteúdo de '${DOWNLOAD_DIR}'." >&2
    # Considerar se é um erro fatal
fi

# Criar flag de sucesso para esta etapa
touch "${SUCCESS_FLAG}"
echo "${LOG_PREFIX} Preparação dos artefatos da aplicação (incluindo templates de config) concluída com sucesso."
echo "${LOG_PREFIX} Flag de sucesso criada em: ${SUCCESS_FLAG}"

exit 0

