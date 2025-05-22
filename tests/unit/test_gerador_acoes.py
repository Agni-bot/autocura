"""
Testes do gerador de ações do sistema.
"""
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from src.acoes.gerador_acoes import GeradorAcoes, Acao
from src.services.diagnostico.rede_neural import Diagnostico

@pytest.fixture
def gerador():
    """Fixture que fornece uma instância do gerador de ações para os testes."""
    return GeradorAcoes()

@pytest.fixture
def diagnostico_cpu():
    """Fixture que fornece um diagnóstico de alta CPU para os testes."""
    return Diagnostico(
        timestamp=datetime.now(),
        anomalia_detectada=True,
        score_anomalia=0.9,
        padrao_detectado="alta_cpu",
        confianca=0.8,
        metricas_relevantes=["cpu_usage"],
        recomendacoes=["Verificar processos com alto consumo de CPU"]
    )

@pytest.fixture
def diagnostico_memoria():
    """Fixture que fornece um diagnóstico de alta memória para os testes."""
    return Diagnostico(
        timestamp=datetime.now(),
        anomalia_detectada=True,
        score_anomalia=0.85,
        padrao_detectado="alta_memoria",
        confianca=0.75,
        metricas_relevantes=["memory_usage"],
        recomendacoes=["Verificar vazamentos de memória"]
    )

def test_gerar_acao_manutencao():
    """Testa a geração de ação de manutenção."""
    gerador = GeradorAcoes()
    
    # Simular contexto
    contexto = {
        "tipo": "manutencao",
        "prioridade": "alta",
        "descricao": "Corrigir bug crítico",
        "componente": "api",
        "impacto": "alto"
    }
    
    # Gerar ação
    acao = gerador.gerar_acao(contexto)
    
    # Verificar resultado
    assert acao["tipo"] == "manutencao"
    assert acao["prioridade"] == "alta"
    assert acao["status"] == "pendente"
    assert acao["componente"] == "api"
    assert acao["impacto"] == "alto"

def test_gerar_acao_hotfix():
    """Testa a geração de ação de hotfix."""
    gerador = GeradorAcoes()
    
    # Simular contexto
    contexto = {
        "tipo": "hotfix",
        "prioridade": "critica",
        "descricao": "Corrigir vulnerabilidade de segurança",
        "componente": "autenticacao",
        "impacto": "critico"
    }
    
    # Gerar ação
    acao = gerador.gerar_acao(contexto)
    
    # Verificar resultado
    assert acao["tipo"] == "hotfix"
    assert acao["prioridade"] == "critica"
    assert acao["status"] == "pendente"
    assert acao["componente"] == "autenticacao"
    assert acao["impacto"] == "critico"

def test_gerar_acao_refatoracao():
    """Testa a geração de ação de refatoração."""
    gerador = GeradorAcoes()
    
    # Simular contexto
    contexto = {
        "tipo": "refatoracao",
        "prioridade": "media",
        "descricao": "Melhorar estrutura do código",
        "componente": "core",
        "impacto": "medio"
    }
    
    # Gerar ação
    acao = gerador.gerar_acao(contexto)
    
    # Verificar resultado
    assert acao["tipo"] == "refatoracao"
    assert acao["prioridade"] == "media"
    assert acao["status"] == "pendente"
    assert acao["componente"] == "core"
    assert acao["impacto"] == "medio"

def test_gerar_acao_redesign():
    """Testa a geração de ação de redesign."""
    gerador = GeradorAcoes()
    
    # Simular contexto
    contexto = {
        "tipo": "redesign",
        "prioridade": "baixa",
        "descricao": "Redesenhar interface do usuário",
        "componente": "frontend",
        "impacto": "baixo"
    }
    
    # Gerar ação
    acao = gerador.gerar_acao(contexto)
    
    # Verificar resultado
    assert acao["tipo"] == "redesign"
    assert acao["prioridade"] == "baixa"
    assert acao["status"] == "pendente"
    assert acao["componente"] == "frontend"
    assert acao["impacto"] == "baixo"

