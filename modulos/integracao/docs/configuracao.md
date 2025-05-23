# Configuração

Este documento descreve as configurações disponíveis para o módulo de integração.

## 🔧 Configurações Gerais

### Configuração Base

```python
from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache

class Settings(BaseSettings):
    # Configurações gerais
    APP_NAME: str = "autocura-integracao"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Configurações de API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_TIMEOUT: int = 60
    
    # Configurações de segurança
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configurações de banco de dados
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "integracao"
    DB_USER: str = "postgres"
    DB_PASSWORD: str
    
    # Configurações de Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Configurações de Kafka
    KAFKA_BOOTSTRAP_SERVERS: List[str] = ["localhost:9092"]
    KAFKA_CONSUMER_GROUP_ID: str = "integracao-group"
    
    # Configurações de monitoramento
    PROMETHEUS_PORT: int = 9090
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

## 🔐 Configurações de Segurança

### Autenticação

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

class SecurityConfig:
    def __init__(self, settings: Settings):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
        
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
```

### CORS

```python
from fastapi.middleware.cors import CORSMiddleware
from typing import List

class CORSConfig:
    def __init__(self, settings: Settings):
        self.origins = settings.CORS_ALLOWED_ORIGINS
        self.methods = settings.CORS_ALLOWED_METHODS
        self.headers = settings.CORS_ALLOWED_HEADERS
        self.credentials = settings.CORS_ALLOW_CREDENTIALS
        
    def get_middleware(self):
        return CORSMiddleware(
            app=app,
            allow_origins=self.origins,
            allow_credentials=self.credentials,
            allow_methods=self.methods,
            allow_headers=self.headers,
        )
```

## 📊 Configurações de Monitoramento

### Prometheus

```python
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator

class MetricsConfig:
    def __init__(self, settings: Settings):
        self.prefix = settings.PROMETHEUS_METRICS_PREFIX
        
        # Métricas de requisições
        self.requests_total = Counter(
            f"{self.prefix}requests_total",
            "Total de requisições",
            ["method", "endpoint", "status"]
        )
        
        # Métricas de latência
        self.request_duration = Histogram(
            f"{self.prefix}request_duration_seconds",
            "Duração das requisições",
            ["method", "endpoint"]
        )
        
        # Métricas de fila
        self.queue_size = Gauge(
            f"{self.prefix}queue_size",
            "Tamanho da fila de mensagens"
        )
        
    def setup_instrumentator(self, app):
        instrumentator = Instrumentator(
            should_group_status_codes=False,
            excluded_handlers=["/metrics"],
            instrument=app
        )
        instrumentator.instrument(app)
        return instrumentator
```

### Logging

```python
import logging
from logging.handlers import RotatingFileHandler
import json

class LoggingConfig:
    def __init__(self, settings: Settings):
        self.level = settings.LOG_LEVEL
        self.format = settings.LOG_FORMAT
        self.file = settings.LOG_FILE
        self.max_bytes = settings.LOG_MAX_BYTES
        self.backup_count = settings.LOG_BACKUP_COUNT
        
    def setup_logging(self):
        logger = logging.getLogger("integracao")
        logger.setLevel(self.level)
        
        # Handler para arquivo
        file_handler = RotatingFileHandler(
            self.file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        
        # Formato JSON
        if self.format == "json":
            class JsonFormatter(logging.Formatter):
                def format(self, record):
                    log_record = {
                        "timestamp": self.formatTime(record),
                        "level": record.levelname,
                        "message": record.getMessage(),
                        "module": record.module,
                        "function": record.funcName,
                        "line": record.lineno
                    }
                    if record.exc_info:
                        log_record["exception"] = self.formatException(record.exc_info)
                    return json.dumps(log_record)
            
            file_handler.setFormatter(JsonFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
        
        logger.addHandler(file_handler)
        return logger
```

## 🔄 Configurações de Mensageria

### Redis

```python
from redis import Redis
from typing import Optional

class RedisConfig:
    def __init__(self, settings: Settings):
        self.host = settings.REDIS_HOST
        self.port = settings.REDIS_PORT
        self.db = settings.REDIS_DB
        self.password = settings.REDIS_PASSWORD
        
    def get_client(self) -> Redis:
        return Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=True
        )
```

### Kafka

```python
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from typing import List

class KafkaConfig:
    def __init__(self, settings: Settings):
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.group_id = settings.KAFKA_CONSUMER_GROUP_ID
        
    async def get_producer(self) -> AIOKafkaProducer:
        return AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers
        )
        
    async def get_consumer(self, topics: List[str]) -> AIOKafkaConsumer:
        return AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id
        )
```

## 📝 Exemplo de Uso

```python
from fastapi import FastAPI, Depends
from .config import get_settings, Settings

app = FastAPI()
settings = get_settings()

# Configurações de segurança
security_config = SecurityConfig(settings)
cors_config = CORSConfig(settings)
app.add_middleware(cors_config.get_middleware())

# Configurações de monitoramento
metrics_config = MetricsConfig(settings)
instrumentator = metrics_config.setup_instrumentator(app)

# Configurações de logging
logging_config = LoggingConfig(settings)
logger = logging_config.setup_logging()

# Configurações de mensageria
redis_config = RedisConfig(settings)
kafka_config = KafkaConfig(settings)

@app.on_event("startup")
async def startup_event():
    # Inicializar métricas
    instrumentator.expose(app)
    
    # Inicializar Redis
    redis_client = redis_config.get_client()
    app.state.redis = redis_client
    
    # Inicializar Kafka
    producer = await kafka_config.get_producer()
    await producer.start()
    app.state.kafka_producer = producer
    
    logger.info("Aplicação iniciada")

@app.on_event("shutdown")
async def shutdown_event():
    # Fechar conexões
    await app.state.kafka_producer.stop()
    app.state.redis.close()
    
    logger.info("Aplicação encerrada")
```

## 📚 Referências

- [FastAPI Settings](https://fastapi.tiangolo.com/advanced/settings/)
- [Pydantic Settings](https://pydantic-docs.helpmanual.io/usage/settings/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [Kafka Python Client](https://kafka-python.readthedocs.io/)
- [Python Logging](https://docs.python.org/3/library/logging.html) 