"""Pydantic schemas for Habitation demographic and spatial entities."""

import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class HabitationItem(BaseModel):
    """Demographic and spatial representation of a settlement habitation."""
    id: uuid.UUID
    name: str
    district: str
    taluk: str
    state: str
    population: int
    vulnerable_population: int
    elderly_population: int
    children_population: int
    disabled_population: int
    kutcha_houses_pct: float
    elevation: float
    slope: float
    distance_to_road: float
    geometry: Optional[Dict[str, Any]] = Field(None, description="GeoJSON polygon or point boundary")


class HabitationDetail(HabitationItem):
    """Detailed habitation view with calculated risk and vulnerability previews."""
    hazard_risk_score: Optional[int] = None
    hazard_severity: Optional[str] = None
    vulnerability_score: Optional[int] = None
    vulnerability_severity: Optional[str] = None
    priority_tier: Optional[str] = None
