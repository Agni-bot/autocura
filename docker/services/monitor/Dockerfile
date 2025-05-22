FROM autocura-base:latest

# Copiar código fonte
COPY src/ /app/src/
COPY config/ /app/config/

# Configurar variáveis de ambiente específicas do monitor
ENV SERVICE_NAME=monitor
ENV MONITOR_INTERVAL=60

# Comando para iniciar o monitor
CMD ["python", "-m", "src.monitor.main"] 