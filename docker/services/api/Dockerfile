FROM autocura-base:latest

# Copiar código fonte
COPY src/ /app/src/
COPY config/ /app/config/

# Expor porta da API
EXPOSE 8000

# Configurar variáveis de ambiente específicas da API
ENV SERVICE_NAME=api
ENV PORT=8000

# Comando para iniciar a API
CMD ["python", "-m", "src.api.main"] 