def test_verificar_dependencias():
    """Testa a verificação de dependências."""
    gerador = GeradorAcoes()
    
    # Simular ação com dependências
    acao = {
        "id": "test_1",
        "tipo": "manutencao",
        "dependencias": [
            {"id": "dep_1", "status": "concluida"},
            {"id": "dep_2", "status": "concluida"}
        ]
    }
    
    # Verificar dependências
    resultado = gerador.verificar_dependencias(acao)
    
    # Verificar resultado
    assert resultado == True

def test_verificar_dependencias_pendentes():
    """Testa a verificação de dependências pendentes."""
    gerador = GeradorAcoes()
    
    # Simular ação com dependências pendentes
    acao = {
        "id": "test_1",
        "tipo": "manutencao",
        "dependencias": [
            {"id": "dep_1", "status": "concluida"},
            {"id": "dep_2", "status": "pendente"}
        ]
    }
    
    # Verificar dependências
    resultado = gerador.verificar_dependencias(acao)
    
    # Verificar resultado
    assert resultado == False

def test_executar_acao_manutencao():
    """Testa a execução de ação de manutenção."""
    gerador = GeradorAcoes()
    
    # Simular ação
    acao = {
        "id": "test_1",
        "tipo": "manutencao",
        "status": "pendente",
        "componente": "api"
    }
    
    # Executar ação
    resultado = gerador.executar_acao(acao)
    
    # Verificar resultado
    assert resultado["status"] == "concluida"
    assert resultado["sucesso"] == True
    assert resultado["timestamp_conclusao"] is not None

def test_executar_acao_hotfix():
    """Testa a execução de ação de hotfix."""
    gerador = GeradorAcoes()
    
    # Simular ação
    acao = {
        "id": "test_1",
        "tipo": "hotfix",
        "status": "pendente",
        "componente": "autenticacao"
    }
    
    # Executar ação
    resultado = gerador.executar_acao(acao)
    
    # Verificar resultado
    assert resultado["status"] == "concluida"
    assert resultado["sucesso"] == True
    assert resultado["timestamp_conclusao"] is not None

def test_executar_acao_refatoracao():
    """Testa a execução de ação de refatoração."""
    gerador = GeradorAcoes()
    
    # Simular ação
    acao = {
        "id": "test_1",
        "tipo": "refatoracao",
        "status": "pendente",
        "componente": "core"
    }
    
    # Executar ação
    resultado = gerador.executar_acao(acao)
    
    # Verificar resultado
    assert resultado["status"] == "concluida"
    assert resultado["sucesso"] == True
    assert resultado["timestamp_conclusao"] is not None

def test_executar_acao_redesign():
    """Testa a execução de ação de redesign."""
    gerador = GeradorAcoes()
    
    # Simular ação
    acao = {
        "id": "test_1",
        "tipo": "redesign",
        "status": "pendente",
        "componente": "frontend"
    }
    
    # Executar ação
    resultado = gerador.executar_acao(acao)
    
    # Verificar resultado
    assert resultado["status"] == "concluida"
    assert resultado["sucesso"] == True
    assert resultado["timestamp_conclusao"] is not None

def test_obter_estatisticas():
    """Testa a obtenção de estatísticas."""
    gerador = GeradorAcoes()
    
    # Simular ações
    acoes = [
        {"id": "test_1", "status": "concluida"},
        {"id": "test_2", "status": "pendente"},
        {"id": "test_3", "status": "concluida"}
    ]
    
    # Obter estatísticas
    estatisticas = gerador.obter_estatisticas(acoes)
    
    # Verificar resultado
    assert estatisticas["total"] == 3
    assert estatisticas["concluidas"] == 2
    assert estatisticas["pendentes"] == 1

