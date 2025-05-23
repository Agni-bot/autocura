#!/bin/bash
# Descrição: Etapa 04 - Criar Estrutura de Diretórios da Aplicação
# Este script cria os diretórios necessários para a instalação e operação do sistema.

set -e

LOG_PREFIX="[ETAPA 04]"
FLAG_FILE_DIR="/tmp"
PREVIOUS_FLAG="${FLAG_FILE_DIR}/.etapa_03_ok"
SUCCESS_FLAG="${FLAG_FILE_DIR}/.etapa_04_ok"

# Configurações de diretórios (ajuste conforme necessário)
# Usar variáveis para caminhos críticos
BASE_INSTALL_DIR="/opt/meuapp"
CONFIG_DIR="/etc/meuapp"
LOG_DIR="/var/log/meuapp"
DATA_DIR="/var/lib/meuapp"
TMP_DIR="/tmp/meuapp"

# Usuário e grupo da aplicação (definidos na Etapa 03)
APP_USER="meuappuser"
APP_GROUP="meuappgroup"

# Verificar se a etapa anterior foi concluída
echo "${LOG_PREFIX} Verificando conclusão da Etapa 03..."
if [ ! -f "${PREVIOUS_FLAG}" ]; then
    echo "${LOG_PREFIX} Erro: A Etapa 03 (configurar_usuarios_grupos) não foi concluída com sucesso." >&2
    echo "${LOG_PREFIX} Execute o script 03_configurar_usuarios_grupos.sh primeiro." >&2
    exit 1
fi
echo "${LOG_PREFIX} Etapa 03 concluída. Prosseguindo com a criação de diretórios."

DIRECTORIES_TO_CREATE=(
    "${BASE_INSTALL_DIR}"
    "${CONFIG_DIR}"
    "${LOG_DIR}"
    "${DATA_DIR}"
    "${TMP_DIR}"
)

echo "${LOG_PREFIX} Iniciando criação da estrutura de diretórios..."

for DIR_PATH in "${DIRECTORIES_TO_CREATE[@]}"; do
    echo "${LOG_PREFIX} Verificando/Criando diretório: ${DIR_PATH}"
    if [ -d "${DIR_PATH}" ]; then
        echo "${LOG_PREFIX} Diretório '${DIR_PATH}' já existe."
    else
        if sudo mkdir -p "${DIR_PATH}"; then
            echo "${LOG_PREFIX} Diretório '${DIR_PATH}' criado com sucesso."
        else
            echo "${LOG_PREFIX} Erro: Falha ao criar o diretório '${DIR_PATH}'." >&2
            exit 1
        fi
    fi

    # Definir permissões e propriedade
    # Permissões podem variar: 755 para diretórios onde o usuário precisa listar/entrar,
    # 770 ou 750 se o grupo precisa de escrita, etc.
    # Exemplo: Dono (appuser) tem rwx, Grupo (appgroup) tem r-x, Outros não têm nada.
    echo "${LOG_PREFIX} Definindo proprietário '${APP_USER}:${APP_GROUP}' para '${DIR_PATH}'..."
    if sudo chown "${APP_USER}:${APP_GROUP}" "${DIR_PATH}"; then
        echo "${LOG_PREFIX} Proprietário definido com sucesso para '${DIR_PATH}'."
    else
        echo "${LOG_PREFIX} Erro: Falha ao definir proprietário para '${DIR_PATH}'." >&2
        # Considerar se é um erro fatal
    fi

    echo "${LOG_PREFIX} Definindo permissões (ex: 770) para '${DIR_PATH}'..."
    # 770: User=rwx, Group=rwx, Other=---
    # Ajuste conforme a necessidade de segurança da sua aplicação
    if sudo chmod 770 "${DIR_PATH}"; then # Exemplo, pode ser 750, 700, etc.
        echo "${LOG_PREFIX} Permissões definidas com sucesso para '${DIR_PATH}'."
    else
        echo "${LOG_PREFIX} Erro: Falha ao definir permissões para '${DIR_PATH}'." >&2
        # Considerar se é um erro fatal
    fi
done

# Criar flag de sucesso para esta etapa
touch "${SUCCESS_FLAG}"
echo "${LOG_PREFIX} Criação da estrutura de diretórios concluída com sucesso."
echo "${LOG_PREFIX} Flag de sucesso criada em: ${SUCCESS_FLAG}"

exit 0

