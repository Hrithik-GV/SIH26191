"""Pydantic schemas for the Executive Disaster Management Dashboard."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DashboardUrgentHabitation(BaseModel):
    """Compact summary of a high-priority vulnerable habitation for dashboard display."""
    habitation_id: str
    habitation_name: str
    district: str
    priority: str
    priority_score: int
    hazard_score: int
    vulnerability_score: int
    vulnerable_population: int
    recommended_site_name: Optional[str] = None
    recommended_site_distance_km: Optional[float] = None


class DashboardResponse(BaseModel):
    """
    Executive Disaster Management Dashboard metric aggregation.
    Provides key decision-support metrics, capacity metrics, and telemetry status.
    """
    total_habitations: int = Field(..., description="Total habitations surveyed in jurisdiction")
    habitations_in_critical_zones: int = Field(..., description="Habitations intersecting CRITICAL or HIGH red zones")
    population_at_risk: int = Field(..., description="Total vulnerable population residing in red zones")
    immediate_relocation_count: int = Field(..., description="Habitations classified as IMMEDIATE relocation urgency")
    short_term_relocation_count: int = Field(..., description="Habitations classified as SHORT_TERM relocation urgency")
    medium_term_relocation_count: int = Field(..., description="Habitations classified as MEDIUM_TERM relocation urgency")
    monitor_relocation_count: int = Field(default=0, description="Habitations classified under routine MONITOR status")
    total_relocation_capacity: int = Field(..., description="Total gross capacity across all candidate parcels")
    available_relocation_capacity: int = Field(..., description="Net available intake capacity after current occupancy")
    active_alerts: int = Field(..., description="Number of currently active emergency disaster bulletins / warnings")
    latest_data_timestamps: Dict[str, Optional[datetime]] = Field(
        ...,
        description="Most recent observation timestamps across rainfall, river stages, disaster alerts, and ingestion",
    )
    average_risk_score: float = Field(..., description="Regional average composite hazard risk score (0-100)")
    average_vulnerability_score: float = Field(..., description="Regional average socio-demographic vulnerability score (0-100)")
    capacity_deficit: int = Field(
        default=0,
        description="Net regional deficit if vulnerable population exceeds available relocation intake capacity",
    )
    top_urgent_habitations: List[DashboardUrgentHabitation] = Field(
        default_factory=list,
        description="Top habitations requiring immediate administrative evacuation",
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Dashboard computation timestamp")
