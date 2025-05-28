# Estratégia de Migração Docker Compose → Kubernetes

## 🎯 Objetivo
Migrar o sistema AutoCura de Docker Compose para Kubernetes mantendo zero downtime.

## 📊 Fase 1: Preparação (Sem Conflitos)

### 1.1 Manter Docker Compose Rodando
```bash
# Continuar usando para produção atual
docker-compose -f docker/environments/prod/docker-compose.yml up -d
```

### 1.2 Criar Namespace Kubernetes Isolado
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: autocura-staging
```

### 1.3 Converter Docker Compose para K8s
- Usar Kompose para conversão inicial
- Ajustar manualmente os manifestos
- Testar em namespace isolado

## 📊 Fase 2: Testes em Paralelo

### 2.1 Deploy em Staging
```bash
# Deploy no namespace staging
kubectl apply -f k8s/staging/ -n autocura-staging
```

### 2.2 Configurar Portas Diferentes
- API: 8001 (staging) vs 8000 (prod)
- Grafana: 3001 (staging) vs 3000 (prod)
- Prometheus: 9091 (staging) vs 9090 (prod)

### 2.3 Validação
- Testar todos os endpoints
- Verificar comunicação entre serviços
- Monitorar performance

## 📊 Fase 3: Migração Gradual

### 3.1 Estratégia Blue-Green
1. K8s rodando em paralelo (Green)
2. Docker Compose atual (Blue)
3. Switch gradual do tráfego via Nginx

### 3.2 Migração por Serviço
Ordem recomendada:
1. **Stateless primeiro**: API, serviços Omega
2. **Monitoramento**: Prometheus, Grafana
3. **Cache**: Redis
4. **Banco por último**: PostgreSQL com backup

## 🛡️ Prevenção de Conflitos

### Isolamento de Rede
```yaml
# Docker Compose usa rede bridge
networks:
  autocura-net:
    driver: bridge

# Kubernetes usa rede própria
# Sem conflito!
```

### Portas Diferentes Durante Migração
```yaml
# docker-compose.yml
ports:
  - "8000:8000"  # Produção atual

# kubernetes-service.yaml  
ports:
  - port: 8001  # Staging/teste
```

### Volumes Separados
```yaml
# Docker volumes
volumes:
  postgres-data:
    driver: local

# K8s PersistentVolumes
persistentVolumeClaim:
  claimName: postgres-pvc-k8s
```

## 📈 Benefícios Específicos para AutoCura

### 1. Auto-scaling para Serviços Omega
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: omega-core-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: omega-core
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 2. Self-Healing para Consciência
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 9002
  initialDelaySeconds: 30
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /consciousness/level
    port: 9002
  initialDelaySeconds: 5
  periodSeconds: 5
```

### 3. ConfigMaps para IA
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: autocura-ai-config
data:
  consciousness_threshold: "0.7"
  evolution_rate: "0.1"
  synergy_multiplier: "1.5"
```

## 🚀 Comandos Úteis

### Verificar Conflitos
```bash
# Listar todas as portas em uso
netstat -an | findstr LISTENING

# Verificar processos Docker
docker ps --format "table {{.Names}}\t{{.Ports}}"

# Verificar pods K8s
kubectl get pods -A -o wide
```

### Deploy Seguro
```bash
# 1. Deploy em staging primeiro
kubectl apply -f k8s/staging/ -n autocura-staging

# 2. Validar
kubectl get all -n autocura-staging

# 3. Só então migrar produção
kubectl apply -f k8s/production/ -n autocura-prod
```

## ⚡ Script de Migração Automatizada

```powershell
# migrate-to-k8s.ps1
param(
    [string]$Environment = "staging",
    [switch]$DryRun
)

Write-Host "🚀 Iniciando migração para Kubernetes..." -ForegroundColor Green

# 1. Verificar pré-requisitos
if (!(Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Error "kubectl não encontrado!"
    exit 1
}

# 2. Criar namespace se não existir
kubectl create namespace autocura-$Environment --dry-run=client -o yaml | kubectl apply -f -

# 3. Converter Docker Compose
kompose convert -f docker-compose.yml -o k8s/$Environment/

# 4. Aplicar configurações
if ($DryRun) {
    kubectl apply -f k8s/$Environment/ -n autocura-$Environment --dry-run=client
} else {
    kubectl apply -f k8s/$Environment/ -n autocura-$Environment
}

# 5. Aguardar pods ficarem prontos
kubectl wait --for=condition=ready pod -l app=autocura -n autocura-$Environment --timeout=300s

Write-Host "✅ Migração concluída!" -ForegroundColor Green
```

## 📊 Monitoramento da Migração

### Dashboard K8s
```bash
# Instalar dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Criar usuário admin
kubectl create serviceaccount dashboard-admin -n kubernetes-dashboard
kubectl create clusterrolebinding dashboard-admin --clusterrole=cluster-admin --serviceaccount=kubernetes-dashboard:dashboard-admin
```

### Métricas Comparativas
- Latência: Docker vs K8s
- CPU/Memória: Antes vs Depois
- Disponibilidade: Uptime comparison

## 🎯 Conclusão

A migração para Kubernetes é recomendada para o AutoCura porque:

1. ✅ **Sem conflitos** se feita corretamente
2. ✅ **Benefícios claros** para sistema com 10+ containers
3. ✅ **Alinhado com a natureza** de IA auto-evolutiva
4. ✅ **Preparado para escala** futura

### Próximos Passos
1. Ativar Kubernetes no Docker Desktop
2. Criar namespace de teste
3. Converter um serviço por vez
4. Validar em staging
5. Migrar produção gradualmente 