<<<<<<< HEAD
FROM python:3.9-slim

WORKDIR /app

# Cria diretórios necessários
RUN mkdir -p /app/visualizacoes && \
    mkdir -p /app/logs && \
    mkdir -p /app/templates && \
    chmod 777 /app/visualizacoes && \
    chmod 777 /app/logs && \
    chmod 777 /app/templates

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Configura logging para arquivo
=======
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/logs /app/visualizacoes /app/templates && \
    chmod 777 /app/logs /app/visualizacoes /app/templates

>>>>>>> origin/main
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV LOG_FILE=/app/logs/observabilidade.log

EXPOSE 8080

CMD ["python", "observabilidade.py"]
