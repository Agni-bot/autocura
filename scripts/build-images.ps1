# Script para construir e enviar imagens Docker
$services = @("monitoramento", "diagnostico", "gerador", "observabilidade", "portal")
$registry = "localhost:5000"
$tag = "latest"

foreach ($service in $services) {
    Write-Host "Construindo imagem do serviço $service..."
    
    # Verificar qual Dockerfile usar
    $dockerfile = "Dockerfile.$service"
    if (-not (Test-Path "src\$service\$dockerfile")) {
        $dockerfile = "Dockerfile"
    }
    
    # Construir a imagem
    docker build -t "$registry/autocura/$service`:$tag" -f "src\$service\$dockerfile" "src\$service"
    
    # Enviar a imagem para o registry
    Write-Host "Enviando imagem do serviço $service para o registry..."
    docker push "$registry/autocura/$service`:$tag"
}

Write-Host "Todas as imagens foram construídas e enviadas com sucesso!" 