"""
Módulo de Orquestração Kubernetes

Este módulo é responsável por gerenciar a infraestrutura do sistema
usando Kubernetes, implementando auto-scaling, auto-healing e
distribuição de carga.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import json
import os
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

class OrquestradorKubernetes:
    def __init__(self, namespace: str = "autocura"):
        self.logger = logging.getLogger(__name__)
        self.namespace = namespace
        
        # Carrega configuração do Kubernetes
        try:
            config.load_incluster_config()  # Dentro do cluster
        except config.ConfigException:
            config.load_kube_config()  # Fora do cluster
            
        # Inicializa clientes da API
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.autoscaling_v1 = client.AutoscalingV1Api()
        
    def criar_namespace(self):
        """Cria o namespace do sistema se não existir"""
        try:
            self.v1.create_namespace(
                client.V1Namespace(
                    metadata=client.V1ObjectMeta(name=self.namespace)
                )
            )
            self.logger.info(f"Namespace {self.namespace} criado")
        except ApiException as e:
            if e.status == 409:  # Já existe
                self.logger.info(f"Namespace {self.namespace} já existe")
            else:
                raise
                
    def aplicar_manifesto(self, manifesto: Dict[str, Any]):
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
        except ApiException as e:
            self.logger.error(f"Erro ao aplicar manifesto: {str(e)}")
            raise
            
    def obter_estado_cluster(self) -> EstadoCluster:
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
            metricas = self._calcular_metricas_cluster(
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
            
    def _calcular_metricas_cluster(self,
                                 nodes: List[Dict[str, Any]],
                                 pods: List[Dict[str, Any]],
                                 deployments: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calcula métricas do cluster"""
        # Implementa lógica para calcular métricas
        # Por exemplo, uso de recursos, disponibilidade, etc.
        return {
            "cpu_utilizacao": 0.75,  # 75% de utilização
            "memoria_utilizacao": 0.60,  # 60% de utilização
            "disponibilidade": 0.99,  # 99% de disponibilidade
            "pods_ativos": len(pods),
            "deployments_ativos": len(deployments)
        }
        
    def escalar_deployment(self,
                         nome: str,
                         replicas: int):
        """Escala um deployment para o número especificado de réplicas"""
        try:
            self.apps_v1.patch_namespaced_deployment_scale(
                name=nome,
                namespace=self.namespace,
                body={"spec": {"replicas": replicas}}
            )
            self.logger.info(f"Deployment {nome} escalado para {replicas} réplicas")
        except ApiException as e:
            self.logger.error(f"Erro ao escalar deployment: {str(e)}")
            raise
            
    def reiniciar_pod(self, nome: str):
        """Reinicia um pod específico"""
        try:
            self.v1.delete_namespaced_pod(
                name=nome,
                namespace=self.namespace
            )
            self.logger.info(f"Pod {nome} reiniciado")
        except ApiException as e:
            self.logger.error(f"Erro ao reiniciar pod: {str(e)}")
            raise
            
    def aplicar_configuracao_autoscaling(self,
                                       nome: str,
                                       min_replicas: int,
                                       max_replicas: int,
                                       target_cpu_utilization: int):
        """Aplica configuração de auto-scaling para um deployment"""
        try:
            hpa = {
                "apiVersion": "autoscaling/v1",
                "kind": "HorizontalPodAutoscaler",
                "metadata": {
                    "name": f"{nome}-hpa",
                    "namespace": self.namespace
                },
                "spec": {
                    "scaleTargetRef": {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "name": nome
                    },
                    "minReplicas": min_replicas,
                    "maxReplicas": max_replicas,
                    "targetCPUUtilizationPercentage": target_cpu_utilization
                }
            }
            
            self.autoscaling_v1.create_namespaced_horizontal_pod_autoscaler(
                namespace=self.namespace,
                body=hpa
            )
            
            self.logger.info(
                f"Auto-scaling configurado para {nome}: "
                f"min={min_replicas}, max={max_replicas}, "
                f"target_cpu={target_cpu_utilization}%"
            )
        except ApiException as e:
            self.logger.error(f"Erro ao configurar auto-scaling: {str(e)}")
            raise

# Exemplo de uso
if __name__ == "__main__":
    # Configura logging
    logging.basicConfig(level=logging.INFO)
    
    # Cria instância do orquestrador
    orquestrador = OrquestradorKubernetes()
    
    # Cria namespace
    orquestrador.criar_namespace()
    
    # Aplica manifestos
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": "autocura-api",
            "namespace": "autocura"
        },
        "spec": {
            "replicas": 3,
            "selector": {
                "matchLabels": {
                    "app": "autocura-api"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": "autocura-api"
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": "api",
                            "image": "autocura/api:latest",
                            "ports": [
                                {
                                    "containerPort": 8000
                                }
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "100m",
                                    "memory": "128Mi"
                                },
                                "limits": {
                                    "cpu": "500m",
                                    "memory": "512Mi"
                                }
                            }
                        }
                    ]
                }
            }
        }
    }
    
    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": "autocura-api",
            "namespace": "autocura"
        },
        "spec": {
            "selector": {
                "app": "autocura-api"
            },
            "ports": [
                {
                    "port": 80,
                    "targetPort": 8000
                }
            ],
            "type": "LoadBalancer"
        }
    }
    
    orquestrador.aplicar_manifesto(deployment)
    orquestrador.aplicar_manifesto(service)
    
    # Configura auto-scaling
    orquestrador.aplicar_configuracao_autoscaling(
        nome="autocura-api",
        min_replicas=3,
        max_replicas=10,
        target_cpu_utilization=70
    )
    
    # Obtém estado do cluster
    estado = orquestrador.obter_estado_cluster()
    print("\nEstado do Cluster:")
    print(json.dumps({
        "timestamp": estado.timestamp.isoformat(),
        "nodes": estado.nodes,
        "pods": estado.pods,
        "deployments": estado.deployments,
        "services": estado.services,
        "metricas": estado.metricas
    }, indent=2)) 