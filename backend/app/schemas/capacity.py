"""Pydantic schemas for Relocation-Site Carrying Capacity Assessment APIs."""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field


class FactorCapacitiesBreakdown(BaseModel):
    """Individual capacity limits computed across all civil and ecological pillars."""
    usable_land: int = Field(..., ge=0, description="Capacity based on usable buildable land area and density norm")
    water_supply: int = Field(..., ge=0, description="Capacity based on daily potable water supply yield and LPCD norm")
    sanitation: int = Field(..., ge=0, description="Capacity based on decentralized sewage and septic absorption units")
    healthcare: int = Field(..., ge=0, description="Capacity supported by accessible primary healthcare and hospital beds")
    electricity: int = Field(..., ge=0, description="Capacity supported by power grid transmission and transformer capacity")
    road_access: int = Field(..., ge=0, description="Capacity supported by road lane width and emergency logistics throughput")


class SiteCarryingCapacityResponse(BaseModel):
    """Transparent multi-pillar carrying capacity assessment for a candidate relocation parcel."""
    site_id: Any = Field(..., description="Unique relocation site identifier (UUID, integer, or string)")
    site_name: Optional[str] = Field(None, description="Descriptive parcel name")
    gross_capacity: int = Field(..., ge=0, description="Theoretical maximum population based on physical buildable land area")
    infrastructure_capacity: int = Field(..., ge=0, description="Bottleneck capacity sustained by composite civil utilities (sanitation, healthcare, electricity, roads)")
    water_capacity: int = Field(..., ge=0, description="Maximum population sustainable by local potable water yield (70 LPCD)")
    final_capacity: int = Field(..., ge=0, description="Sustainable carrying capacity capped by the most limiting critical civil resource")
    current_population: int = Field(..., ge=0, description="Existing population residing on or already relocated to the site")
    available_capacity: int = Field(..., ge=0, description="Net remaining capacity buffer available for displaced persons")
    limiting_factors: List[str] = Field(..., description="Identified resource constraints that reduce capacity below gross land area")
    factor_capacities: Optional[FactorCapacitiesBreakdown] = Field(None, description="Detailed per-factor capacity breakdown")
    assumptions: Optional[Dict[str, str]] = Field(None, description="Documented engineering and civic planning assumptions")
    calculated_at: datetime = Field(..., description="Calculation timestamp")
