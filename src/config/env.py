"""
Módulo de configuração de ambiente.
"""
import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Configurações Gerais
APP_NAME: str = os.getenv("APP_NAME", "autocura")
APP_ENV: str = os.getenv("APP_ENV", "development")
DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# API
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))
API_WORKERS: int = int(os.getenv("API_WORKERS", "4"))
API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "60"))

# Banco de Dados
DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
DB_NAME: str = os.getenv("DB_NAME", "autocura")
DB_USER: str = os.getenv("DB_USER", "postgres")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))

# Redis
REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")

# Elasticsearch
ES_HOST: str = os.getenv("ES_HOST", "localhost")
ES_PORT: int = int(os.getenv("ES_PORT", "9200"))
ES_USERNAME: str = os.getenv("ES_USERNAME", "elastic")
ES_PASSWORD: str = os.getenv("ES_PASSWORD", "changeme")

# Prometheus
PROMETHEUS_HOST: str = os.getenv("PROMETHEUS_HOST", "localhost")
PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", "9090"))

# Grafana
GRAFANA_HOST: str = os.getenv("GRAFANA_HOST", "localhost")
GRAFANA_PORT: int = int(os.getenv("GRAFANA_PORT", "3000"))
GRAFANA_USER: str = os.getenv("GRAFANA_USER", "admin")
GRAFANA_PASSWORD: str = os.getenv("GRAFANA_PASSWORD", "admin")

# Segurança
JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION: int = int(os.getenv("JWT_EXPIRATION", "3600"))
CORS_ORIGINS: List[str] = eval(os.getenv("CORS_ORIGINS", '["http://localhost:3000"]'))
RATE_LIMIT: int = int(os.getenv("RATE_LIMIT", "100"))
RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

# Notificações
SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "your-email@gmail.com")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "your-app-password")
SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

# Kubernetes
K8S_NAMESPACE: str = os.getenv("K8S_NAMESPACE", "autocura")
K8S_REPLICAS: int = int(os.getenv("K8S_REPLICAS", "3"))
K8S_RESOURCE_LIMITS_CPU: str = os.getenv("K8S_RESOURCE_LIMITS_CPU", "1")
K8S_RESOURCE_LIMITS_MEMORY: str = os.getenv("K8S_RESOURCE_LIMITS_MEMORY", "1Gi")
K8S_RESOURCE_REQUESTS_CPU: str = os.getenv("K8S_RESOURCE_REQUESTS_CPU", "0.5")
K8S_RESOURCE_REQUESTS_MEMORY: str = os.getenv("K8S_RESOURCE_REQUESTS_MEMORY", "512Mi")

# Backup
BACKUP_ENABLED: bool = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
BACKUP_INTERVAL: int = int(os.getenv("BACKUP_INTERVAL", "86400"))
BACKUP_RETENTION: int = int(os.getenv("BACKUP_RETENTION", "7"))
BACKUP_PATH: str = os.getenv("BACKUP_PATH", "/backup")
BACKUP_COMPRESSION: bool = os.getenv("BACKUP_COMPRESSION", "true").lower() == "true"

# Monitoramento
METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"
METRICS_INTERVAL: int = int(os.getenv("METRICS_INTERVAL", "15"))
ALERT_CPU_THRESHOLD: int = int(os.getenv("ALERT_CPU_THRESHOLD", "80"))
ALERT_MEMORY_THRESHOLD: int = int(os.getenv("ALERT_MEMORY_THRESHOLD", "85"))
ALERT_LATENCY_THRESHOLD: int = int(os.getenv("ALERT_LATENCY_THRESHOLD", "1000"))

# Ética
ETHICS_ENABLED: bool = os.getenv("ETHICS_ENABLED", "true").lower() == "true"
ETHICS_CHECK_INTERVAL: int = int(os.getenv("ETHICS_CHECK_INTERVAL", "300"))
ETHICS_VIOLATION_THRESHOLD: int = int(os.getenv("ETHICS_VIOLATION_THRESHOLD", "3"))
ETHICS_REPORT_INTERVAL: int = int(os.getenv("ETHICS_REPORT_INTERVAL", "86400"))

# Autonomia
AUTONOMY_INITIAL_LEVEL: int = int(os.getenv("AUTONOMY_INITIAL_LEVEL", "1"))
AUTONOMY_CHECK_INTERVAL: int = int(os.getenv("AUTONOMY_CHECK_INTERVAL", "600"))
AUTONOMY_ADVANCE_THRESHOLD: float = float(os.getenv("AUTONOMY_ADVANCE_THRESHOLD", "0.95"))
AUTONOMY_REGRESS_THRESHOLD: float = float(os.getenv("AUTONOMY_REGRESS_THRESHOLD", "0.7"))

# Cache
CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))
CACHE_CLEANUP_INTERVAL: int = int(os.getenv("CACHE_CLEANUP_INTERVAL", "300"))

# Logging
LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
LOG_FILE: str = os.getenv("LOG_FILE", "/var/log/autocura/app.log")
LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", "10485760"))
LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
LOG_COMPRESSION: bool = os.getenv("LOG_COMPRESSION", "true").lower() == "true" 