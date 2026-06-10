"""Audit Reporting Main Application."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.audit_routes import router as audit_router


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="KYC Audit Reporting API",
        description="Regulator-Ready Reports and Audit Trail Management",
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

    app.include_router(audit_router, prefix="/api/v1", tags=["audit"])

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)