"""Normalizer for Central Water Commission (CWC / WIMS) river telemetry records."""

from datetime import datetime, timezone
from typing import Any, Dict
from dateutil import parser as date_parser
from geoalchemy2.elements import WKTElement


class RiverNormalizer:
    """Normalizes raw river hydrometry payloads into standard PostGIS-ready dictionary."""

    @staticmethod
    def normalize(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts and converts fields into a standard dictionary compatible with
        the RiverObservation SQLAlchemy model.
        """
        station_name = str(record["station_name"]).strip()
        water_level = round(float(record["water_level"]), 2)
        danger_level = round(float(record["danger_level"]), 2)
        lat = float(record["latitude"])
        lon = float(record["longitude"])

        raw_time = record["observation_time"]
        if isinstance(raw_time, str):
            dt = date_parser.parse(raw_time)
        elif isinstance(raw_time, datetime):
            dt = raw_time
        else:
            dt = datetime.now(timezone.utc)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return {
            "station_name": station_name,
            "water_level": water_level,
            "danger_level": danger_level,
            "observation_time": dt,
            "geometry": WKTElement(f"POINT({lon:.6f} {lat:.6f})", srid=4326),
        }
