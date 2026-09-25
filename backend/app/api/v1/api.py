"""API v1 Central Router Registration."""

from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    health,
    dashboard,
    hazards,
    habitations,
    vulnerability,
    relocation_sites,
    relocation,
    alerts,
    data_sources,
    analytics,
    risk,
)

api_router = APIRouter()

# Register the 9 designated API groups + diagnostics
api_router.include_router(health.router, tags=["Health & Diagnostics"])
api_router.include_router(dashboard.router, tags=["Executive Dashboard"])
api_router.include_router(hazards.router, tags=["Hazard Zones"])
api_router.include_router(habitations.router, tags=["Habitations & Settlements"])
api_router.include_router(vulnerability.router, tags=["Population Vulnerability Assessment"])
api_router.include_router(relocation_sites.router, tags=["Relocation Sites"])
api_router.include_router(relocation.router, tags=["Relocation Urgency & Priorities"])
api_router.include_router(alerts.router, tags=["Emergency Alerts & Warnings"])
api_router.include_router(data_sources.router, tags=["Data Sources & Real-Time Ingestion"])
api_router.include_router(analytics.router, tags=["Analytics & Visualizations"])
api_router.include_router(risk.router, tags=["Hazard Risk Assessment"])
