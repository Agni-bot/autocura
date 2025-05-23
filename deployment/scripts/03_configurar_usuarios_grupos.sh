#!/bin/bash
# Descrição: Etapa 03 - Configurar Usuários e Grupos Dedicados
# Este script cria um usuário e um grupo dedicados para a aplicação, se não existirem.

set -e

LOG_PREFIX="[ETAPA 03]"
FLAG_FILE_DIR="/tmp"
PREVIOUS_FLAG="${FLAG_FILE_DIR}/.etapa_02_ok"
SUCCESS_FLAG="${FLAG_FILE_DIR}/.etapa_03_ok"

# Configurações do usuário e grupo da aplicação
APP_USER="meuappuser"
APP_GROUP="meuappgroup"
USER_SHELL="/bin/false" # Shell de nologin para usuários de serviço
USER_HOME_DIR_BASE="/home" # Diretório base para o home do usuário, se necessário (opcional)
# USER_HOME_DIR="${USER_HOME_DIR_BASE}/${APP_USER}" # Descomente se um diretório home for necessário

# Verificar se a etapa anterior foi concluída
echo "${LOG_PREFIX} Verificando conclusão da Etapa 02..."
if [ ! -f "${PREVIOUS_FLAG}" ]; then
    echo "${LOG_PREFIX} Erro: A Etapa 02 (instalar_dependencias) não foi concluída com sucesso." >&2
    echo "${LOG_PREFIX} Execute o script 02_instalar_dependencias.sh primeiro." >&2
    exit 1
fi
echo "${LOG_PREFIX} Etapa 02 concluída. Prosseguindo com a configuração de usuários e grupos."

# 1. Verificar e Criar Grupo da Aplicação
echo "${LOG_PREFIX} Verificando se o grupo '${APP_GROUP}' existe..."
if getent group "${APP_GROUP}" > /dev/null; then
    echo "${LOG_PREFIX} Grupo '${APP_GROUP}' já existe."
else
    echo "${LOG_PREFIX} Grupo '${APP_GROUP}' não encontrado. Criando grupo..."
    if sudo groupadd "${APP_GROUP}"; then
        echo "${LOG_PREFIX} Grupo '${APP_GROUP}' criado com sucesso."
    else
        echo "${LOG_PREFIX} Erro: Falha ao criar o grupo '${APP_GROUP}'." >&2
        exit 1
    fi
fi

# 2. Verificar e Criar Usuário da Aplicação
echo "${LOG_PREFIX} Verificando se o usuário '${APP_USER}' existe..."
if id "${APP_USER}" &>/dev/null; then
    echo "${LOG_PREFIX} Usuário '${APP_USER}' já existe."
    # Opcional: verificar se o usuário pertence ao grupo correto e ajustar se necessário
    if ! groups "${APP_USER}" | grep -q "\b${APP_GROUP}\b"; then
        echo "${LOG_PREFIX} Usuário '${APP_USER}' não pertence ao grupo '${APP_GROUP}'. Adicionando..."
        if sudo usermod -a -G "${APP_GROUP}" "${APP_USER}"; then
            echo "${LOG_PREFIX} Usuário '${APP_USER}' adicionado ao grupo '${APP_GROUP}' com sucesso."
        else
            echo "${LOG_PREFIX} Erro: Falha ao adicionar usuário '${APP_USER}' ao grupo '${APP_GROUP}'." >&2
            # Não sair necessariamente, mas registrar o erro
        fi
    fi
else
    echo "${LOG_PREFIX} Usuário '${APP_USER}' não encontrado. Criando usuário..."
    # Criar usuário do sistema (-r), com grupo primário APP_GROUP, shell de nologin.
    # A opção -m para criar diretório home é opcional e depende da necessidade da aplicação.
    # Se for criar home, certifique-se que USER_HOME_DIR está definido e o diretório base existe.
    # CREATE_HOME_OPTION="-m -d ${USER_HOME_DIR}" # Descomente e ajuste se precisar de home
    CREATE_HOME_OPTION=""
    if sudo useradd -r -s "${USER_SHELL}" -g "${APP_GROUP}" ${CREATE_HOME_OPTION} "${APP_USER}"; then
        echo "${LOG_PREFIX} Usuário '${APP_USER}' criado com sucesso e adicionado ao grupo '${APP_GROUP}'."
    else
        echo "${LOG_PREFIX} Erro: Falha ao criar o usuário '${APP_USER}'." >&2
        exit 1
    fi
fi

# Criar flag de sucesso para esta etapa
touch "${SUCCESS_FLAG}"
echo "${LOG_PREFIX} Configuração de usuários e grupos concluída com sucesso."
echo "${LOG_PREFIX} Flag de sucesso criada em: ${SUCCESS_FLAG}"

exit 0

