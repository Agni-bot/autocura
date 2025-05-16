from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/diagnostico", tags=["diagnostico"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def diagnostico_home(request: Request):
    return templates.TemplateResponse("diagnostico/index.html", {"request": request})

@router.get("/analysis", response_class=HTMLResponse)
async def analysis(request: Request):
    return templates.TemplateResponse("diagnostico/analysis.html", {"request": request}) 