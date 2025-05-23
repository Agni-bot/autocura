FROM autocura-base:latest

# Copiar código fonte e testes
COPY src/ /app/src/
COPY tests/ /app/tests/
COPY config/ /app/config/
COPY pytest.ini .
COPY pytest_async.ini .

# Configurar variáveis de ambiente para testes
ENV PYTHONPATH=/app
ENV TEST_ENV=true

# Comando para executar os testes
CMD ["pytest", "-v", "--cov=src", "--cov-report=xml", "--cov-report=html"] 