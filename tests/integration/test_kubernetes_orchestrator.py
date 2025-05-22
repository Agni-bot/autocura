import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch
from kubernetes.client.rest import ApiException
from src.orchestration.kubernetes_orchestrator import KubernetesOrchestrator

@pytest.fixture
def config():
    """Fixture que fornece configuração para os testes."""
    return {
        "namespace": "test"
    }

@pytest.fixture
def orchestrator(config):
    """Fixture que fornece uma instância do orquestrador Kubernetes para os testes."""
    with patch("kubernetes.config.load_kube_config"):
        return KubernetesOrchestrator(config)

@pytest.mark.asyncio
async def test_inicializacao(orchestrator):
    """Testa a inicialização do orquestrador."""
    assert orchestrator.config is not None
    assert orchestrator.namespace == "test"
    assert orchestrator.v1 is not None
    assert orchestrator.apps_v1 is not None
    assert orchestrator.autoscaling_v1 is not None

@pytest.mark.asyncio
async def test_criar_deployment(orchestrator):
    """Testa a criação de um deployment."""
    nome = "test-app"
    imagem = "test-image:latest"
    
    # Mock da resposta da API
    with patch.object(orchestrator.apps_v1, "create_namespaced_deployment") as mock_create:
        mock_create.return_value = Mock()
        
        sucesso = await orchestrator.criar_deployment(nome, imagem)
        assert sucesso
        
        # Verifica se o deployment foi criado com os parâmetros corretos
        args, kwargs = mock_create.call_args
        assert kwargs["namespace"] == "test"
        assert kwargs["body"].metadata.name == nome
        assert kwargs["body"].spec.template.spec.containers[0].image == imagem

@pytest.mark.asyncio
async def test_criar_deployment_falha(orchestrator):
    """Testa falha na criação de um deployment."""
    nome = "test-app"
    imagem = "test-image:latest"
    
    # Mock da resposta da API com erro
    with patch.object(orchestrator.apps_v1, "create_namespaced_deployment") as mock_create:
        mock_create.side_effect = ApiException(status=500)
        
        sucesso = await orchestrator.criar_deployment(nome, imagem)
        assert not sucesso

@pytest.mark.asyncio
async def test_atualizar_deployment(orchestrator):
    """Testa a atualização de um deployment."""
    nome = "test-app"
    
    # Mock do deployment existente
    deployment = Mock()
    deployment.spec.replicas = 1
    deployment.spec.template.spec.containers = [Mock()]
    
    with patch.object(orchestrator.apps_v1, "read_namespaced_deployment", return_value=deployment), \
         patch.object(orchestrator.apps_v1, "patch_namespaced_deployment") as mock_patch:
        
        sucesso = await orchestrator.atualizar_deployment(nome, replicas=3)
        assert sucesso
        
        # Verifica se o deployment foi atualizado
        args, kwargs = mock_patch.call_args
        assert kwargs["namespace"] == "test"
        assert kwargs["body"].spec.replicas == 3

@pytest.mark.asyncio
async def test_deletar_deployment(orchestrator):
    """Testa a deleção de um deployment."""
    nome = "test-app"
    
    with patch.object(orchestrator.apps_v1, "delete_namespaced_deployment") as mock_delete:
        sucesso = await orchestrator.deletar_deployment(nome)
        assert sucesso
        
        # Verifica se o deployment foi deletado
        args, kwargs = mock_delete.call_args
        assert kwargs["namespace"] == "test"
        assert kwargs["name"] == nome

@pytest.mark.asyncio
async def test_obter_status_deployment(orchestrator):
    """Testa a obtenção do status de um deployment."""
    nome = "test-app"
    
    # Mock do deployment
    deployment = Mock()
    deployment.metadata.name = nome
    deployment.spec.replicas = 3
    deployment.status.available_replicas = 3
    deployment.status.updated_replicas = 3
    deployment.status.conditions = [Mock(type="Available", message="Deployment is available")]
    
    with patch.object(orchestrator.apps_v1, "read_namespaced_deployment", return_value=deployment):
        status = await orchestrator.obter_status_deployment(nome)
        
        assert status["nome"] == nome
        assert status["replicas"] == 3
        assert status["replicas_disponiveis"] == 3
        assert status["replicas_atualizadas"] == 3
        assert status["condicao"] == "Available"
        assert status["mensagem"] == "Deployment is available"

