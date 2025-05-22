FROM autocura-base:latest

# Copiar código fonte
COPY src/ /app/src/
COPY config/ /app/config/

# Configurar variáveis de ambiente específicas do validador
ENV SERVICE_NAME=validador
ENV VALIDATION_INTERVAL=60

# Comando para iniciar o validador
CMD ["python", "-m", "src.validador.main"] 