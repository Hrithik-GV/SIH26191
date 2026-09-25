"""Relocation Prioritization Configuration, Weights and Classification Thresholds."""

from typing import Dict, Any
from pydantic import BaseModel, Field


class RelocationPriorityThresholds:
    """Prototype urgency classification brackets for habitations.
    
    IMPORTANT: These are prototype classifications for research and demonstration
    purposes and must not be represented as official statutory government thresholds.
    """
    IMMEDIATE_MIN = 81
    SHORT_TERM_MIN = 61
    MEDIUM_TERM_MIN = 31
    MONITOR_MIN = 0

    @classmethod
    def get_priority(cls, score: int) -> str:
        """Map 0-100 relocation priority score to urgency classification."""
        if score >= cls.IMMEDIATE_MIN:
            return "IMMEDIATE"
        elif score >= cls.SHORT_TERM_MIN:
            return "SHORT_TERM"
        elif score >= cls.MEDIUM_TERM_MIN:
            return "MEDIUM_TERM"
        else:
            return "MONITOR"


class RelocationPriorityWeightConfig(BaseModel):
    """Transparent weights for the 7 prototype relocation prioritization factors."""
    hazard_risk: float = Field(0.25, description="Composite environmental hazard risk (25%)")
    population_vulnerability: float = Field(0.20, description="Socio-demographic vulnerability of residents (20%)")
    exposed_population: float = Field(0.15, description="Scale of human lives at immediate risk (15%)")
    disaster_history: float = Field(0.10, description="Recurrence of past landslide or flood disasters (10%)")
    infrastructure_vulnerability: float = Field(0.10, description="Housing and civil infrastructure fragility (10%)")
    evacuation_difficulty: float = Field(0.10, description="Single egress, terrain cutoff, and bridge bottlenecks (10%)")
    site_availability: float = Field(0.10, description="Availability and proximity of safe relocation parcels (10%)")

    def validate_weights(self) -> bool:
        total = (
            self.hazard_risk
            + self.population_vulnerability
            + self.exposed_population
            + self.disaster_history
            + self.infrastructure_vulnerability
            + self.evacuation_difficulty
            + self.site_availability
        )
        return abs(total - 1.0) < 1e-5


default_priority_weights = RelocationPriorityWeightConfig()


DECISION_SUPPORT_DISCLAIMER: str = (
    "DISCLAIMER: This relocation prioritization assessment and site recommendation is an "
    "automated decision-support analytical output intended for authorized disaster management "
    "authorities (NDMA, SDMA, DDMA). This system does NOT make final executive relocation decisions; "
    "all relocation actions and administrative directives must be verified and issued by designated human authorities."
)

PROTOTYPE_PRIORITY_ASSUMPTIONS: Dict[str, str] = {
    "classification_nature": "Prototype experimental thresholds (81-100 IMMEDIATE, 61-80 SHORT_TERM, 31-60 MEDIUM_TERM, 0-30 MONITOR)",
    "official_status": "Non-governmental decision support prototype; not an official statutory mandate",
    "site_matching_heuristic": "Multi-criteria spatial ranking: 40% proximity (ellipsoidal distance), 35% parcel suitability score, 25% capacity sufficiency",
    "safety_guarantee": "Candidate relocation parcels overlapping active VERY_HIGH hazard zones are strictly excluded",
    "human_in_the_loop": "Authorized disaster management officials must conduct ground verification prior to executing physical relocation",
}
