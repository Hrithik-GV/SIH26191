from datetime import datetime, timezone
from fastapi import APIRouter, status
from backend.app.core.config import settings
from backend.app.schemas.health import HealthResponse, DatabaseStatus
from backend.app.db.session import check_database_connection

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System Health & Diagnostic Check",
    description="Returns live system health status, timestamp, environment, database and subsystem readiness.",
)
async def get_health_status() -> HealthResponse:
    """Return backend runtime status, timestamp, and database connectivity."""
    db_check = check_database_connection()
    overall_status = "healthy" if db_check["connected"] else "degraded"

    return HealthResponse(
        status=overall_status,
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
        database=DatabaseStatus(
            connected=db_check["connected"],
            latency_ms=db_check.get("latency_ms"),
            postgis_version=db_check.get("postgis_version"),
            detail=db_check.get("detail", ""),
        ),
        services={
            "api": "operational",
            "gis_layer": "configured",
            "ml_layer": "configured",
        },
    )


@router.get(
    "/ping",
    summary="Simple Liveness Ping",
    description="Fast lightweight ping returning pong and server timestamp.",
)
async def ping():
    return {
        "ping": "pong",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "online",
    }
