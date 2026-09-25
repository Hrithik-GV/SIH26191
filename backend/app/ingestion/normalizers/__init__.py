"""Ingestion normalizers package."""

from backend.app.ingestion.normalizers.rainfall_normalizer import RainfallNormalizer
from backend.app.ingestion.normalizers.river_normalizer import RiverNormalizer
from backend.app.ingestion.normalizers.alert_normalizer import AlertNormalizer

__all__ = [
    "RainfallNormalizer",
    "RiverNormalizer",
    "AlertNormalizer",
]
