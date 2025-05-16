# scripts/iniciar_portal.ps1
# Script para port-forward dos principais serviços do autocura e abrir o portal central (Observabilidade)

$namespace = "autocura"

# Observabilidade (Portal Central)
Start-Process powershell -ArgumentList "kubectl port-forward -n $namespace svc/observabilidade 8000:8080"

# Outros serviços (se quiser acessar individualmente)
Start-Process powershell -ArgumentList "kubectl port-forward -n $namespace svc/will 5000:5000"
Start-Process powershell -ArgumentList "kubectl port-forward -n $namespace svc/monitoramento 9080:8080"
Start-Process powershell -ArgumentList "kubectl port-forward -n $namespace svc/gerador 9081:8080"
Start-Process powershell -ArgumentList "kubectl port-forward -n $namespace svc/diagnostico 9082:8080"
Start-Process powershell -ArgumentList "kubectl port-forward -n $namespace svc/executor-acoes 9083:8080"
Start-Process powershell -ArgumentList "kubectl port-forward -n $namespace svc/grafana 3000:3000"
Start-Process powershell -ArgumentList "kubectl port-forward -n $namespace svc/kibana 5601:5601"
Start-Process powershell -ArgumentList "kubectl port-forward -n $namespace svc/elasticsearch 9200:9200"
Start-Process powershell -ArgumentList "kubectl port-forward -n $namespace svc/prometheus-server 9090:80"

Start-Sleep -Seconds 3
Start-Process "http://localhost:8000"

Write-Host "Portal Central (Observabilidade) aberto em http://localhost:8000"
Write-Host "Endpoints Will disponíveis em http://localhost:5000"
Write-Host "Monitoramento: http://localhost:9080"
Write-Host "Gerador: http://localhost:9081"
Write-Host "Diagnóstico: http://localhost:9082"
Write-Host "Executor Ações: http://localhost:9083"
Write-Host "Grafana: http://localhost:3000"
Write-Host "Kibana: http://localhost:5601"
Write-Host "Elasticsearch: http://localhost:9200"
Write-Host "Prometheus: http://localhost:9090" 