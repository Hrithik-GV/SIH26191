"""Data Ingestion Pipeline and APScheduler for Near-Real-Time Feeds."""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from backend.app.ingestion.config import ingestion_settings
from backend.app.ingestion.status_registry import source_registry
from backend.app.ingestion.providers.base import BaseProvider, IngestionFetchResult
from backend.app.ingestion.providers.mosdac import MOSDACProvider
from backend.app.ingestion.providers.cwc_wims import CWCWIMSProvider
from backend.app.ingestion.providers.ndma_sachet import NDMASachetProvider
from backend.app.ingestion.providers.imd import IMDWeatherProvider
from backend.app.ingestion.validators import RainfallValidator, RiverValidator, AlertValidator
from backend.app.ingestion.normalizers import RainfallNormalizer, RiverNormalizer, AlertNormalizer
from backend.app.models.observation import RainfallObservation, RiverObservation
from backend.app.models.disaster_event import DisasterEvent
from backend.app.db.session import SessionLocal

logger = logging.getLogger("sih26191.ingestion")


@dataclass
class IngestionJobResult:
    """Summary metrics of an executed ingestion cycle."""
    source_id: str
    status: str  # 'SUCCESS', 'CACHED', 'FAILED', 'VALIDATION_ERROR'
    records_fetched: int = 0
    records_valid: int = 0
    records_inserted: int = 0
    records_duplicate: int = 0
    latency_ms: float = 0.0
    error: Optional[str] = None


class IngestionPipeline:
    """Coordinates provider fetching, validation, normalization, and PostGIS persistence."""

    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {
            "mosdac_isro": MOSDACProvider(),
            "cwc_wims": CWCWIMSProvider(),
            "ndma_sachet": NDMASachetProvider(),
            "imd_weather": IMDWeatherProvider(),
        }

    def ingest_source(self, source_id: str, db: Optional[Session] = None) -> IngestionJobResult:
        """
        Executes an end-to-end ingestion cycle for a single data source.
        1. Fetch payload with HTTP 304 caching
        2. Validate individual records
        3. Normalize into database schema
        4. Prevent duplicate records in PostGIS
        5. Persist new observations
        6. Update status registry metrics
        """
        provider = self.providers.get(source_id)
        if not provider:
            err = f"Unknown provider source ID: {source_id}"
            logger.error(err)
            return IngestionJobResult(source_id=source_id, status="FAILED", error=err)

        start_time = time.perf_counter()

        try:
            # 1. Fetch data
            fetch_result: IngestionFetchResult = provider.fetch()

            # 2. Handle HTTP 304 / ETag / Last-Modified caching
            if fetch_result.is_cached_304:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                source_registry.record_run(
                    source_id=source_id,
                    status="CACHED",
                    records_count=0,
                    duration_ms=elapsed_ms,
                    message="304 Not Modified - Upstream data is current, transfer skipped",
                    is_live=provider.is_live,
                    etag=fetch_result.etag,
                    last_modified=fetch_result.last_modified,
                )
                return IngestionJobResult(
                    source_id=source_id,
                    status="CACHED",
                    records_fetched=0,
                    latency_ms=elapsed_ms,
                )

            # 3. Validate & Normalize
            raw_records = fetch_result.records
            valid_normalized: List[Dict[str, Any]] = []

            for raw_record in raw_records:
                is_valid, norm_dict = self._validate_and_normalize(source_id, raw_record)
                if is_valid and norm_dict:
                    valid_normalized.append(norm_dict)

            # 4. Deduplicate and Persist into PostGIS
            inserted_count = 0
            duplicate_count = 0

            if db is not None and valid_normalized:
                for norm_dict in valid_normalized:
                    if self._is_duplicate(source_id, norm_dict, db):
                        duplicate_count += 1
                    else:
                        entity = self._create_entity(source_id, norm_dict)
                        db.add(entity)
                        inserted_count += 1

                try:
                    db.commit()
                except Exception as commit_err:
                    db.rollback()
                    logger.error(f"Error committing records for {source_id}: {commit_err}")
                    raise commit_err

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            # 5. Record run in singleton status registry
            status = "SUCCESS" if inserted_count > 0 or len(valid_normalized) > 0 else "CACHED"
            msg = f"Fetched {len(raw_records)} records, {inserted_count} inserted, {duplicate_count} duplicates skipped"
            source_registry.record_run(
                source_id=source_id,
                status=status,
                records_count=inserted_count,
                duration_ms=elapsed_ms,
                message=msg,
                is_live=provider.is_live,
                etag=fetch_result.etag,
                last_modified=fetch_result.last_modified,
            )

            return IngestionJobResult(
                source_id=source_id,
                status=status,
                records_fetched=len(raw_records),
                records_valid=len(valid_normalized),
                records_inserted=inserted_count,
                records_duplicate=duplicate_count,
                latency_ms=elapsed_ms,
            )

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"Ingestion failed for {source_id}: {e}", exc_info=True)
            source_registry.record_run(
                source_id=source_id,
                status="FAILED",
                records_count=0,
                duration_ms=elapsed_ms,
                message=f"Ingestion failed: {str(e)}",
                error=str(e),
                is_live=provider.is_live,
            )
            return IngestionJobResult(
                source_id=source_id,
                status="FAILED",
                latency_ms=elapsed_ms,
                error=str(e),
            )

    def _validate_and_normalize(self, source_id: str, record: Dict[str, Any]) -> tuple[bool, Optional[Dict[str, Any]]]:
        """Validates and normalizes an individual observation record."""
        if source_id in ("mosdac_isro", "imd_weather"):
            val_res = RainfallValidator.validate(record)
            if not val_res.is_valid:
                logger.warning(f"Rainfall validation error: {val_res.errors}")
                return False, None
            return True, RainfallNormalizer.normalize(record)

        elif source_id == "cwc_wims":
            val_res = RiverValidator.validate(record)
            if not val_res.is_valid:
                logger.warning(f"River validation error: {val_res.errors}")
                return False, None
            return True, RiverNormalizer.normalize(record)

        elif source_id == "ndma_sachet":
            val_res = AlertValidator.validate(record)
            if not val_res.is_valid:
                logger.warning(f"Alert validation error: {val_res.errors}")
                return False, None
            return True, AlertNormalizer.normalize(record)

        return False, None

    def _is_duplicate(self, source_id: str, norm_dict: Dict[str, Any], db: Session) -> bool:
        """Checks database for duplicate records before insertion."""
        try:
            if source_id in ("mosdac_isro", "imd_weather"):
                existing = db.query(RainfallObservation.id).filter(
                    RainfallObservation.source == norm_dict["source"],
                    RainfallObservation.observation_time == norm_dict["observation_time"],
                    RainfallObservation.latitude == norm_dict["latitude"],
                    RainfallObservation.longitude == norm_dict["longitude"],
                ).first()
                return existing is not None

            elif source_id == "cwc_wims":
                existing = db.query(RiverObservation.id).filter(
                    RiverObservation.station_name == norm_dict["station_name"],
                    RiverObservation.observation_time == norm_dict["observation_time"],
                ).first()
                return existing is not None

            elif source_id == "ndma_sachet":
                existing = db.query(DisasterEvent.id).filter(
                    DisasterEvent.source == norm_dict["source"],
                    DisasterEvent.event_time == norm_dict["event_time"],
                    DisasterEvent.disaster_type == norm_dict["disaster_type"],
                ).first()
                return existing is not None

        except Exception as check_err:
            logger.warning(f"Duplicate check encountered error (will attempt insert): {check_err}")
            return False

        return False

    def _create_entity(self, source_id: str, norm_dict: Dict[str, Any]) -> Any:
        """Instantiates the corresponding SQLAlchemy database model."""
        if source_id in ("mosdac_isro", "imd_weather"):
            return RainfallObservation(**norm_dict)
        elif source_id == "cwc_wims":
            return RiverObservation(**norm_dict)
        elif source_id == "ndma_sachet":
            return DisasterEvent(**norm_dict)
        raise ValueError(f"Unknown source ID for entity creation: {source_id}")


