from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Observabilidade")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="app/templates")

# Import and include routers
from app.routes import portal, monitoramento, diagnostico, gerador

app.include_router(portal.router)
app.include_router(monitoramento.router)
app.include_router(diagnostico.router)
app.include_router(gerador.router)

@app.get("/")
async def root():
    return {"message": "Observabilidade API is running"}