@pytest.mark.asyncio
async def test_configurar_autoscaling(orchestrator):
    """Testa a configuração de autoscaling."""
    nome = "test-app"
    min_replicas = 2
    max_replicas = 5
    target_cpu = 80
    
    with patch.object(orchestrator.autoscaling_v1, "create_namespaced_horizontal_pod_autoscaler") as mock_create:
        sucesso = await orchestrator.configurar_autoscaling(nome, min_replicas, max_replicas, target_cpu)
        assert sucesso
        
        # Verifica se o HPA foi criado
        args, kwargs = mock_create.call_args
        assert kwargs["namespace"] == "test"
        assert kwargs["body"].metadata.name == f"{nome}-hpa"
        assert kwargs["body"].spec.min_replicas == min_replicas
        assert kwargs["body"].spec.max_replicas == max_replicas
        assert kwargs["body"].spec.target_cpu_utilization_percentage == target_cpu

@pytest.mark.asyncio
async def test_obter_metricas_deployment(orchestrator):
    """Testa a obtenção de métricas de um deployment."""
    nome = "test-app"
    
    # Mock dos pods
    pod1 = Mock()
    pod1.status.phase = "Running"
    pod1.metadata.name = "pod1"
    
    pod2 = Mock()
    pod2.status.phase = "Pending"
    pod2.metadata.name = "pod2"
    
    pods = Mock()
    pods.items = [pod1, pod2]
    
    # Mock das métricas dos pods
    pod_metrics = Mock()
    pod_metrics.containers = [
        Mock(usage={"cpu": "500m", "memory": "256Mi"})
    ]
    
    with patch.object(orchestrator.v1, "list_namespaced_pod", return_value=pods), \
         patch.object(orchestrator.v1, "read_namespaced_pod_metrics", return_value=pod_metrics):
        
        metricas = await orchestrator.obter_metricas_deployment(nome)
        
        assert metricas["pods"] == 2
        assert metricas["pods_ready"] == 1
        assert metricas["cpu_usage"] == 0.5
        assert metricas["memory_usage"] == 256

@pytest.mark.asyncio
async def test_verificar_saude_deployment(orchestrator):
    """Testa a verificação de saúde de um deployment."""
    nome = "test-app"
    
    # Mock do status e métricas
    status = {
        "replicas": 3,
        "replicas_disponiveis": 3
    }
    
    metricas = {
        "cpu_usage": 50,
        "memory_usage": 50
    }
    
    with patch.object(orchestrator, "obter_status_deployment", return_value=status), \
         patch.object(orchestrator, "obter_metricas_deployment", return_value=metricas):
        
        saude = await orchestrator.verificar_saude_deployment(nome)
        
        assert saude["status"] == "ok"
        assert saude["mensagem"] == "Deployment saudável"
        assert "detalhes" in saude

@pytest.mark.asyncio
async def test_verificar_saude_deployment_warning(orchestrator):
    """Testa a verificação de saúde de um deployment com warning."""
    nome = "test-app"
    
    # Mock do status e métricas com valores críticos
    status = {
        "replicas": 3,
        "replicas_disponiveis": 2
    }
    
    metricas = {
        "cpu_usage": 90,
        "memory_usage": 90
    }
    
    with patch.object(orchestrator, "obter_status_deployment", return_value=status), \
         patch.object(orchestrator, "obter_metricas_deployment", return_value=metricas):
        
        saude = await orchestrator.verificar_saude_deployment(nome)
        
        assert saude["status"] == "warning"
        assert "warning" in saude["mensagem"].lower() 