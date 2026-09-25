"""Habitation Service: Querying, Filtering, Pagination, and Spatial Formatting."""

import uuid
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import func, or_, desc, asc
from sqlalchemy.orm import Session

from backend.app.models.habitation import Habitation
from backend.app.schemas.common import GeoJSONFeature, GeoJSONFeatureCollection, geometry_to_geojson
from backend.app.schemas.habitation import HabitationItem, HabitationDetail
from backend.app.services.risk_engine import compute_habitation_risk_from_db
from backend.app.services.vulnerability_engine import compute_habitation_vulnerability_from_db
from backend.app.services.priority_engine import compute_habitation_priority_from_db


class HabitationService:
    """Encapsulates database querying, filtering, and GeoJSON transformations for Habitations."""

    @staticmethod
    def get_habitations(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        district: Optional[str] = None,
        taluk: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "name",
        order: str = "asc",
    ) -> Tuple[List[HabitationItem], int]:
        """Fetches paginated, filtered, and sorted habitations."""
        query = db.query(Habitation)

        # Filters
        if district:
            query = query.filter(Habitation.district.ilike(f"%{district}%"))
        if taluk:
            query = query.filter(Habitation.taluk.ilike(f"%{taluk}%"))
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Habitation.name.ilike(search_pattern),
                    Habitation.district.ilike(search_pattern),
                    Habitation.taluk.ilike(search_pattern),
                )
            )

        total = query.count()

        # Sorting
        sort_column = getattr(Habitation, sort_by, Habitation.name)
        if order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Pagination
        offset = (page - 1) * page_size
        records = query.offset(offset).limit(page_size).all()

        items = [
            HabitationItem(
                id=h.id,
                name=h.name,
                district=h.district,
                taluk=h.taluk,
                state=h.state,
                population=h.population,
                vulnerable_population=h.vulnerable_population,
                elderly_population=h.elderly_population,
                children_population=h.children_population,
                disabled_population=h.disabled_population,
                kutcha_houses_pct=h.kutcha_houses_pct,
                elevation=h.elevation,
                slope=h.slope,
                distance_to_road=h.distance_to_road,
                geometry=geometry_to_geojson(h.geometry),
            )
            for h in records
        ]

        return items, total

    @staticmethod
    def get_habitation_by_id(db: Session, habitation_id: uuid.UUID) -> Optional[HabitationDetail]:
        """Retrieves a single habitation with risk and vulnerability previews."""
        h = db.query(Habitation).filter(Habitation.id == habitation_id).first()
        if not h:
            return None

        # Try to enrich with computed risk & vulnerability previews
        risk_score = None
        risk_sev = None
        vuln_score = None
        vuln_sev = None
        priority_tier = None

        try:
            risk = compute_habitation_risk_from_db(db, h.id)
            if risk and isinstance(risk, dict):
                risk_score = risk.get("overall_score")
                risk_sev = risk.get("severity")
            elif risk:
                risk_score = getattr(risk, "overall_score", None)
                risk_sev = getattr(risk, "severity", None)
        except Exception:
            pass

        try:
            vuln = compute_habitation_vulnerability_from_db(db, h.id)
            if vuln and isinstance(vuln, dict):
                vuln_score = vuln.get("vulnerability_score")
                vuln_sev = vuln.get("severity")
            elif vuln:
                vuln_score = getattr(vuln, "vulnerability_score", None)
                vuln_sev = getattr(vuln, "severity", None)
        except Exception:
            pass

        try:
            prio = compute_habitation_priority_from_db(db, h.id)
            if prio and isinstance(prio, dict):
                priority_tier = prio.get("priority")
            elif prio:
                priority_tier = getattr(prio, "priority", None)
        except Exception:
            pass

        return HabitationDetail(
            id=h.id,
            name=h.name,
            district=h.district,
            taluk=h.taluk,
            state=h.state,
            population=h.population,
            vulnerable_population=h.vulnerable_population,
            elderly_population=h.elderly_population,
            children_population=h.children_population,
            disabled_population=h.disabled_population,
            kutcha_houses_pct=h.kutcha_houses_pct,
            elevation=h.elevation,
            slope=h.slope,
            distance_to_road=h.distance_to_road,
            geometry=geometry_to_geojson(h.geometry),
            hazard_risk_score=risk_score,
            hazard_severity=risk_sev,
            vulnerability_score=vuln_score,
            vulnerability_severity=vuln_sev,
            priority_tier=priority_tier,
        )

    @staticmethod
    def get_feature_collection(
        db: Session,
        district: Optional[str] = None,
        taluk: Optional[str] = None,
    ) -> GeoJSONFeatureCollection:
        """Returns standard GeoJSON FeatureCollection of habitations."""
        query = db.query(Habitation)
        if district:
            query = query.filter(Habitation.district.ilike(f"%{district}%"))
        if taluk:
            query = query.filter(Habitation.taluk.ilike(f"%{taluk}%"))

        habitations = query.all()
        features = []

        for h in habitations:
            geom_dict = geometry_to_geojson(h.geometry)
            features.append(
                GeoJSONFeature(
                    id=str(h.id),
                    geometry=geom_dict,
                    properties={
                        "id": str(h.id),
                        "name": h.name,
                        "district": h.district,
                        "taluk": h.taluk,
                        "state": h.state,
                        "population": h.population,
                        "vulnerable_population": h.vulnerable_population,
                        "kutcha_houses_pct": h.kutcha_houses_pct,
                        "elevation": h.elevation,
                        "slope": h.slope,
                    },
                )
            )

        return GeoJSONFeatureCollection(features=features)
