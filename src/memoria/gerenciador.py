"""
Módulo de Gerenciamento de Memória

Este módulo é responsável por gerenciar a memória do sistema,
armazenando e recuperando informações de forma eficiente e
persistente.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import json
import os
import sqlite3
from pathlib import Path
import hashlib
import pickle
from enum import Enum

class TipoMemoria(Enum):
    """Tipos de memória do sistema"""
    EPISODICA = "episodica"  # Memória de eventos e experiências
    SEMANTICA = "semantica"  # Memória de conhecimento e conceitos
    PROCEDURAL = "procedural"  # Memória de procedimentos e habilidades
    META = "meta"  # Memória sobre o próprio sistema

@dataclass
class EntradaMemoria:
    """Representa uma entrada na memória do sistema"""
    id: str
    tipo: TipoMemoria
    timestamp: datetime
    conteudo: Dict[str, Any]
    tags: List[str]
    peso: float
    relacionamentos: List[str]

class GerenciadorMemoria:
    def __init__(self, diretorio_base: str = "memoria"):
        self.logger = logging.getLogger(__name__)
        self.diretorio_base = Path(diretorio_base)
        self.db_path = self.diretorio_base / "memoria.db"
        self.cache_path = self.diretorio_base / "cache"
        
        # Cria diretórios necessários
        self.diretorio_base.mkdir(exist_ok=True)
        self.cache_path.mkdir(exist_ok=True)
        
        # Inicializa banco de dados
        self._inicializar_db()
        
    def _inicializar_db(self):
        """Inicializa o banco de dados SQLite"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Cria tabela de memória
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memoria (
            id TEXT PRIMARY KEY,
            tipo TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            tags TEXT NOT NULL,
            peso REAL NOT NULL,
            relacionamentos TEXT NOT NULL
        )
        """)
        
        # Cria índices
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_memoria_tipo ON memoria(tipo)
        """)
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_memoria_tags ON memoria(tags)
        """)
        
        conn.commit()
        conn.close()
        
    def _gerar_id(self, conteudo: Dict[str, Any]) -> str:
        """Gera um ID único para uma entrada de memória"""
        # Usa hash do conteúdo para gerar ID
        conteudo_str = json.dumps(conteudo, sort_keys=True)
        return hashlib.sha256(conteudo_str.encode()).hexdigest()
        
    def armazenar(self,
                 tipo: TipoMemoria,
                 conteudo: Dict[str, Any],
                 tags: Optional[List[str]] = None,
                 peso: float = 1.0,
                 relacionamentos: Optional[List[str]] = None) -> str:
        """Armazena uma entrada na memória"""
        # Gera ID
        id = self._gerar_id(conteudo)
        
        # Prepara dados
        timestamp = datetime.now().isoformat()
        tags = tags or []
        relacionamentos = relacionamentos or []
        
        # Converte para JSON
        conteudo_json = json.dumps(conteudo)
        tags_json = json.dumps(tags)
        relacionamentos_json = json.dumps(relacionamentos)
        
        # Armazena no banco de dados
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO memoria
            (id, tipo, timestamp, conteudo, tags, peso, relacionamentos)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                id,
                tipo.value,
                timestamp,
                conteudo_json,
                tags_json,
                peso,
                relacionamentos_json
            ))
            
            conn.commit()
            self.logger.info(f"Entrada armazenada: {id}")
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao armazenar entrada: {str(e)}")
            raise
            
        finally:
            conn.close()
            
        # Atualiza cache
        self._atualizar_cache(id, tipo, conteudo)
        
        return id
        
    def recuperar(self,
                 id: str) -> Optional[EntradaMemoria]:
        """Recupera uma entrada da memória pelo ID"""
        # Tenta recuperar do cache primeiro
        cache_path = self.cache_path / f"{id}.pkl"
        if cache_path.exists():
            try:
                with open(cache_path, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                self.logger.warning(f"Erro ao recuperar do cache: {str(e)}")
                
        # Se não estiver em cache, recupera do banco
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            SELECT tipo, timestamp, conteudo, tags, peso, relacionamentos
            FROM memoria
            WHERE id = ?
            """, (id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            tipo, timestamp, conteudo_json, tags_json, peso, relacionamentos_json = row
            
            # Converte de JSON
            conteudo = json.loads(conteudo_json)
            tags = json.loads(tags_json)
            relacionamentos = json.loads(relacionamentos_json)
            
            # Cria objeto
            entrada = EntradaMemoria(
                id=id,
                tipo=TipoMemoria(tipo),
                timestamp=datetime.fromisoformat(timestamp),
                conteudo=conteudo,
                tags=tags,
                peso=peso,
                relacionamentos=relacionamentos
            )
            
            # Atualiza cache
            self._atualizar_cache(id, TipoMemoria(tipo), conteudo)
            
            return entrada
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao recuperar entrada: {str(e)}")
            raise
            
        finally:
            conn.close()
            
    def buscar(self,
              tipo: Optional[TipoMemoria] = None,
              tags: Optional[List[str]] = None,
              peso_minimo: float = 0.0,
              limite: int = 100) -> List[EntradaMemoria]:
        """Busca entradas na memória por critérios"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # Constrói query
            query = "SELECT id FROM memoria WHERE 1=1"
            params = []
            
            if tipo:
                query += " AND tipo = ?"
                params.append(tipo.value)
                
            if tags:
                tags_json = json.dumps(tags)
                query += " AND tags LIKE ?"
                params.append(f"%{tags_json}%")
                
            if peso_minimo > 0:
                query += " AND peso >= ?"
                params.append(peso_minimo)
                
            query += " ORDER BY peso DESC LIMIT ?"
            params.append(limite)
            
            # Executa query
            cursor.execute(query, params)
            
            # Recupera entradas
            ids = [row[0] for row in cursor.fetchall()]
            entradas = []
            
            for id in ids:
                entrada = self.recuperar(id)
                if entrada:
                    entradas.append(entrada)
                    
            return entradas
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao buscar entradas: {str(e)}")
            raise
            
        finally:
            conn.close()
            
    def _atualizar_cache(self,
                        id: str,
                        tipo: TipoMemoria,
                        conteudo: Dict[str, Any]):
        """Atualiza o cache de memória"""
        cache_path = self.cache_path / f"{id}.pkl"
        
        try:
            # Cria entrada
            entrada = EntradaMemoria(
                id=id,
                tipo=tipo,
                timestamp=datetime.now(),
                conteudo=conteudo,
                tags=[],
                peso=1.0,
                relacionamentos=[]
            )
            
            # Salva no cache
            with open(cache_path, "wb") as f:
                pickle.dump(entrada, f)
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar cache: {str(e)}")
            
    def limpar_cache(self):
        """Limpa o cache de memória"""
        try:
            for cache_file in self.cache_path.glob("*.pkl"):
                cache_file.unlink()
            self.logger.info("Cache limpo")
        except Exception as e:
            self.logger.error(f"Erro ao limpar cache: {str(e)}")
            
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas da memória"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # Total de entradas
            cursor.execute("SELECT COUNT(*) FROM memoria")
            total_entradas = cursor.fetchone()[0]
            
            # Entradas por tipo
            cursor.execute("""
            SELECT tipo, COUNT(*) as count
            FROM memoria
            GROUP BY tipo
            """)
            entradas_por_tipo = {
                row[0]: row[1]
                for row in cursor.fetchall()
            }
            
            # Média de peso
            cursor.execute("SELECT AVG(peso) FROM memoria")
            media_peso = cursor.fetchone()[0]
            
            # Total de tags únicas
            cursor.execute("SELECT DISTINCT json_each.value FROM memoria, json_each(memoria.tags)")
            tags_unicas = len(cursor.fetchall())
            
            return {
                "total_entradas": total_entradas,
                "entradas_por_tipo": entradas_por_tipo,
                "media_peso": media_peso,
                "tags_unicas": tags_unicas,
                "tamanho_cache": len(list(self.cache_path.glob("*.pkl")))
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao obter estatísticas: {str(e)}")
            raise
            
        finally:
            conn.close()

# Exemplo de uso
if __name__ == "__main__":
    # Configura logging
    logging.basicConfig(level=logging.INFO)
    
    # Cria instância do gerenciador
    gerenciador = GerenciadorMemoria()
    
    # Armazena algumas entradas
    id1 = gerenciador.armazenar(
        tipo=TipoMemoria.EPISODICA,
        conteudo={
            "evento": "inicializacao",
            "status": "sucesso",
            "timestamp": datetime.now().isoformat()
        },
        tags=["sistema", "inicializacao"],
        peso=1.0
    )
    
    id2 = gerenciador.armazenar(
        tipo=TipoMemoria.SEMANTICA,
        conteudo={
            "conceito": "autocura",
            "definicao": "Capacidade de auto-recuperação",
            "exemplos": ["monitoramento", "diagnóstico", "ação"]
        },
        tags=["conceito", "autocura"],
        peso=0.8
    )
    
    # Recupera entrada
    entrada = gerenciador.recuperar(id1)
    print("\nEntrada Recuperada:")
    print(json.dumps({
        "id": entrada.id,
        "tipo": entrada.tipo.value,
        "timestamp": entrada.timestamp.isoformat(),
        "conteudo": entrada.conteudo,
        "tags": entrada.tags,
        "peso": entrada.peso
    }, indent=2))
    
    # Busca entradas
    entradas = gerenciador.buscar(
        tipo=TipoMemoria.SEMANTICA,
        tags=["conceito"]
    )
    print("\nEntradas Encontradas:")
    for e in entradas:
        print(json.dumps({
            "id": e.id,
            "tipo": e.tipo.value,
            "conteudo": e.conteudo,
            "tags": e.tags
        }, indent=2))
        
    # Obtém estatísticas
    estatisticas = gerenciador.obter_estatisticas()
    print("\nEstatísticas da Memória:")
    print(json.dumps(estatisticas, indent=2)) 