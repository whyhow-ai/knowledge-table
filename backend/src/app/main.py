"""Main module for the Knowledge Table API service."""

import logging
from typing import Dict
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings, Settings
from app.api.v1.api import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=get_settings().project_name,
    openapi_url=f"{get_settings().api_v1_str}/openapi.json",
)

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().project_name,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the API router
app.include_router(api_router, prefix=get_settings().api_v1_str)


@app.get("/ping")
async def pong(settings: Settings = Depends(get_settings)):
    return {
        "ping": "pong!",
        "environment": settings.environment,
        "testing": settings.testing
    }
