import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import json
import os
from pathlib import Path

from src.orchestration.orquestrador_conhecimento import OrquestradorConhecimento, Documento

@pytest.fixture
def config():
    """Fixture com configuração básica para os testes."""
    return {
        "base_dir": "test_docs"
    }

@pytest.fixture
def orquestrador(config):
    """Fixture com instância do orquestrador de conhecimento."""
    return OrquestradorConhecimento(config)

@pytest.fixture
def documento_exemplo():
    """Fixture com documento de exemplo."""
    return {
        "tipo": "arquitetura",
        "conteudo": {
            "titulo": "Arquitetura do Sistema",
            "descricao": "Descrição da arquitetura",
            "componentes": ["Componente 1", "Componente 2"]
        },
        "autor": "Teste",
        "tags": ["arquitetura", "sistema"]
    }

@pytest.mark.asyncio
async def test_inicializacao(orquestrador, config):
    """Testa a inicialização do orquestrador."""
    assert orquestrador.config == config
    assert orquestrador.base_dir == Path(config["base_dir"])
    assert orquestrador.cache_documentos == {}
    assert orquestrador.indice_relacionamentos == {}
    assert orquestrador.historico_versoes == {}
    assert orquestrador.tipos_documento is not None

@pytest.mark.asyncio
async def test_criar_documento(orquestrador, documento_exemplo):
    """Testa a criação de documentos."""
    # Cria documento válido
    documento = await orquestrador.criar_documento(
        documento_exemplo["tipo"],
        documento_exemplo["conteudo"],
        documento_exemplo["autor"],
        documento_exemplo["tags"]
    )
    
    assert documento is not None
    assert documento.tipo == documento_exemplo["tipo"]
    assert documento.conteudo == documento_exemplo["conteudo"]
    assert documento.autor == documento_exemplo["autor"]
    assert documento.tags == documento_exemplo["tags"]
    assert documento.versao == "1.0"
    assert documento.relacionamentos == []
    
    # Verifica cache
    assert documento.id in orquestrador.cache_documentos
    
    # Verifica arquivo
    caminho = orquestrador.base_dir / f"{documento.id}.md"
    assert caminho.exists()
    
    # Tenta criar documento com tipo inválido
    documento = await orquestrador.criar_documento(
        "tipo_invalido",
        documento_exemplo["conteudo"],
        documento_exemplo["autor"],
        documento_exemplo["tags"]
    )
    assert documento is None

@pytest.mark.asyncio
async def test_atualizar_documento(orquestrador, documento_exemplo):
    """Testa a atualização de documentos."""
    # Cria documento
    documento = await orquestrador.criar_documento(
        documento_exemplo["tipo"],
        documento_exemplo["conteudo"],
        documento_exemplo["autor"],
        documento_exemplo["tags"]
    )
    
    # Atualiza documento
    novo_conteudo = {
        "titulo": "Arquitetura Atualizada",
        "descricao": "Nova descrição",
        "componentes": ["Componente 1", "Componente 2", "Componente 3"]
    }
    
    sucesso = await orquestrador.atualizar_documento(
        documento.id,
        novo_conteudo,
        "Novo Autor"
    )
    
    assert sucesso
    assert orquestrador.cache_documentos[documento.id].conteudo == novo_conteudo
    assert orquestrador.cache_documentos[documento.id].versao == "1.1"
    assert orquestrador.cache_documentos[documento.id].autor == "Novo Autor"
    
    # Tenta atualizar documento inexistente
    sucesso = await orquestrador.atualizar_documento(
        "doc_inexistente",
        novo_conteudo,
        "Autor"
    )
    assert not sucesso

@pytest.mark.asyncio
async def test_obter_documento(orquestrador, documento_exemplo):
    """Testa a obtenção de documentos."""
    # Cria documento
    documento = await orquestrador.criar_documento(
        documento_exemplo["tipo"],
        documento_exemplo["conteudo"],
        documento_exemplo["autor"],
        documento_exemplo["tags"]
    )
    
    # Obtém do cache
    doc_cache = await orquestrador.obter_documento(documento.id)
    assert doc_cache == documento
    
    # Limpa cache e obtém do disco
    orquestrador.cache_documentos = {}
    doc_disco = await orquestrador.obter_documento(documento.id)
    assert doc_disco is not None
    assert doc_disco.id == documento.id
    
    # Tenta obter documento inexistente
    doc_inexistente = await orquestrador.obter_documento("doc_inexistente")
    assert doc_inexistente is None

