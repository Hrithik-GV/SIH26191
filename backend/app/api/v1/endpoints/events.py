"""Live Disaster Event Streaming (SSE) and Simulation Endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services.event_broker import event_broker
from backend.app.services.disaster_update_orchestrator import DisasterUpdateOrchestrator

logger = logging.getLogger("sih26191.events_api")

router = APIRouter(prefix="/events", tags=["Live Disaster Events & SSE Streaming"])


@router.get(
    "/stream",
    summary="Server-Sent Events (SSE) Live Disaster Stream",
    description=(
        "Streams live real-time disaster notifications via Server-Sent Events (RFC 8895). "
        "Emits events: NEW_ALERT, HAZARD_UPDATED, HABITATION_PRIORITY_CHANGED, RELOCATION_SITE_UPDATED, and DASHBOARD_UPDATED."
    ),
    response_class=StreamingResponse,
)
async def stream_disaster_events():
    """
    Subscribes the client to real-time disaster telemetry updates over HTTP.
    Keeps connection alive with periodic 15-second ping comments.
    """
    return StreamingResponse(
        event_broker.subscribe(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disables Nginx reverse proxy buffering
            "Content-Type": "text/event-stream",
        },
    )


@router.get(
    "/recent",
    summary="Get Recent Disaster Events History",
    description="Fetches recent disaster events emitted by the telemetry pipeline for dashboard review.",
)
def get_recent_events(limit: int = Query(20, ge=1, le=50)):
    """Returns the most recent events stored in the in-memory ring buffer."""
    return {
        "total": len(event_broker.get_recent_events(limit=limit)),
        "events": event_broker.get_recent_events(limit=limit),
    }


@router.post(
    "/simulate",
    summary="Trigger Live Disaster Update Scenario",
    description=(
        "Executes the full 6-step disaster update pipeline for a live demonstration: "
        "1. Store observation -> 2. Identify affected regions -> 3. Recalculate hazards -> "
        "4. Recalculate habitation priorities -> 5. Identify suitable relocation sites -> 6. Update dashboard."
    ),
)
def simulate_disaster_scenario(
    scenario: str = Query(
        "heavy_rainfall",
        description="Scenario to execute: 'heavy_rainfall', 'river_surge', or 'landslide_warning'",
    ),
    db: Session = Depends(get_db),
):
    """Triggers end-to-end reactive risk pipeline and broadcasts SSE events to all connected clients."""
    valid_scenarios = ("heavy_rainfall", "river_surge", "landslide_warning")
    if scenario not in valid_scenarios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scenario '{scenario}'. Must be one of: {', '.join(valid_scenarios)}",
        )

    try:
        pipeline_result = DisasterUpdateOrchestrator.trigger_live_scenario(scenario, db=db)
        return {
            "status": "SUCCESS",
            "scenario": scenario,
            "pipeline_result": pipeline_result,
            "message": "6-step pipeline executed successfully and SSE events broadcasted to all active dashboards.",
        }
    except Exception as e:
        logger.error(f"Error executing scenario '{scenario}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing scenario: {str(e)}",
        )
