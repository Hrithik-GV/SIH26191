"""Validator for Rainfall Telemetry and Satellite Precipitation Records."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from dateutil import parser as date_parser


@dataclass
class ValidationResult:
    """Result of validating an ingestion payload record."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)


class RainfallValidator:
    """
    Validates rainfall telemetry records from IMD Automated Weather Stations
    and MOSDAC / ISRO INSAT satellite precipitation products.
    """

    MAX_REASONABLE_RAINFALL_MM = 1500.0  # Max realistic 24-hr meteorological threshold
    MIN_RAINFALL_MM = 0.0

    @classmethod
    def validate(cls, record: Dict[str, Any]) -> ValidationResult:
        errors = []

        # Validate rainfall_mm
        rainfall = record.get("rainfall_mm")
        if rainfall is None:
            errors.append("Missing required field: 'rainfall_mm'")
        else:
            try:
                rain_val = float(rainfall)
                if rain_val < cls.MIN_RAINFALL_MM or rain_val > cls.MAX_REASONABLE_RAINFALL_MM:
                    errors.append(f"Rainfall {rain_val}mm out of reasonable range [0, {cls.MAX_REASONABLE_RAINFALL_MM}]")
            except (ValueError, TypeError):
                errors.append(f"Invalid rainfall_mm value: {rainfall}")

        # Validate latitude
        lat = record.get("latitude")
        if lat is None:
            errors.append("Missing required field: 'latitude'")
        else:
            try:
                lat_val = float(lat)
                if not (-90.0 <= lat_val <= 90.0):
                    errors.append(f"Latitude {lat_val} out of range [-90, 90]")
            except (ValueError, TypeError):
                errors.append(f"Invalid latitude value: {lat}")

        # Validate longitude
        lon = record.get("longitude")
        if lon is None:
            errors.append("Missing required field: 'longitude'")
        else:
            try:
                lon_val = float(lon)
                if not (-180.0 <= lon_val <= 180.0):
                    errors.append(f"Longitude {lon_val} out of range [-180, 180]")
            except (ValueError, TypeError):
                errors.append(f"Invalid longitude value: {lon}")

        # Validate observation timestamp
        obs_time = record.get("observation_time")
        if not obs_time:
            errors.append("Missing required field: 'observation_time'")
        else:
            if isinstance(obs_time, str):
                try:
                    parsed = date_parser.parse(obs_time)
                except Exception as ex:
                    errors.append(f"Invalid observation_time format: {obs_time} ({ex})")
            elif not isinstance(obs_time, datetime):
                errors.append(f"observation_time must be ISO string or datetime object, got: {type(obs_time)}")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
