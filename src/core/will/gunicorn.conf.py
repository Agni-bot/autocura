"""
Configuração do Gunicorn para o sistema Will.
"""

import multiprocessing
import os

# Número de workers
workers = multiprocessing.cpu_count() * 2 + 1

# Configurações de timeout
timeout = 120
keepalive = 5

# Configurações de logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")

# Configurações de worker
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações de performance
backlog = 2048
graceful_timeout = 30

# Configurações de SSL (se necessário)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"

# Configurações de proxy
forwarded_allow_ips = "*"
proxy_protocol = True
proxy_allow_ips = "*"

# Configurações de worker
preload_app = True
reload = os.getenv("ENVIRONMENT", "development") == "development" 