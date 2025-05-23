#!/bin/bash

# Cores para output
VERDE='\033[0;32m'
VERMELHO='\033[0;31m'
AMARELO='\033[1;33m'
NC='\033[0m'

echo -e "${AMARELO}Iniciando testes do módulo de diagnóstico avançado...${NC}\n"

# Verifica se o ambiente virtual está ativado
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${VERMELHO}Erro: Ambiente virtual não está ativado${NC}"
    echo "Por favor, ative o ambiente virtual antes de executar os testes"
    exit 1
fi

# Instala dependências de desenvolvimento
echo -e "${AMARELO}Instalando dependências de desenvolvimento...${NC}"
pip install -e ".[dev]"

# Executa testes com cobertura
echo -e "\n${AMARELO}Executando testes com cobertura...${NC}"
pytest tests/test_diagnostico_avancado.py -v --cov=src.core.diagnostico_avancado --cov-report=term-missing

# Verifica resultado dos testes
if [ $? -eq 0 ]; then
    echo -e "\n${VERDE}✓ Todos os testes passaram com sucesso!${NC}"
else
    echo -e "\n${VERMELHO}✗ Alguns testes falharam${NC}"
    exit 1
fi

# Executa verificações de código
echo -e "\n${AMARELO}Executando verificações de código...${NC}"

# Black
echo -e "\n${AMARELO}Verificando formatação com Black...${NC}"
black --check src/core/diagnostico_avancado.py tests/test_diagnostico_avancado.py

# Flake8
echo -e "\n${AMARELO}Verificando estilo com Flake8...${NC}"
flake8 src/core/diagnostico_avancado.py tests/test_diagnostico_avancado.py

# MyPy
echo -e "\n${AMARELO}Verificando tipos com MyPy...${NC}"
mypy src/core/diagnostico_avancado.py tests/test_diagnostico_avancado.py

# ISort
echo -e "\n${AMARELO}Verificando imports com ISort...${NC}"
isort --check-only src/core/diagnostico_avancado.py tests/test_diagnostico_avancado.py

echo -e "\n${VERDE}✓ Todas as verificações de código passaram!${NC}"
echo -e "\n${VERDE}Testes e verificações concluídos com sucesso!${NC}" 