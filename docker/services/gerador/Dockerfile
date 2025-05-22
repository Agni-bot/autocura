FROM autocura-base:latest

# Copiar código fonte
COPY src/ /app/src/
COPY config/ /app/config/

# Configurar variáveis de ambiente específicas do gerador
ENV SERVICE_NAME=gerador
ENV GENERATION_INTERVAL=120

# Comando para iniciar o gerador
CMD ["python", "-m", "src.gerador.main"] 