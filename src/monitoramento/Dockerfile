FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
<<<<<<< HEAD
=======
    build-essential \
>>>>>>> origin/main
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Configura o ambiente Python
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

<<<<<<< HEAD
EXPOSE 8080

CMD ["uvicorn", "monitoramento:app", "--host", "0.0.0.0", "--port", "8080"]
=======
RUN mkdir -p /app/logs /app/visualizacoes /app/templates && \
    chmod 777 /app/logs /app/visualizacoes /app/templates

ENV LOG_LEVEL=INFO
ENV LOG_FILE=/app/logs/monitoramento.log

EXPOSE 8080

CMD ["python", "monitoramento.py"]
>>>>>>> origin/main
