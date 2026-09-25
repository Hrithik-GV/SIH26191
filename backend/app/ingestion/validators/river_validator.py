"""Validator for Central Water Commission (CWC / WIMS) River Hydrometry Telemetry."""

from datetime import datetime
from typing import Any, Dict, List
from dateutil import parser as date_parser
from backend.app.ingestion.validators.rainfall_validator import ValidationResult


class RiverValidator:
    """
    Validates river stage and hydrometric discharge records from
    CWC / WIMS / NWIC telemetry stations.
    """

    MAX_REASONABLE_STAGE_M = 250.0  # Max realistic river stage level in meters
    MIN_STAGE_M = 0.0

    @classmethod
    def validate(cls, record: Dict[str, Any]) -> ValidationResult:
        errors = []

        # Station name
        station_name = record.get("station_name")
        if not station_name or not str(station_name).strip():
            errors.append("Missing or empty required field: 'station_name'")

        # Water level
        water_level = record.get("water_level")
        if water_level is None:
            errors.append("Missing required field: 'water_level'")
        else:
            try:
                wl_val = float(water_level)
                if wl_val < cls.MIN_STAGE_M or wl_val > cls.MAX_REASONABLE_STAGE_M:
                    errors.append(f"Water level {wl_val}m out of reasonable range [0, {cls.MAX_REASONABLE_STAGE_M}]")
            except (ValueError, TypeError):
                errors.append(f"Invalid water_level value: {water_level}")

        # Danger level
        danger_level = record.get("danger_level")
        if danger_level is None:
            errors.append("Missing required field: 'danger_level'")
        else:
            try:
                dl_val = float(danger_level)
                if dl_val <= 0.0 or dl_val > cls.MAX_REASONABLE_STAGE_M:
                    errors.append(f"Danger level {dl_val}m out of reasonable range (0, {cls.MAX_REASONABLE_STAGE_M}]")
            except (ValueError, TypeError):
                errors.append(f"Invalid danger_level value: {danger_level}")

        # Latitude
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

        # Longitude
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

        # Observation timestamp
        obs_time = record.get("observation_time")
        if not obs_time:
            errors.append("Missing required field: 'observation_time'")
        else:
            if isinstance(obs_time, str):
                try:
                    date_parser.parse(obs_time)
                except Exception as ex:
                    errors.append(f"Invalid observation_time format: {obs_time} ({ex})")
            elif not isinstance(obs_time, datetime):
                errors.append(f"observation_time must be ISO string or datetime object, got: {type(obs_time)}")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
