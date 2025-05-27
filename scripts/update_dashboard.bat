@echo off
echo ====================================
echo ATUALIZANDO DASHBOARD AUTOCURA
echo ====================================

cd docker

echo.
echo ===== PARANDO CONTAINER DO DASHBOARD =====
docker-compose -f docker-compose.simple.yml stop autocura-dashboard

echo.
echo ===== REMOVENDO CONTAINER ANTIGO =====
docker-compose -f docker-compose.simple.yml rm -f autocura-dashboard

echo.
echo ===== INICIANDO DASHBOARD ATUALIZADO =====
docker-compose -f docker-compose.simple.yml up -d autocura-dashboard

echo.
echo ===== STATUS DOS CONTAINERS =====
docker-compose -f docker-compose.simple.yml ps

echo.
echo ====================================
echo DASHBOARD ATUALIZADO COM SUCESSO!
echo ====================================
echo.
echo Dashboard: http://localhost:8080
echo API: http://localhost:8001
echo.
echo O dashboard agora contem a Interface de Aprovacao Manual integrada!
echo Navegue para a aba "Aprovacoes" para testar.
echo.
pause 