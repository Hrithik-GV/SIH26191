"""Normalizer for IMD AWS and MOSDAC satellite rainfall telemetry records."""

from datetime import datetime, timezone
from typing import Any, Dict
from dateutil import parser as date_parser
from geoalchemy2.elements import WKTElement


class RainfallNormalizer:
    """Normalizes raw rainfall payloads into standard PostGIS-ready dictionary."""

    @staticmethod
    def normalize(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts and converts fields into a standard dictionary compatible with
        the RainfallObservation SQLAlchemy model.
        """
        lat = float(record["latitude"])
        lon = float(record["longitude"])
        rain_mm = round(float(record["rainfall_mm"]), 2)

        raw_time = record["observation_time"]
        if isinstance(raw_time, str):
            dt = date_parser.parse(raw_time)
        elif isinstance(raw_time, datetime):
            dt = raw_time
        else:
            dt = datetime.now(timezone.utc)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        source = str(record.get("source") or record.get("satellite") or "UNKNOWN_RAINFALL_FEED")

        return {
            "latitude": lat,
            "longitude": lon,
            "rainfall_mm": rain_mm,
            "observation_time": dt,
            "source": source,
            "geometry": WKTElement(f"POINT({lon:.6f} {lat:.6f})", srid=4326),
        }
