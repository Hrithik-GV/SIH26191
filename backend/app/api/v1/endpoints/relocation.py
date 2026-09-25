"""FastAPI endpoints for Relocation Prioritization, Allocation Recommendations, and Urgency Support."""

import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
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

router = APIRouter(prefix="/relocation", tags=["Relocation Urgency & Recommendations"])


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
    priority: Optional[str] = Query(None, description="Filter by priority tier: IMMEDIATE, SHORT_TERM, MEDIUM_TERM, MONITOR"),
    db: Session = Depends(get_db),
) -> HabitationPrioritiesSummaryResponse:
    """Compile multi-habitation relocation priority rankings and regional breakdown."""
    try:
        summary = compute_all_habitations_priorities_summary(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error calculating relocation priorities summary: {str(e)}",
        )

    if priority:
        prio_upper = priority.strip().upper()
        summary.priorities = [p for p in summary.priorities if p.priority == prio_upper]

    return summary


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
) -> HabitationPriorityResponse:
    """Calculate transparent relocation priority for an individual vulnerable settlement."""
    try:
        priority_data = compute_habitation_priority_from_db(db, habitation_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error calculating habitation relocation priority: {str(e)}",
        )

    if not priority_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitation with id '{habitation_id}' not found.",
        )

    return priority_data


@router.get(
    "/recommendation/{habitation_id}",
    response_model=HabitationRelocationRecommendationResponse,
    summary="Generate Actionable Relocation Allocation Recommendation",
    description=(
        "Produces an actionable relocation allocation plan identifying the best suitable candidate site, "
        "checking capacity sufficiency against vulnerable population, identifying alternative backup parcels, "
        "and attaching decision-support disclaimers."
    ),
)
def get_relocation_recommendation(
    habitation_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> HabitationRelocationRecommendationResponse:
    """Generate structured relocation recommendation for administrative decision support."""
    try:
        recommendation = compute_habitation_priority_from_db(db, habitation_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error generating relocation recommendation: {str(e)}",
        )

    if not recommendation or "error" in recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habitation with id '{habitation_id}' not found.",
        )

    return HabitationRelocationRecommendationResponse(**recommendation)


@router.get(
    "/summary",
    summary="Get High-Level Relocation Urgency Summary",
    description="Returns aggregate counts of immediate, short-term, and medium-term relocation needs.",
)
def get_relocation_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    summary = compute_all_habitations_priorities_summary(db)
    if isinstance(summary, dict):
        return {
            "total_habitations": summary.get("total_habitations", 0),
            "immediate_count": summary.get("immediate_count", 0),
            "short_term_count": summary.get("short_term_count", 0),
            "medium_term_count": summary.get("medium_term_count", 0),
            "monitor_count": summary.get("monitor_count", 0),
            "average_priority_score": summary.get("average_priority_score", 0.0),
            "calculated_at": summary.get("calculated_at"),
        }
    return {
        "total_habitations": getattr(summary, "total_habitations", 0),
        "immediate_count": getattr(summary, "immediate_count", 0),
        "short_term_count": getattr(summary, "short_term_count", 0),
        "medium_term_count": getattr(summary, "medium_term_count", 0),
        "monitor_count": getattr(summary, "monitor_count", 0),
        "average_priority_score": getattr(summary, "average_priority_score", 0.0),
        "calculated_at": getattr(summary, "calculated_at", None),
    }
