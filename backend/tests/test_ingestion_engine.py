"""Comprehensive Unit and Integration Tests for Real-Time Data Ingestion Layer."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ingestion.providers.mosdac import MOSDACProvider, MOSDACDemoProvider
from backend.app.ingestion.providers.cwc_wims import CWCWIMSProvider, CWCWIMSDemoProvider
from backend.app.ingestion.providers.ndma_sachet import NDMASachetProvider, NDMASachetDemoProvider
from backend.app.ingestion.providers.imd import IMDWeatherProvider, IMDDemoProvider
from backend.app.ingestion.validators import RainfallValidator, RiverValidator, AlertValidator
from backend.app.ingestion.normalizers import RainfallNormalizer, RiverNormalizer, AlertNormalizer
from backend.app.ingestion.status_registry import source_registry, DataSourceStatusRegistry
from backend.app.ingestion.scheduler.pipeline import (
    IngestionPipeline,
    run_all_ingestion_jobs,
)
from backend.app.db.session import get_db

client = TestClient(app)


# ==============================================================================
# 1. PROVIDER TESTS
# ==============================================================================

def test_mosdac_demo_provider():
    """Verify MOSDAC demonstration provider returns realistic, properly labeled records."""
    provider = MOSDACDemoProvider()
    res = provider.fetch()

    assert not res.is_cached_304
    assert res.is_mock_data is True
    assert len(res.records) >= 2
    assert "DEMO" in res.data_source

    rec = res.records[0]
    assert "rainfall_mm" in rec
    assert rec["rainfall_mm"] > 0
    assert 11.0 <= rec["latitude"] <= 12.0
    assert 75.0 <= rec["longitude"] <= 77.0
    assert rec["is_mock_data"] is True


def test_cwc_wims_demo_provider():
    """Verify CWC river telemetry provider returns valid hydrometry stations."""
    provider = CWCWIMSDemoProvider()
    res = provider.fetch()

    assert not res.is_cached_304
    assert res.is_mock_data is True
    assert len(res.records) >= 3

    stations = [r["station_name"] for r in res.records]
    assert any("Iruvanjippuzha" in s for s in stations)
    assert any("Chaliyar" in s for s in stations)

    rec = res.records[0]
    assert rec["water_level"] > 0
    assert rec["danger_level"] > 0


def test_ndma_sachet_demo_provider():
    """Verify NDMA SACHET CAP provider returns valid emergency alert structure."""
    provider = NDMASachetDemoProvider()
    res = provider.fetch()

    assert not res.is_cached_304
    assert res.is_mock_data is True
    assert len(res.records) >= 1

    alert = res.records[0]
    assert alert["msgType"] == "Alert"
    assert alert["severity"] in ("CRITICAL", "SEVERE", "MODERATE")
    assert "polygon" in alert
    assert "Meppadi" in alert["headline"] or "Chooralmala" in alert["headline"]


def test_imd_weather_demo_provider():
    """Verify IMD Automated Weather Station provider returns valid weather metrics."""
    provider = IMDDemoProvider()
    res = provider.fetch()

    assert not res.is_cached_304
    assert res.is_mock_data is True
    assert len(res.records) >= 2

    station = res.records[0]
    assert "rainfall_mm" in station
    assert station["rainfall_mm"] >= 0.0
    assert "temperature_c" in station
    assert "humidity_pct" in station


def test_production_provider_fallback_when_unconfigured():
    """Verify production providers fall back gracefully to demo providers when API keys are absent."""
    mosdac = MOSDACProvider()
    assert mosdac.is_live is False
    res = mosdac.fetch()
    assert res.is_mock_data is True

    cwc = CWCWIMSProvider()
    assert cwc.is_live is False
    res_cwc = cwc.fetch()
    assert res_cwc.is_mock_data is True


# ==============================================================================
# 2. VALIDATOR TESTS
# ==============================================================================

def test_rainfall_validator_valid_and_invalid():
    """Verify RainfallValidator accepts legitimate payloads and rejects invalid inputs."""
    valid_rec = {
        "rainfall_mm": 125.4,
        "latitude": 11.535,
        "longitude": 76.138,
        "observation_time": "2026-09-25T12:00:00Z",
    }
    val = RainfallValidator.validate(valid_rec)
    assert val.is_valid is True
    assert len(val.errors) == 0

    # Negative rainfall
    bad_rain = dict(valid_rec, rainfall_mm=-10.0)
    assert RainfallValidator.validate(bad_rain).is_valid is False

    # Out of range coordinate
    bad_lat = dict(valid_rec, latitude=120.0)
    assert RainfallValidator.validate(bad_lat).is_valid is False

    # Missing observation time
    bad_time = dict(valid_rec)
    del bad_time["observation_time"]
    assert RainfallValidator.validate(bad_time).is_valid is False


def test_river_validator_valid_and_invalid():
    """Verify RiverValidator checks stage levels and station metadata."""
    valid_rec = {
        "station_name": "Chooralmala Feeder Gauge",
        "water_level": 7.5,
        "danger_level": 6.0,
        "latitude": 11.54,
        "longitude": 76.15,
        "observation_time": datetime.now(timezone.utc).isoformat(),
    }
    assert RiverValidator.validate(valid_rec).is_valid is True

    # Empty station name
    bad_stn = dict(valid_rec, station_name="")
    assert RiverValidator.validate(bad_stn).is_valid is False

    # Negative danger level
    bad_danger = dict(valid_rec, danger_level=-1.0)
    assert RiverValidator.validate(bad_danger).is_valid is False


def test_alert_validator_valid_and_invalid():
    """Verify AlertValidator validates Common Alerting Protocol rules."""
    valid_cap = {
        "identifier": "CAP_TEST_001",
        "event": "Landslide Hazard Warning",
        "severity": "CRITICAL",
        "sent": "2026-09-25T14:30:00Z",
        "polygon": "11.53,76.13 11.55,76.13 11.55,76.16 11.53,76.16 11.53,76.13",
    }
    assert AlertValidator.validate(valid_cap).is_valid is True

    # Unrecognized severity
    bad_sev = dict(valid_cap, severity="CATASTROPHIC_UNKNOWN")
    assert AlertValidator.validate(bad_sev).is_valid is False

    # Missing spatial geometry
    bad_geo = dict(valid_cap)
    del bad_geo["polygon"]
    assert AlertValidator.validate(bad_geo).is_valid is False


# ==============================================================================
# 3. NORMALIZER TESTS
# ==============================================================================

def test_rainfall_normalizer():
    """Verify RainfallNormalizer converts raw telemetry into standard PostGIS-ready dictionary."""
    rec = {
        "latitude": 11.535,
        "longitude": 76.138,
        "rainfall_mm": 142.54,
        "observation_time": "2026-09-25T12:00:00+00:00",
        "source": "IMD_AWS",
    }
    norm = RainfallNormalizer.normalize(rec)

    assert norm["latitude"] == 11.535
    assert norm["longitude"] == 76.138
    assert norm["rainfall_mm"] == 142.54
    assert norm["source"] == "IMD_AWS"
    assert norm["observation_time"].tzinfo is not None
    assert "POINT(76.138000 11.535000)" in str(norm["geometry"].data)


def test_river_normalizer():
    """Verify RiverNormalizer correctly structures hydrometric models."""
    rec = {
        "station_name": "Meppadi Feeder",
        "latitude": 11.542,
        "longitude": 76.115,
        "water_level": 5.4,
        "danger_level": 4.8,
        "observation_time": "2026-09-25T12:00:00Z",
    }
    norm = RiverNormalizer.normalize(rec)

    assert norm["station_name"] == "Meppadi Feeder"
    assert norm["water_level"] == 5.4
    assert norm["danger_level"] == 4.8
    assert "POINT(76.115000 11.542000)" in str(norm["geometry"].data)


def test_alert_normalizer_polygon_parsing():
    """Verify AlertNormalizer translates CAP lat,lon polygons to PostGIS POLYGON((lon lat))."""
    rec = {
        "event": "Debris Flow & Flash Flood Warning",
        "severity": "CRITICAL",
        "sent": "2026-09-25T10:00:00Z",
        "polygon": "11.530,76.130 11.560,76.130 11.560,76.165 11.530,76.165 11.530,76.130",
        "source": "NDMA_SACHET",
    }
    norm = AlertNormalizer.normalize(rec)

    assert norm["disaster_type"] in ("landslide", "flash_flood")
    assert norm["severity"] == "CRITICAL"
    assert "POLYGON((" in str(norm["geometry"].data)
    # Check that longitude comes first in PostGIS format
    assert "76.130000 11.530000" in str(norm["geometry"].data)


# ==============================================================================
# 4. STATUS REGISTRY & CACHING TESTS
# ==============================================================================

def test_status_registry_tracking():
    """Verify DataSourceStatusRegistry records executions, metrics, and calculates relative freshness."""
    registry = DataSourceStatusRegistry()

    # Record a run
    registry.record_run(
        source_id="mosdac_isro",
        status="SUCCESS",
        records_count=5,
        duration_ms=45.2,
        message="Fetched 5 records",
        is_live=False,
    )

    status = registry.get_source_status("mosdac_isro")
    assert status is not None
    assert status.status == "DEMO_MODE"
    assert status.is_mock_data is True
    assert status.total_records_ingested == 5
    assert status.data_freshness in ("Just now", "0 seconds ago", "1 seconds ago")

    logs = registry.get_recent_logs(limit=5)
    assert len(logs) == 1
    assert logs[0].source_id == "mosdac_isro"


# ==============================================================================
# 5. PIPELINE & DEDUPLICATION TESTS
# ==============================================================================

def test_ingestion_pipeline_with_mock_db():
    """Verify end-to-end ingestion pipeline performs deduplication against database session."""
    pipeline = IngestionPipeline()

    mock_db = MagicMock()
    # First run: no duplicate exists
    mock_db.query.return_value.filter.return_value.first.return_value = None

    res1 = pipeline.ingest_source("mosdac_isro", db=mock_db)
    assert res1.status in ("SUCCESS", "CACHED")
    assert res1.records_fetched > 0
    assert res1.records_inserted > 0
    assert res1.records_duplicate == 0
    assert mock_db.commit.called

    # Second run: simulates existing duplicate
    mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
    mock_db.commit.reset_mock()

    res2 = pipeline.ingest_source("mosdac_isro", db=mock_db)
    assert res2.records_duplicate == res2.records_fetched
    assert res2.records_inserted == 0


def test_run_all_ingestion_jobs():
    """Verify run_all_ingestion_jobs triggers all 4 data feeds."""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    results = run_all_ingestion_jobs(db=mock_db)
    assert len(results) == 4
    source_ids = [r.source_id for r in results]
    assert "mosdac_isro" in source_ids
    assert "cwc_wims" in source_ids
    assert "ndma_sachet" in source_ids
    assert "imd_weather" in source_ids


# ==============================================================================
# 6. REST API ENDPOINT TESTS
# ==============================================================================

def test_get_data_sources_status_endpoint():
    """Verify GET /api/data-sources/status returns source metadata, freshness, and status."""
    response = client.get("/api/data-sources/status")
    assert response.status_code == 200

    data = response.json()
    assert "total_sources" in data
    assert data["total_sources"] == 4
    assert "sources" in data
    assert len(data["sources"]) == 4

    # Verify required response fields
    first_source = data["sources"][0]
    assert "source" in first_source
    assert "last_update" in first_source
    assert "status" in first_source
    assert "data_freshness" in first_source
    assert "data_mode" in first_source
    assert "is_mock_data" in first_source


def test_get_single_data_source_status():
    """Verify GET /api/data-sources/{source_id} returns details for specific feed."""
    response = client.get("/api/data-sources/cwc_wims")
    assert response.status_code == 200
    data = response.json()
    assert data["source_id"] == "cwc_wims"
    assert "Central Water Commission" in data["source"]

    # Test 404 for unknown feed
    res_404 = client.get("/api/data-sources/non_existent_feed")
    assert res_404.status_code == 404


def test_trigger_ingestion_endpoint():
    """Verify POST /api/data-sources/trigger initiates on-demand ingestion."""
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_session
    try:
        response = client.post("/api/data-sources/trigger?source_id=imd_weather")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["source_id"] == "imd_weather"
        assert data[0]["records_fetched"] > 0
    finally:
        app.dependency_overrides.clear()
