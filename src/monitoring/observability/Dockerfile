# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uvicorn && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Configura o ambiente Python
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV LOG_FILE=/app/logs/observabilidade.log
ENV MONITORAMENTO_URL=http://monitoramento:8081
ENV DIAGNOSTICO_URL=http://diagnostico:5002
ENV GERADOR_URL=http://gerador:5003

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Set Python path
ENV PYTHONPATH=/app

# Switch to non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 5003

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/health || exit 1

# Command to run the application using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5003", "--reload"]
