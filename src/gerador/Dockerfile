<<<<<<< HEAD
FROM python:3.9-slim

WORKDIR /app
=======
FROM python:3.11-slim
>>>>>>> origin/main

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
<<<<<<< HEAD
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Definir variáveis de ambiente padrão
ENV SCORE_MINIMO=0.3
ENV TIMEOUT_API=5
ENV MAX_ACOES_REDESIGN=2
ENV PRIORIDADE_HOTFIX=0.8
ENV PRIORIDADE_REFATORACAO=0.5
ENV PRIORIDADE_REDESIGN=0.3

# Expor a porta
EXPOSE 8082

# Comando para executar a aplicação
CMD ["python", "gerador.py"]
=======
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código
COPY . .

# Expor a porta
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "app.py"]
>>>>>>> origin/main
