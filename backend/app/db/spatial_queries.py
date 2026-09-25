"""Spatial utility functions for PostGIS queries in SIH 2026 Disaster Management."""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, text, and_
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_Intersects, ST_Distance, ST_DWithin, ST_Area, ST_Transform, ST_AsGeoJSON, ST_Intersection

from backend.app.models.habitation import Habitation
from backend.app.models.hazard_zone import HazardZone
from backend.app.models.relocation import RelocationSite, RelocationRecommendation
from backend.app.models.observation import RiverObservation, RainfallObservation


def get_habitations_in_hazard_zones(
    db: Session,
    hazard_type: Optional[str] = None,
    severity: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Find all habitations whose spatial boundary intersects an active hazard red zone.
    Uses PostGIS ST_Intersects accelerated by GiST spatial index.
    """
    query = (
        db.query(
            Habitation.id.label("habitation_id"),
            Habitation.name.label("habitation_name"),
            Habitation.district,
            Habitation.state,
            Habitation.population,
            Habitation.vulnerable_population,
            HazardZone.id.label("hazard_zone_id"),
            HazardZone.hazard_type,
            HazardZone.severity,
            HazardZone.risk_score,
            func.ST_AsGeoJSON(Habitation.geometry).label("habitation_geojson"),
            func.ST_AsGeoJSON(HazardZone.geometry).label("hazard_geojson"),
        )
        .join(HazardZone, ST_Intersects(Habitation.geometry, HazardZone.geometry))
    )

    if hazard_type:
        query = query.filter(HazardZone.hazard_type == hazard_type)
    if severity:
        query = query.filter(HazardZone.severity == severity)

    results = []
    for row in query.all():
        results.append({
            "habitation_id": str(row.habitation_id),
            "habitation_name": row.habitation_name,
            "district": row.district,
            "state": row.state,
            "population": row.population,
            "vulnerable_population": row.vulnerable_population,
            "hazard_zone_id": str(row.hazard_zone_id),
            "hazard_type": row.hazard_type,
            "severity": row.severity,
            "risk_score": row.risk_score,
            "habitation_geojson": row.habitation_geojson,
            "hazard_geojson": row.hazard_geojson,
        })
    return results


def get_habitation_hazard_exposure(
    db: Session,
    habitation_id: uuid.UUID,
) -> Dict[str, Any]:
    """
    Compute precise spatial red-zone overlap percentage and intersecting hazard profiles
    for a specific vulnerable habitation.
    """
    habitation = db.query(Habitation).filter(Habitation.id == habitation_id).first()
    if not habitation:
        return {"error": "Habitation not found"}

    # SQL query calculating total area and intersection area in square meters using EPSG:3857 (Web Mercator)
    stmt = text("""
        SELECT 
            hz.id AS hazard_id,
            hz.hazard_type,
            hz.severity,
            hz.risk_score,
            ROUND(ST_Area(ST_Transform(h.geometry, 3857))::numeric, 2) AS total_habitation_area_sqm,
            ROUND(ST_Area(ST_Transform(ST_Intersection(h.geometry, hz.geometry), 3857))::numeric, 2) AS overlap_area_sqm,
            ROUND(
                (ST_Area(ST_Transform(ST_Intersection(h.geometry, hz.geometry), 3857)) / 
                 NULLIF(ST_Area(ST_Transform(h.geometry, 3857)), 0) * 100)::numeric, 1
            ) AS overlap_percentage
        FROM habitations h
        JOIN hazard_zones hz ON ST_Intersects(h.geometry, hz.geometry)
        WHERE h.id = :hab_id
    """)

    rows = db.execute(stmt, {"hab_id": habitation_id}).mappings().all()

    intersecting_hazards = []
    max_overlap_pct = 0.0
    total_area = 0.0

    for r in rows:
        total_area = float(r["total_habitation_area_sqm"])
        overlap_pct = float(r["overlap_percentage"]) if r["overlap_percentage"] is not None else 0.0
        if overlap_pct > max_overlap_pct:
            max_overlap_pct = overlap_pct

        intersecting_hazards.append({
            "hazard_id": str(r["hazard_id"]),
            "hazard_type": r["hazard_type"],
            "severity": r["severity"],
            "risk_score": float(r["risk_score"]),
            "overlap_area_sqm": float(r["overlap_area_sqm"]),
            "overlap_percentage": overlap_pct,
        })

    return {
        "habitation_id": str(habitation.id),
        "habitation_name": habitation.name,
        "population": habitation.population,
        "vulnerable_population": habitation.vulnerable_population,
        "total_area_sqm": total_area,
        "max_overlap_percentage": max_overlap_pct,
        "is_critical_risk": max_overlap_pct >= 50.0 or any(h["severity"] == "VERY_HIGH" for h in intersecting_hazards),
        "intersecting_hazards": intersecting_hazards,
    }


def find_nearest_safe_relocation_sites(
    db: Session,
    habitation_id: uuid.UUID,
    max_distance_meters: float = 35000.0,
    min_capacity: int = 100,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Find nearest candidate relocation sites with sufficient carrying capacity,
    calculating geodesic distance (WGS84 ellipsoidal distance) and excluding
    sites overlapping severe hazard zones.
    """
    stmt = text("""
        SELECT 
            rs.id AS site_id,
            rs.name AS site_name,
            rs.available_capacity,
            rs.estimated_capacity,
            rs.suitability_score,
            rs.water_score,
            rs.road_access_score,
            rs.healthcare_score,
            rs.hazard_score,
            ROUND(ST_Distance(h.geometry::geography, rs.geometry::geography)::numeric, 1) AS distance_meters,
            ST_AsGeoJSON(rs.geometry) AS site_geojson
        FROM habitations h
        CROSS JOIN relocation_sites rs
        WHERE h.id = :hab_id
          AND rs.available_capacity >= :min_capacity
          AND ST_DWithin(h.geometry::geography, rs.geometry::geography, :max_dist)
          -- Exclude relocation sites that intersect ANY active VERY_HIGH hazard zone
          AND NOT EXISTS (
              SELECT 1 FROM hazard_zones hz
              WHERE hz.severity = 'VERY_HIGH'
                AND ST_Intersects(rs.geometry, hz.geometry)
          )
        ORDER BY distance_meters ASC, rs.suitability_score DESC
        LIMIT :limit;
    """)

    rows = db.execute(stmt, {
        "hab_id": habitation_id,
        "min_capacity": min_capacity,
        "max_dist": max_distance_meters,
        "limit": limit,
    }).mappings().all()

    candidates = []
    for r in rows:
        candidates.append({
            "site_id": str(r["site_id"]),
            "site_name": r["site_name"],
            "distance_meters": float(r["distance_meters"]),
            "distance_km": round(float(r["distance_meters"]) / 1000.0, 2),
            "available_capacity": r["available_capacity"],
            "estimated_capacity": r["estimated_capacity"],
            "suitability_score": float(r["suitability_score"]),
            "water_score": float(r["water_score"]),
            "road_access_score": float(r["road_access_score"]),
            "healthcare_score": float(r["healthcare_score"]),
            "hazard_score": float(r["hazard_score"]),
            "site_geojson": r["site_geojson"],
        })
    return candidates


def get_active_river_danger_alerts(db: Session) -> List[Dict[str, Any]]:
    """
    Query river telemetry stations where measured water level exceeds danger threshold.
    """
    alerts = (
        db.query(
            RiverObservation.id,
            RiverObservation.station_name,
            RiverObservation.water_level,
            RiverObservation.danger_level,
            (RiverObservation.water_level - RiverObservation.danger_level).label("exceedance_m"),
            RiverObservation.observation_time,
            func.ST_AsGeoJSON(RiverObservation.geometry).label("station_geojson"),
        )
        .filter(RiverObservation.water_level >= RiverObservation.danger_level)
        .order_by(text("exceedance_m DESC"))
        .all()
    )

    return [
        {
            "station_id": str(a.id),
            "station_name": a.station_name,
            "water_level": a.water_level,
            "danger_level": a.danger_level,
            "exceedance_m": round(a.exceedance_m, 2),
            "observation_time": a.observation_time.isoformat(),
            "station_geojson": a.station_geojson,
        }
        for a in alerts
    ]


def get_rainfall_in_radius(
    db: Session,
    longitude: float,
    latitude: float,
    radius_meters: float = 20000.0,
    hours: int = 6,
) -> List[Dict[str, Any]]:
    """
    Fetch rainfall observations within radius meters of a coordinate within the last N hours.
    """
    time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
    stmt = text("""
        SELECT 
            id,
            latitude,
            longitude,
            rainfall_mm,
            observation_time,
            source,
            ROUND(ST_Distance(
                geometry::geography, 
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
            )::numeric, 1) AS distance_meters
        FROM rainfall_observations
        WHERE observation_time >= :cutoff
          AND ST_DWithin(
              geometry::geography,
              ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
              :radius
          )
        ORDER BY rainfall_mm DESC;
    """)

    rows = db.execute(stmt, {
        "lon": longitude,
        "lat": latitude,
        "radius": radius_meters,
        "cutoff": time_threshold,
    }).mappings().all()

    return [
        {
            "id": str(r["id"]),
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "rainfall_mm": r["rainfall_mm"],
            "observation_time": r["observation_time"].isoformat(),
            "source": r["source"],
            "distance_km": round(float(r["distance_meters"]) / 1000.0, 2),
        }
        for r in rows
    ]
