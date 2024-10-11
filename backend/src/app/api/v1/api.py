"""API for the Knowledge Table."""

from fastapi import APIRouter

from app.api.v1.endpoints import document, graph, query

api_router = APIRouter()
api_router.include_router(
    document.router, prefix="/document", tags=["document"]
)
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
