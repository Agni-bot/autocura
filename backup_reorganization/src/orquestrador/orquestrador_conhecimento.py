import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import os
from pathlib import Path

@dataclass
class Documento:
    """Representa um documento do sistema."""
    id: str
    tipo: str
    conteudo: Dict[str, Any]
    timestamp: datetime
    versao: str
    autor: str
    tags: List[str]
    relacionamentos: List[str]

class OrquestradorConhecimento:
    """Módulo Orquestrador de Conhecimento para gerenciar a documentação do sistema."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o orquestrador de conhecimento.
        
        Args:
            config: Configuração do orquestrador
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Diretório base para documentação
        self.base_dir = Path(config.get("base_dir", "docs"))
        self.base_dir.mkdir(exist_ok=True)
        
        # Cache de documentos
        self.cache_documentos: Dict[str, Documento] = {}
        
        # Índice de relacionamentos
        self.indice_relacionamentos: Dict[str, List[str]] = {}
        
        # Histórico de versões
        self.historico_versoes: Dict[str, List[str]] = {}
        
        # Configuração de tipos de documento
        self.tipos_documento = {
            "arquitetura": {
                "extensao": ".md",
                "template": "templates/arquitetura.md"
            },
            "api": {
                "extensao": ".yaml",
                "template": "templates/api.yaml"
            },
            "modelo": {
                "extensao": ".json",
                "template": "templates/modelo.json"
            },
            "dados": {
                "extensao": ".json",
                "template": "templates/dados.json"
            },
            "etica": {
                "extensao": ".md",
                "template": "templates/etica.md"
            }
        }
        
        self.logger.info("Orquestrador de Conhecimento inicializado")
    
    async def criar_documento(self, tipo: str, conteudo: Dict[str, Any], autor: str, tags: List[str] = None) -> Optional[Documento]:
        """Cria um novo documento.
        
        Args:
            tipo: Tipo do documento
            conteudo: Conteúdo do documento
            autor: Autor do documento
            tags: Tags do documento
            
        Returns:
            Documento criado ou None em caso de erro
        """
        if tipo not in self.tipos_documento:
            self.logger.error(f"Tipo de documento desconhecido: {tipo}")
            return None
        
        try:
            # Gera ID único
            doc_id = f"{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Cria documento
            documento = Documento(
                id=doc_id,
                tipo=tipo,
                conteudo=conteudo,
                timestamp=datetime.now(),
                versao="1.0",
                autor=autor,
                tags=tags or [],
                relacionamentos=[]
            )
            
            # Salva documento
            await self._salvar_documento(documento)
            
            # Atualiza cache
            self.cache_documentos[doc_id] = documento
            
            # Atualiza índice
            await self._atualizar_indice(documento)
            
            self.logger.info(f"Documento criado: {doc_id}")
            return documento
            
        except Exception as e:
            self.logger.error(f"Erro ao criar documento: {e}")
            return None
    
    async def atualizar_documento(self, doc_id: str, conteudo: Dict[str, Any], autor: str) -> bool:
        """Atualiza um documento existente.
        
        Args:
            doc_id: ID do documento
            conteudo: Novo conteúdo
            autor: Autor da atualização
            
        Returns:
            True se atualizado com sucesso
        """
        if doc_id not in self.cache_documentos:
            self.logger.error(f"Documento não encontrado: {doc_id}")
            return False
        
        try:
            documento = self.cache_documentos[doc_id]
            
            # Incrementa versão
            versao_atual = float(documento.versao)
            nova_versao = f"{versao_atual + 0.1:.1f}"
            
            # Atualiza documento
            documento.conteudo = conteudo
            documento.timestamp = datetime.now()
            documento.versao = nova_versao
            documento.autor = autor
            
            # Salva documento
            await self._salvar_documento(documento)
            
            # Atualiza histórico
            if doc_id not in self.historico_versoes:
                self.historico_versoes[doc_id] = []
            self.historico_versoes[doc_id].append(nova_versao)
            
            self.logger.info(f"Documento atualizado: {doc_id} (versão {nova_versao})")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar documento: {e}")
            return False
    
    async def obter_documento(self, doc_id: str) -> Optional[Documento]:
        """Obtém um documento pelo ID.
        
        Args:
            doc_id: ID do documento
            
        Returns:
            Documento ou None se não encontrado
        """
        if doc_id in self.cache_documentos:
            return self.cache_documentos[doc_id]
        
        try:
            # Tenta carregar do disco
            documento = await self._carregar_documento(doc_id)
            if documento:
                self.cache_documentos[doc_id] = documento
            return documento
            
        except Exception as e:
            self.logger.error(f"Erro ao obter documento: {e}")
            return None
    
    async def buscar_documentos(self, tipo: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Documento]:
        """Busca documentos por tipo e/ou tags.
        
        Args:
            tipo: Tipo do documento (opcional)
            tags: Tags do documento (opcional)
            
        Returns:
            Lista de documentos encontrados
        """
        documentos = []
        
        for doc_id, documento in self.cache_documentos.items():
            if tipo and documento.tipo != tipo:
                continue
                
            if tags and not all(tag in documento.tags for tag in tags):
                continue
                
            documentos.append(documento)
        
        return documentos
    
    async def adicionar_relacionamento(self, doc_id: str, doc_relacionado_id: str) -> bool:
        """Adiciona um relacionamento entre documentos.
        
        Args:
            doc_id: ID do documento
            doc_relacionado_id: ID do documento relacionado
            
        Returns:
            True se adicionado com sucesso
        """
        if doc_id not in self.cache_documentos or doc_relacionado_id not in self.cache_documentos:
            self.logger.error("Documento(s) não encontrado(s)")
            return False
        
        try:
            # Adiciona relacionamento bidirecional
            self.cache_documentos[doc_id].relacionamentos.append(doc_relacionado_id)
            self.cache_documentos[doc_relacionado_id].relacionamentos.append(doc_id)
            
            # Atualiza índice
            if doc_id not in self.indice_relacionamentos:
                self.indice_relacionamentos[doc_id] = []
            if doc_relacionado_id not in self.indice_relacionamentos:
                self.indice_relacionamentos[doc_relacionado_id] = []
                
            self.indice_relacionamentos[doc_id].append(doc_relacionado_id)
            self.indice_relacionamentos[doc_relacionado_id].append(doc_id)
            
            # Salva documentos
            await self._salvar_documento(self.cache_documentos[doc_id])
            await self._salvar_documento(self.cache_documentos[doc_relacionado_id])
            
            self.logger.info(f"Relacionamento adicionado: {doc_id} <-> {doc_relacionado_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar relacionamento: {e}")
            return False
    
    async def obter_relacionamentos(self, doc_id: str) -> List[Documento]:
        """Obtém os documentos relacionados.
        
        Args:
            doc_id: ID do documento
            
        Returns:
            Lista de documentos relacionados
        """
        if doc_id not in self.cache_documentos:
            return []
        
        documentos = []
        for rel_id in self.cache_documentos[doc_id].relacionamentos:
            if rel_id in self.cache_documentos:
                documentos.append(self.cache_documentos[rel_id])
        
        return documentos
    
    async def gerar_indice(self) -> Dict[str, Any]:
        """Gera um índice completo da documentação.
        
        Returns:
            Dicionário com índice
        """
        indice = {
            "timestamp": datetime.now(),
            "total_documentos": len(self.cache_documentos),
            "por_tipo": {},
            "por_tag": {},
            "relacionamentos": self.indice_relacionamentos,
            "versoes": self.historico_versoes
        }
        
        # Conta documentos por tipo
        for doc in self.cache_documentos.values():
            if doc.tipo not in indice["por_tipo"]:
                indice["por_tipo"][doc.tipo] = 0
            indice["por_tipo"][doc.tipo] += 1
            
            # Conta documentos por tag
            for tag in doc.tags:
                if tag not in indice["por_tag"]:
                    indice["por_tag"][tag] = 0
                indice["por_tag"][tag] += 1
        
        return indice
    
    async def _salvar_documento(self, documento: Documento) -> None:
        """Salva um documento no disco.
        
        Args:
            documento: Documento a ser salvo
        """
        tipo_config = self.tipos_documento[documento.tipo]
        caminho = self.base_dir / f"{documento.id}{tipo_config['extensao']}"
        
        # Cria diretório se necessário
        caminho.parent.mkdir(exist_ok=True)
        
        # Salva documento
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(documento.__dict__, f, indent=2, default=str)
    
    async def _carregar_documento(self, doc_id: str) -> Optional[Documento]:
        """Carrega um documento do disco.
        
        Args:
            doc_id: ID do documento
            
        Returns:
            Documento carregado ou None se não encontrado
        """
        # Tenta encontrar o arquivo
        for tipo, config in self.tipos_documento.items():
            caminho = self.base_dir / f"{doc_id}{config['extensao']}"
            if caminho.exists():
                try:
                    with open(caminho, "r", encoding="utf-8") as f:
                        dados = json.load(f)
                        return Documento(**dados)
                except Exception as e:
                    self.logger.error(f"Erro ao carregar documento: {e}")
                    return None
        
        return None
    
    async def _atualizar_indice(self, documento: Documento) -> None:
        """Atualiza o índice de relacionamentos.
        
        Args:
            documento: Documento a ser indexado
        """
        # Adiciona ao índice de relacionamentos
        if documento.id not in self.indice_relacionamentos:
            self.indice_relacionamentos[documento.id] = []
        
        # Adiciona ao histórico de versões
        if documento.id not in self.historico_versoes:
            self.historico_versoes[documento.id] = []
        self.historico_versoes[documento.id].append(documento.versao) 