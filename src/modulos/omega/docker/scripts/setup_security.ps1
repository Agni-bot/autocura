# Script PowerShell para configurar segurança do Sistema AutoCura
# Execute este script para gerar senhas seguras automaticamente

Write-Host "🔐 Configurador de Segurança - Sistema AutoCura" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Função para gerar senha segura
function Generate-SecurePassword {
    param([int]$length = 32)
    
    $chars = @()
    $chars += 65..90 | ForEach-Object { [char]$_ }  # A-Z
    $chars += 97..122 | ForEach-Object { [char]$_ } # a-z
    $chars += 48..57 | ForEach-Object { [char]$_ }  # 0-9
    $chars += @('!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+')
    
    $password = -join ($chars | Get-Random -Count $length)
    return $password
}

# Função para gerar chave hexadecimal
function Generate-HexKey {
    param([int]$bytes = 32)
    
    $randomBytes = New-Object byte[] $bytes
    [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($randomBytes)
    return [System.BitConverter]::ToString($randomBytes).Replace('-', '').ToLower()
}

# Gerar senhas
Write-Host "Gerando senhas seguras..." -ForegroundColor Yellow
$dbPassword = Generate-SecurePassword -length 32
$redisPassword = Generate-SecurePassword -length 32
$secretKey = Generate-HexKey -bytes 32
$jwtSecret = Generate-HexKey -bytes 64
$grafanaPassword = Generate-SecurePassword -length 20

# Criar conteúdo do arquivo .env
$envContent = @"
# ================================================
# Arquivo de Configuração - Sistema AutoCura
# Gerado em: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# ================================================

# 🗄️ Banco de Dados
DB_PASSWORD=$dbPassword
REDIS_PASSWORD=$redisPassword

# 🔐 Segurança
SECRET_KEY=$secretKey
JWT_SECRET=$jwtSecret

# 🔑 API Keys (ADICIONE SUAS CHAVES REAIS)
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# 📊 Monitoramento
GRAFANA_PASSWORD=$grafanaPassword

# ⚙️ Configurações do Sistema
AUTOCURA_ENV=production
OMEGA_ENABLED=true
CONSCIOUSNESS_LEVEL=TRANSCENDENT
LOG_LEVEL=INFO

# 🔧 Limites de Recursos
MAX_MEMORY_GB=16
MAX_CPU_CORES=8
MAX_EVOLUTION_GENERATIONS=1000
MAX_THOUGHT_STREAM_SIZE=10000

# 🌐 URLs de Serviços (NÃO ALTERE)
REDIS_URL=redis://redis:6379/0
POSTGRES_URL=postgresql://autocura:${DB_PASSWORD}@postgres:5432/autocura

# 🛡️ Configurações de Segurança da Evolução
EVOLUTION_SAFETY_LEVEL=HIGH
ALLOW_ARCHITECTURE_CHANGES=false
REQUIRE_HUMAN_APPROVAL=true

# 🧠 Configurações de Consciência
CONSCIOUSNESS_MONITORING_INTERVAL=1.0
EMERGENCE_VALIDATION_THRESHOLD=0.75
PHI_CALCULATION_ENABLED=true

# 💾 Backup e Recuperação
BACKUP_ENABLED=true
BACKUP_INTERVAL_HOURS=6
BACKUP_RETENTION_DAYS=30

# 📧 Notificações
NOTIFICATION_WEBHOOK_URL=
ALERT_EMAIL=admin@autocura.ai

# 🚀 Feature Flags
ENABLE_QUANTUM_INTEGRATION=true
ENABLE_NANO_INTEGRATION=true
ENABLE_CREATIVE_MODE=true
ENABLE_EMPATHY_SIMULATION=true
"@

# Salvar arquivo .env
$envPath = ".env"
$envContent | Out-File -FilePath $envPath -Encoding UTF8

Write-Host "`n✅ Arquivo .env criado com sucesso!" -ForegroundColor Green
Write-Host "📍 Localização: $((Get-Location).Path)\$envPath" -ForegroundColor Cyan

# Mostrar resumo das senhas geradas
Write-Host "`n📋 RESUMO DAS CREDENCIAIS GERADAS:" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Yellow
Write-Host "DB_PASSWORD:      " -NoNewline; Write-Host $dbPassword -ForegroundColor Green
Write-Host "REDIS_PASSWORD:   " -NoNewline; Write-Host $redisPassword -ForegroundColor Green
Write-Host "GRAFANA_PASSWORD: " -NoNewline; Write-Host $grafanaPassword -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Red
Write-Host "1. Guarde essas senhas em um local seguro (gerenciador de senhas)" -ForegroundColor Yellow
Write-Host "2. Adicione sua chave da OpenAI no arquivo .env" -ForegroundColor Yellow
Write-Host "3. Nunca commite o arquivo .env no Git" -ForegroundColor Yellow
Write-Host ""

# Criar .gitignore se não existir
if (-not (Test-Path ".gitignore")) {
    ".env`n*.log`n*.key`n*.pem" | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "✅ Arquivo .gitignore criado" -ForegroundColor Green
}

# Verificar se .env está no .gitignore
$gitignoreContent = Get-Content ".gitignore" -ErrorAction SilentlyContinue
if ($gitignoreContent -notcontains ".env") {
    Add-Content -Path ".gitignore" -Value "`n.env"
    Write-Host "✅ Adicionado .env ao .gitignore" -ForegroundColor Green
}

Write-Host "`n🎉 Configuração de segurança concluída!" -ForegroundColor Green
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Edite o arquivo .env e adicione sua chave da OpenAI" -ForegroundColor White
Write-Host "2. Execute: docker-compose -f docker-compose.omega.yml up -d" -ForegroundColor White
Write-Host "3. Acesse: http://localhost:8000" -ForegroundColor White 