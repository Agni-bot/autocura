# Cores para output
$RED = [System.ConsoleColor]::Red
$GREEN = [System.ConsoleColor]::Green
$YELLOW = [System.ConsoleColor]::Yellow

Write-Host "Iniciando build das imagens Docker..." -ForegroundColor $YELLOW

# Build da imagem base
Write-Host "`nConstruindo imagem base..." -ForegroundColor $YELLOW
docker build -t autocura-base:latest -f Dockerfile.base .
if ($LASTEXITCODE -eq 0) {
    Write-Host "Imagem base construída com sucesso!" -ForegroundColor $GREEN
} else {
    Write-Host "Falha ao construir imagem base" -ForegroundColor $RED
    exit 1
}

# Build das imagens dos serviços
$services = @("api", "monitor", "diagnostico", "gerador", "guardiao", "validador", "observador")

foreach ($service in $services) {
    Write-Host "`nConstruindo imagem do serviço $service..." -ForegroundColor $YELLOW
    docker build -t autocura-$service:latest -f Dockerfile.$service .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Imagem do serviço $service construída com sucesso!" -ForegroundColor $GREEN
    } else {
        Write-Host "Falha ao construir imagem do serviço $service" -ForegroundColor $RED
        exit 1
    }
}

Write-Host "`nTodas as imagens foram construídas com sucesso!" -ForegroundColor $GREEN 