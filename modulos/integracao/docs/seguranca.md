# Guia de Segurança

Este documento descreve as práticas de segurança implementadas no módulo de integração.

## 🔒 Autenticação

### JWT (JSON Web Tokens)

- Algoritmo: HS256
- Expiração: 60 minutos
- Refresh token: 7 dias
- Claims personalizados:
  - `sub`: ID do usuário
  - `roles`: Lista de roles
  - `permissions`: Lista de permissões
  - `scope`: Escopo de acesso

### Exemplo de Token

```json
{
  "sub": "user123",
  "roles": ["admin", "operator"],
  "permissions": ["read", "write", "delete"],
  "scope": "api",
  "iat": 1516239022,
  "exp": 1516242622
}
```

### Implementação

```python
from jose import jwt
from datetime import datetime, timedelta

def gerar_tokens(usuario: str, roles: List[str]) -> Dict[str, str]:
    """Gera access token e refresh token.

    Args:
        usuario: ID do usuário
        roles: Lista de roles

    Returns:
        Dicionário com access token e refresh token
    """
    access_token = jwt.encode(
        {
            "sub": usuario,
            "roles": roles,
            "exp": datetime.utcnow() + timedelta(minutes=60)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    refresh_token = jwt.encode(
        {
            "sub": usuario,
            "exp": datetime.utcnow() + timedelta(days=7)
        },
        REFRESH_SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
```

## 🛡️ Autorização

### RBAC (Role-Based Access Control)

#### Roles

- `admin`: Acesso total
- `operator`: Operações de sistema
- `monitor`: Apenas leitura
- `service`: Acesso de serviço

#### Permissões

- `read`: Leitura de dados
- `write`: Escrita de dados
- `delete`: Remoção de dados
- `execute`: Execução de ações
- `configure`: Configuração do sistema

### Implementação

```python
from functools import wraps
from typing import List, Callable

def requer_roles(roles: List[str]):
    """Decorator para verificar roles.

    Args:
        roles: Lista de roles necessárias

    Returns:
        Decorator
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            token = kwargs.get('token')
            if not token:
                raise UnauthorizedError("Token não fornecido")

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_roles = payload.get('roles', [])

            if not any(role in user_roles for role in roles):
                raise ForbiddenError("Acesso negado")

            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## 🔐 Criptografia

### SSL/TLS

- Versão mínima: TLS 1.2
- Cipher suites:
  - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
  - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
- Certificados:
  - Validação de CA
  - Verificação de hostname
  - Revogação de certificados

### Implementação

```python
import ssl

def criar_contexto_ssl() -> ssl.SSLContext:
    """Cria contexto SSL seguro.

    Returns:
        Contexto SSL
    """
    context = ssl.create_default_context()
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(
        certfile='certs/cert.pem',
        keyfile='certs/key.pem'
    )
    context.load_verify_locations('certs/ca.pem')
    return context
```

## 🚫 Rate Limiting

### Limites

- IP: 100 requisições/minuto
- Usuário: 1000 requisições/hora
- Serviço: 10000 requisições/hora

### Implementação

```python
from redis import Redis
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def verificar_limite(
        self,
        chave: str,
        limite: int,
        periodo: int
    ) -> bool:
        """Verifica se excedeu o limite.

        Args:
            chave: Chave de identificação
            limite: Número máximo de requisições
            periodo: Período em segundos

        Returns:
            True se dentro do limite
        """
        pipe = self.redis.pipeline()
        now = datetime.utcnow()
        key = f"ratelimit:{chave}:{now.strftime('%Y%m%d%H%M')}"

        pipe.incr(key)
        pipe.expire(key, periodo)
        resultado = await pipe.execute()

        return resultado[0] <= limite
```

## 🔍 Auditoria

### Logs de Segurança

- Autenticação
- Autorização
- Ações críticas
- Erros de segurança
- Tentativas de acesso

### Implementação

```python
import logging
from datetime import datetime

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('logs/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_auth(
        self,
        usuario: str,
        sucesso: bool,
        ip: str,
        detalhes: Dict[str, Any]
    ):
        """Registra tentativa de autenticação.

        Args:
            usuario: Nome do usuário
            sucesso: Se autenticação foi bem sucedida
            ip: IP do cliente
            detalhes: Detalhes adicionais
        """
        self.logger.info(
            f"Auth attempt - User: {usuario}, "
            f"Success: {sucesso}, IP: {ip}, "
            f"Details: {detalhes}"
        )
```

## 🚨 Monitoramento de Segurança

### Métricas

- Tentativas de autenticação
- Falhas de autenticação
- Acessos negados
- Erros de segurança
- Tempo de resposta

### Implementação

```python
from prometheus_client import Counter, Histogram

AUTH_ATTEMPTS = Counter(
    'auth_attempts_total',
    'Total de tentativas de autenticação',
    ['success']
)

AUTH_LATENCY = Histogram(
    'auth_latency_seconds',
    'Latência de autenticação'
)

@AUTH_LATENCY.time()
async def autenticar(credenciais: Dict[str, str]) -> bool:
    """Autentica um usuário.

    Args:
        credenciais: Credenciais do usuário

    Returns:
        True se autenticação bem sucedida
    """
    try:
        # Autenticação
        sucesso = True
    except Exception:
        sucesso = False
    finally:
        AUTH_ATTEMPTS.labels(success=sucesso).inc()
        return sucesso
```

## 📋 Checklist de Segurança

### Configuração

- [ ] SSL/TLS habilitado
- [ ] Cipher suites seguros
- [ ] Certificados válidos
- [ ] Headers de segurança
- [ ] Rate limiting configurado

### Autenticação

- [ ] JWT implementado
- [ ] Tokens com expiração
- [ ] Refresh tokens
- [ ] Validação de tokens
- [ ] Logout implementado

### Autorização

- [ ] RBAC implementado
- [ ] Permissões granulares
- [ ] Validação de escopo
- [ ] Cache de permissões
- [ ] Logs de acesso

### Dados

- [ ] Criptografia em trânsito
- [ ] Criptografia em repouso
- [ ] Sanitização de inputs
- [ ] Validação de dados
- [ ] Backup seguro

### Monitoramento

- [ ] Logs de segurança
- [ ] Métricas de segurança
- [ ] Alertas configurados
- [ ] Auditoria habilitada
- [ ] Relatórios gerados

## 🔄 Atualizações de Segurança

1. Monitorar vulnerabilidades
2. Atualizar dependências
3. Aplicar patches
4. Testar mudanças
5. Documentar alterações

## 📚 Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://auth0.com/blog/jwt-security-best-practices/)
- [TLS Configuration](https://ssl-config.mozilla.org/)
- [Security Headers](https://securityheaders.com/)
- [Rate Limiting](https://www.nginx.com/blog/rate-limiting-nginx/) 