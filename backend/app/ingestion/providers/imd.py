"""India Meteorological Department (IMD) Automated Weather Station (AWS) Provider."""

import time
from datetime import datetime, timezone
from typing import Dict, List, Any
from backend.app.ingestion.providers.base import BaseProvider, IngestionFetchResult
from backend.app.ingestion.config import ingestion_settings


class IMDWeatherProvider(BaseProvider):
    """Production provider for IMD AWS and weather telemetry."""

    def __init__(self):
        super().__init__(
            source_id="imd_weather",
            name="India Meteorological Department (IMD) AWS Telemetry",
            base_url=ingestion_settings.imd_base_url,
            api_key=ingestion_settings.imd_api_key,
            enabled=ingestion_settings.imd_enabled,
            is_live=bool(ingestion_settings.imd_api_key),
        )

    def fetch(self) -> IngestionFetchResult:
        """Fetch live IMD AWS observations or fall back to demonstration provider."""
        if not self.is_live or not self.api_key:
            return IMDDemoProvider().fetch()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        url = f"{self.base_url}/aws/rainfall/realtime"
        return self._execute_http_get_with_retry(url, headers=headers)


class IMDDemoProvider(BaseProvider):
    """Demonstration proxy provider for IMD Automated Weather Stations."""

    def __init__(self):
        super().__init__(
            source_id="imd_weather",
            name="India Meteorological Department (IMD) AWS Telemetry",
            is_live=False,
        )

    def fetch(self) -> IngestionFetchResult:
        """Generate structured demonstration weather telemetry with explicit mock labeling."""
        start = time.time()
        now = datetime.now(timezone.utc)

        mock_records = [
            {
                "station_id": "IMD_AWS_MEPPADI_01",
                "station_name": "IMD AWS Station - Meppadi Hills",
                "latitude": 11.551,
                "longitude": 76.126,
                "rainfall_mm": 165.0,
                "observation_time": now.isoformat(),
                "temperature_c": 21.4,
                "humidity_pct": 98.0,
                "wind_speed_kmh": 28.5,
                "source": "DEMO_IMD_AWS_TELEMETRY",
                "is_mock_data": True,
            },
            {
                "station_id": "IMD_AWS_KALPETTA_02",
                "station_name": "IMD AWS Station - Kalpetta South",
                "latitude": 11.605,
                "longitude": 76.082,
                "rainfall_mm": 118.0,
                "observation_time": now.isoformat(),
                "temperature_c": 22.1,
                "humidity_pct": 94.0,
                "wind_speed_kmh": 19.0,
                "source": "DEMO_IMD_AWS_TELEMETRY",
                "is_mock_data": True,
            },
        ]

        elapsed_ms = (time.time() - start) * 1000.0
        return IngestionFetchResult(
            records=mock_records,
            etag=f'"imd-aws-demo-{int(now.timestamp()) // 300}"',
            last_modified=now.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            is_cached_304=False,
            is_mock_data=True,
            data_source="DEMO_IMD_AWS_TELEMETRY",
            latency_ms=elapsed_ms,
        )