# Global pipeline instance
ingestion_pipeline = IngestionPipeline()


def run_all_ingestion_jobs(db: Optional[Session] = None) -> List[IngestionJobResult]:
    """
    Executes ingestion across all registered data feeds sequentially.
    Manages database session lifecycle if db is not passed.
    """
    close_session = False
    if db is None:
        try:
            db = SessionLocal()
            close_session = True
        except Exception as conn_err:
            logger.warning(f"Database session unavailable for scheduled ingestion: {conn_err}")
            db = None

    results: List[IngestionJobResult] = []
    total_new_records = 0

    try:
        for source_id in ingestion_pipeline.providers.keys():
            res = ingestion_pipeline.ingest_source(source_id, db=db)
            results.append(res)
            total_new_records += res.records_inserted

        logger.info(f"Ingestion cycle completed: {len(results)} sources queried, {total_new_records} new records inserted.")
    finally:
        if close_session and db:
            db.close()

    return results


class IngestionScheduler:
    """Manages APScheduler background polling for real-time telemetry feeds."""

    def __init__(self):
        self._scheduler = None

    def start(self, interval_seconds: Optional[int] = None):
        """Starts background periodic polling jobs."""
        from apscheduler.schedulers.background import BackgroundScheduler

        if self._scheduler and self._scheduler.running:
            logger.info("Ingestion scheduler is already running.")
            return

        interval = interval_seconds or ingestion_settings.polling_interval_seconds
        self._scheduler = BackgroundScheduler(timezone="UTC")
        self._scheduler.add_job(
            run_all_ingestion_jobs,
            "interval",
            seconds=interval,
            id="sih26191_ingestion_job",
            replace_existing=True,
        )
        self._scheduler.start()
        logger.info(f"Ingestion scheduler started with {interval}s interval.")

    def stop(self):
        """Stops the scheduler safely."""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("Ingestion scheduler stopped.")

    @property
    def is_running(self) -> bool:
        return self._scheduler.running if self._scheduler else False


# Singleton scheduler instance
ingestion_scheduler = IngestionScheduler()
