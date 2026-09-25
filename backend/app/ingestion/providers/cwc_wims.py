"""Central Water Commission (CWC / WIMS / NWIC) Hydrometric River Gauging Provider."""

import time
from datetime import datetime, timezone
from typing import Dict, List, Any
from backend.app.ingestion.providers.base import BaseProvider, IngestionFetchResult
from backend.app.ingestion.config import ingestion_settings


class CWCWIMSProvider(BaseProvider):
    """Production provider for CWC / India-WRIS / WIMS hydrometric river telemetry."""

    def __init__(self):
        super().__init__(
            source_id="cwc_wims",
            name="Central Water Commission (CWC / WIMS) River Hydrometry",
            base_url=ingestion_settings.cwc_wims_base_url,
            api_key=ingestion_settings.cwc_wims_api_key,
            enabled=ingestion_settings.cwc_wims_enabled,
            is_live=bool(ingestion_settings.cwc_wims_api_key),
        )

    def fetch(self) -> IngestionFetchResult:
        """Fetch live river gauge measurements or fall back to demonstration provider."""
        if not self.is_live or not self.api_key:
            return CWCWIMSDemoProvider().fetch()

        headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json",
        }
        url = f"{self.base_url}/telemetry/river-stages/realtime"
        return self._execute_http_get_with_retry(url, headers=headers)


class CWCWIMSDemoProvider(BaseProvider):
    """Demonstration proxy provider for CWC / NWIC river gauge telemetry."""

    def __init__(self):
        super().__init__(
            source_id="cwc_wims",
            name="Central Water Commission (CWC / WIMS) River Hydrometry",
            is_live=False,
        )

    def fetch(self) -> IngestionFetchResult:
        """Generate structured demonstration river telemetry with explicit mock labeling."""
        start = time.time()
        now = datetime.now(timezone.utc)

        mock_records = [
            {
                "observation_id": f"CWC_IRUVANJI_{int(now.timestamp())}",
                "station_name": "Iruvanjippuzha - Chooralmala Bridge",
                "river_basin": "Chaliyar Basin",
                "latitude": 11.536,
                "longitude": 76.152,
                "water_level": 8.75,
                "danger_level": 6.50,
                "warning_level": 5.80,
                "flow_trend": "RISING",
                "observation_time": now.isoformat(),
                "source": "DEMO_CWC_NWIC_TELEMETRY",
                "is_mock_data": True,
            },
            {
                "observation_id": f"CWC_CHALIYAR_{int(now.timestamp())}",
                "station_name": "Chaliyar - Nilambur Confluence",
                "river_basin": "Chaliyar Basin",
                "latitude": 11.450,
                "longitude": 76.220,
                "water_level": 14.35,
                "danger_level": 13.80,
                "warning_level": 12.50,
                "flow_trend": "STEADY_HIGH",
                "observation_time": now.isoformat(),
                "source": "DEMO_CWC_NWIC_TELEMETRY",
                "is_mock_data": True,
            },
            {
                "observation_id": f"CWC_MEPPADI_{int(now.timestamp())}",
                "station_name": "Meppadi Upstream Feeder Gauge",
                "river_basin": "Kabini Sub-basin",
                "latitude": 11.542,
                "longitude": 76.115,
                "water_level": 4.30,
                "danger_level": 5.20,
                "warning_level": 4.50,
                "flow_trend": "RISING_MODERATE",
                "observation_time": now.isoformat(),
                "source": "DEMO_CWC_NWIC_TELEMETRY",
                "is_mock_data": True,
            },
        ]

        elapsed_ms = (time.time() - start) * 1000.0
        return IngestionFetchResult(
            records=mock_records,
            etag=f'"cwc-wims-demo-{int(now.timestamp()) // 300}"',
            last_modified=now.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            is_cached_304=False,
            is_mock_data=True,
            data_source="DEMO_CWC_NWIC_TELEMETRY",
            latency_ms=elapsed_ms,
        )
