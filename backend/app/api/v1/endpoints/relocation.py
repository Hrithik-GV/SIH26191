"""FastAPI endpoints for Relocation-Site Suitability Assessment & Spatial Queries."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.relocation import (
    RelocationSiteResponse,
    SiteSuitabilityAssessmentResponse,
    NearbySitesSummaryResponse,
)
from backend.app.schemas.capacity import SiteCarryingCapacityResponse
from backend.app.services.suitability_engine import (
    get_all_relocation_sites_from_db,
    get_relocation_site_by_id_from_db,
    compute_site_assessment_from_db,
    find_suitable_nearby_sites_for_habitation,
)
from backend.app.services.capacity_engine import compute_site_capacity_from_db

router = APIRouter()


@router.get(
    "/relocation-sites",
    response_model=List[RelocationSiteResponse],
    summary="List Candidate Relocation Sites",
    description=(
        "Retrieves all candidate resettlement sites with available land parcel area, "
        "carrying capacity, baseline infrastructure ratings, and GeoJSON boundary geometry."
    ),
)
def get_relocation_sites(
    min_suitability: float = Query(0.0, ge=0.0, le=100.0, description="Filter sites with minimum suitability score"),
    min_capacity: int = Query(0, ge=0, description="Filter sites with minimum available capacity buffer"),
    db: Session = Depends(get_db),
):
    """List candidate resettlement parcels filtered by minimum score and capacity."""
    try:
        sites = get_all_relocation_sites_from_db(
            db,
            min_suitability=min_suitability,
            min_capacity=min_capacity,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database query error fetching relocation sites: {str(e)}",
        )

    return [RelocationSiteResponse(**s) for s in sites]


@router.get(
    "/relocation-sites/nearby/{habitation_id}",
    response_model=NearbySitesSummaryResponse,
    summary="Find Suitable Relocation Sites Near Affected Habitation",
    description=(
        "Performs spatial GIS ellipsoidal distance analysis to rank candidate relocation parcels "
        "within proximity radius of a vulnerable habitation. Strictly excludes any sites overlapping "
        "active VERY_HIGH hazard zones."
    ),
)
def get_nearby_relocation_sites(
    habitation_id: uuid.UUID,
    max_distance_km: float = Query(35.0, ge=1.0, le=200.0, description="Search radius in kilometers"),
    min_capacity: int = Query(50, ge=0, description="Minimum available capacity buffer"),
    limit: int = Query(5, ge=1, le=50, description="Max candidate sites to rank"),
    db: Session = Depends(get_db),
):
    """Rank nearby candidate resettlement sites for a specific vulnerable habitation."""
    try:
        result = find_suitable_nearby_sites_for_habitation(
            db=db,
            habitation_id=habitation_id,
            max_distance_meters=max_distance_km * 1000.0,
            min_capacity=min_capacity,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Spatial query error finding nearby sites: {str(e)}",
        )

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitation with id '{habitation_id}' not found.",
        )

    return NearbySitesSummaryResponse(**result)


@router.get(
    "/relocation-sites/{id}",
    response_model=RelocationSiteResponse,
    summary="Get Relocation Site Profile",
    description="Fetches detailed attributes, capacity figures, and GeoJSON geometry for a single candidate site.",
)
def get_relocation_site(
    id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Retrieve single relocation site by UUID."""
    try:
        site = get_relocation_site_by_id_from_db(db, id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database query error retrieving relocation site: {str(e)}",
        )

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relocation site with id '{id}' not found.",
        )

    return RelocationSiteResponse(**site)


@router.get(
    "/relocation-sites/{id}/assessment",
    response_model=SiteSuitabilityAssessmentResponse,
    summary="Calculate Relocation-Site Suitability Assessment",
    description=(
        "Calculates transparent 0-100 composite suitability score considering flood risk, landslide risk, "
        "slope, elevation, available land area, road access, hospital/school proximity, water & electricity availability, "
        "current occupancy, and carrying capacity. Generates category sub-scores (hazard_safety_score, accessibility_score, "
        "infrastructure_score, capacity_score), strengths, limitations, and classification bracket."
    ),
)
def get_site_assessment(
    id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Calculate and return explainable suitability evaluation for a relocation site."""
    try:
        assessment = compute_site_assessment_from_db(db, id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error evaluating site suitability: {str(e)}",
        )

    if "error" in assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relocation site with id '{id}' not found.",
        )

    return SiteSuitabilityAssessmentResponse(**assessment)


@router.get(
    "/relocation-sites/{id}/capacity",
    response_model=SiteCarryingCapacityResponse,
    summary="Calculate Relocation-Site Carrying Capacity Assessment",
    description=(
        "Calculates transparent sustainable carrying capacity for a candidate relocation site. "
        "Adheres to Liebig's Law of the Minimum (bottleneck principle) evaluating usable buildable land area, "
        "safe resettlement density, potable water yield (70 LPCD), decentralized sanitation, healthcare surge, "
        "electricity grid limits, road accessibility, and existing population. Returns gross capacity, "
        "infrastructure capacity, water capacity, final capacity, available capacity, and dynamic limiting factors."
    ),
)
def get_site_capacity(
    id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Calculate and return transparent multi-pillar carrying capacity assessment for a relocation site."""
    try:
        capacity_result = compute_site_capacity_from_db(db, id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error evaluating site carrying capacity: {str(e)}",
        )

    if "error" in capacity_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relocation site with id '{id}' not found.",
        )

    return SiteCarryingCapacityResponse(**capacity_result)
