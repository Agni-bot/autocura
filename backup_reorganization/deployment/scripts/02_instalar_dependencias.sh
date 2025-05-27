#!/bin/bash
# Descrição: Etapa 02 - Instalar Dependências do Sistema
# Este script instala os pacotes de software e bibliotecas necessários.

set -e

LOG_PREFIX="[ETAPA 02]"
FLAG_FILE_DIR="/tmp"
PREVIOUS_FLAG="${FLAG_FILE_DIR}/.etapa_01_ok"
SUCCESS_FLAG="${FLAG_FILE_DIR}/.etapa_02_ok"

# Lista de dependências (ajuste conforme necessário)
# Exemplo para um sistema que pode precisar de curl, wget, jq e git
DEPENDENCIES=("curl" "wget" "jq" "git" "unzip")

# Verificar se a etapa anterior foi concluída
echo "${LOG_PREFIX} Verificando conclusão da Etapa 01..."
if [ ! -f "${PREVIOUS_FLAG}" ]; then
    echo "${LOG_PREFIX} Erro: A Etapa 01 (validar_ambiente) não foi concluída com sucesso." >&2
    echo "${LOG_PREFIX} Execute o script 01_validar_ambiente.sh primeiro." >&2
    exit 1
fi
echo "${LOG_PREFIX} Etapa 01 concluída. Prosseguindo com a instalação de dependências."

# Determinar o gerenciador de pacotes (exemplo para Debian/Ubuntu e RHEL/CentOS/Fedora)
PACKAGE_MANAGER=""
UPDATE_COMMAND=""
INSTALL_COMMAND=""

if command -v apt-get &> /dev/null; then
    PACKAGE_MANAGER="apt-get"
    UPDATE_COMMAND="sudo apt-get update -y"
    INSTALL_COMMAND="sudo apt-get install -y"
echo "${LOG_PREFIX} Gerenciador de pacotes detectado: apt-get"
elif command -v yum &> /dev/null; then
    PACKAGE_MANAGER="yum"
    UPDATE_COMMAND="sudo yum check-update || true" # yum check-update pode sair com 100 se houver updates
    INSTALL_COMMAND="sudo yum install -y"
echo "${LOG_PREFIX} Gerenciador de pacotes detectado: yum"
elif command -v dnf &> /dev/null; then
    PACKAGE_MANAGER="dnf"
    UPDATE_COMMAND="sudo dnf check-update || true"
    INSTALL_COMMAND="sudo dnf install -y"
echo "${LOG_PREFIX} Gerenciador de pacotes detectado: dnf"
else
    echo "${LOG_PREFIX} Erro: Gerenciador de pacotes não suportado (apt-get, yum, dnf não encontrados)." >&2
    exit 1
fi

# Atualizar listas de pacotes
echo "${LOG_PREFIX} Atualizando listas de pacotes usando ${PACKAGE_MANAGER}..."
if ! ${UPDATE_COMMAND}; then
    echo "${LOG_PREFIX} Erro: Falha ao atualizar listas de pacotes." >&2
    exit 1
fi
echo "${LOG_PREFIX} Listas de pacotes atualizadas com sucesso."

# Instalar dependências
if [ ${#DEPENDENCIES[@]} -gt 0 ]; then
    echo "${LOG_PREFIX} Instalando as seguintes dependências: ${DEPENDENCIES[*]}..."
    INSTALL_CMD_FULL="${INSTALL_COMMAND}"
    for pkg in "${DEPENDENCIES[@]}"; do
        INSTALL_CMD_FULL="${INSTALL_CMD_FULL} ${pkg}"
    done

    if ! ${INSTALL_CMD_FULL}; then
        echo "${LOG_PREFIX} Erro: Falha ao instalar uma ou mais dependências (${DEPENDENCIES[*]})." >&2
        exit 1
    fi
    echo "${LOG_PREFIX} Todas as dependências listadas foram processadas pelo gerenciador de pacotes."
else
    echo "${LOG_PREFIX} Nenhuma dependência listada para instalação."
fi

# Verificar se as dependências foram realmente instaladas
ALL_INSTALLED=true
for pkg in "${DEPENDENCIES[@]}"; do
    echo "${LOG_PREFIX} Verificando instalação de ${pkg}..."
    # A forma de verificar varia. Para executáveis, `command -v` é bom.
    # Para bibliotecas, pode ser mais complexo (ex: `dpkg -s libcurl4-openssl-dev` ou `rpm -q libcurl-devel`)
    # Simplificando para `command -v` para pacotes que fornecem comandos comuns.
    # Para pacotes como 'unzip', o comando é 'unzip'. Para 'jq', é 'jq'.
    # Se o nome do pacote e do comando diferirem, ajuste aqui.
    COMMAND_TO_CHECK=${pkg}
    if [ "${pkg}" == "python3-pip" ]; then # Exemplo de ajuste
        COMMAND_TO_CHECK="pip3"
    fi

    if ! command -v "${COMMAND_TO_CHECK}" &> /dev/null; then
        # Segunda tentativa para alguns casos, ex: pacotes de desenvolvimento que não instalam comandos diretos
        # ou se a verificação inicial falhou por algum motivo e o gerenciador de pacotes disse que instalou.
        echo "${LOG_PREFIX} Aviso: Comando '${COMMAND_TO_CHECK}' não encontrado diretamente para o pacote '${pkg}'. A instalação pode ter sido bem-sucedida se for uma biblioteca."
        # Não vamos falhar aqui, pois o gerenciador de pacotes não reportou erro.
        # Poderia adicionar uma verificação mais específica se necessário.
    else
        echo "${LOG_PREFIX} Pacote/Comando ${COMMAND_TO_CHECK} verificado."
    fi
done

# Criar flag de sucesso para esta etapa
touch "${SUCCESS_FLAG}"
echo "${LOG_PREFIX} Instalação de dependências concluída."
echo "${LOG_PREFIX} Flag de sucesso criada em: ${SUCCESS_FLAG}"

exit 0

