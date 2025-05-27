from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="AutoCura API", description="API para o sistema AutoCura", version="1.0.0")

class HealthCheck(BaseModel):
    status: str
    message: str

@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(status="ok", message="API funcionando corretamente.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 