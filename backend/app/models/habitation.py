import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from backend.app.db.base import Base


class Habitation(Base):
    """
    Vulnerable or monitored human settlements within disaster-prone jurisdictions.
    """
    __tablename__ = "habitations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    population = Column(Integer, nullable=False, default=0)
    vulnerable_population = Column(Integer, nullable=False, default=0)
    
    # PostGIS geometry polygon or multipolygon boundary (WGS84 SRID 4326)
    geometry = Column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=True),
        nullable=False
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    recommendations = relationship(
        "RelocationRecommendation",
        back_populates="habitation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("idx_habitations_district_state", "district", "state"),
    )

    def __repr__(self) -> str:
        return f"<Habitation(id={self.id}, name='{self.name}', district='{self.district}')>"
