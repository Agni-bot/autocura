# Imagem base
FROM python:3.10-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de dependências
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código fonte
COPY src/ src/
COPY config/ config/
COPY scripts/ scripts/

# Cria diretórios necessários
RUN mkdir -p logs data

# Define variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expõe porta do Prometheus
EXPOSE 9090

# Comando para executar o sistema
CMD ["python", "src/main.py"] 