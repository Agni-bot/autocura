# Script de automação para o sistema Autocura
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('install', 'test', 'lint', 'build', 'clean', 'monitor', 'backup', 'restore')]
    [string]$Action = 'install',
    
    [Parameter(Mandatory=$false)]
    [string]$Environment = 'dev'
)

$ErrorActionPreference = 'Stop'

function Write-Status {
    param([string]$Message)
    Write-Host "`n[Autocura] $Message" -ForegroundColor Cyan
}

function Install-Dependencies {
    Write-Status "Instalando dependências..."
    python -m pip install --upgrade pip
    pip install -e ".[dev,monitoring,security]"
}

function Run-Tests {
    Write-Status "Executando testes..."
    pytest --cov=src tests/ --cov-report=term-missing
}

function Run-Linting {
    Write-Status "Executando verificações de código..."
    black . --check
    flake8 .
    isort . --check-only
    mypy src/
}

function Build-Project {
    Write-Status "Construindo projeto..."
    docker-compose build
}

function Clean-Project {
    Write-Status "Limpando arquivos temporários..."
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue -Path @(
        "**/__pycache__",
        "**/.pytest_cache",
        "**/.coverage",
        "**/htmlcov",
        "**/.mypy_cache",
        "**/.ruff_cache"
    )
}

function Start-Monitoring {
    Write-Status "Iniciando monitoramento..."
    docker-compose up -d prometheus grafana
    Start-Process "http://localhost:3000"  # Grafana
    Start-Process "http://localhost:9090"  # Prometheus
}

function Backup-Data {
    Write-Status "Realizando backup..."
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "backup/$timestamp"
    New-Item -ItemType Directory -Force -Path $backupDir
    
    Copy-Item -Recurse -Force @(
        "config",
        "data",
        "logs"
    ) -Destination $backupDir
    
    Compress-Archive -Path $backupDir -DestinationPath "$backupDir.zip"
    Remove-Item -Recurse -Force $backupDir
}

function Restore-Data {
    param([string]$BackupFile)
    
    if (-not $BackupFile) {
        Write-Error "Arquivo de backup não especificado"
        return
    }
    
    Write-Status "Restaurando backup..."
    Expand-Archive -Path $BackupFile -DestinationPath "restore_temp"
    Copy-Item -Recurse -Force "restore_temp/*" .
    Remove-Item -Recurse -Force "restore_temp"
}

# Execução principal
try {
    switch ($Action) {
        'install' { Install-Dependencies }
        'test' { Run-Tests }
        'lint' { Run-Linting }
        'build' { Build-Project }
        'clean' { Clean-Project }
        'monitor' { Start-Monitoring }
        'backup' { Backup-Data }
        'restore' { Restore-Data -BackupFile $args[0] }
    }
} catch {
    Write-Error "Erro durante a execução: $_"
    exit 1
} 