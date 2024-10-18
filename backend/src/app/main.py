"""Main module for the Knowledge Table API service."""

import logging
from typing import Any, Dict

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import Settings, get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_str}/openapi.json",
)

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_router, prefix=settings.api_v1_str)


@app.get("/ping")
async def pong(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    """Ping the API to check if it's running."""
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing,
    }
