"""Pydantic schemas for Analytical Distributions and Visualization."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class RiskDistributionItem(BaseModel):
    """Histogram bucket representing risk severity distribution."""
    bracket: str = Field(..., description="Risk tier: LOW (0-30), MODERATE (31-60), HIGH (61-80), CRITICAL (81-100)")
    count: int = Field(..., description="Number of habitations in this tier")
    population: int = Field(..., description="Total population in this tier")
    vulnerable_population: int = Field(..., description="Vulnerable population in this tier")


class VulnerabilityFactorComparison(BaseModel):
    """Average factor scores across the jurisdiction."""
    factor: str = Field(..., description="Demographic vulnerability factor name")
    average_score: float = Field(..., description="Average normalized score (0-100)")
    highest_habitation: str = Field(..., description="Habitation experiencing highest score")
    critical_habitations_count: int = Field(..., description="Count of habitations scoring >= 80 on this factor")


class CapacityVsNeedItem(BaseModel):
    """Relocation capacity versus population relocation need per site/zone."""
    site_id: str
    site_name: str
    usable_area_sqm: float
    total_capacity: int
    available_capacity: int
    matched_demand_population: int
    balance: int = Field(..., description="Net surplus (+) or deficit (-)")
    status: str = Field(..., description="SURPLUS, BALANCED, DEFICIT")


class HazardExposureItem(BaseModel):
    """Multi-hazard exposure breakdown."""
    hazard_type: str = Field(..., description="Type of hazard: flood, landslide, debris_flow, compound")
    affected_habitations: int
    affected_population: int
    critical_overlap_count: int


class AnalyticsOverviewResponse(BaseModel):
    """Comprehensive analytical metrics suitable for Recharts and analytical dashboards."""
    total_habitations: int
    total_population: int
    total_vulnerable_population: int
    total_safe_capacity: int
    regional_net_balance: int
    risk_distribution: List[RiskDistributionItem]
    vulnerability_factors: List[VulnerabilityFactorComparison]
    capacity_vs_need: List[CapacityVsNeedItem]
    hazard_exposures: List[HazardExposureItem]
