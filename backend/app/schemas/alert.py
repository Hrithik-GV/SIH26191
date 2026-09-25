"""Pydantic schemas for Emergency Disaster Alerts and Bulletins."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AlertItem(BaseModel):
    """Emergency alert / disaster warning record."""
    id: str
    disaster_type: str
    severity: str
    event_time: datetime
    source: str
    headline: Optional[str] = None
    description: Optional[str] = None
    area_desc: Optional[str] = None
    is_active: bool = True
    geometry: Optional[Dict[str, Any]] = Field(None, description="GeoJSON polygon or point boundary")


class AlertsSummaryResponse(BaseModel):
    """Aggregated summary of active disaster warnings."""
    total_alerts: int
    critical_count: int
    severe_count: int
    moderate_count: int
    alerts: List[AlertItem]
