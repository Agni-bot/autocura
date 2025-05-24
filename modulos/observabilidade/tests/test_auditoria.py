import pytest
from datetime import datetime, timedelta
from ..src.auditoria.ethical_auditor import EthicalAuditor, EthicalDecision

@pytest.fixture
def auditor():
    """Fixture para criar instância do auditor"""
    return EthicalAuditor()

@pytest.fixture
def sample_context():
    """Fixture com contexto de exemplo"""
    return {
        "reasoning": "Análise de risco para decisão automática",
        "alternatives": ["Opção A", "Opção B"],
        "stakeholders": ["Usuários", "Sistema"],
        "sensitive_data": False,
        "data_retention": "30 dias"
    }

@pytest.fixture
def sample_impact():
    """Fixture com análise de impacto de exemplo"""
    return {
        "bias_analysis": {
            "bias_score": 0.2,
            "affected_groups": ["Grupo A"]
        },
        "risk_assessment": {
            "risk_score": 0.3,
            "mitigations": ["Backup", "Validação"]
        }
    }

def test_audit_decision(auditor, sample_context, sample_impact):
    """Testa auditoria de decisão"""
    decision = auditor.audit_decision(
        decision_type="risk_assessment",
        context=sample_context,
        impact_analysis=sample_impact
    )
    
    assert isinstance(decision, EthicalDecision)
    assert decision.decision_type == "risk_assessment"
    assert decision.ethical_score >= 0 and decision.ethical_score <= 1
    assert decision.validation_status in ["approved", "review_needed"]
    assert len(decision.recommendations) >= 0

def test_ethical_score_calculation(auditor, sample_context, sample_impact):
    """Testa cálculo do score ético"""
    decision = auditor.audit_decision(
        decision_type="test",
        context=sample_context,
        impact_analysis=sample_impact
    )
    
    # Score deve estar entre 0 e 1
    assert 0 <= decision.ethical_score <= 1
    
    # Contexto com dados sensíveis deve reduzir score
    context_with_sensitive = {**sample_context, "sensitive_data": True}
    decision_sensitive = auditor.audit_decision(
        decision_type="test",
        context=context_with_sensitive,
        impact_analysis=sample_impact
    )
    assert decision_sensitive.ethical_score < decision.ethical_score

def test_recommendations_generation(auditor):
    """Testa geração de recomendações"""
    # Caso com baixo score
    low_score_context = {
        "reasoning": "Teste",
        "alternatives": ["A"],
        "stakeholders": ["S"]
    }
    low_score_impact = {
        "bias_analysis": {"bias_score": 0.8},
        "risk_assessment": {"risk_score": 0.9}
    }
    
    decision = auditor.audit_decision(
        decision_type="test",
        context=low_score_context,
        impact_analysis=low_score_impact
    )
    
    assert len(decision.recommendations) > 0
    assert any("Revisão manual" in rec for rec in decision.recommendations)
    assert any("viés significativo" in rec for rec in decision.recommendations)
    assert any("Risco elevado" in rec for rec in decision.recommendations)

def test_decisions_history(auditor, sample_context, sample_impact):
    """Testa histórico de decisões"""
    # Adiciona algumas decisões
    for i in range(3):
        auditor.audit_decision(
            decision_type=f"test_{i}",
            context=sample_context,
            impact_analysis=sample_impact
        )
    
    # Recupera histórico completo
    history = auditor.get_decisions_history()
    assert len(history) == 3
    
    # Filtra por período
    now = datetime.now()
    start_time = (now - timedelta(minutes=5)).isoformat()
    end_time = (now + timedelta(minutes=5)).isoformat()
    
    filtered_history = auditor.get_decisions_history(start_time, end_time)
    assert len(filtered_history) == 3
    
    # Filtra período sem decisões
    future_start = (now + timedelta(hours=1)).isoformat()
    future_end = (now + timedelta(hours=2)).isoformat()
    
    empty_history = auditor.get_decisions_history(future_start, future_end)
    assert len(empty_history) == 0

def test_config_loading(auditor):
    """Testa carregamento de configuração"""
    assert auditor.ethical_threshold == 0.8
    assert "monitoring_interval" in auditor.config
    assert "alert_threshold" in auditor.config
    assert "max_decisions_history" in auditor.config

def test_history_trimming(auditor, sample_context, sample_impact):
    """Testa limpeza do histórico"""
    # Adiciona mais decisões que o limite
    max_history = auditor.config["max_decisions_history"]
    for i in range(max_history + 10):
        auditor.audit_decision(
            decision_type=f"test_{i}",
            context=sample_context,
            impact_analysis=sample_impact
        )
    
    # Verifica se histórico foi limitado
    history = auditor.get_decisions_history()
    assert len(history) == max_history 