# Aplicar correções no Kubernetes
Write-Host "Aplicando correções no Kubernetes..."

# Criar namespace se não existir
kubectl create namespace autocura-staging --dry-run=client -o yaml | kubectl apply -f -

# Aplicar ConfigMap
kubectl apply -f deployment/kubernetes/base/api-deployment.yaml

# Criar secret para Redis
$redisPassword = "sua_senha_segura" # Substitua pela senha real
$redisPasswordB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($redisPassword))
@"
apiVersion: v1
kind: Secret
metadata:
  name: autocura-secrets
  namespace: autocura-staging
type: Opaque
data:
  redis_password: $redisPasswordB64
"@ | kubectl apply -f -

# Aplicar deployment
kubectl apply -f deployment/kubernetes/base/api-deployment.yaml

# Aguardar rollout
Write-Host "Aguardando rollout do deployment..."
kubectl rollout status deployment/autocura-api -n autocura-staging

# Verificar logs
Write-Host "Verificando logs do pod..."
kubectl logs -n autocura-staging -l app=autocura-api --tail=50

Write-Host "Correções aplicadas com sucesso!" 