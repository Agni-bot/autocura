import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from pathlib import Path
import threading
import time
import hashlib

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("cache")

class Cache:
    """Sistema de cache"""
    
    def __init__(self, config_path: str = "config/cache.json"):
        self.config = self._carregar_config(config_path)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        self.thread_limpeza = None
        self.running = False
        logger.info("Sistema de Cache inicializado")
    
    def _carregar_config(self, config_path: str) -> Dict[str, Any]:
        """Carrega a configuração do cache"""
        try:
            caminho_config = Path(config_path)
            if caminho_config.exists():
                with open(caminho_config, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("Arquivo de configuração não encontrado. Usando configuração padrão.")
                return self._criar_config_padrao()
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {str(e)}")
            return self._criar_config_padrao()
    
    def _criar_config_padrao(self) -> Dict[str, Any]:
        """Cria configuração padrão do cache"""
        return {
            "configuracoes": {
                "max_tamanho": 1000,
                "ttl_padrao": 3600,
                "limpeza_intervalo": 300,
                "politica_limpeza": "lru"
            },
            "tipos_cache": {
                "metricas": {
                    "ttl": 300,
                    "max_tamanho": 100
                },
                "diagnosticos": {
                    "ttl": 3600,
                    "max_tamanho": 50
                },
                "configuracoes": {
                    "ttl": 86400,
                    "max_tamanho": 20
                }
            }
        }
    
    def iniciar(self) -> None:
        """Inicia o sistema de cache"""
        try:
            if self.running:
                logger.warning("Cache já está em execução")
                return
            
            self.running = True
            self.thread_limpeza = threading.Thread(target=self._executar_limpeza)
            self.thread_limpeza.start()
            
            logger.info("Cache iniciado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar cache: {str(e)}")
            self.running = False
    
    def parar(self) -> None:
        """Para o sistema de cache"""
        try:
            if not self.running:
                logger.warning("Cache não está em execução")
                return
            
            self.running = False
            if self.thread_limpeza:
                self.thread_limpeza.join()
            
            logger.info("Cache parado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao parar cache: {str(e)}")
    
    def _executar_limpeza(self) -> None:
        """Executa o processo de limpeza do cache"""
        try:
            while self.running:
                self._limpar_cache()
                time.sleep(self.config["configuracoes"]["limpeza_intervalo"])
            
        except Exception as e:
            logger.error(f"Erro no processo de limpeza: {str(e)}")
            self.running = False
    
    def _limpar_cache(self) -> None:
        """Limpa itens expirados do cache"""
        try:
            with self.lock:
                agora = datetime.now()
                chaves_remover = []
                
                # Identifica itens expirados
                for chave, valor in self.cache.items():
                    if valor["expiracao"] < agora:
                        chaves_remover.append(chave)
                
                # Remove itens expirados
                for chave in chaves_remover:
                    del self.cache[chave]
                
                # Verifica limite de tamanho
                if len(self.cache) > self.config["configuracoes"]["max_tamanho"]:
                    self._aplicar_politica_limpeza()
                
                logger.info(f"Cache limpo: {len(chaves_remover)} itens removidos")
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {str(e)}")
    
    def _aplicar_politica_limpeza(self) -> None:
        """Aplica política de limpeza quando cache excede limite"""
        try:
            if self.config["configuracoes"]["politica_limpeza"] == "lru":
                # Remove itens menos recentemente usados
                itens_ordenados = sorted(
                    self.cache.items(),
                    key=lambda x: x[1]["ultimo_acesso"]
                )
                
                # Remove 20% dos itens mais antigos
                num_remover = int(len(self.cache) * 0.2)
                for chave, _ in itens_ordenados[:num_remover]:
                    del self.cache[chave]
                
                logger.info(f"Política LRU aplicada: {num_remover} itens removidos")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar política de limpeza: {str(e)}")
    
    def _gerar_chave(self, tipo: str, identificador: str) -> str:
        """Gera chave única para o cache"""
        try:
            # Combina tipo e identificador
            chave_base = f"{tipo}:{identificador}"
            
            # Gera hash MD5
            return hashlib.md5(chave_base.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Erro ao gerar chave: {str(e)}")
            raise
    
    def obter(self, tipo: str, identificador: str) -> Optional[Any]:
        """Obtém item do cache"""
        try:
            chave = self._gerar_chave(tipo, identificador)
            
            with self.lock:
                if chave in self.cache:
                    item = self.cache[chave]
                    
                    # Verifica expiração
                    if item["expiracao"] > datetime.now():
                        # Atualiza último acesso
                        item["ultimo_acesso"] = datetime.now()
                        return item["valor"]
                    else:
                        # Remove item expirado
                        del self.cache[chave]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter item do cache: {str(e)}")
            return None
    
    def definir(self, tipo: str, identificador: str, valor: Any) -> None:
        """Define item no cache"""
        try:
            chave = self._gerar_chave(tipo, identificador)
            
            # Obtém configuração do tipo
            config_tipo = self.config["tipos_cache"].get(
                tipo,
                {
                    "ttl": self.config["configuracoes"]["ttl_padrao"],
                    "max_tamanho": self.config["configuracoes"]["max_tamanho"]
                }
            )
            
            with self.lock:
                # Verifica limite do tipo
                if len(self.cache) >= config_tipo["max_tamanho"]:
                    self._aplicar_politica_limpeza()
                
                # Define item
                self.cache[chave] = {
                    "valor": valor,
                    "tipo": tipo,
                    "identificador": identificador,
                    "criacao": datetime.now(),
                    "ultimo_acesso": datetime.now(),
                    "expiracao": datetime.now() + timedelta(seconds=config_tipo["ttl"])
                }
            
            logger.info(f"Item definido no cache: {tipo}:{identificador}")
            
        except Exception as e:
            logger.error(f"Erro ao definir item no cache: {str(e)}")
    
    def remover(self, tipo: str, identificador: str) -> None:
        """Remove item do cache"""
        try:
            chave = self._gerar_chave(tipo, identificador)
            
            with self.lock:
                if chave in self.cache:
                    del self.cache[chave]
                    logger.info(f"Item removido do cache: {tipo}:{identificador}")
            
        except Exception as e:
            logger.error(f"Erro ao remover item do cache: {str(e)}")
    
    def limpar_tipo(self, tipo: str) -> None:
        """Limpa todos os itens de um tipo específico"""
        try:
            with self.lock:
                chaves_remover = []
                
                # Identifica itens do tipo
                for chave, valor in self.cache.items():
                    if valor["tipo"] == tipo:
                        chaves_remover.append(chave)
                
                # Remove itens
                for chave in chaves_remover:
                    del self.cache[chave]
                
                logger.info(f"Cache limpo para tipo '{tipo}': {len(chaves_remover)} itens removidos")
            
        except Exception as e:
            logger.error(f"Erro ao limpar tipo do cache: {str(e)}")
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        try:
            with self.lock:
                return {
                    "total_itens": len(self.cache),
                    "tipos": {
                        tipo: len([v for v in self.cache.values() if v["tipo"] == tipo])
                        for tipo in self.config["tipos_cache"].keys()
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do cache: {str(e)}")
            return {} 