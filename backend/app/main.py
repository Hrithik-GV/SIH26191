from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from backend.app.api.v1.api import api_router
from backend.app.api.v1.endpoints.health import get_health_status


from backend.app.ingestion.config import ingestion_settings
from backend.app.ingestion.scheduler import ingestion_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    logger.info(
        f"Starting {settings.PROJECT_NAME} v{settings.VERSION} "
        f"[env: {settings.ENVIRONMENT}, debug: {settings.DEBUG}]"
    )
    logger.info(f"Allowed CORS Origins: {settings.CORS_ORIGINS}")

    if ingestion_settings.auto_start_scheduler:
        logger.info("Initializing APScheduler real-time ingestion background worker...")
        ingestion_scheduler.start()

    yield

    if ingestion_scheduler.is_running:
        logger.info("Shutting down APScheduler background worker...")
        ingestion_scheduler.stop()

    logger.info(f"Shutting down {settings.PROJECT_NAME}...")


def create_application() -> FastAPI:
    """FastAPI application factory."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=(
            "Backend API for SIH 2026 Problem Statement 26191: "
            "Intelligent Identification of Hazard-Based Red Zones, "
            "Carrying Capacity Assessment, and Immediate Relocation Needs."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. CORS Configuration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Register Global Exception Handlers
    application.add_exception_handler(AppException, app_exception_handler)
    application.add_exception_handler(StarletteHTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(Exception, generic_exception_handler)

    # 3. Direct Root & Health Endpoints
    @application.get("/", tags=["Root"])
    async def root():
        return {
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "docs": "/docs",
            "health": "/health",
            "api_v1": settings.API_V1_STR,
        }

    # Direct /health endpoint for Docker healthchecks & direct monitoring
    application.add_api_route(
        "/health",
        get_health_status,
        methods=["GET"],
        tags=["Health & Diagnostics"],
        summary="Root Health Endpoint",
    )

    # 4. Include Versioned & Direct API Routes (/api and /api/v1)
    application.include_router(api_router, prefix="/api")
    if settings.API_V1_STR != "/api":
        application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
        log_level=settings.BACKEND_LOG_LEVEL.lower(),
    )
