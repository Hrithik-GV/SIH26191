"""Ingestion providers package."""

from backend.app.ingestion.providers.base import BaseProvider, IngestionFetchResult
from backend.app.ingestion.providers.mosdac import MOSDACProvider, MOSDACDemoProvider
from backend.app.ingestion.providers.cwc_wims import CWCWIMSProvider, CWCWIMSDemoProvider
from backend.app.ingestion.providers.ndma_sachet import NDMASachetProvider, NDMASachetDemoProvider
from backend.app.ingestion.providers.imd import IMDWeatherProvider, IMDDemoProvider

__all__ = [
    "BaseProvider",
    "IngestionFetchResult",
    "MOSDACProvider",
    "MOSDACDemoProvider",
    "CWCWIMSProvider",
    "CWCWIMSDemoProvider",
    "NDMASachetProvider",
    "NDMASachetDemoProvider",
    "IMDWeatherProvider",
    "IMDDemoProvider",
]
