"""Analytics API Router: Situation Distributions, Histograms, and Visualizations."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.analytics import (
    AnalyticsOverviewResponse,
    RiskDistributionItem,
    VulnerabilityFactorComparison,
    CapacityVsNeedItem,
    HazardExposureItem,
)
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Visualizations"])


@router.get(
    "",
    response_model=AnalyticsOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Full Analytics Overview Package",
    description="Returns consolidated analytics payload for frontend charts (Recharts): risk histogram, vulnerability factors, capacity vs demand, and hazard exposure.",
)
def get_analytics_overview(db: Session = Depends(get_db)) -> AnalyticsOverviewResponse:
    """Computes comprehensive statistical distributions."""
    try:
        return AnalyticsService.get_analytics_overview(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable for analytics: {str(e)}",
        )


@router.get(
    "/risk-distribution",
    response_model=List[RiskDistributionItem],
    summary="Risk Severity Histogram Breakdown",
    description="Returns population and settlement distribution across 4 risk brackets (LOW, MODERATE, HIGH, CRITICAL).",
)
def get_risk_distribution(db: Session = Depends(get_db)) -> List[RiskDistributionItem]:
    """Returns risk distribution buckets."""
    try:
        return AnalyticsService.get_risk_distribution(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable for risk distribution: {str(e)}",
        )


@router.get(
    "/vulnerability-breakdown",
    response_model=List[VulnerabilityFactorComparison],
    summary="Vulnerability Demographic Factor Comparison",
    description="Returns average scores and critical habitation counts across all 9 demographic vulnerability factors.",
)
def get_vulnerability_breakdown(db: Session = Depends(get_db)) -> List[VulnerabilityFactorComparison]:
    """Returns demographic factor score comparison."""
    try:
        return AnalyticsService.get_vulnerability_breakdown(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable for vulnerability breakdown: {str(e)}",
        )


@router.get(
    "/capacity-vs-need",
    response_model=List[CapacityVsNeedItem],
    summary="Relocation Capacity vs Urgent Population Demand",
    description="Evaluates intake capacity buffer versus matched vulnerable population demand per site/zone.",
)
def get_capacity_vs_need(db: Session = Depends(get_db)) -> List[CapacityVsNeedItem]:
    """Returns capacity vs demand balance per candidate parcel."""
    try:
        return AnalyticsService.get_capacity_vs_need(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable for capacity vs need: {str(e)}",
        )


@router.get(
    "/hazard-exposure",
    response_model=List[HazardExposureItem],
    summary="Multi-Hazard Population Exposure Breakdown",
    description="Returns count of habitations and population exposed to individual hazard types.",
)
def get_hazard_exposure(db: Session = Depends(get_db)) -> List[HazardExposureItem]:
    """Returns population exposed per hazard type."""
    try:
        return AnalyticsService.get_hazard_exposure(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable for hazard exposure: {str(e)}",
        )
