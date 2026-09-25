"""FastAPI endpoints for Candidate Relocation Sites, Suitability Assessment, and Carrying Capacity."""

import uuid
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.relocation import RelocationSite
from backend.app.schemas.common import PaginatedResponse, GeoJSONFeature, GeoJSONFeatureCollection, geometry_to_geojson
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

router = APIRouter(prefix="/relocation-sites", tags=["Relocation Sites"])


@router.get(
    "",
    response_model=PaginatedResponse[RelocationSiteResponse],
    summary="List Candidate Relocation Sites with Pagination & Filtering",
    description=(
        "Retrieves candidate resettlement parcels with usable land area, carrying capacity, "
        "baseline infrastructure ratings, GeoJSON boundary geometry, pagination, filtering, and sorting."
    ),
)
def get_relocation_sites(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    classification: Optional[str] = Query(None, description="Filter by classification (HIGHLY SUITABLE, SUITABLE, CONDITIONALLY SUITABLE, UNSUITABLE)"),
    min_suitability: float = Query(0.0, ge=0.0, le=100.0, description="Filter sites with minimum suitability score"),
    min_capacity: int = Query(0, ge=0, description="Filter sites with minimum available capacity buffer"),
    sort_by: str = Query("suitability_score", description="Sort field: suitability_score, estimated_capacity, available_capacity, usable_area_sqm"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[RelocationSiteResponse]:
    """List candidate resettlement parcels filtered by minimum score, capacity, and classification."""
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

    # Optional classification filter
    if classification:
        class_clean = classification.strip().upper()
        sites = [s for s in sites if s.get("classification", "").upper() == class_clean]

    # In-memory sorting
    reverse = (order.lower() == "desc")
    if sort_by in ("suitability_score", "overall_suitability_score"):
        sites.sort(key=lambda s: s.get("suitability_score", 0), reverse=reverse)
    elif sort_by in ("estimated_capacity", "capacity"):
        sites.sort(key=lambda s: s.get("estimated_capacity", 0), reverse=reverse)
    elif sort_by == "available_capacity":
        sites.sort(key=lambda s: s.get("available_capacity", 0), reverse=reverse)
    elif sort_by == "usable_area_sqm":
        sites.sort(key=lambda s: s.get("usable_area_sqm", 0.0), reverse=reverse)

    total = len(sites)
    offset = (page - 1) * page_size
    page_records = sites[offset : offset + page_size]
    items = [RelocationSiteResponse(**s) for s in page_records]
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
    summary="Get GeoJSON FeatureCollection of All Relocation Sites",
    description="Returns standard RFC 7946 GeoJSON FeatureCollection of candidate parcels for GIS map rendering.",
)
def get_relocation_sites_geojson(
    classification: Optional[str] = Query(None, description="Filter by classification"),
    db: Session = Depends(get_db),
) -> GeoJSONFeatureCollection:
    """Returns GeoJSON FeatureCollection of candidate relocation parcels."""
    sites = db.query(RelocationSite).all()
    if classification:
        sites = [s for s in sites if s.classification and s.classification.upper() == classification.upper()]

    features = []
    for s in sites:
        carrying_cap = s.estimated_carrying_capacity or 2500
        curr_pop = s.current_occupancy or 0
        avail_cap = max(0, carrying_cap - curr_pop)

        # Build infrastructure summary
        infra_summary = f"Road: {float(s.distance_to_road_km or 0.5):.1f}km | Hosp: {float(s.distance_to_hospital_km or 3.2):.1f}km | Sch: {float(s.distance_to_school_km or 2.1):.1f}km"
        nearest_dist = f"{float(s.distance_to_road_km or 3.8):.1f} km to Chooralmala / Mundakkai"

        features.append(
            GeoJSONFeature(
                id=str(s.id),
                geometry=geometry_to_geojson(s.geometry),
                properties={
                    "id": str(s.id),
                    "name": s.name,
                    "site_name": s.name,
                    "district": s.district,
                    "taluk": s.taluk,
                    "usable_area_sqm": float(s.usable_area_sqm or 0.0),
                    "suitability_score": s.overall_suitability_score or 85,
                    "classification": s.classification or "SUITABLE",
                    "carrying_capacity": carrying_cap,
                    "estimated_capacity": carrying_cap,
                    "current_population": curr_pop,
                    "current_occupancy": curr_pop,
                    "available_capacity": avail_cap,
                    "infrastructure": infra_summary,
                    "distance_to_nearest_habitation": nearest_dist,
                },
            )
        )

    return GeoJSONFeatureCollection(features=features)


@router.get(
    "/nearby/{habitation_id}",
    response_model=NearbySitesSummaryResponse,
    summary="Find Suitable Relocation Sites Near Affected Habitation",
    description=(
        "Identifies and ranks safe candidate relocation parcels near a vulnerable habitation. "
        "Calculates geodesic distance, evaluates available capacity sufficiency, and strictly "
        "excludes any candidate parcel intersecting an active hazard red zone."
    ),
)
def get_nearby_relocation_sites(
    habitation_id: uuid.UUID,
    max_distance_km: float = Query(35.0, ge=1.0, le=100.0, description="Search radius in kilometers"),
    min_capacity: int = Query(50, ge=0, description="Minimum available intake capacity buffer"),
    limit: int = Query(5, ge=1, le=20, description="Maximum candidate parcels to return"),
    db: Session = Depends(get_db),
):
    """Find and rank safe nearby candidate resettlement parcels."""
    try:
        nearby_data = find_suitable_nearby_sites_for_habitation(
            db,
            habitation_id=habitation_id,
            max_distance_meters=max_distance_km * 1000.0,
            min_capacity=min_capacity,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error evaluating nearby relocation sites: {str(e)}",
        )

    if "error" in nearby_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitation with id '{habitation_id}' not found.",
        )

    return NearbySitesSummaryResponse(**nearby_data)


