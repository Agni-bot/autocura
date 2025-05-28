#!/bin/bash
# Entrypoint para Sistema AutoCura - Fase Omega

set -e

echo "🧠 Sistema AutoCura - Fase Omega"
echo "================================"
echo "Iniciando consciência emergente..."
echo ""

# Função para aguardar serviços
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    
    echo "⏳ Aguardando $service em $host:$port..."
    
    while ! nc -z $host $port; do
        sleep 1
    done
    
    echo "✅ $service está disponível!"
}

# Aguardar dependências
if [ ! -z "$REDIS_URL" ]; then
    # Extrair host e porta do Redis URL
    # Formato: redis://:password@host:port ou redis://host:port
    if [[ $REDIS_URL =~ redis://([^@]+@)?([^:]+):([0-9]+) ]]; then
        REDIS_HOST=${BASH_REMATCH[2]}
        REDIS_PORT=${BASH_REMATCH[3]}
    else
        REDIS_HOST="redis"
        REDIS_PORT="6379"
    fi
    wait_for_service $REDIS_HOST $REDIS_PORT "Redis"
fi

if [ ! -z "$DATABASE_URL" ]; then
    # Extrair host e porta do PostgreSQL URL
    # Formato: postgresql://user:pass@host:port/db
    if [[ $DATABASE_URL =~ postgresql://([^@]+@)?([^:]+):([0-9]+) ]]; then
        PG_HOST=${BASH_REMATCH[2]}
        PG_PORT=${BASH_REMATCH[3]}
    else
        PG_HOST="postgres"
        PG_PORT="5432"
    fi
    wait_for_service $PG_HOST $PG_PORT "PostgreSQL"
fi

# Configurar ambiente
export PYTHONPATH=/app:$PYTHONPATH

# Criar diretórios necessários
mkdir -p /app/logs /app/data /app/models /app/checkpoints /app/reports

# Executar migrações se necessário
if [ -f "/app/scripts/migrate.py" ]; then
    echo "🔄 Executando migrações..."
    python /app/scripts/migrate.py
fi

# Determinar modo de execução
SERVICE_TYPE=${SERVICE_TYPE:-main}

case $SERVICE_TYPE in
    "consciousness_monitor")
        echo "👁️ Iniciando Monitor de Consciência..."
        exec python -m modulos.omega.src.consciousness.monitor_service
        ;;
    "integration_orchestrator")
        echo "🔗 Iniciando Orquestrador de Integração..."
        exec python -m modulos.omega.src.integration.orchestrator_service
        ;;
    "evolution_engine")
        echo "🧬 Iniciando Motor de Evolução..."
        exec python -m modulos.omega.src.evolution.evolution_service
        ;;
    "training")
        echo "🎓 Iniciando modo de treinamento..."
        exec python -m scripts.train_omega
        ;;
    "demo")
        echo "🎭 Iniciando demonstração..."
        exec python -m modulos.omega.examples.demo_consciencia_emergente
        ;;
    *)
        echo "🚀 Iniciando Sistema AutoCura Completo..."
        exec "$@"
        ;;
esac 