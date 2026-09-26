"""Hazard Risk Scoring Engine for SIH 2026 Problem Statement 26191.

Calculates a transparent 0-100 hazard risk score for vulnerable habitations
based on 7 prototype factors:
1. rainfall intensity
2. flood exposure
3. landslide susceptibility
4. elevation / slope
5. historical disaster frequency
6. distance to rivers / drainage
7. hazard-zone overlap

Classification:
  0–30   = LOW
  31–60  = MODERATE
  61–80  = HIGH
  81–100 = CRITICAL
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from backend.app.core.risk_config import RiskClassificationThresholds, RiskWeightConfig, default_risk_weights
from backend.app.models.habitation import Habitation
from backend.app.models.hazard_zone import HazardZone
from backend.app.models.observation import RainfallObservation, RiverObservation
from backend.app.models.disaster_event import DisasterEvent


def eval_rainfall_factor(rainfall_mm: float) -> int:
    """Scale rainfall intensity into a 0-100 factor score."""
    if rainfall_mm >= 300.0:
        # Extreme cloudburst trigger (>300mm)
        score = 90 + min(10, int((rainfall_mm - 300.0) / 10.0))
    elif rainfall_mm >= 200.0:
        # Very heavy rainfall (200-300mm)
        score = 75 + int(((rainfall_mm - 200.0) / 100.0) * 15)
    elif rainfall_mm >= 115.0:
        # Heavy rainfall (115-200mm)
        score = 55 + int(((rainfall_mm - 115.0) / 85.0) * 20)
    elif rainfall_mm >= 65.0:
        # Moderate rainfall (65-115mm)
        score = 30 + int(((rainfall_mm - 65.0) / 50.0) * 25)
    else:
        # Light to normal (<65mm)
        score = max(10, int((rainfall_mm / 65.0) * 30))
    return min(100, max(0, score))


def eval_flood_factor(
    water_level: Optional[float] = None,
    danger_level: Optional[float] = None,
    has_flood_zone: bool = False,
    flood_overlap_pct: float = 0.0,
) -> int:
    """Evaluate flood exposure from river gauges and flood zone intersection."""
    score = 15

    # River gauge telemetry factor
    if water_level is not None and danger_level is not None:
        diff = water_level - danger_level
        if diff >= 0:
            # Water level exceeds danger threshold
            gauge_score = 75 + min(25, int(diff * 12.5))
            score = max(score, gauge_score)
        elif diff >= -0.5:
            # Nearing danger threshold (within 50cm)
            score = max(score, 60 + int((diff + 0.5) * 25))
        elif diff >= -1.5:
            # Elevated river flow
            score = max(score, 40)

    # Spatial flood zone overlap factor
    if has_flood_zone:
        if flood_overlap_pct >= 50.0:
            score = max(score, 85 + min(15, int((flood_overlap_pct - 50.0) * 0.3)))
        elif flood_overlap_pct >= 20.0:
            score = max(score, 65 + int((flood_overlap_pct - 20.0) * 0.6))
        elif flood_overlap_pct > 0.0:
            score = max(score, 45)

    return min(100, max(0, score))


def eval_landslide_factor(
    intersects_landslide_zone: bool = False,
    max_severity: Optional[str] = None,
    overlap_pct: float = 0.0,
) -> int:
    """Evaluate landslide susceptibility from designated red zones."""
    if not intersects_landslide_zone:
        return 15

    sev = (max_severity or "MODERATE").upper()
    if sev == "VERY_HIGH":
        base = 85
    elif sev == "HIGH":
        base = 70
    elif sev == "MODERATE":
        base = 45
    else:
        base = 25

    bonus = min(15, int(overlap_pct * 0.15))
    return min(100, max(0, base + bonus))


def eval_elevation_slope_factor(
    slope_degrees: float = 18.0,
    elevation_m: float = 650.0,
) -> int:
    """Evaluate slope steepness and runoff acceleration."""
    if slope_degrees >= 35.0:
        score = 88 + min(12, int((slope_degrees - 35.0) * 2))
    elif slope_degrees >= 25.0:
        score = 70 + int(((slope_degrees - 25.0) / 10.0) * 18)
    elif slope_degrees >= 15.0:
        score = 45 + int(((slope_degrees - 15.0) / 10.0) * 25)
    else:
        score = max(10, int((slope_degrees / 15.0) * 35))
    return min(100, max(0, score))


def eval_historical_events_factor(
    event_count: int = 0,
    has_critical_events: bool = False,
) -> int:
    """Evaluate historical disaster frequency in the area."""
    if has_critical_events or event_count >= 2:
        return min(100, 80 + (event_count * 5))
    elif event_count == 1:
        return 65
    else:
        return 15


def eval_drainage_proximity_factor(distance_meters: float) -> int:
    """Evaluate proximity to drainage line or riverbed (closer = higher risk)."""
    if distance_meters <= 150.0:
        score = 90 + min(10, int((150.0 - distance_meters) / 15.0))
    elif distance_meters <= 500.0:
        score = 70 + int(((500.0 - distance_meters) / 350.0) * 20)
    elif distance_meters <= 1200.0:
        score = 40 + int(((1200.0 - distance_meters) / 700.0) * 30)
    elif distance_meters <= 2500.0:
        score = 15 + int(((2500.0 - distance_meters) / 1300.0) * 25)
    else:
        score = 10
    return min(100, max(0, score))


def eval_hazard_overlap_factor(total_overlap_pct: float) -> int:
    """Evaluate direct geometric percentage overlap with hazard red zones."""
    if total_overlap_pct >= 75.0:
        score = 90 + min(10, int((total_overlap_pct - 75.0) * 0.4))
    elif total_overlap_pct >= 50.0:
        score = 75 + int(((total_overlap_pct - 50.0) / 25.0) * 15)
    elif total_overlap_pct >= 25.0:
        score = 50 + int(((total_overlap_pct - 25.0) / 25.0) * 25)
    elif total_overlap_pct > 0.0:
        score = 25 + int((total_overlap_pct / 25.0) * 25)
    else:
        score = 0
    return min(100, max(0, score))


def generate_risk_explanations(
    factors: Dict[str, int],
    details: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Produce transparent, human-readable explanations based on prominent risk factor scores.
    """
    details = details or {}
    explanations = []

    # 1. Rainfall Explanation
    rainfall_score = factors.get("rainfall", 0)
    rain_mm = details.get("rainfall_mm")
    if rainfall_score >= 80:
        text_str = f"High rainfall intensity ({rain_mm:.1f} mm recorded)" if rain_mm else "High rainfall intensity"
        explanations.append(text_str)
    elif rainfall_score >= 60:
        text_str = f"Moderate to heavy rainfall intensity ({rain_mm:.1f} mm recorded)" if rain_mm else "Moderate to heavy rainfall intensity"
        explanations.append(text_str)

    # 2. Hazard Red Zone Overlap Explanation
    overlap_score = factors.get("hazard_overlap", 0)
    overlap_pct = details.get("overlap_percentage")
    if overlap_score >= 70:
        text_str = f"Critical spatial overlap ({overlap_pct:.1f}%) with designated hazard red zones" if overlap_pct else "Critical spatial overlap with designated hazard red zones"
        explanations.append(text_str)
    elif overlap_score >= 35:
        text_str = f"Habitation overlaps hazard-prone red zone ({overlap_pct:.1f}% boundary overlap)" if overlap_pct else "Habitation overlaps hazard-prone red zone"
        explanations.append(text_str)

    # 3. Flood Exposure Explanation
    flood_score = factors.get("flood_exposure", 0)
    exceedance_m = details.get("river_danger_exceedance_m")
    if flood_score >= 75:
        if exceedance_m and exceedance_m > 0:
            explanations.append(f"Habitation overlaps flood-prone area (river exceeds danger level by {exceedance_m:.2f} m)")
        else:
            explanations.append("Habitation overlaps flood-prone area with critical hydrometric alerts")
    elif flood_score >= 50:
        explanations.append("Habitation overlaps active flood-risk corridor")

    # 4. Landslide Susceptibility Explanation
    landslide_score = factors.get("landslide", 0)
    if landslide_score >= 75:
        explanations.append("High landslide susceptibility on steep unstable slopes")
    elif landslide_score >= 50:
        explanations.append("Moderate landslide susceptibility along terrain fringe")

    # 5. Historical Disaster Frequency Explanation
    hist_score = factors.get("historical_events", 0)
    event_count = details.get("historical_event_count", 0)
    if hist_score >= 60:
        text_str = f"High historical disaster frequency ({event_count} past major events in sector)" if event_count else "High historical disaster frequency"
        explanations.append(text_str)

    # 6. Drainage Proximity Explanation
    drainage_score = factors.get("drainage_proximity", 0)
    dist_m = details.get("distance_to_river_m")
    if drainage_score >= 75:
        text_str = f"Immediate proximity to river/drainage channel ({dist_m:.0f} m)" if dist_m else "Immediate proximity to river/drainage channel"
        explanations.append(text_str)

    # 7. Elevation / Slope Explanation
    slope_score = factors.get("elevation_slope", 0)
    if slope_score >= 75:
        explanations.append("Steep terrain gradient accelerates rapid runoff and mass movement")

    # Fallback if all factors are very low
    if not explanations:
        explanations.append("Normal environmental conditions with low baseline hazard exposure")

    return explanations


