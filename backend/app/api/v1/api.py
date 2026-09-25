from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, hazards, risk, vulnerability, relocation, prioritization, data_sources

api_router = APIRouter()

# Register endpoint routers
api_router.include_router(health.router, tags=["Health & Diagnostics"])
api_router.include_router(hazards.router, tags=["Hazard Zones"])
api_router.include_router(risk.router, tags=["Hazard Risk Assessment"])
api_router.include_router(vulnerability.router, tags=["Population Vulnerability Assessment"])
api_router.include_router(relocation.router, tags=["Relocation Site Suitability"])
api_router.include_router(prioritization.router, tags=["Relocation Prioritization & Decision Support"])
api_router.include_router(data_sources.router, tags=["Data Sources & Real-Time Ingestion"])

