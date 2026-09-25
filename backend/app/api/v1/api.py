from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, hazards, risk

api_router = APIRouter()

# Register endpoint routers
api_router.include_router(health.router, tags=["Health & Diagnostics"])
api_router.include_router(hazards.router, tags=["Hazard Zones"])
api_router.include_router(risk.router, tags=["Hazard Risk Assessment"])
