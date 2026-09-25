import uuid
from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from backend.app.db.base import Base


class DisasterEvent(Base):
    """
    Historical or real-time recorded disaster incident footprints (landslides, flash floods, tremors).
    """
    __tablename__ = "disaster_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    disaster_type = Column(String(50), nullable=False, index=True)  # 'landslide', 'flash_flood', 'cloudburst'
    severity = Column(String(20), nullable=False, index=True)       # 'CRITICAL', 'SEVERE', 'MODERATE'
    event_time = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(String(100), nullable=False)                    # 'STATE_EOC', 'NDRF', 'FIELD_REPORT'

    # PostGIS geometry: Point (epicenter/occurrence) or Polygon (scar / inundation area)
    geometry = Column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=True),
        nullable=False
    )

    __table_args__ = (
        Index("idx_disaster_events_type_time", "disaster_type", "event_time"),
    )

    def __repr__(self) -> str:
        return f"<DisasterEvent(id={self.id}, type='{self.disaster_type}', time='{self.event_time}')>"
