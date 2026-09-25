import uuid
from sqlalchemy import Column, String, Float, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from backend.app.db.base import Base


class RainfallObservation(Base):
    """
    Automated Weather Station (AWS) and telemetry rainfall measurements.
    """
    __tablename__ = "rainfall_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    rainfall_mm = Column(Float, nullable=False)
    observation_time = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(String(100), nullable=False)  # e.g., 'IMD_AWS', 'STATE_PORTAL'

    # PostGIS Point representation for fast spatial joins & radius queries
    geometry = Column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=True
    )

    __table_args__ = (
        Index("idx_rainfall_time_source", "observation_time", "source"),
    )

    def __repr__(self) -> str:
        return f"<RainfallObservation(id={self.id}, rain={self.rainfall_mm}mm, time='{self.observation_time}')>"


class RiverObservation(Base):
    """
    Central Water Commission (CWC) and hydrometric river gauging telemetry.
    """
    __tablename__ = "river_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    station_name = Column(String(150), nullable=False, index=True)
    water_level = Column(Float, nullable=False)   # Current level in meters
    danger_level = Column(Float, nullable=False)  # Flood warning threshold in meters
    observation_time = Column(DateTime(timezone=True), nullable=False, index=True)

    # PostGIS Point representing station geographic position
    geometry = Column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False
    )

    __table_args__ = (
        Index("idx_river_station_time", "station_name", "observation_time"),
    )

    def __repr__(self) -> str:
        return f"<RiverObservation(id={self.id}, station='{self.station_name}', level={self.water_level}m)>"