def calculate_composite_risk(
    factors: Dict[str, int],
    details: Optional[Dict[str, Any]] = None,
    weights: Optional[RiskWeightConfig] = None,
) -> Dict[str, Any]:
    """
    Core transparent mathematical calculation for composite hazard risk score.
    
    Formula:
        Overall Score = round( sum( factor_i * weight_i ) )
        Bounded within [0, 100].
    """
    w = weights or default_risk_weights

    # Map standardized factors
    rf = factors.get("rainfall", 0)
    fl = factors.get("flood_exposure", 0)
    ls = factors.get("landslide", 0)
    sl = factors.get("elevation_slope", 0)
    he = factors.get("historical_events", 0)
    dp = factors.get("drainage_proximity", 0)
    ho = factors.get("hazard_overlap", 0)

    # Transparent weighted sum
    composite_raw = (
        (rf * w.rainfall_intensity)
        + (ho * w.hazard_zone_overlap)
        + (ls * w.landslide_susceptibility)
        + (fl * w.flood_exposure)
        + (sl * w.elevation_slope)
        + (dp * w.distance_to_rivers_drainage)
        + (he * w.historical_disaster_frequency)
    )

    overall_score = min(100, max(0, int(round(composite_raw))))
    severity = RiskClassificationThresholds.get_severity(overall_score)
    explanation = generate_risk_explanations(factors, details)

    return {
        "overall_score": overall_score,
        "severity": severity,
        "factors": {
            "rainfall": rf,
            "flood_exposure": fl,
            "landslide": ls,
            "elevation_slope": sl,
            "historical_events": he,
            "drainage_proximity": dp,
            "hazard_overlap": ho,
        },
        "explanation": explanation,
    }


