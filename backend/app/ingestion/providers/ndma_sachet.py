"""NDMA SACHET Common Alerting Protocol (CAP) EOC Feed Provider."""

import time
from datetime import datetime, timezone
from typing import Dict, List, Any
from backend.app.ingestion.providers.base import BaseProvider, IngestionFetchResult
from backend.app.ingestion.config import ingestion_settings


class NDMASachetProvider(BaseProvider):
    """Production provider for NDMA SACHET CAP emergency warnings and bulletins."""

    def __init__(self):
        super().__init__(
            source_id="ndma_sachet",
            name="NDMA SACHET Common Alerting Protocol (CAP) EOC Feed",
            base_url=ingestion_settings.ndma_sachet_feed_url,
            api_key=ingestion_settings.ndma_sachet_api_key,
            enabled=ingestion_settings.ndma_sachet_enabled,
            is_live=bool(ingestion_settings.ndma_sachet_api_key),
        )

    def fetch(self) -> IngestionFetchResult:
        """Fetch live SACHET CAP XML/JSON feed or fall back to demonstration provider."""
        if not self.is_live or not self.api_key:
            return NDMASachetDemoProvider().fetch()

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
        }
        return self._execute_http_get_with_retry(self.base_url, headers=headers)


class NDMASachetDemoProvider(BaseProvider):
    """Demonstration proxy provider for NDMA SACHET CAP alert feeds."""

    def __init__(self):
        super().__init__(
            source_id="ndma_sachet",
            name="NDMA SACHET Common Alerting Protocol (CAP) EOC Feed",
            is_live=False,
        )

    def fetch(self) -> IngestionFetchResult:
        """Generate structured Common Alerting Protocol (CAP) alerts with explicit mock labeling."""
        start = time.time()
        now = datetime.now(timezone.utc)

        mock_records = [
            {
                "identifier": f"CAP_SACHET_NDMA_{int(now.timestamp())}_01",
                "sender": "KSDMA_EMERGENCY_OPS_CENTRE",
                "sent": now.isoformat(),
                "status": "Actual",
                "msgType": "Alert",
                "scope": "Public",
                "event": "Flash Flood & Landslide Warning",
                "urgency": "Immediate",
                "severity": "CRITICAL",
                "certainty": "Observed",
                "headline": "Red Alert: Massive debris movement and river inundation in Meppadi-Chooralmala belt",
                "description": "Continuous high-intensity rainfall exceeding 300mm has induced active debris movement. Evacuation of vulnerable habitations advised.",
                "areaDesc": "Chooralmala, Mundakkai, Meppadi, Wayanad",
                "polygon": "11.530,76.130 11.560,76.130 11.560,76.165 11.530,76.165 11.530,76.130",
                "source": "DEMO_NDMA_SACHET_CAP",
                "is_mock_data": True,
            }
        ]

        elapsed_ms = (time.time() - start) * 1000.0
        return IngestionFetchResult(
            records=mock_records,
            etag=f'"sachet-cap-demo-{int(now.timestamp()) // 300}"',
            last_modified=now.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            is_cached_304=False,
            is_mock_data=True,
            data_source="DEMO_NDMA_SACHET_CAP",
            latency_ms=elapsed_ms,
        )
