import json
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.db.session import get_db
from backend.app.models.hazard_zone import HazardZone
from backend.app.schemas.risk import HazardZoneResponse

router = APIRouter()


@router.get(
    "/hazards",
    response_model=List[HazardZoneResponse],
    summary="List All Hazard Red Zones",
    description="Retrieve all hazard zones with GeoJSON-compatible geometry, filterable by hazard type and severity.",
)
def list_hazard_zones(
    hazard_type: Optional[str] = Query(None, description="Filter by hazard type (e.g. landslide, flash_flood)"),
    severity: Optional[str] = Query(None, description="Filter by severity (e.g. VERY_HIGH, HIGH, MODERATE)"),
    db: Session = Depends(get_db),
):
    """Fetch hazard red zones with PostGIS ST_AsGeoJSON geometry."""
    query = """
        SELECT 
            id,
            hazard_type,
            risk_score,
            severity,
            source,
            timestamp,
            ST_AsGeoJSON(geometry) AS geojson
        FROM hazard_zones
        WHERE 1=1
    """
    params = {}
    if hazard_type:
        query += " AND LOWER(hazard_type) = LOWER(:hazard_type)"
        params["hazard_type"] = hazard_type
    if severity:
        query += " AND UPPER(severity) = UPPER(:severity)"
        params["severity"] = severity

    query += " ORDER BY risk_score DESC;"

    try:
        rows = db.execute(text(query), params).mappings().all()
    except Exception as e:
        # Graceful fallback if database is in disconnected/initialization state
        return []

    results = []
    for r in rows:
        results.append(
            HazardZoneResponse(
                id=r["id"],
                hazard_type=r["hazard_type"],
                risk_score=r["risk_score"],
                severity=r["severity"],
                source=r["source"],
                timestamp=r["timestamp"],
                geometry=json.loads(r["geojson"]) if r["geojson"] else {},
            )
        )
    return results


@router.get(
    "/hazards/{id}",
    response_model=HazardZoneResponse,
    summary="Get Hazard Zone by ID",
    description="Retrieve single hazard red zone details and GeoJSON geometry.",
)
def get_hazard_zone(
    id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Fetch a single hazard zone by UUID."""
    stmt = text("""
        SELECT 
            id,
            hazard_type,
            risk_score,
            severity,
            source,
            timestamp,
            ST_AsGeoJSON(geometry) AS geojson
        FROM hazard_zones
        WHERE id = :hz_id;
    """)
    try:
        row = db.execute(stmt, {"hz_id": id}).mappings().first()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unavailable: {str(e)}",
        )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hazard zone with id '{id}' not found.",
        )

    return HazardZoneResponse(
        id=row["id"],
        hazard_type=row["hazard_type"],
        risk_score=row["risk_score"],
        severity=row["severity"],
        source=row["source"],
        timestamp=row["timestamp"],
        geometry=json.loads(row["geojson"]) if row["geojson"] else {},
    )
