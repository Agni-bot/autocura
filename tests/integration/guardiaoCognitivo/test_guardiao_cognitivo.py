import pytest
import json
import time
from unittest.mock import patch, MagicMock

# Importa a app Flask e a instância do GuardiaoCognitivo do módulo principal
from src.guardiao.guardiao_cognitivo import app, guardiao_singleton, DiagnosticoInfo, PlanoAcaoInfo, CONFIG_GUARDIAN

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Garante que o guardião comece parado para os testes
        guardiao_singleton.parar()
        yield client
        # Limpa o estado do guardião após os testes, se necessário
        guardiao_singleton.parar()
        guardiao_singleton.historico_diagnosticos.clear()
        guardiao_singleton.historico_planos_acao.clear()

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("DIAGNOSTICO_SERVICE_URL", "http://mock-diagnostico:8080/api")
    monkeypatch.setenv("ACAO_SERVICE_URL", "http://mock-acao:8080/api")
    monkeypatch.setenv("MONITORAMENTO_SERVICE_URL", "http://mock-monitoramento:8080/api")
    monkeypatch.setenv("ALERT_WEBHOOK_URL", "http://mock-webhook.com/alert")
    monkeypatch.setenv("EMERGENCY_TARGET_NAMESPACE", "test-autocura")
    monkeypatch.setenv("EMERGENCY_TARGET_DEPLOYMENTS", "mock-diagnostico,mock-acao")
    # Força recarga da configuração no singleton para usar os mocks
    CONFIG_GUARDIAN.update({
        "api_diagnostico_url": "http://mock-diagnostico:8080/api",
        "api_gerador_acoes_url": "http://mock-acao:8080/api",
        "api_monitoramento_url": "http://mock-monitoramento:8080/api",
        "alert_webhook_url": "http://mock-webhook.com/alert",
        "emergency_target_namespace": "test-autocura",
        "emergency_target_deployments": "mock-diagnostico,mock-acao",
        "intervalo_verificacao_segundos": 1 # Intervalo curto para testes
    })
    # Reinicializa o cliente K8s com mocks se necessário, ou mock diretamente
    guardiao_singleton._inicializar_kube_client = MagicMock() # Evita chamadas reais ao K8s
    guardiao_singleton.kube_api_client = MagicMock()

# --- Testes da API --- 

def test_health_check_parado(client):
    response = client.get("/health")
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data["status"] == "healthy" # Mesmo parado, o serviço Flask está healthy
    assert data["guardian_running"] is False

def test_start_stop_guardian(client):
    # Testa iniciar
    response_start = client.post("/api/guardian/start")
    assert response_start.status_code == 200
    assert json.loads(response_start.data)["message"] == "Guardião Cognitivo iniciando..."
    time.sleep(0.1) # Dá um tempo para a thread iniciar
    assert guardiao_singleton.rodando is True
    assert guardiao_singleton.thread_monitoramento is not None
    assert guardiao_singleton.thread_monitoramento.is_alive() is True

    # Testa status rodando
    response_status_running = client.get("/api/guardian/status")
    data_running = json.loads(response_status_running.data)
    assert response_status_running.status_code == 200
    assert data_running["running"] is True

    # Testa health check rodando
    response_health_running = client.get("/health")
    data_health_running = json.loads(response_health_running.data)
    assert response_health_running.status_code == 200
    assert data_health_running["status"] == "healthy"
    assert data_health_running["guardian_running"] is True
    assert data_health_running["monitoring_thread_active"] is True

    # Testa parar
    response_stop = client.post("/api/guardian/stop")
    assert response_stop.status_code == 200
    assert json.loads(response_stop.data)["message"] == "Guardião Cognitivo parando..."
    time.sleep(0.1) # Dá um tempo para a thread parar
    assert guardiao_singleton.rodando is False
    # A thread pode não ter finalizado completamente, mas o rodando deve ser False

# --- Testes de Eventos --- 

def test_new_diagnosis_event(client):
    diag_data = {
        "id": "diag123",
        "timestamp": time.time(),
        "anomalias_detectadas": [("anomalia_A", 0.8)],
        "confianca_geral": 0.85
    }
    response = client.post("/event/new_diagnosis", json=diag_data)
    assert response.status_code == 201
    assert json.loads(response.data)["message"] == "Diagnóstico recebido"
    assert len(guardiao_singleton.historico_diagnosticos) == 1
    assert guardiao_singleton.historico_diagnosticos[0].id == "diag123"

