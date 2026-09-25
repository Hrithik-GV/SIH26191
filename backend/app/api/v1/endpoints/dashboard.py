"""Dashboard API Router: Situational Awareness & Operational KPI Aggregation."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.dashboard import DashboardResponse
from backend.app.services.dashboard_service import DashboardService

logger = logging.getLogger("sih26191.api.dashboard")

router = APIRouter(prefix="/dashboard", tags=["Executive Dashboard"])


@router.get(
    "",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Executive Disaster Management Dashboard Summary",
    description=(
        "Returns aggregated executive situational KPIs across all analytic engines: "
        "total habitations, habitations in critical zones, population at risk, "
        "immediate/short-term/medium-term relocation counts, total vs available capacity, "
        "active emergency alerts count, and latest data observation timestamps."
    ),
)
def get_dashboard(db: Session = Depends(get_db)) -> DashboardResponse:
    """Computes and returns the consolidated executive situational dashboard."""
    try:
        logger.info("Generating executive dashboard KPIs...")
        return DashboardService.get_dashboard_summary(db)
    except Exception as e:
        logger.error(f"Error generating dashboard summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable for dashboard: {str(e)}",
        )
