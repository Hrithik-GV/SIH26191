from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DatabaseStatus(BaseModel):
    connected: bool = Field(..., description="PostgreSQL connection status")
    latency_ms: Optional[float] = Field(None, description="Ping latency in milliseconds")
    postgis_version: Optional[str] = Field(None, description="PostGIS extension version if available")
    detail: str = Field(..., description="Status summary or error details")


class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    app_name: str = Field(..., example="SIH 2026 - Disaster Risk & Relocation Assessment")
    version: str = Field(..., example="1.0.0")
    environment: str = Field(..., example="development")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    database: DatabaseStatus
    services: Dict[str, str] = Field(
        default_factory=lambda: {
            "api": "operational",
            "gis_layer": "configured",
            "ml_layer": "configured",
        }
    )
