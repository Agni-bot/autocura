FROM autocura-base:latest

# Copiar código fonte
COPY src/ /app/src/
COPY config/ /app/config/

# Configurar variáveis de ambiente específicas do guardião
ENV SERVICE_NAME=guardiao
ENV GUARDIAN_INTERVAL=45

# Comando para iniciar o guardião
CMD ["python", "-m", "src.guardiao.main"] 