"""Sistema de segurança do módulo core."""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from .interfaces import SecurityInterface
from .config.config import config
from .logging import logger

class Security(SecurityInterface):
    """Sistema de segurança."""
    
    def __init__(self):
        """Inicializa o sistema de segurança."""
        self._users: Dict[str, Dict[str, Any]] = {}
        self._permissions: Dict[str, Dict[str, list]] = {}
        self._tokens: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self) -> None:
        """Inicializa o sistema de segurança."""
        await logger.log("INFO", "Sistema de segurança inicializado")
        
    async def shutdown(self) -> None:
        """Desliga o sistema de segurança."""
        await logger.log("INFO", "Sistema de segurança desligado")
        
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Autentica um usuário ou serviço."""
        username = credentials.get("username")
        password = credentials.get("password")
        
        if not username or not password:
            await logger.log("WARNING", "Tentativa de autenticação sem credenciais")
            return False
            
        user = self._users.get(username)
        if not user:
            await logger.log("WARNING", f"Tentativa de autenticação com usuário inexistente: {username}")
            return False
            
        # Verifica senha
        hashed_password = self._hash_password(password)
        if user["password"] != hashed_password:
            await logger.log("WARNING", f"Tentativa de autenticação com senha inválida: {username}")
            return False
            
        await logger.log("INFO", f"Usuário autenticado: {username}")
        return True
        
    async def authorize(self, subject: str, action: str,
                       resource: str) -> bool:
        """Verifica se um sujeito tem permissão para uma ação."""
        if subject not in self._permissions:
            await logger.log("WARNING", f"Tentativa de autorização para sujeito sem permissões: {subject}")
            return False
            
        resource_perms = self._permissions[subject].get(resource, [])
        has_permission = action in resource_perms
        
        if not has_permission:
            await logger.log("WARNING", 
                           f"Tentativa de ação não autorizada: {subject} -> {action} -> {resource}")
            
        return has_permission
        
    async def encrypt(self, data: Any) -> bytes:
        """Criptografa dados."""
        try:
            # Em produção, usar biblioteca de criptografia adequada
            return str(data).encode()
        except Exception as e:
            await logger.log("ERROR", f"Erro ao criptografar dados: {e}")
            raise
            
    async def decrypt(self, data: bytes) -> Any:
        """Descriptografa dados."""
        try:
            # Em produção, usar biblioteca de criptografia adequada
            return data.decode()
        except Exception as e:
            await logger.log("ERROR", f"Erro ao descriptografar dados: {e}")
            raise
            
    def _hash_password(self, password: str) -> str:
        """Gera hash de senha."""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${hashed}"
        
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verifica senha contra hash."""
        salt, stored_hash = hashed.split("$")
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == stored_hash
        
    async def create_user(self, username: str, password: str,
                         permissions: Optional[Dict[str, list]] = None) -> None:
        """Cria um novo usuário."""
        if username in self._users:
            await logger.log("WARNING", f"Tentativa de criar usuário existente: {username}")
            return
            
        self._users[username] = {
            "password": self._hash_password(password),
            "created_at": datetime.now().isoformat()
        }
        
        if permissions:
            self._permissions[username] = permissions
            
        await logger.log("INFO", f"Usuário criado: {username}")
        
    async def delete_user(self, username: str) -> None:
        """Remove um usuário."""
        if username in self._users:
            del self._users[username]
            if username in self._permissions:
                del self._permissions[username]
            await logger.log("INFO", f"Usuário removido: {username}")
            
    async def update_permissions(self, username: str,
                               permissions: Dict[str, list]) -> None:
        """Atualiza permissões de um usuário."""
        if username not in self._users:
            await logger.log("WARNING", f"Tentativa de atualizar permissões de usuário inexistente: {username}")
            return
            
        self._permissions[username] = permissions
        await logger.log("INFO", f"Permissões atualizadas para usuário: {username}")
        
    async def generate_token(self, username: str) -> str:
        """Gera token JWT para um usuário."""
        if username not in self._users:
            await logger.log("WARNING", f"Tentativa de gerar token para usuário inexistente: {username}")
            return ""
            
        payload = {
            "sub": username,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + config.JWT_EXPIRATION
        }
        
        token = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
        self._tokens[token] = {
            "username": username,
            "created_at": datetime.now().isoformat()
        }
        
        await logger.log("INFO", f"Token gerado para usuário: {username}")
        return token
        
    async def validate_token(self, token: str) -> bool:
        """Valida um token JWT."""
        try:
            payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
            username = payload["sub"]
            
            if username not in self._users:
                await logger.log("WARNING", f"Token válido para usuário inexistente: {username}")
                return False
                
            if token not in self._tokens:
                await logger.log("WARNING", f"Token não encontrado no registro: {username}")
                return False
                
            return True
            
        except jwt.ExpiredSignatureError:
            await logger.log("WARNING", "Token expirado")
            return False
        except jwt.InvalidTokenError as e:
            await logger.log("WARNING", f"Token inválido: {e}")
            return False

# Instância global do sistema de segurança
security = Security() 