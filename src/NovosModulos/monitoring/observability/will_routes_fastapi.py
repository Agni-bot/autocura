import os
from fastapi import APIRouter, HTTPException, Request, Body
from services.will_service import WillService
from typing import Optional
from services.config import settings

router = APIRouter(tags=["will"])

# Inicializa o WillService com a variável de ambiente
will_service = WillService(settings.WILL_API_URL)

@router.get("/status")
def get_status():
    status = will_service.get_system_status()
    if "error" in status:
        raise HTTPException(status_code=500, detail=status)
    return status

@router.post("/decision")
def get_decision(data: dict = Body(...)):
    asset = data.get("asset")
    volume = data.get("volume", 10000)
    if not asset:
        raise HTTPException(status_code=400, detail="Missing required parameter: asset")
    decision = will_service.get_trading_decision(asset, volume)
    if "error" in decision:
        raise HTTPException(status_code=500, detail=decision)
    return decision

@router.get("/sentiment")
def get_sentiment(currency_pair: Optional[str] = None):
    sentiment = will_service.get_news_sentiment(currency_pair)
    if "error" in sentiment:
        raise HTTPException(status_code=500, detail=sentiment)
    return sentiment

@router.get("/analysis/{asset}")
def get_analysis(asset: str):
    analysis = will_service.get_combined_analysis(asset)
    if "error" in analysis:
        raise HTTPException(status_code=500, detail=analysis)
    return analysis 