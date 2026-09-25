"""Pydantic schemas for Relocation Prioritization and Decision-Support APIs."""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class RecommendedRelocationSiteDetail(BaseModel):
    """Details of the spatial match for a candidate relocation parcel."""
    site_id: uuid.UUID
    site_name: str
    distance_km: float = Field(..., ge=0.0, description="Spatial ellipsoidal distance in kilometers")
    distance_meters: float = Field(..., ge=0.0)
    suitability_score: int = Field(..., ge=0, le=100)
    classification: str
    available_capacity: int = Field(..., ge=0)
    capacity_sufficient: bool = Field(..., description="True if parcel can absorb the entire vulnerable population")
    match_score: float = Field(..., ge=0.0, le=100.0, description="Composite spatial proximity, suitability, and capacity score")
    geometry: Optional[Dict[str, Any]] = None


class HabitationPriorityItem(BaseModel):
    """Summary item for habitation priority ranking."""
    habitation_id: uuid.UUID
    habitation_name: str
    district: str
    state: str
    priority_score: int = Field(..., ge=0, le=100, description="0-100 relocation urgency score")
    priority: str = Field(..., description="IMMEDIATE, SHORT_TERM, MEDIUM_TERM, MONITOR")
    vulnerable_population: int
    total_population: int
    hazard_score: int
    vulnerability_score: int
    reasons: List[str]
    recommended_site_id: Optional[uuid.UUID] = None
    recommended_site_name: Optional[str] = None
    recommended_site_distance_km: Optional[float] = None


class HabitationPrioritiesSummaryResponse(BaseModel):
    """Regional summary ranking all habitations by relocation urgency."""
    total_habitations: int
    immediate_count: int
    short_term_count: int
    medium_term_count: int
    monitor_count: int
    average_priority_score: float
    priorities: List[HabitationPriorityItem]
    decision_support_disclaimer: str
    calculated_at: datetime


class HabitationPriorityResponse(BaseModel):
    """Granular relocation priority assessment for a single habitation."""
    habitation_id: uuid.UUID
    habitation_name: str
    district: str
    state: str
    priority_score: int = Field(..., ge=0, le=100)
    priority: str
    factors: Dict[str, int] = Field(..., description="7 individual factor sub-scores (0-100)")
    reasons: List[str] = Field(..., description="Transparent, explainable justifications for priority rating")
    vulnerable_population: int
    total_population: int
    recommended_site: Optional[RecommendedRelocationSiteDetail] = None
    decision_support_disclaimer: str
    geometry: Optional[Dict[str, Any]] = None
    calculated_at: datetime


class HabitationRelocationRecommendationResponse(BaseModel):
    """Complete actionable relocation recommendation mapping habitation to best safe site."""
    habitation_id: uuid.UUID
    habitation_name: str
    district: str
    state: str
    priority: str
    priority_score: int
    vulnerable_population: int
    reasons: List[str]
    best_suitable_site: Optional[RecommendedRelocationSiteDetail] = None
    alternative_sites: List[RecommendedRelocationSiteDetail] = Field(default_factory=list)
    decision_support_disclaimer: str
    calculated_at: datetime
