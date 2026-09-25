"""API Endpoints for Real-Time & Near-Real-Time Data Ingestion Status."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.ingestion.status_registry import source_registry
from backend.app.ingestion.scheduler.pipeline import (
    ingestion_pipeline,
    run_all_ingestion_jobs,
    ingestion_scheduler,
    IngestionJobResult,
)
from backend.app.schemas.data_source import (
    DataSourceStatusResponse,
    DataSourcesSummaryResponse,
    IngestionLogResponse,
)

router = APIRouter(prefix="/data-sources", tags=["Data Sources & Real-Time Ingestion"])


def _format_source_response(s) -> DataSourceStatusResponse:
    """Helper to convert DataSourceStatus internal model to Pydantic response."""
    return DataSourceStatusResponse(
        source_id=s.source_id,
        source=s.name,
        category=s.category,
        status=s.status,
        data_mode=s.data_mode,
        is_mock_data=s.is_mock_data,
        last_update=s.last_update,
        data_freshness=s.data_freshness,
        records_ingested_last_run=s.records_ingested_last_run,
        total_records_ingested=s.total_records_ingested,
        latency_ms=s.latency_ms,
        last_etag=s.last_etag,
        last_modified=s.last_modified,
        last_error=s.last_error,
    )


@router.get(
    "/status",
    response_model=DataSourcesSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Operational Status and Freshness of All Data Sources",
    description=(
        "Returns the real-time operational status, data freshness, connectivity mode, "
        "and HTTP caching state for all 4 primary disaster telemetry feeds: "
        "1. MOSDAC / ISRO Satellite Rainfall, "
        "2. CWC / WIMS River Hydrometry, "
        "3. NDMA SACHET CAP Alerts, and "
        "4. IMD Weather AWS Telemetry. "
        "Explicitly marks demonstration vs live feeds to maintain scientific integrity."
    ),
)
async def get_data_sources_status() -> DataSourcesSummaryResponse:
    """Retrieves operational telemetry feed statuses, freshness, and recent logs."""
    all_statuses = source_registry.get_all_statuses()
    sources_resp = [_format_source_response(s) for s in all_statuses]

    live_count = sum(1 for s in all_statuses if s.data_mode == "LIVE_CONNECTED")
    demo_count = sum(1 for s in all_statuses if s.data_mode == "DEMONSTRATION_PROXY")

    recent_logs = [
        IngestionLogResponse(
            timestamp=log.timestamp,
            source_id=log.source_id,
            status=log.status,
            records_count=log.records_count,
            duration_ms=log.duration_ms,
            message=log.message,
            error=log.error,
        )
        for log in source_registry.get_recent_logs(limit=25)
    ]

    return DataSourcesSummaryResponse(
        total_sources=len(sources_resp),
        live_sources=live_count,
        demo_sources=demo_count,
        scheduler_running=ingestion_scheduler.is_running,
        sources=sources_resp,
        recent_logs=recent_logs,
    )


@router.get(
    "/{source_id}",
    response_model=DataSourceStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Status for a Specific Data Source",
    description="Returns detailed telemetry health, freshness, and latency for a single data source.",
)
async def get_single_source_status(source_id: str) -> DataSourceStatusResponse:
    """Retrieves health and freshness for an individual feed."""
    src = source_registry.get_source_status(source_id)
    if not src:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{source_id}' not found. Valid IDs: mosdac_isro, cwc_wims, ndma_sachet, imd_weather",
        )
    return _format_source_response(src)


@router.post(
    "/trigger",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Trigger On-Demand Ingestion Cycle",
    description="Manually triggers telemetry polling, validation, normalization, and deduplication across data feeds.",
)
async def trigger_ingestion(
    source_id: Optional[str] = Query(None, description="Optional single source ID to ingest (default: all)"),
    db: Session = Depends(get_db),
):
    """Executes an immediate ingestion run, updating PostGIS and status registry."""
    if source_id:
        if source_id not in ingestion_pipeline.providers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source ID '{source_id}' not recognized.",
            )
        job_res = ingestion_pipeline.ingest_source(source_id, db=db)
        return [{
            "source_id": job_res.source_id,
            "status": job_res.status,
            "records_fetched": job_res.records_fetched,
            "records_valid": job_res.records_valid,
            "records_inserted": job_res.records_inserted,
            "records_duplicate": job_res.records_duplicate,
            "latency_ms": job_res.latency_ms,
            "error": job_res.error,
        }]

    results = run_all_ingestion_jobs(db=db)
    return [
        {
            "source_id": r.source_id,
            "status": r.status,
            "records_fetched": r.records_fetched,
            "records_valid": r.records_valid,
            "records_inserted": r.records_inserted,
            "records_duplicate": r.records_duplicate,
            "latency_ms": r.latency_ms,
            "error": r.error,
        }
        for r in results
    ]
