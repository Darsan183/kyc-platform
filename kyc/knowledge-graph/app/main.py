"""Knowledge Graph Main Application."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.graph_routes import router as graph_router
from app.services.graph_service import KnowledgeGraphService


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="KYC Knowledge Graph API",
        description="Neo4j-based Relationship Discovery and Risk Analysis",
        version="1.0.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(graph_router, prefix="/api/v1", tags=["graph"])

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)