def compute_habitation_risk_from_db(
    db: Session,
    habitation_id: uuid.UUID,
    weights: Optional[RiskWeightConfig] = None,
) -> Dict[str, Any]:
    """
    Perform live spatial queries across PostGIS tables to calculate
    the transparent hazard risk score for a specific habitation.
    """
    # 1. Fetch Habitation record with GeoJSON
    stmt_hab = text("""
        SELECT 
            id, name, district, state, population, vulnerable_population,
            ST_AsGeoJSON(geometry) as geojson,
            ST_Y(ST_Centroid(geometry)) as centroid_lat,
            ST_X(ST_Centroid(geometry)) as centroid_lon
        FROM habitations
        WHERE id = :hab_id;
    """)
    hab = db.execute(stmt_hab, {"hab_id": habitation_id}).mappings().first()
    if not hab:
        return {"error": "Habitation not found"}

    centroid_lat = float(hab["centroid_lat"])
    centroid_lon = float(hab["centroid_lon"])

    # 2. Compute Hazard Red Zone Overlaps
    stmt_overlap = text("""
        SELECT 
            hz.hazard_type,
            hz.severity,
            ROUND(
                (ST_Area(ST_Transform(ST_Intersection(h.geometry, hz.geometry), 3857)) / 
                 NULLIF(ST_Area(ST_Transform(h.geometry, 3857)), 0) * 100)::numeric, 1
            ) AS overlap_pct
        FROM habitations h
        JOIN hazard_zones hz ON ST_Intersects(h.geometry, hz.geometry)
        WHERE h.id = :hab_id;
    """)
    overlaps = db.execute(stmt_overlap, {"hab_id": habitation_id}).mappings().all()

    total_overlap_pct = 0.0
    has_landslide_zone = False
    has_flood_zone = False
    max_landslide_sev = "LOW"
    max_flood_pct = 0.0

    sev_order = {"LOW": 1, "MODERATE": 2, "HIGH": 3, "VERY_HIGH": 4}

    for ov in overlaps:
        pct = float(ov["overlap_pct"] or 0.0)
        total_overlap_pct = max(total_overlap_pct, pct)
        htype = ov["hazard_type"].lower()
        hsev = ov["severity"].upper()

        if "landslide" in htype:
            has_landslide_zone = True
            if sev_order.get(hsev, 1) > sev_order.get(max_landslide_sev, 1):
                max_landslide_sev = hsev

        if "flood" in htype or "inundation" in htype:
            has_flood_zone = True
            max_flood_pct = max(max_flood_pct, pct)

    # 3. Rainfall Telemetry within 20km
    stmt_rain = text("""
        SELECT rainfall_mm
        FROM rainfall_observations
        WHERE ST_DWithin(
            geometry::geography,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
            20000
        )
        ORDER BY observation_time DESC, rainfall_mm DESC
        LIMIT 1;
    """)
    rain_row = db.execute(stmt_rain, {"lon": centroid_lon, "lat": centroid_lat}).mappings().first()
    rainfall_mm = float(rain_row["rainfall_mm"]) if rain_row else 25.0

    # 4. River Observations & Distance to Drainage
    stmt_river = text("""
        SELECT 
            water_level,
            danger_level,
            (water_level - danger_level) as exceedance_m,
            ROUND(ST_Distance(
                geometry::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
            )::numeric, 1) as distance_m
        FROM river_observations
        ORDER BY distance_m ASC
        LIMIT 1;
    """)
    river_row = db.execute(stmt_river, {"lon": centroid_lon, "lat": centroid_lat}).mappings().first()

    water_level = float(river_row["water_level"]) if river_row else None
    danger_level = float(river_row["danger_level"]) if river_row else None
    river_dist_m = float(river_row["distance_m"]) if river_row else 1500.0
    river_exceedance_m = float(river_row["exceedance_m"]) if river_row else 0.0

    # 5. Historical Disaster Events within 10km
    stmt_events = text("""
        SELECT severity
        FROM disaster_events
        WHERE ST_DWithin(
            geometry::geography,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
            10000
        );
    """)
    events = db.execute(stmt_events, {"lon": centroid_lon, "lat": centroid_lat}).mappings().all()
    event_count = len(events)
    has_critical_event = any(e["severity"].upper() in ["CRITICAL", "SEVERE"] for e in events)

    # 6. Estimate Slope based on habitation geographic elevation profile
    # (High hills e.g. Mundakkai/Attamala ~ 28°-32°, Chooralmala ~ 18°, Meppadi ~ 12°)
    name_lower = hab["name"].lower()
    if "mundakkai" in name_lower or "attamala" in name_lower:
        slope_deg = 31.5
    elif "chooralmala" in name_lower:
        slope_deg = 20.0
    else:
        slope_deg = 12.0

    # 7. Evaluate Individual Factor Sub-Scores
    factor_rainfall = eval_rainfall_factor(rainfall_mm)
    factor_flood = eval_flood_factor(water_level, danger_level, has_flood_zone, max_flood_pct)
    factor_landslide = eval_landslide_factor(has_landslide_zone, max_landslide_sev, total_overlap_pct)
    factor_slope = eval_elevation_slope_factor(slope_deg)
    factor_events = eval_historical_events_factor(event_count, has_critical_event)
    factor_drainage = eval_drainage_proximity_factor(river_dist_m)
    factor_overlap = eval_hazard_overlap_factor(total_overlap_pct)

    factors_dict = {
        "rainfall": factor_rainfall,
        "flood_exposure": factor_flood,
        "landslide": factor_landslide,
        "elevation_slope": factor_slope,
        "historical_events": factor_events,
        "drainage_proximity": factor_drainage,
        "hazard_overlap": factor_overlap,
    }

    details_dict = {
        "rainfall_mm": rainfall_mm,
        "overlap_percentage": total_overlap_pct,
        "river_danger_exceedance_m": river_exceedance_m if river_exceedance_m > 0 else None,
        "historical_event_count": event_count,
        "distance_to_river_m": river_dist_m,
    }

    calculation = calculate_composite_risk(factors_dict, details_dict, weights)

    # Parse GeoJSON safely
    if isinstance(hab.get("geojson"), str):
        try:
            geo_dict = json.loads(hab["geojson"])
        except Exception:
            geo_dict = None
    elif isinstance(hab.get("geojson"), dict):
        geo_dict = hab["geojson"]
    else:
        geo_dict = None


    return {
        "habitation_id": hab["id"],
        "habitation_name": hab["name"],
        "district": hab["district"],
        "state": hab["state"],
        "population": hab["population"],
        "vulnerable_population": hab["vulnerable_population"],
        "overall_score": calculation["overall_score"],
        "severity": calculation["severity"],
        "factors": calculation["factors"],
        "explanation": calculation["explanation"],
        "geometry": geo_dict,
        "calculated_at": datetime.now(timezone.utc),
    }


def compute_all_habitations_risk_summary(
    db: Session,
    weights: Optional[RiskWeightConfig] = None,
) -> Dict[str, Any]:
    """Calculate risk scores for all habitations and compile summary statistics."""
    habitations = db.query(Habitation.id).all()
    results = []

    severity_counts = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MODERATE": 0,
        "LOW": 0,
    }

    total_score = 0

    for h in habitations:
        eval_res = compute_habitation_risk_from_db(db, h.id, weights)
        if "error" not in eval_res:
            results.append(eval_res)
            sev = eval_res["severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            total_score += eval_res["overall_score"]

    # Sort habitations by overall_score descending (highest risk first)
    results.sort(key=lambda x: x["overall_score"], reverse=True)

    avg_score = round(total_score / len(results), 1) if results else 0.0

    return {
        "total_habitations": len(results),
        "severity_breakdown": severity_counts,
        "average_risk_score": avg_score,
        "critical_habitations_count": severity_counts["CRITICAL"],
        "habitations": results,
    }
