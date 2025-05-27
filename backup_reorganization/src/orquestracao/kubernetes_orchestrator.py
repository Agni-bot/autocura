import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class KubernetesOrchestrator:
    """Módulo de orquestração Kubernetes para gerenciar deployment e escalabilidade."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o orquestrador Kubernetes.
        
        Args:
            config: Configuração do orquestrador
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Carrega configuração do Kubernetes
        try:
            config.load_kube_config()
            self.logger.info("Configuração do Kubernetes carregada")
        except Exception as e:
            self.logger.error(f"Erro ao carregar configuração do Kubernetes: {e}")
            raise
        
        # Inicializa clientes da API
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.autoscaling_v1 = client.AutoscalingV1Api()
        
        # Namespace padrão
        self.namespace = self.config.get("namespace", "default")
        
        self.logger.info("Orquestrador Kubernetes inicializado")
    
    async def criar_deployment(self, nome: str, imagem: str, replicas: int = 1, **kwargs) -> bool:
        """Cria um deployment no Kubernetes.
        
        Args:
            nome: Nome do deployment
            imagem: Imagem Docker
            replicas: Número de réplicas
            **kwargs: Argumentos adicionais
            
        Returns:
            True se o deployment foi criado com sucesso
        """
        try:
            # Configura o container
            container = client.V1Container(
                name=nome,
                image=imagem,
                ports=[client.V1ContainerPort(container_port=kwargs.get("port", 80))],
                resources=client.V1ResourceRequirements(
                    requests=kwargs.get("requests", {"cpu": "100m", "memory": "128Mi"}),
                    limits=kwargs.get("limits", {"cpu": "500m", "memory": "512Mi"})
                )
            )
            
            # Configura o template
            template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": nome}),
                spec=client.V1PodSpec(containers=[container])
            )
            
            # Configura o deployment
            deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(name=nome),
                spec=client.V1DeploymentSpec(
                    replicas=replicas,
                    selector=client.V1LabelSelector(match_labels={"app": nome}),
                    template=template
                )
            )
            
            # Cria o deployment
            self.apps_v1.create_namespaced_deployment(
                namespace=self.namespace,
                body=deployment
            )
            
            self.logger.info(f"Deployment {nome} criado com sucesso")
            return True
            
        except ApiException as e:
            self.logger.error(f"Erro ao criar deployment {nome}: {e}")
            return False
    
    async def atualizar_deployment(self, nome: str, **kwargs) -> bool:
        """Atualiza um deployment existente.
        
        Args:
            nome: Nome do deployment
            **kwargs: Argumentos de atualização
            
        Returns:
            True se o deployment foi atualizado com sucesso
        """
        try:
            # Obtém o deployment atual
            deployment = self.apps_v1.read_namespaced_deployment(
                name=nome,
                namespace=self.namespace
            )
            
            # Atualiza os campos especificados
            if "replicas" in kwargs:
                deployment.spec.replicas = kwargs["replicas"]
            
            if "image" in kwargs:
                deployment.spec.template.spec.containers[0].image = kwargs["image"]
            
            if "resources" in kwargs:
                deployment.spec.template.spec.containers[0].resources = client.V1ResourceRequirements(
                    requests=kwargs["resources"].get("requests", {}),
                    limits=kwargs["resources"].get("limits", {})
                )
            
            # Aplica a atualização
            self.apps_v1.patch_namespaced_deployment(
                name=nome,
                namespace=self.namespace,
                body=deployment
            )
            
            self.logger.info(f"Deployment {nome} atualizado com sucesso")
            return True
            
        except ApiException as e:
            self.logger.error(f"Erro ao atualizar deployment {nome}: {e}")
            return False
    
    async def deletar_deployment(self, nome: str) -> bool:
        """Deleta um deployment.
        
        Args:
            nome: Nome do deployment
            
        Returns:
            True se o deployment foi deletado com sucesso
        """
        try:
            self.apps_v1.delete_namespaced_deployment(
                name=nome,
                namespace=self.namespace
            )
            
            self.logger.info(f"Deployment {nome} deletado com sucesso")
            return True
            
        except ApiException as e:
            self.logger.error(f"Erro ao deletar deployment {nome}: {e}")
            return False
    
    async def obter_status_deployment(self, nome: str) -> Dict[str, Any]:
        """Obtém o status de um deployment.
        
        Args:
            nome: Nome do deployment
            
        Returns:
            Dicionário com status do deployment
        """
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=nome,
                namespace=self.namespace
            )
            
            return {
                "nome": deployment.metadata.name,
                "replicas": deployment.spec.replicas,
                "replicas_disponiveis": deployment.status.available_replicas,
                "replicas_atualizadas": deployment.status.updated_replicas,
                "condicao": deployment.status.conditions[0].type if deployment.status.conditions else None,
                "mensagem": deployment.status.conditions[0].message if deployment.status.conditions else None
            }
            
        except ApiException as e:
            self.logger.error(f"Erro ao obter status do deployment {nome}: {e}")
            return {}
    
    async def configurar_autoscaling(self, nome: str, min_replicas: int, max_replicas: int, target_cpu: int) -> bool:
        """Configura autoscaling para um deployment.
        
        Args:
            nome: Nome do deployment
            min_replicas: Número mínimo de réplicas
            max_replicas: Número máximo de réplicas
            target_cpu: Percentual de CPU alvo
            
        Returns:
            True se o autoscaling foi configurado com sucesso
        """
        try:
            hpa = client.V1HorizontalPodAutoscaler(
                metadata=client.V1ObjectMeta(name=f"{nome}-hpa"),
                spec=client.V1HorizontalPodAutoscalerSpec(
                    scale_target_ref=client.V1CrossVersionObjectReference(
                        api_version="apps/v1",
                        kind="Deployment",
                        name=nome
                    ),
                    min_replicas=min_replicas,
                    max_replicas=max_replicas,
                    target_cpu_utilization_percentage=target_cpu
                )
            )
            
            self.autoscaling_v1.create_namespaced_horizontal_pod_autoscaler(
                namespace=self.namespace,
                body=hpa
            )
            
            self.logger.info(f"Autoscaling configurado para deployment {nome}")
            return True
            
        except ApiException as e:
            self.logger.error(f"Erro ao configurar autoscaling para deployment {nome}: {e}")
            return False
    
    async def obter_metricas_deployment(self, nome: str) -> Dict[str, Any]:
        """Obtém métricas de um deployment.
        
        Args:
            nome: Nome do deployment
            
        Returns:
            Dicionário com métricas do deployment
        """
        try:
            # Obtém pods do deployment
            pods = self.v1.list_namespaced_pod(
                namespace=self.namespace,
                label_selector=f"app={nome}"
            )
            
            metricas = {
                "pods": len(pods.items),
                "pods_ready": 0,
                "cpu_usage": 0,
                "memory_usage": 0
            }
            
            for pod in pods.items:
                if pod.status.phase == "Running":
                    metricas["pods_ready"] += 1
                
                # Obtém métricas do pod
                pod_metrics = self.v1.read_namespaced_pod_metrics(
                    name=pod.metadata.name,
                    namespace=self.namespace
                )
                
                for container in pod_metrics.containers:
                    metricas["cpu_usage"] += float(container.usage["cpu"].replace("m", "")) / 1000
                    metricas["memory_usage"] += float(container.usage["memory"].replace("Mi", ""))
            
            return metricas
            
        except ApiException as e:
            self.logger.error(f"Erro ao obter métricas do deployment {nome}: {e}")
            return {}
    
    async def verificar_saude_deployment(self, nome: str) -> Dict[str, Any]:
        """Verifica a saúde de um deployment.
        
        Args:
            nome: Nome do deployment
            
        Returns:
            Dicionário com status de saúde
        """
        try:
            status = await self.obter_status_deployment(nome)
            metricas = await self.obter_metricas_deployment(nome)
            
            saude = {
                "status": "ok",
                "mensagem": "Deployment saudável",
                "detalhes": {
                    "status": status,
                    "metricas": metricas
                }
            }
            
            # Verifica condições de saúde
            if status.get("replicas_disponiveis", 0) < status.get("replicas", 0):
                saude["status"] = "warning"
                saude["mensagem"] = "Nem todas as réplicas estão disponíveis"
            
            if metricas.get("cpu_usage", 0) > 80:
                saude["status"] = "warning"
                saude["mensagem"] = "Alto uso de CPU"
            
            if metricas.get("memory_usage", 0) > 80:
                saude["status"] = "warning"
                saude["mensagem"] = "Alto uso de memória"
            
            return saude
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar saúde do deployment {nome}: {e}")
            return {
                "status": "error",
                "mensagem": str(e)
            } 