@pytest.mark.asyncio
async def test_buscar_documentos(orquestrador, documento_exemplo):
    """Testa a busca de documentos."""
    # Cria documentos
    doc1 = await orquestrador.criar_documento(
        documento_exemplo["tipo"],
        documento_exemplo["conteudo"],
        documento_exemplo["autor"],
        documento_exemplo["tags"]
    )
    
    doc2 = await orquestrador.criar_documento(
        "api",
        {"titulo": "API", "endpoints": []},
        "Autor",
        ["api", "sistema"]
    )
    
    # Busca por tipo
    docs_tipo = await orquestrador.buscar_documentos(tipo="arquitetura")
    assert len(docs_tipo) == 1
    assert docs_tipo[0].id == doc1.id
    
    # Busca por tags
    docs_tags = await orquestrador.buscar_documentos(tags=["sistema"])
    assert len(docs_tags) == 2
    
    # Busca por tipo e tags
    docs_filtrados = await orquestrador.buscar_documentos(
        tipo="arquitetura",
        tags=["sistema"]
    )
    assert len(docs_filtrados) == 1
    assert docs_filtrados[0].id == doc1.id

@pytest.mark.asyncio
async def test_relacionamentos(orquestrador, documento_exemplo):
    """Testa os relacionamentos entre documentos."""
    # Cria documentos
    doc1 = await orquestrador.criar_documento(
        documento_exemplo["tipo"],
        documento_exemplo["conteudo"],
        documento_exemplo["autor"],
        documento_exemplo["tags"]
    )
    
    doc2 = await orquestrador.criar_documento(
        "api",
        {"titulo": "API", "endpoints": []},
        "Autor",
        ["api", "sistema"]
    )
    
    # Adiciona relacionamento
    sucesso = await orquestrador.adicionar_relacionamento(doc1.id, doc2.id)
    assert sucesso
    
    # Verifica relacionamentos
    rels_doc1 = await orquestrador.obter_relacionamentos(doc1.id)
    assert len(rels_doc1) == 1
    assert rels_doc1[0].id == doc2.id
    
    rels_doc2 = await orquestrador.obter_relacionamentos(doc2.id)
    assert len(rels_doc2) == 1
    assert rels_doc2[0].id == doc1.id
    
    # Tenta adicionar relacionamento com documento inexistente
    sucesso = await orquestrador.adicionar_relacionamento(doc1.id, "doc_inexistente")
    assert not sucesso

@pytest.mark.asyncio
async def test_gerar_indice(orquestrador, documento_exemplo):
    """Testa a geração de índice."""
    # Cria documentos
    doc1 = await orquestrador.criar_documento(
        documento_exemplo["tipo"],
        documento_exemplo["conteudo"],
        documento_exemplo["autor"],
        documento_exemplo["tags"]
    )
    
    doc2 = await orquestrador.criar_documento(
        "api",
        {"titulo": "API", "endpoints": []},
        "Autor",
        ["api", "sistema"]
    )
    
    # Adiciona relacionamento
    await orquestrador.adicionar_relacionamento(doc1.id, doc2.id)
    
    # Gera índice
    indice = await orquestrador.gerar_indice()
    
    assert indice["timestamp"] is not None
    assert indice["total_documentos"] == 2
    assert "arquitetura" in indice["por_tipo"]
    assert "api" in indice["por_tipo"]
    assert "sistema" in indice["por_tag"]
    assert doc1.id in indice["relacionamentos"]
    assert doc2.id in indice["relacionamentos"]
    assert doc1.id in indice["versoes"]
    assert doc2.id in indice["versoes"]

@pytest.mark.asyncio
async def test_persistencia(orquestrador, documento_exemplo):
    """Testa a persistência dos documentos."""
    # Cria documento
    documento = await orquestrador.criar_documento(
        documento_exemplo["tipo"],
        documento_exemplo["conteudo"],
        documento_exemplo["autor"],
        documento_exemplo["tags"]
    )
    
    # Verifica arquivo
    caminho = orquestrador.base_dir / f"{documento.id}.md"
    assert caminho.exists()
    
    # Lê arquivo
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)
        assert dados["id"] == documento.id
        assert dados["tipo"] == documento.tipo
        assert dados["conteudo"] == documento.conteudo
        assert dados["autor"] == documento.autor
        assert dados["tags"] == documento.tags

@pytest.mark.asyncio
async def test_limpeza(orquestrador, config):
    """Testa a limpeza dos arquivos de teste."""
    # Remove diretório de teste
    if os.path.exists(config["base_dir"]):
        for arquivo in os.listdir(config["base_dir"]):
            os.remove(os.path.join(config["base_dir"], arquivo))
        os.rmdir(config["base_dir"]) 