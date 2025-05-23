#!/bin/bash
# Descrição: Etapa 06 - Configurar Aplicação
# Este script configura a aplicação com base em templates ou configurações padrão.

set -e

LOG_PREFIX="[ETAPA 06]"
FLAG_FILE_DIR="/tmp"
PREVIOUS_FLAG="${FLAG_FILE_DIR}/.etapa_05_ok"
SUCCESS_FLAG="${FLAG_FILE_DIR}/.etapa_06_ok"

# Diretórios (definidos em etapas anteriores)
BASE_INSTALL_DIR="/opt/meuapp"
APP_SOURCE_DIR="${BASE_INSTALL_DIR}/src" # Onde os artefatos foram baixados/extraídos
CONFIG_DIR="/etc/meuapp"

# Arquivos de configuração (exemplos)
CONFIG_TEMPLATE_FILE="${APP_SOURCE_DIR}/config/meuapp.conf.template"
CONFIG_TARGET_FILE="${CONFIG_DIR}/meuapp.conf"

# Usuário da aplicação
APP_USER="meuappuser"

# Verificar se a etapa anterior foi concluída
echo "${LOG_PREFIX} Verificando conclusão da Etapa 05..."
if [ ! -f "${PREVIOUS_FLAG}" ]; then
    echo "${LOG_PREFIX} Erro: A Etapa 05 (baixar_artefatos_aplicacao) não foi concluída com sucesso." >&2
    echo "${LOG_PREFIX} Execute o script 05_baixar_artefatos_aplicacao.sh primeiro." >&2
    exit 1
fi
echo "${LOG_PREFIX} Etapa 05 concluída. Prosseguindo com a configuração da aplicação."

echo "${LOG_PREFIX} Iniciando configuração da aplicação..."

# 1. Verificar se o diretório de configuração existe (deve ter sido criado na Etapa 04)
if [ ! -d "${CONFIG_DIR}" ]; then
    echo "${LOG_PREFIX} Erro: Diretório de configuração '${CONFIG_DIR}' não encontrado." >&2
    echo "${LOG_PREFIX} Certifique-se de que a Etapa 04 foi executada corretamente." >&2
    exit 1
fi

# 2. Copiar arquivo de configuração template para o local de destino
# (se o arquivo de configuração final não existir ou se uma atualização for forçada)
echo "${LOG_PREFIX} Verificando arquivo de configuração template: ${CONFIG_TEMPLATE_FILE}"
if [ ! -f "${CONFIG_TEMPLATE_FILE}" ]; then
    echo "${LOG_PREFIX} Aviso: Arquivo de configuração template '${CONFIG_TEMPLATE_FILE}' não encontrado. Pulando cópia de template."
    # Dependendo da aplicação, isso pode ser um erro fatal ou apenas significar que a config é manual.
else
    if [ -f "${CONFIG_TARGET_FILE}" ]; then
        echo "${LOG_PREFIX} Arquivo de configuração '${CONFIG_TARGET_FILE}' já existe. Verifique se precisa ser atualizado manualmente ou faça um backup."
        # Opcional: fazer backup do arquivo existente
        # sudo cp "${CONFIG_TARGET_FILE}" "${CONFIG_TARGET_FILE}.bak_$(date +%Y%m%d%H%M%S)"
        # Opcional: sobrescrever se necessário, ou pular.
        # Para este exemplo, vamos assumir que se existe, não sobrescrevemos automaticamente.
        echo "${LOG_PREFIX} Mantendo arquivo de configuração existente: ${CONFIG_TARGET_FILE}"
    else
        echo "${LOG_PREFIX} Copiando template '${CONFIG_TEMPLATE_FILE}' para '${CONFIG_TARGET_FILE}'..."
        if sudo cp "${CONFIG_TEMPLATE_FILE}" "${CONFIG_TARGET_FILE}"; then
            echo "${LOG_PREFIX} Arquivo de configuração copiado com sucesso."
            # Definir proprietário e permissões para o arquivo de configuração
            sudo chown "${APP_USER}:${APP_USER}" "${CONFIG_TARGET_FILE}" # Ou root:APP_GROUP dependendo da necessidade
            sudo chmod 640 "${CONFIG_TARGET_FILE}" # Ex: User=rw, Group=r, Other=---
        else
            echo "${LOG_PREFIX} Erro: Falha ao copiar o arquivo de configuração template." >&2
            exit 1
        fi
    fi
fi

# 3. Substituir placeholders no arquivo de configuração (Exemplo)
# Esta é uma etapa comum. Suponha que CONFIG_TARGET_FILE tenha placeholders como {{DB_HOST}} ou {{API_PORT}}.
# Estes valores podem vir de variáveis de ambiente, um arquivo de respostas, ou serem fixos.
DB_HOST_VALUE="localhost"
API_PORT_VALUE="8080"

if [ -f "${CONFIG_TARGET_FILE}" ]; then # Apenas se o arquivo de configuração existir
    echo "${LOG_PREFIX} Aplicando configurações dinâmicas em '${CONFIG_TARGET_FILE}' (exemplo)..."
    # Exemplo usando sed. Cuidado com caracteres especiais nos valores.
    # É mais seguro usar ferramentas como `envsubst` se os placeholders forem como $VAR.
    # sudo sed -i "s/{{DB_HOST}}/${DB_HOST_VALUE}/g" "${CONFIG_TARGET_FILE}"
    # sudo sed -i "s/{{API_PORT}}/${API_PORT_VALUE}/g" "${CONFIG_TARGET_FILE}"
    # Para este script, vamos apenas logar a intenção, pois a substituição real é complexa e depende do formato.
    echo "${LOG_PREFIX} (Simulado) Configuração para DB_HOST=${DB_HOST_VALUE} e API_PORT=${API_PORT_VALUE} seria aplicada aqui."
    
    # Validar se o arquivo de configuração é sintaticamente válido (se a aplicação tiver um validador)
    # Exemplo: meuapp_validator --config ${CONFIG_TARGET_FILE}
    # if ! meuapp_validator --config "${CONFIG_TARGET_FILE}"; then
    #     echo "${LOG_PREFIX} Erro: Arquivo de configuração '${CONFIG_TARGET_FILE}' é inválido após substituições." >&2
    #     exit 1
    # fi
    echo "${LOG_PREFIX} (Simulado) Validação de sintaxe do arquivo de configuração passaria aqui."
else
    echo "${LOG_PREFIX} Aviso: Arquivo de configuração alvo '${CONFIG_TARGET_FILE}' não encontrado. Pulando substituição de placeholders."
fi

# 4. Outras tarefas de configuração específicas da aplicação
# Ex: criar links simbólicos, configurar chaves de API, etc.
echo "${LOG_PREFIX} Executando outras tarefas de configuração específicas da aplicação (se houver)..."
# Exemplo: sudo ln -s "${BASE_INSTALL_DIR}/data" "${APP_SOURCE_DIR}/webapp/staticdata"
echo "${LOG_PREFIX} (Simulado) Outras tarefas de configuração seriam executadas aqui."

# Criar flag de sucesso para esta etapa
touch "${SUCCESS_FLAG}"
echo "${LOG_PREFIX} Configuração da aplicação concluída com sucesso."
echo "${LOG_PREFIX} Flag de sucesso criada em: ${SUCCESS_FLAG}"

exit 0

