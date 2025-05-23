#!/bin/bash
# Descrição: Etapa 09 - Limpeza Pós-Instalação
# Este script remove arquivos temporários de instalação que não são mais necessários.

set -e

LOG_PREFIX="[ETAPA 09]"
FLAG_FILE_DIR="/tmp"
PREVIOUS_FLAG="${FLAG_FILE_DIR}/.etapa_08_ok"
SUCCESS_FLAG="${FLAG_FILE_DIR}/.etapa_09_ok"

# Configurações de limpeza (ajuste conforme necessário)
# Diretório onde os artefatos foram baixados (Etapa 05)
DOWNLOAD_DIR_BASE="/opt/meuapp"
ARTIFACT_DOWNLOAD_DIR="${DOWNLOAD_DIR_BASE}/src" # Onde o .tar.gz ou .zip foi baixado
ARTIFACT_FILENAME="meuapp-v1.0.0.tar.gz" # Nome do arquivo baixado, se ainda existir e precisar ser removido

# Outros diretórios/arquivos temporários criados durante a instalação
TEMP_INSTALL_FILES_DIR="/tmp/meuapp_install_temp" # Exemplo de um diretório temporário geral

# Verificar se a etapa anterior foi concluída
echo "${LOG_PREFIX} Verificando conclusão da Etapa 08..."
if [ ! -f "${PREVIOUS_FLAG}" ]; then
    echo "${LOG_PREFIX} Erro: A Etapa 08 (validacao_pos_instalacao) não foi concluída com sucesso." >&2
    echo "${LOG_PREFIX} Execute o script 08_validacao_pos_instalacao.sh primeiro." >&2
    exit 1
fi
echo "${LOG_PREFIX} Etapa 08 concluída. Prosseguindo com a limpeza pós-instalação."

echo "${LOG_PREFIX} Iniciando limpeza pós-instalação..."

# 1. Remover arquivo de artefato baixado (se não foi removido na Etapa 05 e se desejado)
DOWNLOADED_ARTIFACT_PATH="${ARTIFACT_DOWNLOAD_DIR}/${ARTIFACT_FILENAME}"
if [ -f "${DOWNLOADED_ARTIFACT_PATH}" ]; then
    echo "${LOG_PREFIX} Removendo arquivo de artefato baixado: ${DOWNLOADED_ARTIFACT_PATH}"
    if sudo rm -f "${DOWNLOADED_ARTIFACT_PATH}"; then
        echo "${LOG_PREFIX} Arquivo de artefato ${DOWNLOADED_ARTIFACT_PATH} removido com sucesso."
    else
        echo "${LOG_PREFIX} Aviso: Falha ao remover o arquivo de artefato ${DOWNLOADED_ARTIFACT_PATH}. Verifique manualmente." >&2
    fi
else
    echo "${LOG_PREFIX} Arquivo de artefato ${DOWNLOADED_ARTIFACT_PATH} não encontrado ou já removido. Nenhuma ação necessária."
fi

# 2. Remover outros diretórios ou arquivos temporários de instalação
# Exemplo: um diretório temporário usado para extrair arquivos ou guardar logs de instalação específicos.
if [ -d "${TEMP_INSTALL_FILES_DIR}" ]; then
    echo "${LOG_PREFIX} Removendo diretório temporário de instalação: ${TEMP_INSTALL_FILES_DIR}"
    if sudo rm -rf "${TEMP_INSTALL_FILES_DIR}"; then
        echo "${LOG_PREFIX} Diretório temporário ${TEMP_INSTALL_FILES_DIR} removido com sucesso."
    else
        echo "${LOG_PREFIX} Aviso: Falha ao remover o diretório temporário ${TEMP_INSTALL_FILES_DIR}. Verifique manualmente." >&2
    fi
else
    echo "${LOG_PREFIX} Diretório temporário de instalação ${TEMP_INSTALL_FILES_DIR} não encontrado. Nenhuma ação necessária."
fi

# 3. Limpar cache do gerenciador de pacotes (opcional e pode requerer confirmação ou ser específico do sistema)
# Exemplo para apt:
# echo "${LOG_PREFIX} Limpando cache do apt (opcional)..."
# if command -v apt-get &> /dev/null; then
#     if sudo apt-get clean; then
#         echo "${LOG_PREFIX} Cache do apt limpo com sucesso."
#     else
#         echo "${LOG_PREFIX} Aviso: Falha ao limpar o cache do apt."
#     fi
# fi
echo "${LOG_PREFIX} Limpeza de cache do gerenciador de pacotes (ex: apt clean) não implementada neste script. Faça manualmente se necessário."

# 4. Remover os arquivos de flag das etapas anteriores (exceto o último, se este for o script final de uma execução completa)
# Ou, se houver um script orquestrador, ele pode lidar com a limpeza dos flags.
# Por segurança, este script individual não removerá os flags das etapas anteriores automaticamente.
echo "${LOG_PREFIX} Os arquivos de flag (.etapa_NN_ok em ${FLAG_FILE_DIR}) podem ser removidos manualmente após a conclusão bem-sucedida de toda a instalação."

# Criar flag de sucesso para esta etapa
touch "${SUCCESS_FLAG}"
echo "${LOG_PREFIX} Limpeza pós-instalação concluída."
echo "${LOG_PREFIX} Flag de sucesso criada em: ${SUCCESS_FLAG}"

echo "${LOG_PREFIX} A INSTALAÇÃO MODULARIZADA FOI CONCLUÍDA COM SUCESSO!"

exit 0

