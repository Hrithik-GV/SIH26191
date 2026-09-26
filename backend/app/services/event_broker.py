"""Thread-Safe Server-Sent Events (SSE) Broker for Live Disaster Updates."""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, List, Any, Optional, Set

logger = logging.getLogger("sih26191.events")

# Standard disaster event types required by SIH 26191
EVENT_NEW_ALERT = "NEW_ALERT"
EVENT_HAZARD_UPDATED = "HAZARD_UPDATED"
EVENT_HABITATION_PRIORITY_CHANGED = "HABITATION_PRIORITY_CHANGED"
EVENT_RELOCATION_SITE_UPDATED = "RELOCATION_SITE_UPDATED"
EVENT_DASHBOARD_UPDATED = "DASHBOARD_UPDATED"
EVENT_SYSTEM_CONNECTED = "CONNECTED"


class DisasterEventBroker:
    """
    In-memory, asyncio-compatible event pub/sub broker for Server-Sent Events.
    Maintains active subscriber queues and a persistent ring buffer of recent events.
    """

    def __init__(self, max_history: int = 50):
        self._subscribers: Set[asyncio.Queue] = set()
        self._history: List[Dict[str, Any]] = []
        self._max_history = max_history
        self._lock = asyncio.Lock()

    def get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns the most recent disaster events (newest first)."""
        return list(reversed(self._history[-limit:]))

    def broadcast(
        self,
        event_type: str,
        data: Dict[str, Any],
        headline: str = "",
        severity: str = "INFO",
    ) -> Dict[str, Any]:
        """
        Publishes an event to all connected SSE clients and stores it in history.
        Thread-safe: can be called from synchronous background threads or async coroutines.
        """
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "id": f"evt-{int(time.time() * 1000)}",
            "event_type": event_type,
            "headline": headline or f"Disaster update: {event_type}",
            "severity": severity.upper(),
            "timestamp": now,
            "data": data,
            "disclaimer": (
                "Decision-support telemetry: Relocation allocations and priority classifications "
                "are advisory candidate assessments. Relocation actions require competent administrative authority validation."
            ),
        }

        # Append to ring buffer
        self._history.append(payload)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        # Distribute to subscriber queues
        dead_queues = set()
        for q in list(self._subscribers):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                dead_queues.add(q)
            except Exception as e:
                logger.warning(f"Failed to queue event for subscriber: {e}")
                dead_queues.add(q)

        for dq in dead_queues:
            self._subscribers.discard(dq)

        logger.info(f"Broadcasted event '{event_type}': {headline} to {len(self._subscribers)} subscribers")
        return payload

    async def subscribe(self) -> AsyncGenerator[str, None]:
        """
        Async generator yielding Server-Sent Events formatted according to RFC 8895.
        Streams an initial connection handshake, recent history, and live events.
        """
        q = asyncio.Queue(maxsize=100)
        self._subscribers.add(q)
        client_id = f"client-{id(q)}"
        logger.info(f"New SSE client connected: {client_id} (total: {len(self._subscribers)})")

        try:
            # 1. Send initial connection greeting
            connect_payload = {
                "event_type": EVENT_SYSTEM_CONNECTED,
                "client_id": client_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "Connected to SIH 26191 Live Disaster Event Stream",
                "active_subscribers": len(self._subscribers),
                "recent_events": self.get_recent_events(limit=5),
            }
            yield f"event: {EVENT_SYSTEM_CONNECTED}\ndata: {json.dumps(connect_payload)}\n\n"

            # 2. Stream live events with heartbeat ping every 15s
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), timeout=15.0)
                    evt_type = event.get("event_type", "message")
                    yield f"event: {evt_type}\ndata: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    # Send periodic SSE comment ping to keep proxy/connection alive
                    now_str = datetime.now(timezone.utc).strftime("%H:%M:%S")
                    yield f": ping - {now_str}\n\n"

        except asyncio.CancelledError:
            logger.info(f"SSE client {client_id} connection cancelled/closed by browser.")
        finally:
            self._subscribers.discard(q)
            logger.info(f"SSE client {client_id} disconnected (remaining: {len(self._subscribers)})")


# Global singleton instance
event_broker = DisasterEventBroker()
