"""Habitation API Router: Settlements, Demographics, GeoJSON Boundaries, and Risk Previews."""

import uuid
import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.common import PaginatedResponse, GeoJSONFeatureCollection
from backend.app.schemas.habitation import HabitationItem, HabitationDetail
from backend.app.schemas.risk import HabitationRiskResponse
from backend.app.schemas.vulnerability import HabitationVulnerabilityResponse
from backend.app.services.habitation_service import HabitationService
from backend.app.services.risk_engine import compute_habitation_risk_from_db
from backend.app.services.vulnerability_engine import compute_habitation_vulnerability_from_db

router = APIRouter(prefix="/habitations", tags=["Habitations & Settlements"])


@router.get(
    "",
    response_model=PaginatedResponse[HabitationItem],
    summary="List All Habitations with Pagination, Filtering & Sorting",
    description="Retrieve surveyed habitations with demographic metrics, GeoJSON polygon boundaries, and filtering.",
)
def list_habitations(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    district: Optional[str] = Query(None, description="Filter by district name (e.g. Wayanad)"),
    taluk: Optional[str] = Query(None, description="Filter by taluk name (e.g. Vythiri, Sulthan Bathery)"),
    search: Optional[str] = Query(None, description="Text search on name, district, or taluk"),
    sort_by: str = Query("name", description="Sort field: name, population, vulnerable_population, elevation, slope"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[HabitationItem]:
    """Retrieves paginated settlements with GeoJSON boundaries."""
    items, total = HabitationService.get_habitations(
        db=db,
        page=page,
        page_size=page_size,
        district=district,
        taluk=taluk,
        search=search,
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
    summary="Get GeoJSON FeatureCollection of All Habitations",
    description="Returns standard RFC 7946 GeoJSON FeatureCollection of habitation boundaries for map display.",
)
def get_habitations_geojson(
    district: Optional[str] = Query(None, description="Filter by district"),
    taluk: Optional[str] = Query(None, description="Filter by taluk"),
    db: Session = Depends(get_db),
) -> GeoJSONFeatureCollection:
    """Returns GeoJSON FeatureCollection of habitation settlements."""
    return HabitationService.get_feature_collection(
        db=db,
        district=district,
        taluk=taluk,
    )


@router.get(
    "/{id}",
    response_model=HabitationDetail,
    summary="Get Habitation Details by ID",
    description="Retrieve a single settlement's demographic profile, GeoJSON geometry, and computed risk/vulnerability tier.",
)
def get_habitation(
    id: uuid.UUID,
    db: Session = Depends(get_db),
) -> HabitationDetail:
    """Fetches single habitation profile with calculated risk and vulnerability previews."""
    hab = HabitationService.get_habitation_by_id(db, id)
    if not hab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitation with id '{id}' not found.",
        )
    return hab


@router.get(
    "/{id}/risk",
    response_model=HabitationRiskResponse,
    summary="Calculate Hazard Risk Score for Habitation",
    description="Computes transparent 0-100 multi-hazard risk score, 7-factor breakdown, and human-readable explanations.",
)
def get_habitation_risk(
    id: uuid.UUID,
    db: Session = Depends(get_db),
) -> HabitationRiskResponse:
    """Executes the hazard risk engine for this specific habitation."""
    risk = compute_habitation_risk_from_db(db, id)
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitation with id '{id}' not found.",
        )
    return risk


@router.get(
    "/{id}/vulnerability",
    response_model=HabitationVulnerabilityResponse,
    summary="Calculate Vulnerability Score for Habitation",
    description="Computes transparent 0-100 socio-demographic vulnerability score and 9-factor breakdown.",
)
def get_habitation_vulnerability(
    id: uuid.UUID,
    db: Session = Depends(get_db),
) -> HabitationVulnerabilityResponse:
    """Executes the population vulnerability engine for this specific habitation."""
    vuln = compute_habitation_vulnerability_from_db(db, id)
    if not vuln or "error" in vuln:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitation with id '{id}' not found.",
        )
    return HabitationVulnerabilityResponse(**vuln)