def test_obter_acoes_pendentes():
    """Testa a obtenção de ações pendentes."""
    gerador = GeradorAcoes()
    
    # Simular ações
    acoes = [
        {"id": "test_1", "status": "concluida"},
        {"id": "test_2", "status": "pendente"},
        {"id": "test_3", "status": "concluida"}
    ]
    
    # Obter ações pendentes
    pendentes = gerador.obter_acoes_pendentes(acoes)
    
    # Verificar resultado
    assert len(pendentes) == 1
    assert pendentes[0]["id"] == "test_2"

def test_obter_acoes_concluidas():
    """Testa a obtenção de ações concluídas."""
    gerador = GeradorAcoes()
    
    # Simular ações
    acoes = [
        {"id": "test_1", "status": "concluida"},
        {"id": "test_2", "status": "pendente"},
        {"id": "test_3", "status": "concluida"}
    ]
    
    # Obter ações concluídas
    concluidas = gerador.obter_acoes_concluidas(acoes)
    
    # Verificar resultado
    assert len(concluidas) == 2
    assert concluidas[0]["id"] == "test_1"
    assert concluidas[1]["id"] == "test_3"

def test_obter_acoes_por_tipo():
    """Testa a obtenção de ações por tipo."""
    gerador = GeradorAcoes()
    
    # Simular ações
    acoes = [
        {"id": "test_1", "tipo": "manutencao"},
        {"id": "test_2", "tipo": "hotfix"},
        {"id": "test_3", "tipo": "manutencao"}
    ]
    
    # Obter ações por tipo
    manutencoes = gerador.obter_acoes_por_tipo(acoes, "manutencao")
    hotfixes = gerador.obter_acoes_por_tipo(acoes, "hotfix")
    
    # Verificar resultado
    assert len(manutencoes) == 2
    assert len(hotfixes) == 1
    assert manutencoes[0]["id"] == "test_1"
    assert manutencoes[1]["id"] == "test_3"
    assert hotfixes[0]["id"] == "test_2"

def test_inicializacao(gerador):
    """Testa a inicialização do gerador de ações."""
    assert gerador.mapeamento_acoes is not None
    assert len(gerador.mapeamento_acoes) > 0
    assert isinstance(gerador.historico_acoes, list)
    assert len(gerador.historico_acoes) == 0

def test_gerar_acao_cpu(gerador, diagnostico_cpu):
    """Testa a geração de ação para alta CPU."""
    acao = gerador.gerar_acao(diagnostico_cpu)
    
    assert acao is not None
    assert acao.tipo == "escalar_horizontal"
    assert acao.prioridade == 2
    assert acao.status == "pendente"
    assert acao.diagnostico == diagnostico_cpu
    assert "min_replicas" in acao.parametros
    assert "max_replicas" in acao.parametros
    assert "target_cpu" in acao.parametros

def test_gerar_acao_memoria(gerador, diagnostico_memoria):
    """Testa a geração de ação para alta memória."""
    acao = gerador.gerar_acao(diagnostico_memoria)
    
    assert acao is not None
    assert acao.tipo == "otimizar_memoria"
    assert acao.prioridade == 2
    assert acao.status == "pendente"
    assert acao.diagnostico == diagnostico_memoria
    assert "clear_cache" in acao.parametros
    assert "gc_threshold" in acao.parametros
    assert "max_memory" in acao.parametros

def test_gerar_acao_sem_anomalia(gerador):
    """Testa a geração de ação quando não há anomalia."""
    diagnostico = Diagnostico(
        timestamp=datetime.now(),
        anomalia_detectada=False,
        score_anomalia=0.1,
        padrao_detectado="normal",
        confianca=0.9,
        metricas_relevantes=[],
        recomendacoes=[]
    )
    
    acao = gerador.gerar_acao(diagnostico)
    assert acao is None

def test_gerar_acao_padrao_desconhecido(gerador):
    """Testa a geração de ação para padrão desconhecido."""
    diagnostico = Diagnostico(
        timestamp=datetime.now(),
        anomalia_detectada=True,
        score_anomalia=0.9,
        padrao_detectado="padrao_desconhecido",
        confianca=0.8,
        metricas_relevantes=[],
        recomendacoes=[]
    )
    
    acao = gerador.gerar_acao(diagnostico)
    assert acao is None

