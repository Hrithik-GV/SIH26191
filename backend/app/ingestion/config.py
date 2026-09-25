"""Configuration settings and environment variable bindings for Data Ingestion Layer."""

import os
from typing import Dict, Any
from pydantic import BaseModel, Field


class IngestionConfig(BaseModel):
    """Runtime configuration for real-time and near-real-time telemetry providers."""

    # General ingestion options
    timeout_seconds: float = Field(
        default=float(os.getenv("INGESTION_TIMEOUT_SECONDS", "10.0")),
        description="HTTP request timeout in seconds",
    )
    max_retries: int = Field(
        default=int(os.getenv("INGESTION_MAX_RETRIES", "3")),
        description="Maximum retry attempts on network or 5xx failures",
    )
    retry_backoff_factor: float = Field(
        default=float(os.getenv("INGESTION_RETRY_BACKOFF_FACTOR", "1.5")),
        description="Exponential backoff factor between retries",
    )
    polling_interval_seconds: int = Field(
        default=int(os.getenv("INGESTION_POLLING_INTERVAL_SECONDS", "300")),
        description="APScheduler polling interval in seconds (default 5 minutes)",
    )
    use_demo_fallbacks: bool = Field(
        default=os.getenv("INGESTION_USE_DEMO_FALLBACKS", "true").lower() in ("true", "1", "yes"),
        description="When real credentials are absent, fall back to labeled demonstration providers",
    )
    auto_start_scheduler: bool = Field(
        default=os.getenv("INGESTION_AUTO_START_SCHEDULER", "false").lower() in ("true", "1", "yes"),
        description="Automatically start APScheduler background polling on application startup",
    )

    # 1. MOSDAC / ISRO (Meteorological and Oceanographic Satellite Data Archival Centre)
    mosdac_base_url: str = Field(
        default=os.getenv("MOSDAC_BASE_URL", "https://api.mosdac.gov.in/v1"),
        description="MOSDAC official API gateway endpoint",
    )
    mosdac_api_key: str = Field(
        default=os.getenv("MOSDAC_API_KEY", ""),
        description="API access token for MOSDAC products (empty if unconfigured)",
    )
    mosdac_enabled: bool = Field(
        default=os.getenv("MOSDAC_ENABLED", "true").lower() in ("true", "1", "yes"),
        description="Enable MOSDAC satellite precipitation ingestion",
    )

    # 2. CWC / WIMS / NWIC (Central Water Commission / Water Information Management System)
    cwc_wims_base_url: str = Field(
        default=os.getenv("CWC_WIMS_BASE_URL", "https://indiawris.gov.in/wims/api"),
        description="CWC/NWIC hydrometric telemetry endpoint",
    )
    cwc_wims_api_key: str = Field(
        default=os.getenv("CWC_WIMS_API_KEY", ""),
        description="API key for national water level telemetry",
    )
    cwc_wims_enabled: bool = Field(
        default=os.getenv("CWC_WIMS_ENABLED", "true").lower() in ("true", "1", "yes"),
        description="Enable CWC river gauge level ingestion",
    )

    # 3. NDMA SACHET CAP (Common Alerting Protocol XML/JSON feed)
    ndma_sachet_feed_url: str = Field(
        default=os.getenv("NDMA_SACHET_FEED_URL", "https://sachet.ndma.gov.in/cap/feed"),
        description="NDMA SACHET CAP emergency disaster alert feed URL",
    )
    ndma_sachet_api_key: str = Field(
        default=os.getenv("NDMA_SACHET_API_KEY", ""),
        description="SACHET partner access token if required",
    )
    ndma_sachet_enabled: bool = Field(
        default=os.getenv("NDMA_SACHET_ENABLED", "true").lower() in ("true", "1", "yes"),
        description="Enable NDMA SACHET alert feed ingestion",
    )

    # 4. IMD (India Meteorological Department AWS)
    imd_base_url: str = Field(
        default=os.getenv("IMD_BASE_URL", "https://mausam.imd.gov.in/api/v1"),
        description="IMD automated weather station telemetry endpoint",
    )
    imd_api_key: str = Field(
        default=os.getenv("IMD_API_KEY", ""),
        description="IMD partner access key",
    )
    imd_enabled: bool = Field(
        default=os.getenv("IMD_ENABLED", "true").lower() in ("true", "1", "yes"),
        description="Enable IMD AWS weather telemetry ingestion",
    )


ingestion_settings = IngestionConfig()
