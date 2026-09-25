"""Base Provider Adapter Interface with HTTP caching, retries, and timeout handling."""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import httpx

from backend.app.ingestion.config import ingestion_settings

logger = logging.getLogger("sih26191.ingestion")


class IngestionFetchResult:
    """Encapsulates the raw payload returned by a provider."""
    def __init__(
        self,
        records: List[Dict[str, Any]],
        etag: Optional[str] = None,
        last_modified: Optional[str] = None,
        is_cached_304: bool = False,
        is_mock_data: bool = False,
        data_source: str = "",
        latency_ms: float = 0.0,
    ):
        self.records = records
        self.etag = etag
        self.last_modified = last_modified
        self.is_cached_304 = is_cached_304
        self.is_mock_data = is_mock_data
        self.data_source = data_source
        self.latency_ms = latency_ms


class BaseProvider(ABC):
    """Abstract provider adapter for real-time and near-real-time environmental telemetry feeds."""

    def __init__(
        self,
        source_id: str,
        name: str,
        base_url: str = "",
        api_key: str = "",
        enabled: bool = True,
        is_live: bool = False,
    ):
        self.source_id = source_id
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.enabled = enabled
        self.is_live = is_live
        
        # HTTP caching states
        self.last_etag: Optional[str] = None
        self.last_modified: Optional[str] = None

    @abstractmethod
    def fetch(self) -> IngestionFetchResult:
        """Fetch raw observations from upstream source with caching and error handling."""
        pass

    def _execute_http_get_with_retry(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> IngestionFetchResult:
        """Execute HTTP GET request with ETag caching, timeout handling, and exponential backoff retry."""
        req_headers = headers or {}
        
        # Pass caching headers if previous values exist
        if self.last_etag:
            req_headers["If-None-Match"] = self.last_etag
        if self.last_modified:
            req_headers["If-Modified-Since"] = self.last_modified

        timeout = ingestion_settings.timeout_seconds
        max_retries = ingestion_settings.max_retries
        backoff = ingestion_settings.retry_backoff_factor

        start_time = time.time()
        last_exception = None

        for attempt in range(1, max_retries + 1):
            try:
                with httpx.Client(timeout=timeout) as client:
                    response = client.get(url, headers=req_headers, params=params)
                    elapsed_ms = (time.time() - start_time) * 1000.0

                    # 304 Not Modified -> Upstream data hasn't changed
                    if response.status_code == 304:
                        logger.info(f"[{self.source_id}] HTTP 304 Not Modified; serving cached observation cycle.")
                        return IngestionFetchResult(
                            records=[],
                            etag=self.last_etag,
                            last_modified=self.last_modified,
                            is_cached_304=True,
                            is_mock_data=False,
                            data_source=self.name,
                            latency_ms=elapsed_ms,
                        )

                    response.raise_for_status()

                    # Save response caching headers
                    etag = response.headers.get("ETag")
                    last_mod = response.headers.get("Last-Modified")
                    if etag:
                        self.last_etag = etag
                    if last_mod:
                        self.last_modified = last_mod

                    data = response.json()
                    records = data if isinstance(data, list) else data.get("records", [data])

                    return IngestionFetchResult(
                        records=records,
                        etag=etag,
                        last_modified=last_mod,
                        is_cached_304=False,
                        is_mock_data=False,
                        data_source=self.name,
                        latency_ms=elapsed_ms,
                    )

            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                last_exception = e
                logger.warning(
                    f"[{self.source_id}] HTTP request failed (attempt {attempt}/{max_retries}): {str(e)}"
                )
                if attempt < max_retries:
                    time.sleep(backoff ** (attempt - 1))

        elapsed_ms = (time.time() - start_time) * 1000.0
        raise RuntimeError(f"[{self.source_id}] Ingestion fetch failed after {max_retries} retries: {str(last_exception)}")
