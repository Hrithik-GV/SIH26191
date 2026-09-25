"""Carrying-Capacity Assessment Configuration and Engineering Norms.

Implements multi-pillar civil and environmental carrying-capacity standards
for candidate relocation sites, adhering to Liebig's Law of the Minimum rather
than simplistic land-area multiplication.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field


class CapacityNormsConfig(BaseModel):
    """Resettlement planning standards and per-capita engineering norms."""
    
    # Spatial norms
    usable_area_ratio: float = Field(
        0.75,
        description="75% net buildable area after 25% reservation for internal roads, drainage setbacks, and green spaces",
    )
    sqm_per_person_norm: float = Field(
        35.0,
        description="35 sqm per person sustainable rural/peri-urban resettlement density (SPHERE & NBC guidelines)",
    )
    
    # Water norms
    water_lpcd_norm: float = Field(
        70.0,
        description="70 Litres Per Capita per Day (LPCD) under Jal Jeevan Mission rural piped supply standard",
    )
    
    # Sanitation norms
    sanitation_persons_per_core: int = Field(
        20,
        description="Maximum 20 persons per decentralized community sanitation / bio-digester core",
    )
    
    # Healthcare norms
    healthcare_persons_per_bed: int = Field(
        500,
        description="500 persons per active clinic/health-center bed within 5km travel buffer",
    )
    
    # Electricity norms
    electricity_kw_per_person: float = Field(
        0.35,
        description="0.35 kW continuous connected grid load per person (1.75 kW per 5-person household)",
    )


default_capacity_norms = CapacityNormsConfig()


# Transparent prototype planning assumptions
PROTOTYPE_CAPACITY_ASSUMPTIONS: Dict[str, str] = {
    "spatial_density_standard": "35 sqm usable land per person (SPHERE / National Building Code disaster resettlement norm)",
    "usable_land_coefficient": "75% net buildable area after civic reservations (drainage, easements, green buffer)",
    "water_consumption_norm": "70 Litres Per Capita per Day (LPCD) based on Jal Jeevan Mission rural piped water benchmark",
    "sanitation_standard": "1 decentralized sanitation / bio-septic processing unit per 20 persons",
    "healthcare_standard": "Primary healthcare capacity of 500 persons per primary health centre (PHC) bed unit within 5km",
    "electricity_standard": "0.35 kW continuous connected load per person (1.75 kW per average household)",
    "road_access_standard": "All-weather arterial highway connection with minimum 2-lane logistics convoy throughput",
    "capacity_model": "Liebig's Law of the Minimum: Sustainable carrying capacity is strictly capped by the scarcest critical civil resource",
    "framework_status": "PROTOTYPE_ASSUMPTIONS_CIVIC_RESIDENCE",
}
