"""Main module for the Knowledge Table API service."""

import pathlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from knowledge_table_api.dependencies import get_milvus_client, get_settings
from knowledge_table_api.services.vector import ensure_collection_exists
from knowledge_table_api.routers import document, graph, query

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = get_milvus_client()
    settings = get_settings()
    ensure_collection_exists(client, settings)
    yield
    # Add any cleanup code here if needed

app = FastAPI(lifespan=lifespan)

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document.router)
app.include_router(query.router)
app.include_router(graph.router)


def locate() -> None:
    """Find absolute path to this file and format for uvicorn."""
    file_path = pathlib.Path(__file__).resolve()
    current_path = pathlib.Path.cwd()

    relative_path = file_path.relative_to(current_path)
    dotted_path = str(relative_path).strip(".py").strip("/").replace("/", ".")

    res = f"{dotted_path}:app"
    print(res)
