"""Normalizer for NDMA SACHET CAP emergency alerts into DisasterEvent entities."""

import re
from datetime import datetime, timezone
from typing import Any, Dict
from dateutil import parser as date_parser
from geoalchemy2.elements import WKTElement


class AlertNormalizer:
    """Normalizes NDMA SACHET Common Alerting Protocol (CAP) records for PostGIS."""

    @classmethod
    def _parse_polygon_wkt(cls, polygon_str: str) -> str:
        """
        Parses CAP polygon string ("lat,lon lat,lon ...") into WKT POLYGON((lon lat, ...)).
        Ensures polygon ring is closed.
        """
        pairs = polygon_str.strip().split()
        coords = []
        for pair in pairs:
            if "," in pair:
                parts = pair.split(",")
                lat_str, lon_str = parts[0].strip(), parts[1].strip()
                coords.append(f"{float(lon_str):.6f} {float(lat_str):.6f}")

        if not coords:
            return ""

        # Ensure ring is closed
        if coords[0] != coords[-1]:
            coords.append(coords[0])

        return f"POLYGON(({', '.join(coords)}))"

    @classmethod
    def normalize(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes CAP alert into fields compatible with the DisasterEvent model.
        """
        # Disaster type classification
        raw_event = str(record.get("event") or record.get("disaster_type") or "incident").lower()
        if "landslide" in raw_event or "debris" in raw_event:
            disaster_type = "landslide"
        elif "flood" in raw_event or "inundation" in raw_event:
            disaster_type = "flash_flood"
        elif "cloudburst" in raw_event or "heavy rain" in raw_event:
            disaster_type = "cloudburst"
        else:
            disaster_type = re.sub(r"[^a-z0-9_]+", "_", raw_event.strip())[:50]

        # Severity
        severity_in = str(record.get("severity", "CRITICAL")).strip().upper()
        if severity_in in ("EXTREME", "CRITICAL"):
            severity = "CRITICAL"
        elif severity_in in ("SEVERE", "HIGH"):
            severity = "SEVERE"
        else:
            severity = "MODERATE"

        # Timestamp
        raw_time = record.get("sent") or record.get("event_time")
        if isinstance(raw_time, str):
            dt = date_parser.parse(raw_time)
        elif isinstance(raw_time, datetime):
            dt = raw_time
        else:
            dt = datetime.now(timezone.utc)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        source = str(record.get("source") or record.get("sender") or "NDMA_SACHET_CAP")

        # Geometry resolution
        polygon_str = record.get("polygon")
        if polygon_str:
            wkt_str = cls._parse_polygon_wkt(polygon_str)
            geom = WKTElement(wkt_str, srid=4326)
        elif record.get("longitude") is not None and record.get("latitude") is not None:
            lon = float(record["longitude"])
            lat = float(record["latitude"])
            geom = WKTElement(f"POINT({lon:.6f} {lat:.6f})", srid=4326)
        else:
            # Fallback default point if bounding coords exist
            geom = WKTElement("POINT(76.130000 11.530000)", srid=4326)

        return {
            "disaster_type": disaster_type,
            "severity": severity,
            "event_time": dt,
            "source": source,
            "geometry": geom,
        }
