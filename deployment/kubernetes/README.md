# AutoCura - Deployment Kubernetes

## 📋 Visão Geral

Este diretório contém todos os manifestos Kubernetes necessários para fazer o deploy do sistema AutoCura em um cluster Kubernetes. A estrutura foi projetada para ser modular, escalável e fácil de gerenciar.

## 🗂️ Estrutura de Diretórios

```
deployment/kubernetes/
├── base/                    # Configurações base
│   ├── namespace.yaml      # Namespaces para diferentes ambientes
│   ├── configmap.yaml      # Configurações do sistema
│   └── secrets.yaml        # Dados sensíveis (senhas, API keys)
├── storage/                # Volumes persistentes
│   └── postgres-pvc.yaml   # PVCs para PostgreSQL, Redis e dados
├── databases/              # Bancos de dados
│   ├── postgres-deployment.yaml
│   └── redis-deployment.yaml
├── apps/                   # Aplicações
│   ├── api-deployment.yaml        # API principal
│   └── omega-deployments.yaml     # Serviços Omega
├── monitoring/             # Monitoramento
│   └── prometheus-grafana.yaml
├── ingress/                # Exposição externa
│   └── nginx-ingress.yaml
├── scripts/                # Scripts auxiliares
│   └── deploy-to-k8s.ps1
└── README.md              # Esta documentação
```

## 🚀 Quick Start

### Pré-requisitos

1. **Docker Desktop** com Kubernetes habilitado
2. **kubectl** instalado e configurado
3. **PowerShell** (Windows) ou **Bash** (Linux/Mac)

### Ativar Kubernetes no Docker Desktop

1. Abra o Docker Desktop
2. Vá em Settings → Kubernetes
3. Marque "Enable Kubernetes"
4. Clique em "Apply & Restart"
5. Aguarde o Kubernetes iniciar (pode levar alguns minutos)

### Deploy Rápido

```powershell
# Windows PowerShell
.\deployment\kubernetes\scripts\deploy-to-k8s.ps1 -Environment staging

# Com build de imagens
.\deployment\kubernetes\scripts\deploy-to-k8s.ps1 -Environment staging -BuildImages

# Dry-run (apenas simula)
.\deployment\kubernetes\scripts\deploy-to-k8s.ps1 -Environment staging -DryRun
```

## 📦 Componentes

### 1. **Bancos de Dados**
- **PostgreSQL**: Banco de dados principal
- **Redis**: Cache e mensageria

### 2. **Aplicações Core**
- **API Principal**: FastAPI com todos os endpoints
- **Omega Core**: Núcleo cognitivo
- **Consciousness Monitor**: Monitor de consciência
- **Evolution Engine**: Motor de evolução
- **Integration Orchestrator**: Orquestrador de integração

### 3. **Monitoramento**
- **Prometheus**: Coleta de métricas
- **Grafana**: Visualização de métricas

### 4. **Infraestrutura**
- **Nginx Ingress**: Proxy reverso e load balancer
- **HPA**: Auto-scaling horizontal
- **PVC**: Armazenamento persistente

## 🔧 Configuração

### Variáveis de Ambiente

Edite `base/configmap.yaml` para ajustar configurações:

```yaml
data:
  CONSCIOUSNESS_THRESHOLD: "0.7"
  EVOLUTION_RATE: "0.1"
  SYNERGY_MULTIPLIER: "1.5"
```

### Secrets

⚠️ **IMPORTANTE**: Antes do deploy, atualize `base/secrets.yaml` com valores reais:

```yaml
stringData:
  POSTGRES_PASSWORD: "senha_segura_aqui"
  REDIS_PASSWORD: "senha_segura_aqui"
  OPENAI_API_KEY: "sk-sua-chave-aqui"
```

### Recursos

Ajuste os recursos em cada deployment conforme necessário:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

## 📊 Monitoramento

### Acessar Grafana

```bash
kubectl port-forward -n autocura-staging service/grafana-service 3000:3000
```

Acesse: http://localhost:3000
- Usuário: admin
- Senha: (definida em secrets.yaml)

### Acessar Prometheus

```bash
kubectl port-forward -n autocura-staging service/prometheus-service 9090:9090
```

Acesse: http://localhost:9090

## 🔍 Comandos Úteis

### Verificar Status

```bash
# Ver todos os recursos
kubectl get all -n autocura-staging

# Ver pods com mais detalhes
kubectl get pods -n autocura-staging -o wide

# Ver logs de um pod
kubectl logs -n autocura-staging <nome-do-pod>

# Ver logs em tempo real
kubectl logs -n autocura-staging -f <nome-do-pod>
```

### Debugging

```bash
# Descrever um pod com problemas
kubectl describe pod -n autocura-staging <nome-do-pod>

# Acessar shell de um container
kubectl exec -it -n autocura-staging <nome-do-pod> -- /bin/sh

# Ver eventos do namespace
kubectl get events -n autocura-staging --sort-by='.lastTimestamp'
```

### Scaling

```bash
# Escalar manualmente
kubectl scale deployment -n autocura-staging autocura-api --replicas=3

# Ver HPA status
kubectl get hpa -n autocura-staging
```

## 🔄 Atualizações

### Atualizar Imagem

```bash
# Atualizar imagem da API
kubectl set image deployment/autocura-api -n autocura-staging api=autocura/api:v1.1

# Verificar rollout status
kubectl rollout status deployment/autocura-api -n autocura-staging
```

### Rollback

```bash
# Ver histórico de revisões
kubectl rollout history deployment/autocura-api -n autocura-staging

# Fazer rollback para revisão anterior
kubectl rollout undo deployment/autocura-api -n autocura-staging
```

## 🛡️ Segurança

### Boas Práticas

1. **Nunca commite secrets reais** no repositório
2. Use **RBAC** para controlar acesso
3. Configure **Network Policies** para isolar pods
4. Use **Pod Security Policies** em produção
5. Habilite **TLS/SSL** para todos os endpoints externos

### Exemplo de Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: autocura-staging
spec:
  podSelector:
    matchLabels:
      app: autocura-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: autocura-staging
    ports:
    - protocol: TCP
      port: 8000
```

## 🚨 Troubleshooting

### Pod não inicia

1. Verifique logs: `kubectl logs -n autocura-staging <pod-name>`
2. Verifique eventos: `kubectl describe pod -n autocura-staging <pod-name>`
3. Verifique recursos: O cluster tem CPU/memória suficiente?

### Erro de conexão com banco

1. Verifique se o PostgreSQL está rodando
2. Verifique as credenciais em secrets
3. Verifique o service name está correto

### Kubernetes não está acessível

1. Verifique se Docker Desktop está rodando
2. Verifique se Kubernetes está habilitado
3. Reinicie o Docker Desktop se necessário

## 📈 Próximos Passos

1. **Configurar CI/CD**: Integrar com GitHub Actions
2. **Helm Charts**: Criar charts para facilitar deploy
3. **Istio Service Mesh**: Para observabilidade avançada
4. **Backup Automatizado**: Configurar backup do PostgreSQL
5. **Monitoring Avançado**: Adicionar alertas no Prometheus

## 🤝 Contribuindo

Para contribuir com melhorias no deployment:

1. Crie uma branch: `git checkout -b feature/melhoria-k8s`
2. Teste localmente com `--dry-run`
3. Documente mudanças neste README
4. Abra um Pull Request

## 📞 Suporte

Em caso de problemas:

1. Verifique a seção de Troubleshooting
2. Consulte os logs dos pods
3. Abra uma issue no repositório
4. Contate a equipe de DevOps

---

**Última atualização**: 2025-05-28
**Versão**: 1.0.0 