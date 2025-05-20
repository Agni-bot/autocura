#!/usr/bin/env python3
"""
Implementação da camada de integração do sistema.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import aiohttp
import websockets
import redis
import msgpack
import yaml

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CamadaIntegracao:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.memoria_path = self.base_dir / 'memoria' / 'memoria_compartilhada.json'
        self.config_path = self.base_dir / 'config' / 'integracao.yaml'
        self.estado: Dict[str, Any] = {
            'ciclo_atual': 0,
            'ultima_execucao': None,
            'conexoes_ativas': {},
            'mensagens_processadas': [],
            'erros': []
        }
        self.adaptadores = {
            'http': self.adaptador_http,
            'websocket': self.adaptador_websocket,
            'redis': self.adaptador_redis,
            'kafka': self.adaptador_kafka
        }
        self.tradutores = {
            'json': self.tradutor_json,
            'msgpack': self.tradutor_msgpack,
            'yaml': self.tradutor_yaml
        }
        self.gateways = {}
        self.fila_mensagens = asyncio.Queue()
    
    async def carregar_configuracao(self):
        """Carrega a configuração da camada de integração."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
            else:
                self.config = {
                    'adaptadores': {
                        'http': {'timeout': 30, 'retries': 3},
                        'websocket': {'ping_interval': 20},
                        'redis': {'host': 'localhost', 'port': 6379},
                        'kafka': {'bootstrap_servers': ['localhost:9092']}
                    },
                    'tradutores': {
                        'json': {'indent': 2},
                        'msgpack': {'use_bin_type': True},
                        'yaml': {'default_flow_style': False}
                    },
                    'gateways': {}
                }
            logger.info("Configuração carregada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {str(e)}")
            raise
    
    async def carregar_memoria(self):
        """Carrega o estado atual da memória compartilhada."""
        try:
            if self.memoria_path.exists():
                with open(self.memoria_path, 'r', encoding='utf-8') as f:
                    memoria = json.load(f)
                    self.estado.update(memoria.get('estado_integracao', {}))
            logger.info("Memória da integração carregada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar memória da integração: {str(e)}")
            raise
    
    async def adaptador_http(self, endpoint: str, metodo: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptador para comunicação HTTP."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    metodo,
                    endpoint,
                    json=dados,
                    timeout=self.config['adaptadores']['http']['timeout']
                ) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Erro no adaptador HTTP: {str(e)}")
            raise
    
    async def adaptador_websocket(self, endpoint: str, mensagem: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptador para comunicação WebSocket."""
        try:
            async with websockets.connect(endpoint) as websocket:
                await websocket.send(json.dumps(mensagem))
                resposta = await websocket.recv()
                return json.loads(resposta)
        except Exception as e:
            logger.error(f"Erro no adaptador WebSocket: {str(e)}")
            raise
    
    async def adaptador_redis(self, chave: str, valor: Any) -> Any:
        """Adaptador para comunicação Redis."""
        try:
            redis_client = redis.Redis(
                host=self.config['adaptadores']['redis']['host'],
                port=self.config['adaptadores']['redis']['port']
            )
            if isinstance(valor, (dict, list)):
                valor = msgpack.packb(valor)
            redis_client.set(chave, valor)
            return redis_client.get(chave)
        except Exception as e:
            logger.error(f"Erro no adaptador Redis: {str(e)}")
            raise
    
    async def adaptador_kafka(self, topico: str, mensagem: Dict[str, Any]) -> None:
        """Adaptador para comunicação Kafka."""
        try:
            # TODO: Implementar adaptador Kafka real
            logger.info(f"Mensagem enviada para o tópico {topico}: {mensagem}")
        except Exception as e:
            logger.error(f"Erro no adaptador Kafka: {str(e)}")
            raise
    
    def tradutor_json(self, dados: Any) -> str:
        """Tradutor para formato JSON."""
        try:
            return json.dumps(dados, indent=self.config['tradutores']['json']['indent'])
        except Exception as e:
            logger.error(f"Erro no tradutor JSON: {str(e)}")
            raise
    
    def tradutor_msgpack(self, dados: Any) -> bytes:
        """Tradutor para formato MessagePack."""
        try:
            return msgpack.packb(dados, use_bin_type=self.config['tradutores']['msgpack']['use_bin_type'])
        except Exception as e:
            logger.error(f"Erro no tradutor MessagePack: {str(e)}")
            raise
    
    def tradutor_yaml(self, dados: Any) -> str:
        """Tradutor para formato YAML."""
        try:
            return yaml.dump(dados, default_flow_style=self.config['tradutores']['yaml']['default_flow_style'])
        except Exception as e:
            logger.error(f"Erro no tradutor YAML: {str(e)}")
            raise
    
    async def registrar_gateway(self, nome: str, config: Dict[str, Any]):
        """Registra um novo gateway de serviço."""
        try:
            self.gateways[nome] = {
                'config': config,
                'status': 'ativo',
                'ultima_verificacao': datetime.now().isoformat()
            }
            logger.info(f"Gateway {nome} registrado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao registrar gateway {nome}: {str(e)}")
            raise
    
    async def verificar_gateways(self):
        """Verifica o status dos gateways registrados."""
        try:
            for nome, gateway in self.gateways.items():
                try:
                    # TODO: Implementar verificação real de status
                    gateway['status'] = 'ativo'
                    gateway['ultima_verificacao'] = datetime.now().isoformat()
                except Exception as e:
                    gateway['status'] = 'inativo'
                    gateway['erro'] = str(e)
                    logger.error(f"Erro ao verificar gateway {nome}: {str(e)}")
        except Exception as e:
            logger.error(f"Erro ao verificar gateways: {str(e)}")
            raise
    
    async def processar_mensagem(self, mensagem: Dict[str, Any]):
        """Processa uma mensagem recebida."""
        try:
            # Extrair informações da mensagem
            origem = mensagem.get('origem')
            destino = mensagem.get('destino')
            protocolo = mensagem.get('protocolo')
            formato = mensagem.get('formato')
            dados = mensagem.get('dados')
            
            # Validar mensagem
            if not all([origem, destino, protocolo, formato, dados]):
                raise ValueError("Mensagem incompleta")
            
            # Traduzir dados se necessário
            if formato in self.tradutores:
                dados = self.tradutores[formato](dados)
            
            # Enviar mensagem usando adaptador apropriado
            if protocolo in self.adaptadores:
                resultado = await self.adaptadores[protocolo](destino, dados)
                
                # Registrar mensagem processada
                self.estado['mensagens_processadas'].append({
                    'timestamp': datetime.now().isoformat(),
                    'origem': origem,
                    'destino': destino,
                    'protocolo': protocolo,
                    'status': 'sucesso',
                    'resultado': resultado
                })
            else:
                raise ValueError(f"Protocolo não suportado: {protocolo}")
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            self.estado['erros'].append({
                'timestamp': datetime.now().isoformat(),
                'mensagem': str(e),
                'detalhes': mensagem
            })
            raise
    
    async def atualizar_memoria(self):
        """Atualiza a memória compartilhada com o novo estado."""
        try:
            self.estado['ultima_execucao'] = datetime.now().isoformat()
            self.estado['ciclo_atual'] += 1
            
            # Carrega memória existente
            if self.memoria_path.exists():
                with open(self.memoria_path, 'r', encoding='utf-8') as f:
                    memoria = json.load(f)
            else:
                memoria = {}
            
            # Atualiza estado da integração
            memoria['estado_integracao'] = self.estado
            
            # Salva memória atualizada
            with open(self.memoria_path, 'w', encoding='utf-8') as f:
                json.dump(memoria, f, indent=2, ensure_ascii=False)
            
            logger.info("Memória da integração atualizada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao atualizar memória da integração: {str(e)}")
            raise
    
    async def ciclo_integracao(self):
        """Executa um ciclo completo de integração."""
        try:
            logger.info("Iniciando ciclo de integração...")
            
            await self.carregar_configuracao()
            await self.carregar_memoria()
            await self.verificar_gateways()
            
            # Processar mensagens pendentes
            while not self.fila_mensagens.empty():
                mensagem = await self.fila_mensagens.get()
                await self.processar_mensagem(mensagem)
            
            await self.atualizar_memoria()
            
            logger.info("Ciclo de integração concluído com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro durante o ciclo de integração: {str(e)}")
            raise
    
    async def executar_continuamente(self, intervalo: int = 60):  # 1 minuto
        """Executa ciclos de integração continuamente."""
        while True:
            try:
                await self.ciclo_integracao()
                await asyncio.sleep(intervalo)
            except Exception as e:
                logger.error(f"Erro no ciclo contínuo de integração: {str(e)}")
                await asyncio.sleep(intervalo)  # Aguarda antes de tentar novamente

async def main():
    """Função principal."""
    integracao = CamadaIntegracao()
    await integracao.executar_continuamente()

if __name__ == '__main__':
    asyncio.run(main()) 