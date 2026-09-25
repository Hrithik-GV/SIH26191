"""Alerts API Router: Emergency Warnings, Bulletins, and CAP Feeds."""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.common import PaginatedResponse, GeoJSONFeatureCollection
from backend.app.schemas.alert import AlertItem, AlertsSummaryResponse
from backend.app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Emergency Alerts & Warnings"])


@router.get(
    "",
    response_model=PaginatedResponse[AlertItem],
    summary="List Active Disaster Warnings & Emergency Alerts",
    description="Retrieve recorded disaster events and active CAP bulletins with pagination, severity filtering, and GeoJSON geometry.",
)
def list_alerts(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    severity: Optional[str] = Query(None, description="Filter by severity: CRITICAL, SEVERE, MODERATE, MINOR"),
    disaster_type: Optional[str] = Query(None, description="Filter by disaster type: landslide, flash_flood, cloudburst"),
    sort_by: str = Query("event_time", description="Sort field: event_time, severity, disaster_type"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[AlertItem]:
    """Retrieves paginated disaster alerts utilizing AlertService."""
    items, total = AlertService.get_alerts(
        db=db,
        page=page,
        page_size=page_size,
        severity=severity,
        disaster_type=disaster_type,
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
    summary="Get GeoJSON FeatureCollection of All Active Alerts",
    description="Returns RFC 7946 GeoJSON FeatureCollection representing active alert polygons and incident epicenters.",
)
def get_alerts_geojson(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    disaster_type: Optional[str] = Query(None, description="Filter by disaster type"),
    db: Session = Depends(get_db),
) -> GeoJSONFeatureCollection:
    """Returns GeoJSON FeatureCollection of alerts for map rendering."""
    return AlertService.get_feature_collection(
        db=db,
        severity=severity,
        disaster_type=disaster_type,
    )


@router.get(
    "/{id}",
    response_model=AlertItem,
    summary="Get Alert Details by ID",
    description="Retrieve details and GeoJSON geometry of a specific disaster event or warning bulletin.",
)
def get_alert_by_id(
    id: str,
    db: Session = Depends(get_db),
) -> AlertItem:
    """Retrieves a single disaster alert."""
    alert = AlertService.get_alert_by_id(db, id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disaster alert '{id}' not found.",
        )
    return alert
