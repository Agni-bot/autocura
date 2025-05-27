@echo off
echo ====================================
echo DIAGNOSTICO E CORRECAO API CONTAINER
echo ====================================

cd docker

echo.
echo ===== VERIFICANDO LOGS DO CONTAINER =====
docker-compose -f docker-compose.simple.yml logs --tail=20 autocura-api

echo.
echo ===== PARANDO TODOS OS CONTAINERS =====
docker-compose -f docker-compose.simple.yml stop

echo.
echo ===== REMOVENDO CONTAINERS PROBLEMATICOS =====
docker-compose -f docker-compose.simple.yml rm -f autocura-api

echo.
echo ===== LIMPANDO IMAGENS E CACHE =====
docker system prune -f

echo.
echo ===== RECONSTRUINDO E INICIANDO APENAS NECESSARIOS =====
docker-compose -f docker-compose.simple.yml up -d autocura-redis
timeout /t 5 /nobreak

echo.
echo ===== INICIANDO API COM CONFIGURACAO CORRIGIDA =====
docker-compose -f docker-compose.simple.yml up -d autocura-api
timeout /t 10 /nobreak

echo.
echo ===== INICIANDO DASHBOARD =====
docker-compose -f docker-compose.simple.yml up -d autocura-dashboard

echo.
echo ===== STATUS FINAL =====
docker-compose -f docker-compose.simple.yml ps

echo.
echo ===== TESTANDO CONECTIVIDADE =====
echo Testando API...
timeout /t 3 /nobreak
curl -s http://localhost:8001/health || echo API nao respondeu

echo.
echo Testando Dashboard...
curl -s http://localhost:8080 | findstr "title" || echo Dashboard nao respondeu

echo.
echo ====================================
echo CORRECAO CONCLUIDA!
echo ====================================
echo.
echo Se ainda houver problemas, execute:
echo docker-compose -f docker-compose.simple.yml logs autocura-api
echo.
pause 