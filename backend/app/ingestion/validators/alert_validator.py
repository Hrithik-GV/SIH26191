"""Validator for NDMA SACHET Common Alerting Protocol (CAP) Bulletins."""

from datetime import datetime
from typing import Any, Dict, List
from dateutil import parser as date_parser
from backend.app.ingestion.validators.rainfall_validator import ValidationResult


class AlertValidator:
    """
    Validates Common Alerting Protocol (CAP v1.2) emergency warning alerts
    from NDMA SACHET and State Disaster Management Authorities.
    """

    VALID_SEVERITIES = {
        "CRITICAL", "SEVERE", "MODERATE", "MINOR", "UNKNOWN",
        "EXTREME",  # CAP standard
    }

    @classmethod
    def validate(cls, record: Dict[str, Any]) -> ValidationResult:
        errors = []

        # Identifier
        identifier = record.get("identifier") or record.get("id")
        if not identifier or not str(identifier).strip():
            errors.append("Missing required field: 'identifier'")

        # Event type / title
        event = record.get("event") or record.get("disaster_type") or record.get("headline")
        if not event or not str(event).strip():
            errors.append("Missing required field: 'event' or 'disaster_type'")

        # Severity
        severity = str(record.get("severity", "")).strip().upper()
        if not severity:
            errors.append("Missing required field: 'severity'")
        elif severity not in cls.VALID_SEVERITIES:
            errors.append(f"Unrecognized severity '{severity}', expected one of {cls.VALID_SEVERITIES}")

        # Timestamp (sent or event_time)
        timestamp = record.get("sent") or record.get("event_time")
        if not timestamp:
            errors.append("Missing required field: 'sent' or 'event_time'")
        else:
            if isinstance(timestamp, str):
                try:
                    date_parser.parse(timestamp)
                except Exception as ex:
                    errors.append(f"Invalid timestamp format: {timestamp} ({ex})")
            elif not isinstance(timestamp, datetime):
                errors.append(f"timestamp must be ISO string or datetime, got: {type(timestamp)}")

        # Spatial geometry: either 'polygon', 'geometry', or 'latitude'/'longitude'
        has_polygon = bool(record.get("polygon"))
        has_geometry = bool(record.get("geometry"))
        has_point = record.get("latitude") is not None and record.get("longitude") is not None

        if not (has_polygon or has_geometry or has_point):
            errors.append("Missing spatial coverage: record must contain 'polygon', 'geometry', or 'latitude'/'longitude'")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
