"""
Módulo de Orquestração Kubernetes

Este módulo é responsável por gerenciar a infraestrutura e deployments do sistema
usando Kubernetes, implementando auto-scaling, auto-healing, distribuição de carga
e monitoramento avançado.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException

@dataclass
class EstadoCluster:
    """Representa o estado atual do cluster Kubernetes"""
    timestamp: datetime
    nodes: List[Dict[str, Any]]
    pods: List[Dict[str, Any]]
    deployments: List[Dict[str, Any]]
    services: List[Dict[str, Any]]
    metricas: Dict[str, float]

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
            config.load_incluster_config()  # Dentro do cluster
        except config.ConfigException:
            config.load_kube_config()  # Fora do cluster
            
        # Inicializa clientes da API
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.autoscaling_v1 = client.AutoscalingV1Api()
        
        # Namespace padrão
        self.namespace = self.config.get("namespace", "autocura")
        
        self.logger.info("Orquestrador Kubernetes inicializado")
        
    async def criar_namespace(self) -> bool:
        """Cria o namespace do sistema se não existir"""
        try:
            self.v1.create_namespace(
                client.V1Namespace(
                    metadata=client.V1ObjectMeta(name=self.namespace)
                )
            )
            self.logger.info(f"Namespace {self.namespace} criado")
            return True
        except ApiException as e:
            if e.status == 409:  # Já existe
                self.logger.info(f"Namespace {self.namespace} já existe")
                return True
            else:
                self.logger.error(f"Erro ao criar namespace: {e}")
                return False

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

    async def aplicar_manifesto(self, manifesto: Dict[str, Any]) -> bool:
        """Aplica um manifesto Kubernetes"""
        try:
            if manifesto["kind"] == "Deployment":
                self.apps_v1.create_namespaced_deployment(
                    namespace=self.namespace,
                    body=manifesto
                )
            elif manifesto["kind"] == "Service":
                self.v1.create_namespaced_service(
                    namespace=self.namespace,
                    body=manifesto
                )
            elif manifesto["kind"] == "HorizontalPodAutoscaler":
                self.autoscaling_v1.create_namespaced_horizontal_pod_autoscaler(
                    namespace=self.namespace,
                    body=manifesto
                )
            else:
                raise ValueError(f"Tipo de manifesto não suportado: {manifesto['kind']}")
                
            self.logger.info(f"Manifesto {manifesto['kind']} aplicado com sucesso")
            return True
        except ApiException as e:
            self.logger.error(f"Erro ao aplicar manifesto: {str(e)}")
            return False

    async def obter_estado_cluster(self) -> EstadoCluster:
        """Obtém o estado atual do cluster"""
        try:
            # Obtém nós
            nodes = self.v1.list_node()
            nodes_info = [
                {
                    "nome": node.metadata.name,
                    "status": node.status.conditions[-1].type,
                    "capacidade": {
                        "cpu": node.status.capacity["cpu"],
                        "memory": node.status.capacity["memory"]
                    }
                }
                for node in nodes.items
            ]
            
            # Obtém pods
            pods = self.v1.list_namespaced_pod(namespace=self.namespace)
            pods_info = [
                {
                    "nome": pod.metadata.name,
                    "status": pod.status.phase,
                    "containers": [
                        {
                            "nome": container.name,
                            "imagem": container.image,
                            "status": container.state
                        }
                        for container in pod.spec.containers
                    ]
                }
                for pod in pods.items
            ]
            
            # Obtém deployments
            deployments = self.apps_v1.list_namespaced_deployment(namespace=self.namespace)
            deployments_info = [
                {
                    "nome": dep.metadata.name,
                    "replicas": dep.spec.replicas,
                    "replicas_disponiveis": dep.status.available_replicas
                }
                for dep in deployments.items
            ]
            
            # Obtém services
            services = self.v1.list_namespaced_service(namespace=self.namespace)
            services_info = [
                {
                    "nome": svc.metadata.name,
                    "tipo": svc.spec.type,
                    "portas": [
                        {
                            "porta": port.port,
                            "alvo": port.target_port
                        }
                        for port in svc.spec.ports
                    ]
                }
                for svc in services.items
            ]
            
            # Calcula métricas
            metricas = await self._calcular_metricas_cluster(
                nodes_info,
                pods_info,
                deployments_info
            )
            
            return EstadoCluster(
                timestamp=datetime.now(),
                nodes=nodes_info,
                pods=pods_info,
                deployments=deployments_info,
                services=services_info,
                metricas=metricas
            )
            
        except ApiException as e:
            self.logger.error(f"Erro ao obter estado do cluster: {str(e)}")
            raise

    async def _calcular_metricas_cluster(self,
                                       nodes: List[Dict[str, Any]],
                                       pods: List[Dict[str, Any]],
                                       deployments: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcula métricas do cluster"""
        try:
            # Obtém métricas de uso de recursos
            metricas = {
                "cpu_utilizacao": 0.0,
                "memoria_utilizacao": 0.0,
                "disponibilidade": 0.0,
                "pods_ativos": len(pods),
                "deployments_ativos": len(deployments)
            }
            
            # Calcula disponibilidade
            pods_rodando = sum(1 for pod in pods if pod["status"] == "Running")
            if pods:
                metricas["disponibilidade"] = pods_rodando / len(pods)
            
            # Calcula uso de recursos
            for node in nodes:
                # Implementar lógica de cálculo de recursos
                pass
                
            return metricas
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular métricas: {e}")
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

    async def verificar_saude_deployment(self, nome: str) -> Dict[str, Any]:
        """Verifica a saúde de um deployment.
        
        Args:
            nome: Nome do deployment
            
        Returns:
            Dicionário com status de saúde
        """
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=nome,
                namespace=self.namespace
            )
            
            pods = self.v1.list_namespaced_pod(
                namespace=self.namespace,
                label_selector=f"app={nome}"
            )
            
            saude = {
                "nome": nome,
                "status": "saudavel",
                "replicas": deployment.spec.replicas,
                "replicas_disponiveis": deployment.status.available_replicas,
                "pods_rodando": 0,
                "pods_falhando": 0,
                "ultima_atualizacao": deployment.status.conditions[0].last_update_time if deployment.status.conditions else None
            }
            
            for pod in pods.items:
                if pod.status.phase == "Running":
                    saude["pods_rodando"] += 1
                else:
                    saude["pods_falhando"] += 1
                    
            if saude["pods_falhando"] > 0:
                saude["status"] = "degradado"
            if saude["pods_rodando"] == 0:
                saude["status"] = "falho"
                
            return saude
            
        except ApiException as e:
            self.logger.error(f"Erro ao verificar saúde do deployment {nome}: {e}")
            return {"nome": nome, "status": "erro", "mensagem": str(e)}

    async def reiniciar_pod(self, nome: str) -> bool:
        """Reinicia um pod específico"""
        try:
            self.v1.delete_namespaced_pod(
                name=nome,
                namespace=self.namespace
            )
            self.logger.info(f"Pod {nome} reiniciado")
            return True
        except ApiException as e:
            self.logger.error(f"Erro ao reiniciar pod: {str(e)}")
            return False 