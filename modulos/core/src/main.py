"""Arquivo principal do módulo core."""

import asyncio
import logging
from typing import Dict, Any

from fastapi import FastAPI
from uvicorn import Config, Server

from .events import EventBus
from .middleware import Middleware
from .logging import StructuredLogger
from .config.config import Config as CoreConfig

class CoreModule:
    """Módulo Core do Sistema de Autocura."""
    
    def __init__(self):
        """Inicializa o módulo core."""
        self.app = FastAPI(
            title="Sistema Autocura - Core",
            description="Módulo Core do Sistema de Autocura",
            version="0.1.0"
        )
        
        # Inicializa componentes
        self.event_bus = EventBus()
        self.middleware = Middleware(self.event_bus)
        self.logger = StructuredLogger(
            log_file=CoreConfig.LOG_FILE_PATH,
            log_format=CoreConfig.LOG_FORMAT,
            log_level=CoreConfig.LOG_LEVEL
        )
        
        # Configura rotas
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura as rotas da API."""
        
        @self.app.get("/health")
        async def health_check():
            """Endpoint de verificação de saúde."""
            return {"status": "ok"}
        
        @self.app.get("/config")
        async def get_config():
            """Retorna as configurações atuais."""
            return CoreConfig.to_dict()
        
        @self.app.get("/modules")
        async def get_modules():
            """Retorna a lista de módulos registrados."""
            return {
                "modules": self.middleware.get_registered_modules()
            }
    
    async def start(self):
        """Inicia o módulo core."""
        try:
            # Configura o servidor
            config = Config(
                self.app,
                host=CoreConfig.CORE_HOST,
                port=CoreConfig.CORE_PORT,
                workers=CoreConfig.CORE_WORKERS,
                log_level=CoreConfig.LOG_LEVEL.lower()
            )
            
            # Inicia o servidor
            server = Server(config)
            await server.serve()
            
        except Exception as e:
            await self.logger.log(
                level="error",
                message=f"Erro ao iniciar o módulo core: {str(e)}"
            )
            raise
    
    async def shutdown(self):
        """Desliga o módulo core."""
        try:
            # Limpa recursos
            self.event_bus.clear_history()
            self.logger.clear_logs()
            
            await self.logger.log(
                level="info",
                message="Módulo core desligado com sucesso"
            )
            
        except Exception as e:
            await self.logger.log(
                level="error",
                message=f"Erro ao desligar o módulo core: {str(e)}"
            )
            raise

async def main():
    """Função principal."""
    core = CoreModule()
    
    try:
        await core.start()
    except KeyboardInterrupt:
        await core.shutdown()
    except Exception as e:
        logging.error(f"Erro fatal: {str(e)}")
        await core.shutdown()
        raise

if __name__ == "__main__":
    asyncio.run(main()) 