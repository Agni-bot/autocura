# Script para gerar relatório de performance do AutoCura

# Cores para output
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Red = [System.ConsoleColor]::Red

# Função para obter métricas do Prometheus
function Get-PrometheusMetrics {
    param (
        [string]$Query,
        [string]$Service
    )
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/query?query=$Query" -Method Get -TimeoutSec 5
        if ($response.status -eq "success" -and $response.data.result.Count -gt 0) {
            return $response.data.result[0].value[1]
        }
        return $null
    } catch {
        Write-Host "❌ Erro ao obter métricas do $Service: $_" -ForegroundColor $Red
        return $null
    }
}

# Função para formatar tempo
function Format-Time {
    param (
        [string]$Seconds
    )
    
    $time = [double]$Seconds
    if ($time -lt 1) {
        return [string]::Format("{0}ms", [math]::Round($time * 1000, 2))
    } elseif ($time -lt 60) {
        return [string]::Format("{0}s", [math]::Round($time, 2))
    } else {
        $minutes = [math]::Floor($time / 60)
        $seconds = $time % 60
        return [string]::Format("{0}m {1}s", $minutes, $seconds)
    }
}

Write-Host "📊 Gerando relatório de performance..." -ForegroundColor $Yellow

# Verificar se o Prometheus está acessível
try {
    $response = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/status/config" -Method Get -TimeoutSec 5
} catch {
    Write-Host "❌ Prometheus não está acessível: $_" -ForegroundColor $Red
    exit 1
}

# Coletar métricas
Write-Host "`n📈 Métricas de Performance" -ForegroundColor $Yellow
Write-Host "----------------------------------------" -ForegroundColor $Yellow

# Taxa de requisições
$reqRate = Get-PrometheusMetrics -Query "rate(requisicoes_total[5m])" -Service "Monitor"
if ($reqRate) {
    Write-Host "Requisições/s: $([math]::Round($reqRate, 2))" -ForegroundColor $Green
}

# Tempo de resposta
$p50 = Get-PrometheusMetrics -Query "histogram_quantile(0.50, rate(tempo_resposta_seconds_bucket[5m]))" -Service "Monitor"
$p95 = Get-PrometheusMetrics -Query "histogram_quantile(0.95, rate(tempo_resposta_seconds_bucket[5m]))" -Service "Monitor"
$p99 = Get-PrometheusMetrics -Query "histogram_quantile(0.99, rate(tempo_resposta_seconds_bucket[5m]))" -Service "Monitor"

if ($p50 -and $p95 -and $p99) {
    Write-Host "Tempo de Resposta:" -ForegroundColor $Green
    Write-Host "  P50: $(Format-Time $p50)" -ForegroundColor $Green
    Write-Host "  P95: $(Format-Time $p95)" -ForegroundColor $Green
    Write-Host "  P99: $(Format-Time $p99)" -ForegroundColor $Green
}

# Taxa de erros
$errorRate = Get-PrometheusMetrics -Query "rate(erros_total[5m])" -Service "Monitor"
if ($errorRate) {
    $errorPercentage = [math]::Round(($errorRate / $reqRate) * 100, 2)
    Write-Host "Taxa de Erros: $errorPercentage%" -ForegroundColor $(if ($errorPercentage -gt 1) { $Red } elseif ($errorPercentage -gt 0.1) { $Yellow } else { $Green })
}

# Métricas por serviço
Write-Host "`n🔍 Métricas por Serviço" -ForegroundColor $Yellow
Write-Host "----------------------------------------" -ForegroundColor $Yellow

