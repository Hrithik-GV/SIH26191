"""Status registry and health tracking for data ingestion sources."""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class IngestionLogEntry(BaseModel):
    """Log record representing an individual ingestion attempt."""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_id: str
    status: str  # 'SUCCESS', 'CACHED', 'FAILED', 'VALIDATION_ERROR'
    records_count: int = 0
    duration_ms: float = 0.0
    message: str = ""
    error: Optional[str] = None


class DataSourceStatus(BaseModel):
    """Operational status and freshness metadata for an individual data source."""
    source_id: str
    name: str
    category: str  # 'RAINFALL', 'RIVER_LEVEL', 'DISASTER_ALERTS', 'METEOROLOGY'
    status: str = "INITIALIZING"  # 'HEALTHY', 'DEMO_MODE', 'DEGRADED', 'OFFLINE'
    data_mode: str = "DEMONSTRATION_PROXY"  # 'LIVE_CONNECTED', 'DEMONSTRATION_PROXY'
    is_mock_data: bool = True
    last_update: Optional[datetime] = None
    data_freshness: str = "Not yet updated"
    records_ingested_last_run: int = 0
    total_records_ingested: int = 0
    last_etag: Optional[str] = None
    last_modified: Optional[str] = None
    latency_ms: float = 0.0
    last_error: Optional[str] = None


class DataSourceStatusRegistry:
    """Singleton in-memory registry tracking real-time feed statuses and ingestion logs."""

    def __init__(self):
        self._sources: Dict[str, DataSourceStatus] = {
            "mosdac_isro": DataSourceStatus(
                source_id="mosdac_isro",
                name="MOSDAC / ISRO Satellite Precipitation Telemetry",
                category="RAINFALL",
            ),
            "cwc_wims": DataSourceStatus(
                source_id="cwc_wims",
                name="Central Water Commission (CWC / WIMS) River Hydrometry",
                category="RIVER_LEVEL",
            ),
            "ndma_sachet": DataSourceStatus(
                source_id="ndma_sachet",
                name="NDMA SACHET Common Alerting Protocol (CAP) EOC Feed",
                category="DISASTER_ALERTS",
            ),
            "imd_weather": DataSourceStatus(
                source_id="imd_weather",
                name="India Meteorological Department (IMD) AWS Telemetry",
                category="METEOROLOGY",
            ),
        }
        self._logs: List[IngestionLogEntry] = []
        self._max_logs = 100

    def record_run(
        self,
        source_id: str,
        status: str,
        records_count: int,
        duration_ms: float,
        message: str = "",
        error: Optional[str] = None,
        is_live: bool = False,
        etag: Optional[str] = None,
        last_modified: Optional[str] = None,
    ):
        """Update source metrics and record an execution log entry."""
        now = datetime.now(timezone.utc)
        
        # 1. Update source status
        if source_id in self._sources:
            src = self._sources[source_id]
            src.last_update = now
            src.records_ingested_last_run = records_count
            src.total_records_ingested += records_count
            src.latency_ms = round(duration_ms, 2)
            src.last_error = error
            src.last_etag = etag or src.last_etag
            src.last_modified = last_modified or src.last_modified
            
            if is_live:
                src.data_mode = "LIVE_CONNECTED"
                src.is_mock_data = False
                src.status = "HEALTHY" if error is None else "DEGRADED"
            else:
                src.data_mode = "DEMONSTRATION_PROXY"
                src.is_mock_data = True
                src.status = "DEMO_MODE" if error is None else "DEGRADED"

            # Compute human-readable data freshness
            src.data_freshness = "Just now"

        # 2. Append log
        log_entry = IngestionLogEntry(
            timestamp=now,
            source_id=source_id,
            status=status,
            records_count=records_count,
            duration_ms=round(duration_ms, 2),
            message=message,
            error=error,
        )
        self._logs.append(log_entry)
        if len(self._logs) > self._max_logs:
            self._logs.pop(0)

    def get_source_status(self, source_id: str) -> Optional[DataSourceStatus]:
        src = self._sources.get(source_id)
        if src and src.last_update:
            src.data_freshness = self._calculate_freshness(src.last_update)
        return src

    def get_all_statuses(self) -> List[DataSourceStatus]:
        results = []
        for src in self._sources.values():
            if src.last_update:
                src.data_freshness = self._calculate_freshness(src.last_update)
            results.append(src)
        return results

    def get_recent_logs(self, limit: int = 20) -> List[IngestionLogEntry]:
        return list(reversed(self._logs[-limit:]))

    def _calculate_freshness(self, dt: datetime) -> str:
        delta = (datetime.now(timezone.utc) - dt).total_seconds()
        if delta < 10:
            return "Just now"
        elif delta < 60:
            return f"{int(delta)} seconds ago"
        elif delta < 3600:
            mins = int(delta / 60)
            return f"{mins} minute{'s' if mins != 1 else ''} ago"
        else:
            hrs = int(delta / 3600)
            return f"{hrs} hour{'s' if hrs != 1 else ''} ago"


# Global singleton registry
source_registry = DataSourceStatusRegistry()