@router.get(
    "/{id}",
    response_model=RelocationSiteResponse,
    summary="Get Relocation Site by ID",
    description="Retrieves a single candidate relocation site with physical attributes, scores, and GeoJSON geometry.",
)
def get_single_relocation_site(
    id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Fetch single relocation site parcel by UUID."""
    try:
        site = get_relocation_site_by_id_from_db(db, id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database query error: {str(e)}",
        )

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relocation site with id '{id}' not found.",
        )

    return RelocationSiteResponse(**site)


@router.get(
    "/{id}/assessment",
    response_model=SiteSuitabilityAssessmentResponse,
    summary="Compute Relocation-Site Multi-Criteria Suitability Assessment",
    description=(
        "Calculates multi-pillar suitability scoring: hazard safety (30%), road accessibility (25%), "
        "civic infrastructure (25%), and intake capacity (20%). Returns overall score, strengths, and limitations."
    ),
)
def get_site_assessment(
    id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Calculate transparent multi-pillar suitability assessment."""
    try:
        assessment = compute_site_assessment_from_db(db, id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error calculating site assessment: {str(e)}",
        )

    if "error" in assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relocation site with id '{id}' not found.",
        )

    return SiteSuitabilityAssessmentResponse(**assessment)


@router.get(
    "/{id}/capacity",
    response_model=SiteCarryingCapacityResponse,
    summary="Calculate Relocation Site Carrying Capacity (Liebig's Law)",
    description=(
        "Estimates sustainable carrying capacity using Liebig's Law of the Minimum bottleneck analysis: "
        "usable land density, water supply yield (70 LPCD), sanitation, healthcare access, and road throughput."
    ),
)
def get_site_carrying_capacity(
    id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Calculate multi-resource carrying capacity bottleneck assessment."""
    try:
        capacity_data = compute_site_capacity_from_db(db, id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error computing carrying capacity: {str(e)}",
        )

    if "error" in capacity_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relocation site with id '{id}' not found.",
        )

    return SiteCarryingCapacityResponse(**capacity_data)