$services = @("monitor", "observador", "validador", "guardiao")
foreach ($service in $services) {
    Write-Host "`n$service" -ForegroundColor $Yellow
    
    # CPU
    $cpu = Get-PrometheusMetrics -Query "rate(process_cpu_seconds_total{job=`"$service`"}[5m])" -Service $service
    if ($cpu) {
        Write-Host "CPU: $([math]::Round($cpu * 100, 2))%" -ForegroundColor $Green
    }
    
    # Memória
    $memory = Get-PrometheusMetrics -Query "process_resident_memory_bytes{job=`"$service`"}" -Service $service
    if ($memory) {
        $memoryMB = [math]::Round($memory / 1MB, 2)
        Write-Host "Memória: ${memoryMB}MB" -ForegroundColor $Green
    }
    
    # Threads
    $threads = Get-PrometheusMetrics -Query "process_open_fds{job=`"$service`"}" -Service $service
    if ($threads) {
        Write-Host "Threads: $threads" -ForegroundColor $Green
    }
}

# Métricas do Redis
Write-Host "`n🔴 Métricas do Redis" -ForegroundColor $Yellow
Write-Host "----------------------------------------" -ForegroundColor $Yellow

$redisMetrics = @(
    @{Query = "redis_connected_clients"; Name = "Clientes Conectados"},
    @{Query = "redis_memory_used_bytes"; Name = "Memória Utilizada"},
    @{Query = "redis_commands_processed_total"; Name = "Comandos Processados"},
    @{Query = "redis_keyspace_hits_total"; Name = "Cache Hits"},
    @{Query = "redis_keyspace_misses_total"; Name = "Cache Misses"}
)

foreach ($metric in $redisMetrics) {
    $value = Get-PrometheusMetrics -Query $metric.Query -Service "Redis"
    if ($value) {
        if ($metric.Query -eq "redis_memory_used_bytes") {
            $value = [string]::Format("{0}MB", [math]::Round($value / 1MB, 2))
        }
        Write-Host "$($metric.Name): $value" -ForegroundColor $Green
    }
}

# Métricas do Elasticsearch
Write-Host "`n🔷 Métricas do Elasticsearch" -ForegroundColor $Yellow
Write-Host "----------------------------------------" -ForegroundColor $Yellow

$esMetrics = @(
    @{Query = "elasticsearch_cluster_health_number_of_nodes"; Name = "Nós"},
    @{Query = "elasticsearch_cluster_health_status"; Name = "Status"},
    @{Query = "elasticsearch_cluster_health_number_of_pending_tasks"; Name = "Tarefas Pendentes"},
    @{Query = "elasticsearch_cluster_health_number_of_in_flight_fetch"; Name = "Fetches em Andamento"}
)

foreach ($metric in $esMetrics) {
    $value = Get-PrometheusMetrics -Query $metric.Query -Service "Elasticsearch"
    if ($value) {
        Write-Host "$($metric.Name): $value" -ForegroundColor $Green
    }
}

# Recomendações
Write-Host "`n💡 Recomendações" -ForegroundColor $Yellow
Write-Host "----------------------------------------" -ForegroundColor $Yellow

if ($errorRate -and $errorRate -gt 0.01) {
    Write-Host "⚠️ Alta taxa de erros detectada. Considere investigar os logs para identificar a causa." -ForegroundColor $Red
}

if ($p95 -and $p95 -gt 1) {
    Write-Host "⚠️ Tempo de resposta P95 acima de 1s. Considere otimizar as operações mais lentas." -ForegroundColor $Yellow
}

$redisMemory = Get-PrometheusMetrics -Query "redis_memory_used_bytes" -Service "Redis"
if ($redisMemory -and $redisMemory -gt 1GB) {
    Write-Host "⚠️ Uso de memória do Redis acima de 1GB. Considere limpar dados antigos ou aumentar a memória disponível." -ForegroundColor $Yellow
}

$esPendingTasks = Get-PrometheusMetrics -Query "elasticsearch_cluster_health_number_of_pending_tasks" -Service "Elasticsearch"
if ($esPendingTasks -and $esPendingTasks -gt 100) {
    Write-Host "⚠️ Alto número de tarefas pendentes no Elasticsearch. Considere aumentar os recursos do cluster." -ForegroundColor $Yellow
} 