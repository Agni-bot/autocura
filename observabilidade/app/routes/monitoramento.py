from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/monitoramento", tags=["monitoramento"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def monitoramento_home(request: Request):
    return templates.TemplateResponse("monitoramento/index.html", {"request": request})

@router.get("/metrics", response_class=HTMLResponse)
async def metrics(request: Request):
    return templates.TemplateResponse("monitoramento/metrics.html", {"request": request}) 