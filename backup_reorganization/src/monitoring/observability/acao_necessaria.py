"""
Módulo de Rotas da Interface Web

Este módulo define as rotas da API REST e as páginas web para gerenciamento
de ações necessárias. Ele integra:
1. Interface web (templates HTML)
2. API REST para operações CRUD
3. Integração com o módulo de ações necessárias
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from typing import List, Optional
from datetime import datetime
import uuid

from ..executor.tela_acao import TelaAcaoNecessaria, AcaoNecessaria

# Inicialização do router e componentes
router = APIRouter()
tela_acao = TelaAcaoNecessaria()
templates = Jinja2Templates(directory="src/portal/templates")

@router.get("/acoes", response_class=HTMLResponse)
async def listar_acoes(request: Request):
    """
    Renderiza a página principal de ações necessárias.
    
    Esta rota:
    1. Obtém ações pendentes e histórico
    2. Renderiza o template com os dados
    3. Exibe a interface para o usuário
    
    Args:
        request: Objeto de requisição FastAPI
        
    Returns:
        HTMLResponse: Página renderizada
    """
    acoes_pendentes = tela_acao.obter_acoes_pendentes()
    historico = tela_acao.obter_historico()
    
    return templates.TemplateResponse(
        "acao_necessaria.html",
        {
            "request": request,
            "acoes_pendentes": acoes_pendentes,
            "historico": historico
        }
    )

@router.post("/api/acoes/aprovar")
async def aprovar_acao(acao_id: str, comentarios: Optional[str] = None):
    """
    Aprova uma ação pendente via API.
    
    Esta rota:
    1. Recebe o ID da ação e comentários opcionais
    2. Aprova a ação no sistema
    3. Retorna status da operação
    
    Args:
        acao_id: ID da ação a ser aprovada
        comentarios: Comentários opcionais
        
    Returns:
        dict: Status da operação
        
    Raises:
        HTTPException: Se a ação não existir ou ocorrer erro
    """
    try:
        tela_acao.aprovar_acao(acao_id, "sistema", comentarios)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/acoes/rejeitar")
async def rejeitar_acao(acao_id: str, comentarios: str):
    """
    Rejeita uma ação pendente via API.
    
    Esta rota:
    1. Recebe o ID da ação e comentários obrigatórios
    2. Rejeita a ação no sistema
    3. Retorna status da operação
    
    Args:
        acao_id: ID da ação a ser rejeitada
        comentarios: Comentários explicando a rejeição
        
    Returns:
        dict: Status da operação
        
    Raises:
        HTTPException: Se a ação não existir ou ocorrer erro
    """
    try:
        tela_acao.rejeitar_acao(acao_id, "sistema", comentarios)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/acoes/executar")
async def executar_acao(acao_id: str):
    """
    Marca uma ação como executada via API.
    
    Esta rota:
    1. Recebe o ID da ação
    2. Marca a ação como executada
    3. Retorna status da operação
    
    Args:
        acao_id: ID da ação a ser executada
        
    Returns:
        dict: Status da operação
        
    Raises:
        HTTPException: Se a ação não existir ou ocorrer erro
    """
    try:
        tela_acao.marcar_como_executada(acao_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/acoes/pendentes")
async def listar_acoes_pendentes():
    """
    Retorna todas as ações pendentes via API.
    
    Esta rota:
    1. Obtém lista de ações pendentes
    2. Retorna em formato JSON
    
    Returns:
        List[AcaoNecessaria]: Lista de ações pendentes
    """
    return tela_acao.obter_acoes_pendentes()

@router.get("/api/acoes/historico")
async def listar_historico():
    """
    Retorna o histórico completo de ações via API.
    
    Esta rota:
    1. Obtém histórico completo
    2. Retorna em formato JSON
    
    Returns:
        List[AcaoNecessaria]: Histórico completo
    """
    return tela_acao.obter_historico() 