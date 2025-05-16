from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/gerador", tags=["gerador"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def gerador_home(request: Request):
    return templates.TemplateResponse("gerador/index.html", {"request": request})

@router.get("/generate", response_class=HTMLResponse)
async def generate(request: Request):
    return templates.TemplateResponse("gerador/generate.html", {"request": request}) 