"""Hazard Service: Querying, Filtering, Sorting, and Spatial FeatureCollection Generation."""

import uuid
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import func, desc, asc
from sqlalchemy.orm import Session

from backend.app.models.hazard_zone import HazardZone
from backend.app.schemas.common import GeoJSONFeature, GeoJSONFeatureCollection, geometry_to_geojson
from backend.app.schemas.risk import HazardZoneResponse


class HazardService:
    """Encapsulates querying, spatial filtering, and GeoJSON export for Hazard Red Zones."""

    @staticmethod
    def get_hazard_zones(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        hazard_type: Optional[str] = None,
        severity: Optional[str] = None,
        min_score: Optional[float] = None,
        sort_by: str = "risk_score",
        order: str = "desc",
    ) -> Tuple[List[HazardZoneResponse], int]:
        """Fetches paginated, filtered, and sorted hazard zones."""
        query = db.query(HazardZone)

        if hazard_type:
            query = query.filter(HazardZone.hazard_type.ilike(f"%{hazard_type}%"))
        if severity:
            query = query.filter(HazardZone.severity == severity.upper())
        if min_score is not None:
            query = query.filter(HazardZone.risk_score >= min_score)

        total = query.count()

        sort_col = getattr(HazardZone, sort_by, HazardZone.risk_score)
        if order.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        offset = (page - 1) * page_size
        records = query.offset(offset).limit(page_size).all()

        items = [
            HazardZoneResponse(
                id=hz.id,
                hazard_type=hz.hazard_type,
                risk_score=hz.risk_score,
                severity=hz.severity,
                source=hz.source,
                timestamp=hz.timestamp,
                geometry=geometry_to_geojson(hz.geometry) or {},
            )
            for hz in records
        ]

        return items, total

    @staticmethod
    def get_hazard_zone_by_id(db: Session, hazard_id: uuid.UUID) -> Optional[HazardZoneResponse]:
        """Retrieves a single hazard zone by its unique identifier."""
        hz = db.query(HazardZone).filter(HazardZone.id == hazard_id).first()
        if not hz:
            return None

        return HazardZoneResponse(
            id=hz.id,
            hazard_type=hz.hazard_type,
            risk_score=hz.risk_score,
            severity=hz.severity,
            source=hz.source,
            timestamp=hz.timestamp,
            geometry=geometry_to_geojson(hz.geometry) or {},
        )

    @staticmethod
    def get_feature_collection(
        db: Session,
        hazard_type: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> GeoJSONFeatureCollection:
        """Generates standard GeoJSON FeatureCollection of hazard zones."""
        query = db.query(HazardZone)
        if hazard_type:
            query = query.filter(HazardZone.hazard_type.ilike(f"%{hazard_type}%"))
        if severity:
            query = query.filter(HazardZone.severity == severity.upper())

        records = query.all()
        features = []

        for hz in records:
            features.append(
                GeoJSONFeature(
                    id=str(hz.id),
                    geometry=geometry_to_geojson(hz.geometry),
                    properties={
                        "id": str(hz.id),
                        "hazard_type": hz.hazard_type,
                        "risk_score": hz.risk_score,
                        "severity": hz.severity,
                        "source": hz.source,
                        "timestamp": hz.timestamp.isoformat() if hz.timestamp else None,
                    },
                )
            )

        return GeoJSONFeatureCollection(features=features)
