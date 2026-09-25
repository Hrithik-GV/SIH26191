import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class GeoJSONGeometry(BaseModel):
    type: str = Field(..., examples=["Polygon", "Point", "MultiPolygon"])
    coordinates: Any = Field(..., description="GeoJSON coordinates array")


class RiskFactors(BaseModel):
    rainfall: int = Field(..., ge=0, le=100, description="Rainfall intensity factor score (0-100)")
    flood_exposure: int = Field(..., ge=0, le=100, description="River gauging and flood exposure score (0-100)")
    landslide: int = Field(..., ge=0, le=100, description="Landslide susceptibility score (0-100)")
    elevation_slope: int = Field(..., ge=0, le=100, description="Terrain elevation and slope angle score (0-100)")
    historical_events: int = Field(..., ge=0, le=100, description="Historical disaster event frequency score (0-100)")
    drainage_proximity: int = Field(..., ge=0, le=100, description="Distance to river/drainage corridor score (0-100)")
    hazard_overlap: int = Field(..., ge=0, le=100, description="Spatial hazard red zone overlap score (0-100)")


class HabitationRiskResponse(BaseModel):
    habitation_id: uuid.UUID
    habitation_name: str
    district: str
    state: str
    population: int
    vulnerable_population: int
    overall_score: int = Field(..., ge=0, le=100, description="Composite hazard risk score (0-100)")
    severity: str = Field(..., description="Severity classification: LOW, MODERATE, HIGH, CRITICAL")
    factors: Dict[str, int] = Field(..., description="Individual factor scores breakdown")
    explanation: List[str] = Field(..., description="Human-readable transparent explanations")
    geometry: Optional[Dict[str, Any]] = Field(None, description="GeoJSON-compatible boundary geometry")
    calculated_at: datetime = Field(..., description="Calculation timestamp")


class HazardZoneResponse(BaseModel):
    id: uuid.UUID
    hazard_type: str
    risk_score: float
    severity: str
    source: str
    timestamp: datetime
    geometry: Dict[str, Any] = Field(..., description="GeoJSON-compatible polygon geometry")


class RiskSummaryResponse(BaseModel):
    total_habitations: int
    severity_breakdown: Dict[str, int]
    average_risk_score: float
    critical_habitations_count: int
    habitations: List[HabitationRiskResponse]
