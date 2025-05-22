from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .api import router as api_router
from .observabilidade import app as flask_app
from fastapi.middleware.wsgi import WSGIMiddleware

# Criar aplicação FastAPI
app = FastAPI(title="Sistema de Autocura - Observabilidade")

# Montar rotas da API
app.include_router(api_router, prefix="/api/observabilidade")

# Configurar arquivos estáticos
app.mount("/static", StaticFiles(directory="src/observabilidade/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="src/observabilidade/templates")

# Montar aplicação Flask existente
app.mount("/", WSGIMiddleware(flask_app))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 