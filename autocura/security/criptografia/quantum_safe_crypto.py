from typing import Dict, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import base64
import os
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GerenciadorCriptografia:
    def __init__(self,
                 chave_mestre: Optional[str] = None,
                 salt: Optional[bytes] = None,
                 iteracoes: int = 100000):
        """
        Inicializa o gerenciador de criptografia.
        
        Args:
            chave_mestre: Chave mestra para derivação de chaves (opcional)
            salt: Salt para derivação de chaves (opcional)
            iteracoes: Número de iterações para derivação de chaves
        """
        self.iteracoes = iteracoes
        self.salt = salt or os.urandom(16)
        
        # Gera ou carrega chave mestra
        if chave_mestre:
            self.chave_mestre = chave_mestre.encode()
        else:
            self.chave_mestre = os.urandom(32)
            
        # Deriva chave de criptografia
        self._derivar_chave()
        
        # Inicializa Fernet para criptografia simétrica
        self.fernet = Fernet(self.chave_criptografia)
        
        # Gera par de chaves RSA
        self._gerar_chaves_rsa()
        
        logger.info("Gerenciador de criptografia inicializado com sucesso")

    def _derivar_chave(self) -> None:
        """
        Deriva a chave de criptografia usando PBKDF2.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=self.iteracoes
        )
        self.chave_criptografia = base64.urlsafe_b64encode(kdf.derive(self.chave_mestre))

    def _gerar_chaves_rsa(self) -> None:
        """
        Gera par de chaves RSA.
        """
        self.chave_privada = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.chave_publica = self.chave_privada.public_key()

    def criptografar_simetrico(self, dados: Union[str, bytes, Dict]) -> bytes:
        """
        Criptografa dados usando criptografia simétrica (Fernet).
        
        Args:
            dados: Dados a serem criptografados
            
        Returns:
            bytes: Dados criptografados
        """
        try:
            if isinstance(dados, dict):
                dados = json.dumps(dados).encode()
            elif isinstance(dados, str):
                dados = dados.encode()
                
            return self.fernet.encrypt(dados)
        except Exception as e:
            logger.error(f"Erro ao criptografar dados: {str(e)}")
            raise

    def descriptografar_simetrico(self, dados_criptografados: bytes) -> Union[str, Dict]:
        """
        Descriptografa dados usando criptografia simétrica (Fernet).
        
        Args:
            dados_criptografados: Dados criptografados
            
        Returns:
            Union[str, Dict]: Dados descriptografados
        """
        try:
            dados = self.fernet.decrypt(dados_criptografados)
            
            # Tenta decodificar como JSON
            try:
                return json.loads(dados)
            except json.JSONDecodeError:
                return dados.decode()
        except Exception as e:
            logger.error(f"Erro ao descriptografar dados: {str(e)}")
            raise

    def criptografar_assimetrico(self, dados: Union[str, bytes]) -> bytes:
        """
        Criptografa dados usando criptografia assimétrica (RSA).
        
        Args:
            dados: Dados a serem criptografados
            
        Returns:
            bytes: Dados criptografados
        """
        try:
            if isinstance(dados, str):
                dados = dados.encode()
                
            return self.chave_publica.encrypt(
                dados,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        except Exception as e:
            logger.error(f"Erro ao criptografar dados assimetricamente: {str(e)}")
            raise

    def descriptografar_assimetrico(self, dados_criptografados: bytes) -> bytes:
        """
        Descriptografa dados usando criptografia assimétrica (RSA).
        
        Args:
            dados_criptografados: Dados criptografados
            
        Returns:
            bytes: Dados descriptografados
        """
        try:
            return self.chave_privada.decrypt(
                dados_criptografados,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        except Exception as e:
            logger.error(f"Erro ao descriptografar dados assimetricamente: {str(e)}")
            raise

    def exportar_chave_publica(self) -> bytes:
        """
        Exporta a chave pública em formato PEM.
        
        Returns:
            bytes: Chave pública em formato PEM
        """
        return self.chave_publica.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def importar_chave_publica(self, chave_publica: bytes) -> None:
        """
        Importa uma chave pública em formato PEM.
        
        Args:
            chave_publica: Chave pública em formato PEM
        """
        self.chave_publica = serialization.load_pem_public_key(chave_publica)

    def rotacionar_chaves(self) -> None:
        """
        Rotaciona as chaves de criptografia.
        """
        # Gera novo salt
        self.salt = os.urandom(16)
        
        # Deriva nova chave
        self._derivar_chave()
        
        # Atualiza Fernet
        self.fernet = Fernet(self.chave_criptografia)
        
        # Gera novo par de chaves RSA
        self._gerar_chaves_rsa()
        
        logger.info("Chaves de criptografia rotacionadas com sucesso") 