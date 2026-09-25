import uuid
from sqlalchemy import Column, String, Float, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from backend.app.db.base import Base


class HazardZone(Base):
    """
    Multi-hazard red zones and risk delineations (e.g. landslide, flood, seismic zones).
    """
    __tablename__ = "hazard_zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    hazard_type = Column(String(50), nullable=False, index=True)  # e.g., 'landslide', 'flash_flood', 'earthquake'
    risk_score = Column(Float, nullable=False)                    # Scale 0.0 - 1.0 (or normalized index)
    severity = Column(String(20), nullable=False, index=True)     # 'VERY_HIGH', 'HIGH', 'MODERATE', 'LOW'
    source = Column(String(100), nullable=False)                  # e.g., 'ISRO_BHUVAN', 'GSI', 'IMD', 'STATE_SDMA'
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # PostGIS geometry polygon or multipolygon delineating hazard extent
    geometry = Column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=True),
        nullable=False
    )

    __table_args__ = (
        Index("idx_hazard_zones_type_severity", "hazard_type", "severity"),
        Index("idx_hazard_zones_time_type", "timestamp", "hazard_type"),
    )

    def __repr__(self) -> str:
        return f"<HazardZone(id={self.id}, type='{self.hazard_type}', severity='{self.severity}')>"
