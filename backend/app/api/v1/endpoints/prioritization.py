"""FastAPI endpoints for Relocation Prioritization and Actionable Recommendations."""

import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.priority import (
    HabitationPrioritiesSummaryResponse,
    HabitationPriorityResponse,
    HabitationRelocationRecommendationResponse,
)
from backend.app.services.priority_engine import (
    compute_all_habitations_priorities_summary,
    compute_habitation_priority_from_db,
)

router = APIRouter(prefix="/relocation")


@router.get(
    "/priorities",
    response_model=HabitationPrioritiesSummaryResponse,
    summary="Rank Habitations by Relocation Urgency",
    description=(
        "Calculates transparent 0-100 relocation priority scores across all monitored habitations, "
        "classifying urgency into IMMEDIATE (81-100), SHORT_TERM (61-80), MEDIUM_TERM (31-60), and MONITOR (0-30). "
        "Identifies best safe candidate resettlement site for each settlement. "
        "NOTE: Decision-support tool for authorized disaster management officials; does not replace executive command."
    ),
)
def get_relocation_priorities(
    db: Session = Depends(get_db),
):
    """Compile multi-habitation relocation priority rankings and regional breakdown."""
    try:
        summary = compute_all_habitations_priorities_summary(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error calculating relocation priorities summary: {str(e)}",
        )

    return HabitationPrioritiesSummaryResponse(**summary)


@router.get(
    "/priorities/{habitation_id}",
    response_model=HabitationPriorityResponse,
    summary="Calculate Habitation Relocation Priority",
    description=(
        "Calculates 0-100 relocation priority score and urgency classification for a specific habitation. "
        "Evaluates multi-hazard risk, demographic vulnerability, exposed population scale, disaster history, "
        "infrastructure fragility, evacuation bottlenecks, and proximity to safe relocation parcels."
    ),
)
def get_habitation_priority(
    habitation_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Retrieve detailed transparent relocation priority evaluation for a single habitation."""
    try:
        result = compute_habitation_priority_from_db(db, habitation_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error evaluating habitation priority: {str(e)}",
        )

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitation with id '{habitation_id}' not found.",
        )

    return HabitationPriorityResponse(**result)


@router.get(
    "/recommendation/{habitation_id}",
    response_model=HabitationRelocationRecommendationResponse,
    summary="Generate Habitation Relocation Recommendation",
    description=(
        "Produces actionable, explainable relocation recommendation mapping a vulnerable habitation "
        "to the best suitable candidate relocation parcel using spatial distance + parcel suitability + available capacity. "
        "Provides dynamic justifications and decision-support disclaimers for authorized authorities."
    ),
)
def get_habitation_relocation_recommendation(
    habitation_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Generate comprehensive relocation recommendation with best matching parcel and alternatives."""
    try:
        result = compute_habitation_priority_from_db(db, habitation_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error generating relocation recommendation: {str(e)}",
        )

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitation with id '{habitation_id}' not found.",
        )

    return HabitationRelocationRecommendationResponse(**result)
