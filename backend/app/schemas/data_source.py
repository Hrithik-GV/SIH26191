"""Pydantic schemas for Data Sources and Ingestion Telemetry Status."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class IngestionLogResponse(BaseModel):
    """Log record representing an individual ingestion attempt."""
    timestamp: datetime = Field(..., description="Timestamp of execution")
    source_id: str = Field(..., description="Unique feed identifier")
    status: str = Field(..., description="Execution status: SUCCESS, CACHED, FAILED, VALIDATION_ERROR")
    records_count: int = Field(default=0, description="Number of new records processed/inserted")
    duration_ms: float = Field(default=0.0, description="Round-trip request and processing latency in ms")
    message: str = Field(default="", description="Execution summary or details")
    error: Optional[str] = Field(default=None, description="Exception details if failed")


class DataSourceStatusResponse(BaseModel):
    """Operational status and data freshness for an individual telemetry source."""
    source_id: str = Field(..., description="Identifier (mosdac_isro, cwc_wims, ndma_sachet, imd_weather)")
    source: str = Field(..., description="Official title / human-readable name of the feed")
    category: str = Field(..., description="Data category (RAINFALL, RIVER_LEVEL, DISASTER_ALERTS, METEOROLOGY)")
    status: str = Field(..., description="Health status (HEALTHY, DEMO_MODE, DEGRADED, OFFLINE)")
    data_mode: str = Field(..., description="Data connectivity mode (LIVE_CONNECTED, DEMONSTRATION_PROXY)")
    is_mock_data: bool = Field(..., description="Flag indicating demonstration data")
    last_update: Optional[datetime] = Field(None, description="Timestamp of last update attempt")
    data_freshness: str = Field(..., description="Human-readable relative time since last observation")
    records_ingested_last_run: int = Field(default=0, description="Records processed in most recent run")
    total_records_ingested: int = Field(default=0, description="Cumulative records processed across all runs")
    latency_ms: float = Field(default=0.0, description="Most recent fetch latency in milliseconds")
    last_etag: Optional[str] = Field(None, description="HTTP ETag caching header")
    last_modified: Optional[str] = Field(None, description="HTTP Last-Modified header")
    last_error: Optional[str] = Field(None, description="Most recent error message if failed")


class DataSourcesSummaryResponse(BaseModel):
    """Comprehensive summary of all ingested data sources and recent activity logs."""
    total_sources: int = Field(..., description="Total configured data sources")
    live_sources: int = Field(..., description="Number of live connected feeds")
    demo_sources: int = Field(..., description="Number of demonstration proxy feeds")
    scheduler_running: bool = Field(..., description="Whether APScheduler background polling is active")
    sources: List[DataSourceStatusResponse] = Field(..., description="List of individual source statuses")
    recent_logs: List[IngestionLogResponse] = Field(default_factory=list, description="Recent ingestion activity logs")
