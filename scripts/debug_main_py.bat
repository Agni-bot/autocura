@echo off
echo ====================================
echo DIAGNOSTICO MAIN.PY - AUTOCURA API
echo ====================================

cd docker

echo.
echo ===== 1. VERIFICANDO LOGS DETALHADOS =====
echo Ultimas 50 linhas de log da API:
docker-compose -f docker-compose.simple.yml logs --tail=50 autocura-api

echo.
echo ===== 2. VERIFICANDO DEPENDENCIAS =====
echo Verificando requirements.txt:
type ..\requirements.txt | findstr /n "."

echo.
echo ===== 3. TESTANDO MAIN.PY LOCALMENTE =====
cd ..
echo Testando se main.py executa localmente:
python -c "
try:
    import sys
    print('Python version:', sys.version)
    print('Verificando imports principais...')
    
    # Testa imports críticos
    try:
        import fastapi
        print('✅ FastAPI disponível')
    except ImportError as e:
        print('❌ FastAPI erro:', e)
    
    try:
        import redis
        print('✅ Redis disponível')
    except ImportError as e:
        print('❌ Redis erro:', e)
        
    try:
        import uvicorn
        print('✅ Uvicorn disponível')
    except ImportError as e:
        print('❌ Uvicorn erro:', e)
        
    print('Tentando importar main...')
    import main
    print('✅ main.py importado com sucesso')
    
except Exception as e:
    print('❌ Erro ao importar main.py:', e)
    import traceback
    traceback.print_exc()
"

echo.
echo ===== 4. VERIFICANDO CONEXAO REDIS =====
echo Testando conexão Redis:
python -c "
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.ping()
    print('✅ Redis conectado com sucesso')
except Exception as e:
    print('❌ Redis erro:', e)
"

echo.
echo ===== 5. REINICIANDO COM LOGS DETALHADOS =====
echo Parando containers...
docker-compose -f docker-compose.simple.yml stop

echo Removendo container da API...
docker-compose -f docker-compose.simple.yml rm -f autocura-api

echo Iniciando Redis primeiro...
docker-compose -f docker-compose.simple.yml up -d autocura-redis
timeout /t 5 /nobreak

echo Iniciando API com logs em tempo real...
echo (Pressione Ctrl+C para parar os logs)
docker-compose -f docker-compose.simple.yml up autocura-api

pause 