"""KYC Agents Main Application."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agent_routes import router as agent_router
from app.api.workflow_routes import router as workflow_router
from app.api.health_routes import router as health_router
from app.api.identity_service import router as identity_router
from app.api.aml_service import router as aml_router
from app.api.adverse_media_service import router as media_router
from app.api.risk_service import router as risk_router
from app.services.observability import setup_observability

def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="KYC Agent Framework",
        description="AI Agents for Autonomous KYC Processing",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )

    # CORS middleware - secure configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:8080"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    )

    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # Routers
    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(agent_router, prefix="/api/agents", tags=["agents"])
    app.include_router(workflow_router, prefix="/api/workflows", tags=["workflows"])
    app.include_router(identity_router, prefix="/api", tags=["identity"])
    app.include_router(aml_router, prefix="/api/aml", tags=["aml"])
    app.include_router(media_router, prefix="/api", tags=["adverse-media"])
    app.include_router(risk_router, prefix="/api", tags=["risk"])

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)