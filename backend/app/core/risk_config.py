"""Scoring configuration and prototype thresholds for SIH 2026 Hazard Risk Engine.

Classification Thresholds (Prototype):
  0–30   = LOW
  31–60  = MODERATE
  61–80  = HIGH
  81–100 = CRITICAL
"""

from typing import Dict
from pydantic import BaseModel, Field


class RiskClassificationThresholds:
    """Severity classification brackets."""
    LOW_MAX = 30
    MODERATE_MAX = 60
    HIGH_MAX = 80
    CRITICAL_MAX = 100

    @classmethod
    def get_severity(cls, score: float) -> str:
        rounded_score = round(score)
        if rounded_score <= cls.LOW_MAX:
            return "LOW"
        elif rounded_score <= cls.MODERATE_MAX:
            return "MODERATE"
        elif rounded_score <= cls.HIGH_MAX:
            return "HIGH"
        else:
            return "CRITICAL"


class RiskWeightConfig(BaseModel):
    """
    Transparent weights assigned to each of the 7 risk factors.
    Weights must sum to 1.0 (100%).
    """
    rainfall_intensity: float = Field(0.20, description="Rainfall accumulation & intensity weight")
    hazard_zone_overlap: float = Field(0.20, description="Direct spatial overlap with hazard red zones")
    landslide_susceptibility: float = Field(0.15, description="Slope instability and landslide hazard zone index")
    flood_exposure: float = Field(0.15, description="River gauging danger exceedance & flood risk")
    elevation_slope: float = Field(0.10, description="Steepness and runoff acceleration factor")
    distance_to_rivers_drainage: float = Field(0.10, description="Proximity to drainage corridors and riverbeds")
    historical_disaster_frequency: float = Field(0.10, description="Historical disaster recurrence factor")

    def validate_weights(self) -> bool:
        total = (
            self.rainfall_intensity
            + self.hazard_zone_overlap
            + self.landslide_susceptibility
            + self.flood_exposure
            + self.elevation_slope
            + self.distance_to_rivers_drainage
            + self.historical_disaster_frequency
        )
        return abs(total - 1.0) < 1e-4


default_risk_weights = RiskWeightConfig()
