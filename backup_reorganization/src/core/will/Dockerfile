# Build stage
FROM python:3.10-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    curl \
    wine \
    wine64 \
    winbind \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.10-slim

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    apt-get update && \
    apt-get install -y \
    curl \
    wine \
    wine64 \
    winbind \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Configura o ambiente Python
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=will.app
ENV FLASK_RUN_HOST=0.0.0.0
ENV LOG_LEVEL=INFO
ENV LOG_FILE=/app/logs/will.log

# Copy application code and MT5
COPY . /app/will
COPY gunicorn.conf.py /app/
COPY requirements.txt /app/
COPY entrypoint.sh /app/

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/data && \
    chown -R appuser:appuser /app

# Set Python path
ENV PYTHONPATH=/app/will

# Switch to non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Command to run the application using Gunicorn with config file
CMD ["gunicorn", "--config", "/app/gunicorn.conf.py", "will.app:app"]

# For development, you might use:
# CMD ["flask", "run"]

