# Middleware

Este documento descreve os middlewares disponíveis no módulo de integração.

## 🔐 Middleware de Autenticação

### AuthMiddleware

```python
from typing import Optional
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from datetime import datetime, timedelta

class AuthMiddleware:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.security = HTTPBearer()
        
    async def __call__(self, request: Request) -> Optional[str]:
        """
        Verifica o token JWT na requisição.
        
        Args:
            request: Requisição HTTP
            
        Returns:
            Optional[str]: ID do usuário autenticado
            
        Raises:
            HTTPException: Se o token for inválido ou expirado
        """
        try:
            # Obter credenciais
            credentials: HTTPAuthorizationCredentials = await self.security(request)
            
            # Decodificar token
            payload = jwt.decode(
                credentials.credentials,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Verificar expiração
            exp = payload.get("exp")
            if not exp or datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=401,
                    detail="Token expirado"
                )
                
            return payload.get("sub")
            
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )
```

## 🔒 Middleware de Autorização

### RBACMiddleware

```python
from typing import List, Optional
from fastapi import Request, HTTPException
from .models import Usuario, Role

class RBACMiddleware:
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles
        
    async def __call__(self, request: Request, user_id: str) -> None:
        """
        Verifica se o usuário tem as permissões necessárias.
        
        Args:
            request: Requisição HTTP
            user_id: ID do usuário autenticado
            
        Raises:
            HTTPException: Se o usuário não tiver permissão
        """
        # Obter usuário
        user = await self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado"
            )
            
        # Verificar roles
        user_roles = [role.name for role in user.roles]
        if not any(role in user_roles for role in self.required_roles):
            raise HTTPException(
                status_code=403,
                detail="Permissão negada"
            )
            
    async def get_user(self, user_id: str) -> Optional[Usuario]:
        """
        Obtém um usuário pelo ID.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Optional[Usuario]: Usuário encontrado ou None
        """
        # Implementar lógica de consulta
        pass
```

## 🔄 Middleware de Retry

### RetryMiddleware

```python
from typing import Callable, Any
from fastapi import Request
import asyncio
from functools import wraps

class RetryMiddleware:
    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0
    ):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
        
    def __call__(self, func: Callable) -> Callable:
        """
        Decorator para adicionar retry em uma função.
        
        Args:
            func: Função a ser decorada
            
        Returns:
            Callable: Função decorada
        """
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = self.delay
            
            for attempt in range(self.max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= self.backoff
                        
            raise last_exception
            
        return wrapper
```

## ⚡ Middleware de Circuit Breaker

### CircuitBreaker

```python
from typing import Callable, Any
from fastapi import Request
import asyncio
from functools import wraps
from datetime import datetime, timedelta

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 60.0
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = None
        self.is_open = False
        
    def __call__(self, func: Callable) -> Callable:
        """
        Decorator para adicionar circuit breaker em uma função.
        
        Args:
            func: Função a ser decorada
            
        Returns:
            Callable: Função decorada
        """
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Verificar se o circuito está aberto
            if self.is_open:
                if self.last_failure_time and \
                   datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.reset_timeout):
                    self.is_open = False
                    self.failures = 0
                else:
                    raise Exception("Circuit breaker está aberto")
                    
            try:
                result = await func(*args, **kwargs)
                self.failures = 0
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = datetime.utcnow()
                
                if self.failures >= self.failure_threshold:
                    self.is_open = True
                    
                raise e
                
        return wrapper
```

## 📊 Middleware de Métricas

### MetricsMiddleware

```python
from typing import Callable
from fastapi import Request, Response
from prometheus_client import Counter, Histogram
import time

class MetricsMiddleware:
    def __init__(self):
        self.requests_total = Counter(
            "http_requests_total",
            "Total de requisições HTTP",
            ["method", "endpoint", "status"]
        )
        
        self.request_duration = Histogram(
            "http_request_duration_seconds",
            "Duração das requisições HTTP",
            ["method", "endpoint"]
        )
        
    async def __call__(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Registra métricas para cada requisição.
        
        Args:
            request: Requisição HTTP
            call_next: Próximo middleware/handler
            
        Returns:
            Response: Resposta HTTP
        """
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Registrar métricas
            self.requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            self.request_duration.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            # Registrar erro
            self.requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500
            ).inc()
            
            raise e
```

## 📝 Exemplo de Uso

```python
from fastapi import FastAPI, Depends
from .middleware import (
    AuthMiddleware,
    RBACMiddleware,
    RetryMiddleware,
    CircuitBreaker,
    MetricsMiddleware
)

# Configuração
app = FastAPI()

# Middlewares
auth_middleware = AuthMiddleware(secret_key="seu_secret_key")
rbac_middleware = RBACMiddleware(required_roles=["admin"])
retry_middleware = RetryMiddleware(max_retries=3)
circuit_breaker = CircuitBreaker(failure_threshold=5)
metrics_middleware = MetricsMiddleware()

# Adicionar middlewares
app.middleware("http")(metrics_middleware)

# Dependências
async def get_current_user(
    request: Request,
    user_id: str = Depends(auth_middleware)
):
    return user_id

async def check_permissions(
    request: Request,
    user_id: str = Depends(get_current_user)
):
    await rbac_middleware(request, user_id)
    return user_id

# Rotas
@app.get("/protected")
@retry_middleware
@circuit_breaker
async def protected_route(
    user_id: str = Depends(check_permissions)
):
    return {"message": "Rota protegida", "user_id": user_id}
```

## 📚 Referências

- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [JWT Python](https://python-jose.readthedocs.io/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Python Decorators](https://docs.python.org/3/glossary.html#term-decorator)
- [Python Async IO](https://docs.python.org/3/library/asyncio.html)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html) 