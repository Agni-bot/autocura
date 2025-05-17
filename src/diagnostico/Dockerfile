FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Configura variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
ENV LOG_LEVEL=INFO
ENV LOG_FILE=/app/logs/diagnostico.log

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

# Cria diretórios necessários
RUN mkdir -p /app/logs /app/visualizacoes /app/templates && \
    chmod 777 /app/logs /app/visualizacoes /app/templates

EXPOSE 8080

CMD ["python", "diagnostico.py"]
