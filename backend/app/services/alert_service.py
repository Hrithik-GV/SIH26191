"""Alert Service: Querying, Filtering, and GeoJSON Formatting for Emergency Warnings."""

from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from backend.app.models.disaster_event import DisasterEvent
from backend.app.schemas.common import GeoJSONFeature, GeoJSONFeatureCollection, geometry_to_geojson
from backend.app.schemas.alert import AlertItem, AlertsSummaryResponse


class AlertService:
    """Encapsulates querying, filtering, and GeoJSON transformations for Disaster Alerts."""

    @staticmethod
    def get_alerts(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        severity: Optional[str] = None,
        disaster_type: Optional[str] = None,
        sort_by: str = "event_time",
        order: str = "desc",
    ) -> Tuple[List[AlertItem], int]:
        """Fetches paginated, filtered, and sorted disaster events and alerts."""
        query = db.query(DisasterEvent)

        if severity:
            query = query.filter(DisasterEvent.severity == severity.upper())
        if disaster_type:
            query = query.filter(DisasterEvent.disaster_type.ilike(f"%{disaster_type}%"))

        total = query.count()

        sort_col = getattr(DisasterEvent, sort_by, DisasterEvent.event_time)
        if order.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        offset = (page - 1) * page_size
        records = query.offset(offset).limit(page_size).all()

        items = [
            AlertItem(
                id=str(ev.id),
                disaster_type=ev.disaster_type,
                severity=ev.severity,
                event_time=ev.event_time,
                source=ev.source,
                headline=f"{ev.severity} alert: {ev.disaster_type.replace('_', ' ').title()}",
                description=f"Active disaster event recorded by {ev.source}",
                is_active=True,
                geometry=geometry_to_geojson(ev.geometry),
            )
            for ev in records
        ]

        return items, total

    @staticmethod
    def get_alert_by_id(db: Session, alert_id: str) -> Optional[AlertItem]:
        """Retrieves a single disaster alert."""
        import uuid
        try:
            val_uuid = uuid.UUID(alert_id)
            ev = db.query(DisasterEvent).filter(DisasterEvent.id == val_uuid).first()
        except ValueError:
            ev = db.query(DisasterEvent).filter(DisasterEvent.source.ilike(f"%{alert_id}%")).first()

        if not ev:
            return None

        return AlertItem(
            id=str(ev.id),
            disaster_type=ev.disaster_type,
            severity=ev.severity,
            event_time=ev.event_time,
            source=ev.source,
            headline=f"{ev.severity} alert: {ev.disaster_type.replace('_', ' ').title()}",
            description=f"Active disaster event recorded by {ev.source}",
            is_active=True,
            geometry=geometry_to_geojson(ev.geometry),
        )

    @staticmethod
    def get_feature_collection(
        db: Session,
        severity: Optional[str] = None,
        disaster_type: Optional[str] = None,
    ) -> GeoJSONFeatureCollection:
        """Returns standard GeoJSON FeatureCollection of emergency alerts."""
        query = db.query(DisasterEvent)
        if severity:
            query = query.filter(DisasterEvent.severity == severity.upper())
        if disaster_type:
            query = query.filter(DisasterEvent.disaster_type.ilike(f"%{disaster_type}%"))

        records = query.all()
        features = []

        for ev in records:
            features.append(
                GeoJSONFeature(
                    id=str(ev.id),
                    geometry=geometry_to_geojson(ev.geometry),
                    properties={
                        "id": str(ev.id),
                        "disaster_type": ev.disaster_type,
                        "severity": ev.severity,
                        "source": ev.source,
                        "event_time": ev.event_time.isoformat() if ev.event_time else None,
                        "headline": f"{ev.severity} alert: {ev.disaster_type.replace('_', ' ').title()}",
                    },
                )
            )

        return GeoJSONFeatureCollection(features=features)
