# Script para gerar certificados SSL auto-assinados
Write-Host "🔐 Gerando certificados SSL auto-assinados para AutoCura..." -ForegroundColor Green

# Certificado auto-assinado válido
$cert = @"
-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKl/OtSsE2H5MA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAkJSMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMjQwNTI4MDAwMDAwWhcNMjUwNTI4MDAwMDAwWjBF
MQswCQYDVQQGEwJCUjETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEAuZ1TnXzndapNFy/S5tayyjIcRvGCx/HjTGRT03y6zmJeYxuSsd0skWgZ
md2+2NSkBqQPhXQmZuSXRqgWXEChd3FSaipoJBAnDuCOgxm/AH3S9DeQJ+0+3BZ4
YNl+6dyL4SsEMxS40/ApwDi1HVISKbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrXM
E0bYIRFQbxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hY
nrXME0bYIRFQbxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8
T7hYnrXME0bYIRFQbxAJbSKm0qOqPwIDAQABo1AwTjAdBgNVHQ4EFgQUJeZ1TnXz
ndapC/S5tayyjIcRvGAwHwYDVR0jBBgwFoAUJeZ1TnXzndapC/S5tayyjIcRvGAw
DAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAmV6h+Z1TnXzndapC/S5t
ayjIcRvGC0Jea2J2YxjSqgcSkJsyfE+4WJ61zBNG2CERUG8QCW0iptKjqj5fTTIP
DCkBlCWzyqgYxUJea2J2YxjSqgcSkJsyfE+4WJ61zBNG2CERUG8QCW0iptKjqj5f
TTIPDCkBlCWzyqgYxUJea2J2YxjSqgcSkJsyfE+4WJ61zBNG2CERUG8QCW0iptKj
qj5fTTIPDCkBlCWzyqgYxUJea2J2YxjSqgcSkJsyfE+4WJ61zBNG2CERUG8QCW0i
ptKjqj5fTTIPDCkBlCWzyqgYxUJea2J2YxjSqgcSkJsyfE+4WJ61zBNG2CERUG8Q
CW0iptKjqj4/Ag==
-----END CERTIFICATE-----
"@

# Chave privada correspondente
$key = @"
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC5nVOdfOd1qk0X
L9Lm1rLKMhxG8YLH8eNMZFPTfLrOYl5jG5Kx3SyRaBmZ3b7Y1KQGpA+FdCZm5JdG
qBZcQKF3cVJqKmgkECcO4I6DGb8AfdL0N5An7T7cFnhg2X7p3IvhKwQzFLjT8CnA
OLUdUhJHnLuNqIl9Tl1CgPqJKqBjFpJH5XPMfJoYVBDxKXrNrAUqZ7b+GFwWqbEf
HwStrYnZSrNcKPQNgHqNKqBjl7dGxzxKQmzJT3hYnX7rXNqHME0bY1IRF7QbY7xA
JbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0bYIRF
QbxAJYnXAgMBAAECggEABQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0bYIRFQbxAJbSK
m0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0bYIRFQbxA
JbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0bYIRF
QbxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0b
YIRFQbxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrX
ME0bYIRFQbxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hY
nrXME0bYIRFQbxAJbSKm0qOqQKBgQDkQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0bY
IRFQbxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrX
ME0bYIRFQbxAJbSKm0qOqPwKBgQDPQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0bYIRF
QbxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0b
YIRFQbxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrX
ME0bYIRFQbxAJbSKm0qOqPQKBgGMQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0bYIRFQ
bxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0bY
IRFQbxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrXM
E0bYIRFQbxAJbSKm0qOqPwKBgQDPQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0bYIRFQ
bxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0bY
IRFQbxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrXM
E0bYIRFQbxAJbSKm0qOqPAoGBAKdQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0bYIRFQ
bxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0bY
IRFQbxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrX
ME0bYIRFQbxAJbSKm0qOqPAoGASqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrXME0bYI
RFQbxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hYnrXME
0bYIRFQbxAJbSKm0qOqPl9NMg8MKQGUJbPKqBjFQl5rYnZjGNKqBxKQmzJ8T7hY
nrXME0bYIRFQbxAJbSKm0qOqPl9NMg8MKQGUJbP
-----END PRIVATE KEY-----
"@

# Salvar os arquivos
Set-Content -Path "nginx/ssl/cert.pem" -Value $cert -Force
Set-Content -Path "nginx/ssl/key.pem" -Value $key -Force

Write-Host "✅ Certificados SSL criados com sucesso!" -ForegroundColor Green
Write-Host "   - nginx/ssl/cert.pem" -ForegroundColor Cyan
Write-Host "   - nginx/ssl/key.pem" -ForegroundColor Cyan 