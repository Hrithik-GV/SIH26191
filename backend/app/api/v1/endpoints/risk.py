import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.risk import HabitationRiskResponse, RiskSummaryResponse
from backend.app.services.risk_engine import (
    compute_habitation_risk_from_db,
    compute_all_habitations_risk_summary,
)

router = APIRouter()


@router.get(
    "/habitations/{id}/risk",
    response_model=HabitationRiskResponse,
    summary="Calculate Habitation Hazard Risk Score",
    description=(
        "Calculates transparent 0-100 hazard risk score for the specified habitation "
        "evaluating rainfall, flood, landslide, slope, historical events, drainage, and red zone overlap. "
        "Returns factor breakdown, human-readable explanations, severity tier, and GeoJSON geometry."
    ),
)
def get_habitation_risk(
    id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Calculate and return transparent hazard risk score for a habitation."""
    try:
        assessment = compute_habitation_risk_from_db(db, id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error evaluating risk from database: {str(e)}",
        )

    if "error" in assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitation with id '{id}' not found.",
        )

    return HabitationRiskResponse(**assessment)


@router.get(
    "/risk/summary",
    response_model=RiskSummaryResponse,
    summary="System-Wide Hazard Risk Summary",
    description=(
        "Evaluates risk across all monitored habitations and compiles summary telemetry, "
        "including severity breakdown (CRITICAL, HIGH, MODERATE, LOW), average risk score, "
        "and prioritized rankings with GeoJSON geometries."
    ),
)
def get_system_risk_summary(
    db: Session = Depends(get_db),
):
    """Aggregate risk assessment summary across all habitations."""
    try:
        summary = compute_all_habitations_risk_summary(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error calculating risk summary: {str(e)}",
        )

    return RiskSummaryResponse(**summary)
