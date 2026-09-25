"""Hazard API Router: Red Zones, Severity Filtering, and GeoJSON Collections."""

import uuid
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.common import PaginatedResponse, GeoJSONFeatureCollection
from backend.app.schemas.risk import HazardZoneResponse
from backend.app.services.hazard_service import HazardService

router = APIRouter(prefix="/hazards", tags=["Hazard Zones"])


@router.get(
    "",
    response_model=PaginatedResponse[HazardZoneResponse],
    summary="List All Hazard Red Zones with Pagination & Filtering",
    description="Retrieve hazard red zones with GeoJSON polygon geometry, pagination, filtering by type/severity, and sorting.",
)
def list_hazard_zones(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    hazard_type: Optional[str] = Query(None, description="Filter by hazard type (e.g. landslide, flash_flood, cloudburst)"),
    severity: Optional[str] = Query(None, description="Filter by severity (VERY_HIGH, HIGH, MODERATE, LOW)"),
    min_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum risk score threshold"),
    sort_by: str = Query("risk_score", description="Sort field: risk_score, hazard_type, severity, timestamp"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[HazardZoneResponse]:
    """Retrieves paginated hazard zones utilizing HazardService."""
    items, total = HazardService.get_hazard_zones(
        db=db,
        page=page,
        page_size=page_size,
        hazard_type=hazard_type,
        severity=severity,
        min_score=min_score,
        sort_by=sort_by,
        order=order,
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items,
    )


@router.get(
    "/geojson",
    response_model=GeoJSONFeatureCollection,
    summary="Get GeoJSON FeatureCollection of All Hazard Zones",
    description="Returns standard RFC 7946 GeoJSON FeatureCollection optimized for MapLibre GL and GIS map layers.",
)
def get_hazard_zones_geojson(
    hazard_type: Optional[str] = Query(None, description="Filter by hazard type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    db: Session = Depends(get_db),
) -> GeoJSONFeatureCollection:
    """Returns GeoJSON FeatureCollection of hazard red zones."""
    return HazardService.get_feature_collection(
        db=db,
        hazard_type=hazard_type,
        severity=severity,
    )


@router.get(
    "/{id}",
    response_model=HazardZoneResponse,
    summary="Get Hazard Zone by ID",
    description="Retrieve a single hazard red zone details and GeoJSON polygon geometry.",
)
def get_hazard_zone(
    id: uuid.UUID,
    db: Session = Depends(get_db),
) -> HazardZoneResponse:
    """Fetches a single hazard zone by UUID."""
    hz = HazardService.get_hazard_zone_by_id(db, id)
    if not hz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hazard zone with id '{id}' not found.",
        )
    return hz