def test_new_action_plan_event(client):
    plan_data = {
        "id": "plan789",
        "diagnostico_id": "diag123",
        "acoes_ids": ["acao_X"],
        "timestamp_geracao": time.time(),
        "status_execucao": "criado"
    }
    response = client.post("/event/new_action_plan", json=plan_data)
    assert response.status_code == 201
    assert json.loads(response.data)["message"] == "Plano de ação recebido"
    assert len(guardiao_singleton.historico_planos_acao) == 1
    assert guardiao_singleton.historico_planos_acao[0].id == "plan789"

# --- Testes da Lógica de Verificação (com mocks) ---

@patch("guardiao_cognitivo.GuardiaoCognitivo._obter_diagnosticos_recentes")
@patch("guardiao_cognitivo.GuardiaoCognitivo._acionar_protocolo_emergencia")
def test_verificar_coerencia_diagnosticos_aciona_emergencia(mock_acionar_emergencia, mock_obter_diagnosticos, client):
    # Configura o mock para retornar diagnósticos de baixa confiança
    diagnosticos_mock = [
        DiagnosticoInfo(id=f"d{i}", timestamp=time.time(), anomalias_detectadas=[], confianca_geral=0.1) 
        for i in range(10)
    ]
    mock_obter_diagnosticos.return_value = diagnosticos_mock
    
    guardiao_singleton.verificar_coerencia_diagnosticos()
    
    mock_obter_diagnosticos.assert_called_once()
    mock_acionar_emergencia.assert_called_once_with(
        "Incoerência de Diagnósticos: Baixa Confiança Generalizada",
        {"total_diagnosticos": 10, "baixa_confianca_count": 10}
    )

@patch("guardiao_cognitivo.GuardiaoCognitivo._obter_planos_acao_concluidos_recentes")
@patch("guardiao_cognitivo.GuardiaoCognitivo._acionar_protocolo_emergencia")
def test_verificar_eficacia_acoes_aciona_emergencia(mock_acionar_emergencia, mock_obter_planos, client):
    planos_mock = [
        PlanoAcaoInfo(id=f"p{i}", diagnostico_id="d1", acoes_ids=[], timestamp_geracao=time.time(), 
                      status_execucao="concluido", resultado_eficacia={"acao1": 0.1}) 
        for i in range(5)
    ]
    mock_obter_planos.return_value = planos_mock
    
    guardiao_singleton.verificar_eficacia_acoes()
    
    mock_obter_planos.assert_called_once()
    mock_acionar_emergencia.assert_called_once_with(
        "Baixa Eficácia de Ações Corretivas",
        {"media_eficacia_recente": pytest.approx(0.1), "num_planos_analisados": 5}
    )

@patch("requests.post") # Mock para o webhook de alerta
@patch("kubernetes.client.AppsV1Api") # Mock para o cliente K8s
def test_acionar_protocolo_emergencia_com_escalonamento(mock_k8s_apps_v1_api, mock_requests_post, client):
    # Simula que o cliente K8s foi inicializado
    mock_api_instance = MagicMock()
    guardiao_singleton.kube_api_client = mock_api_instance
    
    tipo_emergencia = "TESTE_EMERGENCIA"
    detalhes = {"info": "detalhe_teste"}
    
    guardiao_singleton._acionar_protocolo_emergencia(tipo_emergencia, detalhes)
    
    # Verifica se o alerta foi enviado
    mock_requests_post.assert_called_once()
    args, kwargs = mock_requests_post.call_args
    assert CONFIG_GUARDIAN["alert_webhook_url"] in args[0]
    assert tipo_emergencia in kwargs["json"]["text"]
    
    # Verifica se o escalonamento foi tentado para os deployments configurados
    expected_deployments = [d.strip() for d in CONFIG_GUARDIAN["emergency_target_deployments"].split(",")]
    assert mock_api_instance.patch_namespaced_deployment_scale.call_count == len(expected_deployments)
    
    for call_args in mock_api_instance.patch_namespaced_deployment_scale.call_args_list:
        assert call_args.kwargs["namespace"] == CONFIG_GUARDIAN["emergency_target_namespace"]
        assert call_args.kwargs["body"] == {"spec": {"replicas": 0}}
        assert call_args.kwargs["name"] in expected_deployments

# Adicionar mais testes para cobrir outros cenários, como:
# - Não acionar emergência se as condições não forem atendidas.
# - Tratamento de erros nas chamadas de API (mockando requests.get para levantar exceções).
# - Lógica de estabilidade de decisões.
# - Casos de borda e dados inválidos nos endpoints de evento.

