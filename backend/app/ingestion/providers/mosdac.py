"""MOSDAC / ISRO Satellite Rainfall & Hydro-Estimator Telemetry Provider."""

import time
from datetime import datetime, timezone
from typing import Dict, List, Any
from backend.app.ingestion.providers.base import BaseProvider, IngestionFetchResult
from backend.app.ingestion.config import ingestion_settings


class MOSDACProvider(BaseProvider):
    """Production provider for MOSDAC (ISRO) meteorological satellite products."""

    def __init__(self):
        super().__init__(
            source_id="mosdac_isro",
            name="MOSDAC / ISRO Satellite Precipitation Telemetry",
            base_url=ingestion_settings.mosdac_base_url,
            api_key=ingestion_settings.mosdac_api_key,
            enabled=ingestion_settings.mosdac_enabled,
            is_live=bool(ingestion_settings.mosdac_api_key),
        )

    def fetch(self) -> IngestionFetchResult:
        """Fetch live satellite rainfall or fall back to demo provider if unconfigured."""
        if not self.is_live or not self.api_key:
            return MOSDACDemoProvider().fetch()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        url = f"{self.base_url}/products/rainfall/latest"
        return self._execute_http_get_with_retry(url, headers=headers)


class MOSDACDemoProvider(BaseProvider):
    """Demonstration proxy provider for MOSDAC INSAT-3D Hydro-Estimator products."""

    def __init__(self):
        super().__init__(
            source_id="mosdac_isro",
            name="MOSDAC / ISRO Satellite Precipitation Telemetry",
            is_live=False,
        )

    def fetch(self) -> IngestionFetchResult:
        """Generate structured demonstration satellite rainfall telemetry with explicit mock labeling."""
        start = time.time()
        now = datetime.now(timezone.utc)

        # Realistic INSAT-3D / INSAT-3DR Hydro-Estimator (HEM) satellite precipitation grids for Wayanad
        mock_records = [
            {
                "observation_id": f"MOSDAC_INSAT3D_{int(now.timestamp())}_1",
                "satellite": "INSAT-3DR",
                "product": "HEM_RAINFALL_HOURLY",
                "latitude": 11.535,
                "longitude": 76.138,
                "rainfall_mm": 142.5,
                "observation_time": now.isoformat(),
                "resolution_km": 4.0,
                "source": "DEMO_MOSDAC_INSAT3D_HEM",
                "is_mock_data": True,
            },
            {
                "observation_id": f"MOSDAC_INSAT3D_{int(now.timestamp())}_2",
                "satellite": "INSAT-3D",
                "product": "HEM_RAINFALL_HOURLY",
                "latitude": 11.580,
                "longitude": 76.095,
                "rainfall_mm": 98.0,
                "observation_time": now.isoformat(),
                "resolution_km": 4.0,
                "source": "DEMO_MOSDAC_INSAT3D_HEM",
                "is_mock_data": True,
            },
        ]

        elapsed_ms = (time.time() - start) * 1000.0
        return IngestionFetchResult(
            records=mock_records,
            etag=f'"mosdac-demo-{int(now.timestamp()) // 300}"',
            last_modified=now.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            is_cached_304=False,
            is_mock_data=True,
            data_source="DEMO_MOSDAC_INSAT3D_HEM",
            latency_ms=elapsed_ms,
        )
