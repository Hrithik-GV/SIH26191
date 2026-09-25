"""Scoring configuration and prototype thresholds for the Relocation-Site Suitability Engine.

Suitability Classification Brackets (Prototype):
  80–100 = HIGHLY SUITABLE
  60–79  = SUITABLE
  40–59  = CONDITIONALLY SUITABLE
  0–39   = UNSUITABLE

Category Weight Distribution:
  1. Hazard Safety Score (35%): Flood clearance, landslide safety, terrain slope, elevation
  2. Infrastructure Score (25%): Potable water, electricity grid, hospitals, schools
  3. Accessibility Score (20%): All-weather road access, transport connectivity, transit corridors
  4. Capacity Score (20%): Usable parcel area, available carrying capacity buffer, low occupancy ratio
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class SuitabilityClassificationThresholds:
    """Prototype classification brackets for candidate relocation sites."""
    UNSUITABLE_MAX = 39
    CONDITIONALLY_SUITABLE_MAX = 59
    SUITABLE_MAX = 79
    HIGHLY_SUITABLE_MAX = 100

    @classmethod
    def get_classification(cls, score: float) -> str:
        rounded = round(score)
        if rounded <= cls.UNSUITABLE_MAX:
            return "UNSUITABLE"
        elif rounded <= cls.CONDITIONALLY_SUITABLE_MAX:
            return "CONDITIONALLY SUITABLE"
        elif rounded <= cls.SUITABLE_MAX:
            return "SUITABLE"
        return "HIGHLY SUITABLE"


class CategoryWeightConfig(BaseModel):
    """Weights for the 4 core suitability category scores summing to 1.0 (100%)."""
    hazard_safety: float = Field(0.35, description="Freedom from flood, landslide, and steep terrain risk")
    infrastructure: float = Field(0.25, description="Potable water, electricity, hospitals, schools")
    accessibility: float = Field(0.20, description="All-weather road connectivity and transport logistics")
    capacity: float = Field(0.20, description="Available land area, carrying capacity buffer, occupancy")

    def validate_weights(self) -> bool:
        total = self.hazard_safety + self.infrastructure + self.accessibility + self.capacity
        return abs(total - 1.0) < 1e-4


class HazardSafetyWeightConfig(BaseModel):
    """Sub-weights for hazard safety evaluation (summing to 1.0)."""
    flood_risk: float = 0.35
    landslide_risk: float = 0.35
    slope: float = 0.20
    elevation: float = 0.10


class InfrastructureWeightConfig(BaseModel):
    """Sub-weights for civil infrastructure evaluation (summing to 1.0)."""
    water_availability: float = 0.35
    electricity: float = 0.25
    hospital_proximity: float = 0.25
    school_proximity: float = 0.15


class AccessibilityWeightConfig(BaseModel):
    """Sub-weights for transport accessibility (summing to 1.0)."""
    road_access: float = 0.65
    transit_connectivity: float = 0.35


class CapacityWeightConfig(BaseModel):
    """Sub-weights for carrying capacity (summing to 1.0)."""
    available_capacity_buffer: float = 0.45
    available_land_area: float = 0.35
    occupancy_ratio: float = 0.20


default_category_weights = CategoryWeightConfig()
default_hazard_weights = HazardSafetyWeightConfig()
default_infra_weights = InfrastructureWeightConfig()
default_access_weights = AccessibilityWeightConfig()
default_capacity_weights = CapacityWeightConfig()
