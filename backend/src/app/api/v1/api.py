"""API for the Knowledge Table."""

from fastapi import APIRouter

from app.api.v1.endpoints import document, graph, query

api_router = APIRouter()
api_router.include_router(
    document.router, prefix="/documents", tags=["documents"]
)
api_router.include_router(graph.router, prefix="/graphs", tags=["graphs"])
api_router.include_router(query.router, prefix="/queries", tags=["queries"])
