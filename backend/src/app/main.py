"""Main module for the Knowledge Table API service."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.dependencies import get_llm_service, get_settings
from app.services.vector_db.factory import VectorDBFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage the FastAPI lifespan for the application."""
    # Get the settings and LLM service
    settings = get_settings()
    llm_service = get_llm_service()
    logger.info(f"LLM Service: {llm_service}")
    logger.info(f"Vector DB Provider: {settings.vector_db_provider}")
    logger.info(f"API_V1_STR: {settings.API_V1_STR}")
    logger.info(f"Document router prefix: {api_router.prefix}/documents")

    # Create the vector database service
    vector_db_service = VectorDBFactory.create_vector_db_service(
        settings.vector_db_provider, llm_service
    )

    if vector_db_service is None:
        logger.error(
            "Failed to create vector database service. Check your configuration and ensure the correct provider is set."
        )
        raise ValueError("Failed to create vector database service")

    try:
        await vector_db_service.ensure_collection_exists()
        logger.info("Vector database collection ensured.")
    except Exception as e:
        logger.error(f"Failed to ensure collection exists: {str(e)}")
        raise

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
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
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def read_root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "hello, world."}


# The locate() function can be kept if it's used elsewhere in your project
def locate() -> None:
    """Find absolute path to this file and format for uvicorn."""
    import pathlib

    file_path = pathlib.Path(__file__).resolve()
    current_path = pathlib.Path.cwd()

    relative_path = file_path.relative_to(current_path)
    dotted_path = str(relative_path).strip(".py").strip("/").replace("/", ".")

    res = f"{dotted_path}:app"
    print(res)
