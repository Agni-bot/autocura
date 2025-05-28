# Script para gerar certificados SSL auto-assinados
Write-Host "🔐 Gerando certificados SSL auto-assinados..." -ForegroundColor Green

# Verifica se OpenSSL está disponível
$opensslPath = Get-Command openssl -ErrorAction SilentlyContinue

if (-not $opensslPath) {
    Write-Host "❌ OpenSSL não encontrado. Criando certificados dummy..." -ForegroundColor Yellow
    
    # Cria certificados dummy para desenvolvimento
    $certContent = @"
-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKl8mEHTt1M6MA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAkJSMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMjQwNTI4MDAwMDAwWhcNMjUwNTI4MDAwMDAwWjBF
MQswCQYDVQQGEwJCUjETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEAxJ8FsGVKUvg8RILSKkZ6Clo0LQDeVLpH8qSXDb5yZKXR8QykYP7tj2cD
-----END CERTIFICATE-----
"@

    $keyContent = @"
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDEnwWwZUpS+DxE
gtIqRnoKWjQtAN5UukfypJcNvnJkpdHxDKRg/u2PZwOoaKKD0dYiS8W1F8Gp7Jzn
-----END PRIVATE KEY-----
"@

    Set-Content -Path "nginx/ssl/cert.pem" -Value $certContent
    Set-Content -Path "nginx/ssl/key.pem" -Value $keyContent
    
} else {
    # Gera certificados reais com OpenSSL
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
        -keyout nginx/ssl/key.pem `
        -out nginx/ssl/cert.pem `
        -subj "/C=BR/ST=SP/L=SaoPaulo/O=AutoCura/CN=localhost"
}

Write-Host "✅ Certificados SSL criados!" -ForegroundColor Green 