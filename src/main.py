from typing import List, Optional, Dict, Any
from fastapi import APIRouter, FastAPI, HTTPException, Depends, status
import uvicorn
import uuid

app = FastAPI(
    title="Hasaki CRM API",
    description="API for Hasaki CRM system",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to Hasaki CRM API"}


from .api import prospects
api_router = APIRouter()
api_router.include_router(prospects.router, prefix="/prospects", tags=["Prospects"])

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8082, reload=True)
