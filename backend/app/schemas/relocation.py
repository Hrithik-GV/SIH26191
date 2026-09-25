"""Pydantic schemas for Relocation-Site Suitability & Proximity APIs."""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class RelocationSiteResponse(BaseModel):
    """Detailed candidate relocation site profile."""
    id: uuid.UUID
    name: str
    available_area: float = Field(..., description="Available land area in square meters")
    current_population: int = Field(..., description="Current occupancy count")
    estimated_capacity: int = Field(..., description="Maximum ecological and civil carrying capacity")
    available_capacity: int = Field(..., description="Remaining capacity buffer for displaced persons")
    water_score: float = Field(..., description="Water availability rating (0-10)")
    road_access_score: float = Field(..., description="Road accessibility rating (0-10)")
    healthcare_score: float = Field(..., description="Healthcare access rating (0-10)")
    hazard_score: float = Field(..., description="Residual hazard exposure rating (0-10, lower is safer)")
    suitability_score: float = Field(..., description="Composite suitability score (0-100)")
    geometry: Dict[str, Any] = Field(..., description="GeoJSON-compatible polygon boundary")


class CategoryScores(BaseModel):
    """0-100 normalized category sub-scores."""
    hazard_safety_score: int = Field(..., ge=0, le=100, description="Freedom from active floods, landslides, steep terrain")
    accessibility_score: int = Field(..., ge=0, le=100, description="Road access, arterial transit connectivity, logistics")
    infrastructure_score: int = Field(..., ge=0, le=100, description="Potable water, electricity grid, hospitals, schools")
    capacity_score: int = Field(..., ge=0, le=100, description="Available land parcel area and carrying capacity buffer")


class SiteSuitabilityAssessmentResponse(BaseModel):
    """Comprehensive explainable relocation-site suitability evaluation."""
    site_id: uuid.UUID
    site_name: str
    suitability_score: int = Field(..., ge=0, le=100, description="0-100 composite suitability score")
    overall_suitability_score: int = Field(..., ge=0, le=100, description="Overall suitability score (alias to suitability_score)")
    hazard_safety_score: int = Field(..., ge=0, le=100, description="Freedom from flood/landslide hazards and excessive slope")
    accessibility_score: int = Field(..., ge=0, le=100, description="Road access, arterial connectivity, transport egress")
    infrastructure_score: int = Field(..., ge=0, le=100, description="Potable water, electricity grid, hospitals, schools")
    capacity_score: int = Field(..., ge=0, le=100, description="Available land parcel area and carrying capacity buffer")
    classification: str = Field(..., description="HIGHLY SUITABLE, SUITABLE, CONDITIONALLY SUITABLE, UNSUITABLE")
    category_scores: CategoryScores
    factors: Dict[str, int] = Field(..., description="Individual granular factor scores")
    strengths: List[str] = Field(..., description="Key favorable site attributes and safety clearances")
    limitations: List[str] = Field(..., description="Civil constraints or mitigation requirements")
    available_capacity: int
    estimated_capacity: int
    available_area_sqm: float
    geometry: Optional[Dict[str, Any]] = Field(None, description="GeoJSON-compatible polygon boundary")
    calculated_at: datetime = Field(..., description="Assessment calculation timestamp")


class NearbyRelocationSiteResponse(BaseModel):
    """Candidate relocation parcel ranked by spatial proximity to affected habitation."""
    site_id: uuid.UUID
    site_name: str
    distance_km: float = Field(..., ge=0.0)
    distance_meters: float = Field(..., ge=0.0)
    available_capacity: int
    suitability_score: int = Field(..., ge=0, le=100)
    classification: str
    hazard_safe: bool = Field(True, description="True if parcel has verified zero intersection with severe hazard zones")
    proximity_rank: int = Field(..., ge=1)
    geometry: Optional[Dict[str, Any]] = None


class NearbySitesSummaryResponse(BaseModel):
    """Spatial query output ranking nearby safe relocation sites for a vulnerable habitation."""
    habitation_id: uuid.UUID
    habitation_name: str
    vulnerable_population: int
    total_sites_found: int
    recommended_sites: List[NearbyRelocationSiteResponse]
