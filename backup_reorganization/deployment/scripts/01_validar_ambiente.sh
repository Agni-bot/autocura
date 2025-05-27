#!/bin/bash
# Descrição: Etapa 01 - Validar Ambiente de Instalação
# Este script verifica os pré-requisitos básicos do sistema para a instalação.

set -e

LOG_PREFIX="[ETAPA 01]"
FLAG_FILE_DIR="/tmp"
SUCCESS_FLAG="${FLAG_FILE_DIR}/.etapa_01_ok"

# Variáveis de configuração (podem ser externalizadas ou ajustadas)
MIN_DISK_SPACE_MB=1024 # Em MB
REQUIRED_OS="Linux"
REQUIRED_ARCH="x86_64" # ou "aarch64", etc.

echo "${LOG_PREFIX} Iniciando validação do ambiente..."

# 1. Verificar Sistema Operacional
echo "${LOG_PREFIX} Verificando sistema operacional..."
CURRENT_OS=$(uname)
if [ "${CURRENT_OS}" != "${REQUIRED_OS}" ]; then
    echo "${LOG_PREFIX} Erro: Sistema operacional não suportado. Esperado: ${REQUIRED_OS}, Encontrado: ${CURRENT_OS}" >&2
    exit 1
fi
echo "${LOG_PREFIX} Sistema operacional (${CURRENT_OS}) validado."

# 2. Verificar Arquitetura do Sistema
echo "${LOG_PREFIX} Verificando arquitetura do sistema..."
CURRENT_ARCH=$(uname -m)
if [ "${CURRENT_ARCH}" != "${REQUIRED_ARCH}" ]; then
    echo "${LOG_PREFIX} Erro: Arquitetura do sistema não suportada. Esperado: ${REQUIRED_ARCH}, Encontrado: ${CURRENT_ARCH}" >&2
    # Considerar se é um erro fatal ou um aviso, dependendo da aplicação
    # exit 1 
echo "${LOG_PREFIX} Aviso: Arquitetura do sistema (${CURRENT_ARCH}) difere do recomendado (${REQUIRED_ARCH}). Prosseguindo com cautela."
fi
echo "${LOG_PREFIX} Arquitetura do sistema (${CURRENT_ARCH}) verificada."

# 3. Verificar Permissões de Execução (se o script não for root, pode precisar de sudo para outras etapas)
echo "${LOG_PREFIX} Verificando permissões de execução..."
if [ "$(id -u)" -ne 0 ]; then
    echo "${LOG_PREFIX} Aviso: Este script não está sendo executado como root. As etapas subsequentes podem exigir privilégios de superusuário (sudo)."
    # Não sair, apenas avisar. Cada script subsequente deve lidar com sudo se necessário.
fi
echo "${LOG_PREFIX} Permissões verificadas."

# 4. Verificar Espaço em Disco Disponível (no diretório raiz / ou em um diretório de instalação específico)
INSTALL_TARGET_DIR="/"
AVAILABLE_DISK_SPACE_KB=$(df -k "${INSTALL_TARGET_DIR}" | awk 'NR==2 {print $4}')
AVAILABLE_DISK_SPACE_MB=$((AVAILABLE_DISK_SPACE_KB / 1024))

echo "${LOG_PREFIX} Verificando espaço em disco disponível em '${INSTALL_TARGET_DIR}'..."
if [ "${AVAILABLE_DISK_SPACE_MB}" -lt "${MIN_DISK_SPACE_MB}" ]; then
    echo "${LOG_PREFIX} Erro: Espaço em disco insuficiente em '${INSTALL_TARGET_DIR}'. Requerido: ${MIN_DISK_SPACE_MB}MB, Disponível: ${AVAILABLE_DISK_SPACE_MB}MB" >&2
    exit 1
fi
echo "${LOG_PREFIX} Espaço em disco (${AVAILABLE_DISK_SPACE_MB}MB) suficiente."

# 5. Verificar Conectividade Básica com a Internet (pingando um host confiável)
# Esta verificação pode ser opcional dependendo se as etapas futuras precisam de internet.
INTERNET_CHECK_HOST="google.com"
echo "${LOG_PREFIX} Verificando conectividade com a internet (pingando ${INTERNET_CHECK_HOST})..."
if ! ping -c 1 -W 2 "${INTERNET_CHECK_HOST}" > /dev/null 2>&1; then
    echo "${LOG_PREFIX} Aviso: Não foi possível verificar a conectividade com a internet. Algumas etapas futuras podem falhar se precisarem baixar arquivos."
else
    echo "${LOG_PREFIX} Conectividade com a internet verificada."
fi

# Criar flag de sucesso para esta etapa
touch "${SUCCESS_FLAG}"
echo "${LOG_PREFIX} Validação do ambiente concluída com sucesso."
echo "${LOG_PREFIX} Flag de sucesso criada em: ${SUCCESS_FLAG}"

exit 0

