FROM autocura-base:latest

# Copiar código fonte
COPY src/ /app/src/
COPY config/ /app/config/

# Configurar variáveis de ambiente específicas do observador
ENV SERVICE_NAME=observador
ENV OBSERVATION_INTERVAL=30

# Comando para iniciar o observador
CMD ["python", "-m", "src.observador.main"] 