FROM autocura-base:latest

# Copiar código fonte
COPY src/ /app/src/
COPY config/ /app/config/

# Configurar variáveis de ambiente específicas do diagnóstico
ENV SERVICE_NAME=diagnostico
ENV DIAGNOSTIC_INTERVAL=90

# Comando para iniciar o diagnóstico
CMD ["python", "-m", "src.diagnostico.main"] 