def test_obter_acoes_pendentes(gerador, diagnostico_cpu, diagnostico_memoria):
    """Testa a obtenção de ações pendentes."""
    # Gera algumas ações
    acao1 = gerador.gerar_acao(diagnostico_cpu)
    acao2 = gerador.gerar_acao(diagnostico_memoria)
    
    # Atualiza status de uma ação
    gerador.atualizar_status_acao(acao1.id, "sucesso")
    
    # Obtém ações pendentes
    acoes_pendentes = gerador.obter_acoes_pendentes()
    
    assert len(acoes_pendentes) == 1
    assert acoes_pendentes[0].id == acao2.id
    assert acoes_pendentes[0].status == "pendente"

def test_atualizar_status_acao(gerador, diagnostico_cpu):
    """Testa a atualização de status de uma ação."""
    acao = gerador.gerar_acao(diagnostico_cpu)
    
    # Atualiza status
    resultado = {"replicas": 3, "cpu_usage": 0.6}
    sucesso = gerador.atualizar_status_acao(
        acao.id,
        "sucesso",
        resultado
    )
    
    assert sucesso
    assert acao.status == "sucesso"
    assert acao.resultado == resultado

def test_atualizar_status_acao_inexistente(gerador):
    """Testa a atualização de status de uma ação inexistente."""
    sucesso = gerador.atualizar_status_acao(
        "acao_inexistente",
        "sucesso"
    )
    
    assert not sucesso

def test_obter_historico_acoes(gerador, diagnostico_cpu, diagnostico_memoria):
    """Testa a obtenção do histórico de ações com filtros."""
    # Gera algumas ações
    acao1 = gerador.gerar_acao(diagnostico_cpu)
    acao2 = gerador.gerar_acao(diagnostico_memoria)
    
    # Atualiza status
    gerador.atualizar_status_acao(acao1.id, "sucesso")
    
    # Testa filtros
    acoes_cpu = gerador.obter_historico_acoes(tipo="escalar_horizontal")
    assert len(acoes_cpu) == 1
    assert acoes_cpu[0].id == acao1.id
    
    acoes_sucesso = gerador.obter_historico_acoes(status="sucesso")
    assert len(acoes_sucesso) == 1
    assert acoes_sucesso[0].id == acao1.id

def test_obter_estatisticas_acoes(gerador, diagnostico_cpu, diagnostico_memoria):
    """Testa a obtenção de estatísticas das ações."""
    # Gera algumas ações
    acao1 = gerador.gerar_acao(diagnostico_cpu)
    acao2 = gerador.gerar_acao(diagnostico_memoria)
    
    # Atualiza status
    gerador.atualizar_status_acao(acao1.id, "sucesso")
    gerador.atualizar_status_acao(acao2.id, "falha")
    
    # Obtém estatísticas
    stats = gerador.obter_estatisticas_acoes()
    
    assert stats["total"] == 2
    assert stats["por_tipo"]["escalar_horizontal"] == 1
    assert stats["por_tipo"]["otimizar_memoria"] == 1
    assert stats["por_status"]["sucesso"] == 1
    assert stats["por_status"]["falha"] == 1
    assert stats["taxa_sucesso"] == 50.0

def test_limpar_historico(gerador, diagnostico_cpu):
    """Testa a limpeza do histórico de ações."""
    # Gera ação antiga
    acao_antiga = Acao(
        id="acao_antiga",
        tipo="escalar_horizontal",
        descricao="Teste",
        prioridade=1,
        timestamp=datetime.now() - timedelta(days=31),
        diagnostico=diagnostico_cpu,
        parametros={},
        status="sucesso"
    )
    gerador.historico_acoes.append(acao_antiga)
    
    # Gera ação recente
    acao_recente = gerador.gerar_acao(diagnostico_cpu)
    
    # Limpa histórico
    gerador.limpar_historico(dias=30)
    
    assert len(gerador.historico_acoes) == 1
    assert gerador.historico_acoes[0].id == acao_recente.id 