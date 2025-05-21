import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import os
from pathlib import Path
import yaml
from prometheus_client import Counter, Gauge, Histogram

@dataclass
class Configuracao:
    """Representa uma configuração do sistema."""
    id: str
    nome: str
    valor: Any
    tipo: str
    timestamp: datetime
    versao: str
    ambiente: str
    tags: List[str]
    descricao: str

class GerenciadorConfig:
    """Módulo Gerenciador de Configuração para gerenciar configurações do sistema."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o gerenciador de configuração.
        
        Args:
            config: Configuração do gerenciador
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Diretório base para arquivos de configuração
        self.base_dir = Path(config.get("base_dir", "config"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache de configurações
        self.configuracoes: Dict[str, Configuracao] = {}
        
        # Histórico de versões
        self.historico: Dict[str, List[Configuracao]] = {}
        
        # Métricas Prometheus
        self.metricas = {
            "configuracoes_criadas": Counter(
                "configuracoes_criadas",
                "Total de configurações criadas",
                ["tipo", "ambiente"]
            ),
            "configuracoes_atualizadas": Counter(
                "configuracoes_atualizadas",
                "Total de configurações atualizadas",
                ["tipo", "ambiente"]
            ),
            "configuracoes_carregadas": Counter(
                "configuracoes_carregadas",
                "Total de configurações carregadas",
                ["tipo", "ambiente"]
            ),
            "tempo_operacao": Histogram(
                "tempo_operacao_config",
                "Tempo de operações na configuração",
                ["operacao"]
            )
        }
        
        # Configuração de tipos de configuração
        self.tipos_config = {
            "sistema": {
                "formato": "json",
                "obrigatorio": True
            },
            "aplicacao": {
                "formato": "yaml",
                "obrigatorio": True
            },
            "ambiente": {
                "formato": "env",
                "obrigatorio": False
            },
            "secreto": {
                "formato": "json",
                "obrigatorio": False
            }
        }
        
        self.logger.info("Gerenciador de Configuração inicializado")
    
    async def carregar_configuracoes(self) -> None:
        """Carrega configurações do diretório base."""
        try:
            with self.metricas["tempo_operacao"].labels(operacao="carregar").time():
                for arquivo in self.base_dir.glob("**/*"):
                    if not arquivo.is_file():
                        continue
                    
                    # Determina tipo pelo caminho
                    tipo = arquivo.parent.name
                    if tipo not in self.tipos_config:
                        continue
                    
                    # Carrega arquivo
                    try:
                        if arquivo.suffix == ".json":
                            with open(arquivo, "r") as f:
                                dados = json.load(f)
                        elif arquivo.suffix in [".yaml", ".yml"]:
                            with open(arquivo, "r") as f:
                                dados = yaml.safe_load(f)
                        elif arquivo.suffix == ".env":
                            dados = {}
                            with open(arquivo, "r") as f:
                                for linha in f:
                                    if "=" in linha:
                                        chave, valor = linha.strip().split("=", 1)
                                        dados[chave] = valor
                        else:
                            continue
                        
                        # Cria configuração
                        config = Configuracao(
                            id=f"{tipo}_{arquivo.stem}",
                            nome=arquivo.stem,
                            valor=dados,
                            tipo=tipo,
                            timestamp=datetime.fromtimestamp(arquivo.stat().st_mtime),
                            versao="1.0",
                            ambiente=os.getenv("AMBIENTE", "desenvolvimento"),
                            tags=[],
                            descricao=f"Configuração carregada de {arquivo}"
                        )
                        
                        # Adiciona ao cache
                        self.configuracoes[config.id] = config
                        
                        # Atualiza métricas
                        self.metricas["configuracoes_carregadas"].labels(
                            tipo=tipo,
                            ambiente=config.ambiente
                        ).inc()
                        
                        self.logger.info(f"Configuração carregada: {config.id}")
                        
                    except Exception as e:
                        self.logger.error(f"Erro ao carregar arquivo {arquivo}: {e}")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
    
    async def criar_configuracao(self, nome: str, valor: Any, tipo: str, 
                               ambiente: str, tags: List[str] = None,
                               descricao: str = "") -> Optional[Configuracao]:
        """Cria uma nova configuração.
        
        Args:
            nome: Nome da configuração
            valor: Valor da configuração
            tipo: Tipo da configuração
            ambiente: Ambiente da configuração
            tags: Tags da configuração
            descricao: Descrição da configuração
            
        Returns:
            Configuração criada ou None em caso de erro
        """
        if tipo not in self.tipos_config:
            self.logger.error(f"Tipo de configuração desconhecido: {tipo}")
            return None
        
        try:
            with self.metricas["tempo_operacao"].labels(operacao="criar").time():
                # Gera ID único
                config_id = f"{tipo}_{nome}"
                
                # Cria configuração
                config = Configuracao(
                    id=config_id,
                    nome=nome,
                    valor=valor,
                    tipo=tipo,
                    timestamp=datetime.now(),
                    versao="1.0",
                    ambiente=ambiente,
                    tags=tags or [],
                    descricao=descricao
                )
                
                # Salva arquivo
                arquivo = self.base_dir / tipo / f"{nome}.{self.tipos_config[tipo]['formato']}"
                arquivo.parent.mkdir(parents=True, exist_ok=True)
                
                with open(arquivo, "w") as f:
                    if arquivo.suffix == ".json":
                        json.dump(valor, f, indent=2)
                    elif arquivo.suffix in [".yaml", ".yml"]:
                        yaml.dump(valor, f)
                    elif arquivo.suffix == ".env":
                        for chave, valor in valor.items():
                            f.write(f"{chave}={valor}\n")
                
                # Adiciona ao cache
                self.configuracoes[config_id] = config
                
                # Inicializa histórico
                self.historico[config_id] = [config]
                
                # Atualiza métricas
                self.metricas["configuracoes_criadas"].labels(
                    tipo=tipo,
                    ambiente=ambiente
                ).inc()
                
                self.logger.info(f"Configuração criada: {config_id}")
                return config
                
        except Exception as e:
            self.logger.error(f"Erro ao criar configuração: {e}")
            return None
    
    async def atualizar_configuracao(self, config_id: str, valor: Any) -> bool:
        """Atualiza uma configuração existente.
        
        Args:
            config_id: ID da configuração
            valor: Novo valor
            
        Returns:
            True se atualizado com sucesso
        """
        try:
            with self.metricas["tempo_operacao"].labels(operacao="atualizar").time():
                # Obtém configuração
                config = self.configuracoes.get(config_id)
                if not config:
                    return False
                
                # Incrementa versão
                versao_atual = float(config.versao)
                nova_versao = f"{versao_atual + 0.1:.1f}"
                
                # Cria nova versão
                nova_config = Configuracao(
                    id=config.id,
                    nome=config.nome,
                    valor=valor,
                    tipo=config.tipo,
                    timestamp=datetime.now(),
                    versao=nova_versao,
                    ambiente=config.ambiente,
                    tags=config.tags,
                    descricao=config.descricao
                )
                
                # Salva arquivo
                arquivo = self.base_dir / config.tipo / f"{config.nome}.{self.tipos_config[config.tipo]['formato']}"
                
                with open(arquivo, "w") as f:
                    if arquivo.suffix == ".json":
                        json.dump(valor, f, indent=2)
                    elif arquivo.suffix in [".yaml", ".yml"]:
                        yaml.dump(valor, f)
                    elif arquivo.suffix == ".env":
                        for chave, valor in valor.items():
                            f.write(f"{chave}={valor}\n")
                
                # Atualiza cache
                self.configuracoes[config_id] = nova_config
                
                # Adiciona ao histórico
                self.historico[config_id].append(nova_config)
                
                # Atualiza métricas
                self.metricas["configuracoes_atualizadas"].labels(
                    tipo=config.tipo,
                    ambiente=config.ambiente
                ).inc()
                
                self.logger.info(f"Configuração atualizada: {config_id} (versão {nova_versao})")
                return True
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar configuração: {e}")
            return False
    
    async def obter_configuracao(self, config_id: str) -> Optional[Configuracao]:
        """Obtém uma configuração pelo ID.
        
        Args:
            config_id: ID da configuração
            
        Returns:
            Configuração ou None se não encontrada
        """
        return self.configuracoes.get(config_id)
    
    async def buscar_configuracoes(self, tipo: Optional[str] = None,
                                 ambiente: Optional[str] = None,
                                 tags: Optional[List[str]] = None) -> List[Configuracao]:
        """Busca configurações por critérios.
        
        Args:
            tipo: Tipo da configuração (opcional)
            ambiente: Ambiente da configuração (opcional)
            tags: Tags da configuração (opcional)
            
        Returns:
            Lista de configurações encontradas
        """
        configuracoes = []
        
        for config in self.configuracoes.values():
            # Filtra por tipo
            if tipo and config.tipo != tipo:
                continue
            
            # Filtra por ambiente
            if ambiente and config.ambiente != ambiente:
                continue
            
            # Filtra por tags
            if tags and not all(tag in config.tags for tag in tags):
                continue
            
            configuracoes.append(config)
        
        return configuracoes
    
    async def obter_historico(self, config_id: str) -> List[Configuracao]:
        """Obtém o histórico de versões de uma configuração.
        
        Args:
            config_id: ID da configuração
            
        Returns:
            Lista de versões da configuração
        """
        return self.historico.get(config_id, [])
    
    async def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas das configurações.
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {
            "timestamp": datetime.now(),
            "total_configuracoes": len(self.configuracoes),
            "por_tipo": {},
            "por_ambiente": {},
            "por_tag": {},
            "total_versoes": 0
        }
        
        # Conta configurações por tipo, ambiente e tag
        for config in self.configuracoes.values():
            if config.tipo not in stats["por_tipo"]:
                stats["por_tipo"][config.tipo] = 0
            stats["por_tipo"][config.tipo] += 1
            
            if config.ambiente not in stats["por_ambiente"]:
                stats["por_ambiente"][config.ambiente] = 0
            stats["por_ambiente"][config.ambiente] += 1
            
            for tag in config.tags:
                if tag not in stats["por_tag"]:
                    stats["por_tag"][tag] = 0
                stats["por_tag"][tag] += 1
        
        # Conta total de versões
        for historico in self.historico.values():
            stats["total_versoes"] += len(historico)
        
        return stats 