# Deploy do Sistema AutoCura no Kubernetes

Este documento descreve o processo de deploy do sistema AutoCura no Kubernetes.

## 🚀 Módulos Disponíveis

1. **Monitoramento** (`autocura/monitoramento:latest`)
   - Sistema de monitoramento e métricas
   - Integração com Prometheus, Grafana e Loki
   - Métricas de sistema via Node Exporter e cAdvisor

2. **Observador** (`autocura/observador:latest`)
   - Sistema de observabilidade e logs
   - Integração com Elasticsearch

3. **Validador** (`autocura/validador:latest`)
   - Sistema de validação ética
   - Integração com Redis

4. **Guardião** (`autocura/guardiao:latest`)
   - Sistema de proteção e segurança
   - Integração com Redis

## 📋 Pré-requisitos

- Kubernetes 1.20+
- kubectl configurado
- Helm 3.0+
- 4GB RAM disponível por node
- 10GB espaço em disco por node

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/autocura.git
cd autocura
```

2. Aplique os manifests do Kubernetes:
```bash
kubectl apply -f src/monitoramento/k8s/prometheus.yaml
```

## 🛠️ Configuração

Os módulos são configurados através de ConfigMaps e Secrets no Kubernetes:

- `prometheus-config`: Configuração do Prometheus
- `alertmanager-config`: Configuração do Alertmanager
- `grafana-datasources`: Configuração das fontes de dados do Grafana

## 📊 Monitoramento

- Prometheus: http://localhost:9090 (via port-forward)
- Grafana: http://localhost:3000 (via port-forward)
- Loki: http://localhost:3100 (via port-forward)
- Node Exporter: http://localhost:9100 (via port-forward)
- cAdvisor: http://localhost:8080 (via port-forward)
- Alertmanager: http://localhost:9093 (via port-forward)

## 🔍 Verificação do Deploy

Para verificar o status dos pods:

```bash
kubectl get pods -n autocura
```

Para ver os logs de um pod específico:

```bash
kubectl logs -f <pod-name> -n autocura
```

## 🛡️ Segurança

- Todos os módulos rodam em namespaces isolados
- Comunicação via rede Kubernetes dedicada
- Volumes persistentes para dados críticos
- Logs centralizados no Loki
- Alertas configurados via Alertmanager

## 🔄 Manutenção

Para atualizar um deployment:

```bash
kubectl set image deployment/<deployment-name> <container-name>=<new-image> -n autocura
```

Para escalar um deployment:

```bash
kubectl scale deployment <deployment-name> --replicas=<number> -n autocura
```

## 📝 Notas Importantes

1. Os módulos são versionados com tags específicas
2. Backup dos volumes é recomendado antes de atualizações
3. Monitoramento de recursos é essencial
4. Logs devem ser rotacionados periodicamente
5. Grafana dashboards devem ser exportados regularmente
6. Alertas devem ser testados periodicamente
7. Use port-forward para acessar os serviços localmente
8. Configure Ingress para acesso externo quando necessário 