"""
Módulo de Criptografia e Segurança
==================================

Implementa funcionalidades de segurança e criptografia para o sistema.
"""

import os
import json
import logging
import hashlib
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import base64

logger = logging.getLogger(__name__)

class SecurityManager:
    """Gerenciador de segurança do sistema"""
    
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY', self._generate_secret_key())
        self.token_expiry = timedelta(hours=24)
        self.active_tokens = {}
        logger.info("SecurityManager inicializado")
    
    def _generate_secret_key(self) -> str:
        """Gera uma chave secreta segura"""
        return secrets.token_urlsafe(32)
    
    def generate_token(self, user_id: str) -> str:
        """Gera um token de autenticação"""
        token = secrets.token_urlsafe(32)
        self.active_tokens[token] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + self.token_expiry
        }
        return token
    
    def validate_token(self, token: str) -> Optional[str]:
        """Valida um token e retorna o user_id se válido"""
        if token not in self.active_tokens:
            return None
        
        token_data = self.active_tokens[token]
        if datetime.now() > token_data['expires_at']:
            del self.active_tokens[token]
            return None
        
        return token_data['user_id']
    
    def hash_password(self, password: str) -> str:
        """Gera hash seguro de senha"""
        salt = secrets.token_bytes(32)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', 
                                       password.encode('utf-8'), 
                                       salt, 
                                       100000)
        return base64.b64encode(salt + pwd_hash).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica se a senha corresponde ao hash"""
        try:
            decoded = base64.b64decode(password_hash.encode('utf-8'))
            salt = decoded[:32]
            stored_hash = decoded[32:]
            
            pwd_hash = hashlib.pbkdf2_hmac('sha256',
                                          password.encode('utf-8'),
                                          salt,
                                          100000)
            
            return pwd_hash == stored_hash
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {e}")
            return False
    
    def encrypt_data(self, data: Dict[str, Any]) -> str:
        """Criptografa dados sensíveis (implementação simplificada)"""
        # Em produção, usar biblioteca como cryptography
        json_data = json.dumps(data)
        encoded = base64.b64encode(json_data.encode('utf-8'))
        return encoded.decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """Descriptografa dados (implementação simplificada)"""
        try:
            decoded = base64.b64decode(encrypted_data.encode('utf-8'))
            return json.loads(decoded.decode('utf-8'))
        except Exception as e:
            logger.error(f"Erro ao descriptografar: {e}")
            return {}
    
    def cleanup_expired_tokens(self):
        """Remove tokens expirados"""
        now = datetime.now()
        expired = [token for token, data in self.active_tokens.items() 
                  if now > data['expires_at']]
        
        for token in expired:
            del self.active_tokens[token]
        
        if expired:
            logger.info(f"Removidos {len(expired)} tokens expirados")

# Instância global
security_manager = SecurityManager() 