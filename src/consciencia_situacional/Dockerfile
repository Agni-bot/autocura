# Imagem base
FROM python:3.9-slim

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de requisitos
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código fonte
COPY . .

# Expõe porta
EXPOSE 8080

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV CONFIG_PATH=/app/config.yaml

# Comando para executar a aplicação
CMD ["python", "app.py"] 