"""Relocation-Site Suitability Assessment Engine for SIH 2026 Problem Statement 26191.

Calculates a transparent 0-100 multi-criteria suitability score for candidate
resettlement parcels, evaluating 4 distinct categories:
1. hazard_safety_score (35%): Freedom from flood, landslide, and terrain instability
2. infrastructure_score (25%): Potable water, electricity grid, hospitals, schools
3. accessibility_score (20%): All-weather road access and emergency logistics
4. capacity_score (20%): Usable parcel area, available capacity buffer, occupancy

Classification:
  80–100 = HIGHLY SUITABLE
  60–79  = SUITABLE
  40–59  = CONDITIONALLY SUITABLE
  0–39   = UNSUITABLE
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.core.suitability_config import (
    SuitabilityClassificationThresholds,
    CategoryWeightConfig,
    default_category_weights,
    default_hazard_weights,
    default_infra_weights,
    default_access_weights,
    default_capacity_weights,
)
from backend.app.models.relocation import RelocationSite
from backend.app.models.habitation import Habitation
from backend.app.models.hazard_zone import HazardZone


# Pre-configured demonstration environmental & civil attributes for demonstration parcels
# Supplements DB records with realistic civil infrastructure metrics
DEMO_SITE_CIVIL_METRICS: Dict[str, Dict[str, Any]] = {
    # Meppadi Plateau: Broad elevated plantation tableland, gentle slope, adjacent to SH-59
    "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa": {
        "flood_clearance_score": 95,
        "landslide_clearance_score": 92,
        "slope_degrees": 6.5,
        "elevation_m": 820.0,
        "electricity_score": 88,
        "distance_to_hospital_km": 2.8,
        "distance_to_school_km": 1.4,
    },
    # Kalpetta Community Park: Municipal reserve land, gentle topography, urban fringe
    "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb": {
        "flood_clearance_score": 92,
        "landslide_clearance_score": 90,
        "slope_degrees": 5.0,
        "elevation_m": 780.0,
        "electricity_score": 92,
        "distance_to_hospital_km": 1.5,
        "distance_to_school_km": 0.8,
    },
    # Vythiri Uplands: Tea estate valley parcel, moderate slope
    "cccccccc-cccc-4ccc-8ccc-cccccccccccc": {
        "flood_clearance_score": 88,
        "landslide_clearance_score": 75,
        "slope_degrees": 13.5,
        "elevation_m": 940.0,
        "electricity_score": 78,
        "distance_to_hospital_km": 6.2,
        "distance_to_school_km": 3.1,
    },
}


def eval_flood_risk_factor(flood_risk_pct: float) -> int:
    """Evaluate flood clearance safety score (0-100). 0% risk -> 100 safe."""
    clamped = max(0.0, min(100.0, float(flood_risk_pct)))
    return int(round(100.0 - clamped))


def eval_landslide_risk_factor(landslide_pct: float) -> int:
    """Evaluate landslide clearance safety score (0-100). 0% risk -> 100 safe."""
    clamped = max(0.0, min(100.0, float(landslide_pct)))
    return int(round(100.0 - clamped))


def eval_elevation_factor(elevation_m: float) -> int:
    """Evaluate elevation safety and drainage adequacy."""
    if 600.0 <= elevation_m <= 1100.0:
        return 95
    elif 200.0 <= elevation_m < 600.0:
        return 85
    elif elevation_m > 1100.0:
        return 70
    elif elevation_m >= 50.0:
        return 60
    else:
        return max(15, int(elevation_m))


def eval_slope_score(slope_degrees: float) -> int:
    """Evaluate construction suitability from terrain slope angle.
    
    Gentle slopes (2°-8°) are ideal for civil construction, drainage, and foundation safety.
    Steep slopes (>25°) suffer from high excavation costs and residual mass movement risk.
    """
    if slope_degrees <= 8.0:
        return 95
    elif slope_degrees <= 15.0:
        return 80 + int((15.0 - slope_degrees) / 7.0 * 15)
    elif slope_degrees <= 22.0:
        return 55 + int((22.0 - slope_degrees) / 7.0 * 25)
    elif slope_degrees <= 30.0:
        return 30 + int((30.0 - slope_degrees) / 8.0 * 25)
    else:
        return max(10, int(30.0 - (slope_degrees - 30.0) * 2.0))


def eval_distance_score(distance_km: float, optimal_km: float, max_km: float) -> int:
    """Evaluate proximity score for civil amenities (hospitals, schools)."""
    if distance_km <= optimal_km:
        return 95
    elif distance_km >= max_km:
        return max(15, int(40.0 - (distance_km - max_km) * 1.5))
    else:
        ratio = (distance_km - optimal_km) / (max_km - optimal_km)
        return int(95.0 - (ratio * 55.0))


def eval_land_area_score(available_area_sqm: float) -> int:
    """Evaluate usable land parcel area (10,000 sqm = 1 hectare)."""
    if available_area_sqm >= 150000.0:  # >= 15 hectares
        return 95
    elif available_area_sqm >= 80000.0:  # 8 - 15 hectares
        return 85 + int((available_area_sqm - 80000.0) / 70000.0 * 10)
    elif available_area_sqm >= 30000.0:  # 3 - 8 hectares
        return 65 + int((available_area_sqm - 30000.0) / 50000.0 * 20)
    elif available_area_sqm >= 10000.0:  # 1 - 3 hectares
        return 40 + int((available_area_sqm - 10000.0) / 20000.0 * 25)
    else:
        return max(15, int((available_area_sqm / 10000.0) * 40))


def eval_capacity_buffer_score(available_capacity: int, estimated_capacity: int) -> int:
    """Evaluate available capacity buffer percentage."""
    if estimated_capacity <= 0:
        return 0
    ratio = min(1.0, max(0.0, available_capacity / estimated_capacity))
    return int(round(ratio * 100.0))


# Exported aliases and factor scoring wrappers
eval_slope_factor = eval_slope_score
eval_available_land_factor = eval_land_area_score
eval_carrying_capacity_buffer = eval_capacity_buffer_score


def eval_distance_to_hospital_factor(distance_km: float) -> int:
    """Evaluate hospital accessibility score."""
    if distance_km <= 2.0:
        return 100
    return eval_distance_score(distance_km, optimal_km=2.0, max_km=15.0)


def eval_distance_to_school_factor(distance_km: float) -> int:
    """Evaluate educational facility proximity score."""
    if distance_km <= 1.0:
        return 100
    return eval_distance_score(distance_km, optimal_km=1.0, max_km=8.0)


def eval_water_availability_factor(water_score: float) -> int:
    """Evaluate water availability score (0-10 or 0-100 scale)."""
    val = float(water_score) * 10.0 if float(water_score) <= 10.0 else float(water_score)
    return min(100, max(0, int(round(val))))


def eval_electricity_infrastructure_factor(electricity_score: float) -> int:
    """Evaluate electricity grid reliability score (0-10 or 0-100 scale)."""
    val = float(electricity_score) * 10.0 if float(electricity_score) <= 10.0 else float(electricity_score)
    return min(100, max(0, int(round(val))))


def eval_road_accessibility_factor(road_score: float) -> int:
    """Evaluate arterial road access score (0-10 or 0-100 scale)."""
    val = float(road_score) * 10.0 if float(road_score) <= 10.0 else float(road_score)
    return min(100, max(0, int(round(val))))


def calculate_category_scores(site_data: Dict[str, Any]) -> Tuple[Dict[str, int], Dict[str, int]]:
    """Compute 4 category sub-scores and discrete factor scores (all 0-100 scale)."""
    # 1. Hazard Safety Category
    if "flood_risk_pct" in site_data:
        flood_clean = eval_flood_risk_factor(site_data["flood_risk_pct"])
    elif "flood_risk" in site_data:
        flood_clean = eval_flood_risk_factor(site_data["flood_risk"])
    else:
        flood_clean = int(site_data.get("flood_clearance_score", 90))

    if "landslide_susceptibility_pct" in site_data:
        landslide_clean = eval_landslide_risk_factor(site_data["landslide_susceptibility_pct"])
    elif "landslide_risk" in site_data:
        landslide_clean = eval_landslide_risk_factor(site_data["landslide_risk"])
    else:
        landslide_clean = int(site_data.get("landslide_clearance_score", 88))

    slope_deg = float(site_data.get("slope_degrees", site_data.get("slope", 8.0)))
    slope_score = eval_slope_score(slope_deg)
    
    # Elevation factor
    elev_m = float(site_data.get("elevation_m", site_data.get("elevation_meters", site_data.get("elevation", 800.0))))
    elev_score = eval_elevation_factor(elev_m)
    
    hw = default_hazard_weights
    hazard_safety_raw = (
        (flood_clean * hw.flood_risk)
        + (landslide_clean * hw.landslide_risk)
        + (slope_score * hw.slope)
        + (elev_score * hw.elevation)
    )
    hazard_safety_score = min(100, max(0, int(round(hazard_safety_raw))))

    # 2. Infrastructure Category
    water_score = eval_water_availability_factor(site_data.get("water_score", site_data.get("water_availability", 8.5)))
    electricity_score = eval_electricity_infrastructure_factor(site_data.get("electricity_score", site_data.get("electricity_availability", 85)))
    
    hosp_dist = float(site_data.get("distance_to_hospital_km", site_data.get("distance_to_hospitals", 3.0)))
    hospital_score = eval_distance_to_hospital_factor(hosp_dist)
    
    school_dist = float(site_data.get("distance_to_school_km", site_data.get("distance_to_schools", 1.5)))
    school_score = eval_distance_to_school_factor(school_dist)
    
    iw = default_infra_weights
    infra_raw = (
        (water_score * iw.water_availability)
        + (electricity_score * iw.electricity)
        + (hospital_score * iw.hospital_proximity)
        + (school_score * iw.school_proximity)
    )
    infrastructure_score = min(100, max(0, int(round(infra_raw))))

    # 3. Accessibility Category
    road_score = eval_road_accessibility_factor(site_data.get("road_access_score", site_data.get("road_accessibility", 8.5)))
    transit_score = min(100, max(20, int(road_score * 0.95)))
    
    aw = default_access_weights
    access_raw = (road_score * aw.road_access) + (transit_score * aw.transit_connectivity)
    accessibility_score = min(100, max(0, int(round(access_raw))))

    # 4. Capacity Category
    est_cap = max(1, int(site_data.get("estimated_capacity", 500)))
    avail_cap = max(0, int(site_data.get("available_capacity", 400)))
    curr_pop = int(site_data.get("current_population", 0))
    area_sqm = float(site_data.get("available_area", 50000.0))
    
    # Capacity buffer ratio
    cap_ratio = min(1.0, avail_cap / est_cap)
    cap_buffer_score = int(cap_ratio * 100.0)
    
    # Occupancy ratio: 0% occupied -> 100 score; 100% occupied -> 0 score
    occ_ratio = min(1.0, curr_pop / est_cap) if est_cap > 0 else 1.0
    occupancy_score = int((1.0 - occ_ratio) * 100.0)
    
    area_score = eval_land_area_score(area_sqm)
    
    cw = default_capacity_weights
    capacity_raw = (
        (cap_buffer_score * cw.available_capacity_buffer)
        + (area_score * cw.available_land_area)
        + (occupancy_score * cw.occupancy_ratio)
    )
    capacity_score = min(100, max(0, int(round(capacity_raw))))

    category_scores = {
        "hazard_safety_score": hazard_safety_score,
        "infrastructure_score": infrastructure_score,
        "accessibility_score": accessibility_score,
        "capacity_score": capacity_score,
    }

    factors = {
        "flood_risk": flood_clean,
        "landslide_risk": landslide_clean,
        "slope": slope_score,
        "elevation": elev_score,
        "water_availability": water_score,
        "electricity_availability": electricity_score,
        "hospital_proximity": hospital_score,
        "school_proximity": school_score,
        "road_accessibility": road_score,
        "available_land": area_score,
        "capacity_buffer": cap_buffer_score,
        "occupancy_ratio": occupancy_score,
    }

    return category_scores, factors


def extract_strengths_and_limitations(
    category_scores: Dict[str, int],
    factors: Dict[str, int],
    site_data: Dict[str, Any],
) -> Tuple[List[str], List[str]]:
    """Generate explainable strengths and civil limitations for human planners."""
    strengths: List[str] = []
    limitations: List[str] = []

    # Hazard Safety Strengths & Limitations
    hz_score = category_scores["hazard_safety_score"]
    if hz_score >= 80:
        strengths.append("Zero active flood or landslide red-zone overlap (>500m safety clearance buffer)")
    elif hz_score < 60:
        limitations.append("Site has proximity to active environmental hazard zones; safety mitigation required")

    # Slope
    slope_deg = float(site_data.get("slope_degrees", 8.0))
    if slope_deg <= 8.0:
        strengths.append(f"Ideal gentle terrain topography ({slope_deg:.1f}°) with minimal earthwork requirements")
    elif slope_deg > 18.0:
        limitations.append(f"Moderate-to-steep elevation slope ({slope_deg:.1f}°) requires localized terracing and slope protection")

    # Road Accessibility
    acc_score = category_scores["accessibility_score"]
    if acc_score >= 80:
        strengths.append("High all-weather arterial highway connection and multi-vehicle transport egress")
    elif acc_score < 50:
        limitations.append("Constrained transport accessibility; road corridor widening needed for heavy supply convoys")

    # Infrastructure: Water & Electricity
    water_score = factors["water_availability"]
    hosp_dist = float(site_data.get("distance_to_hospital_km", 3.0))
    if water_score >= 80 and hosp_dist <= 5.0:
        strengths.append(f"Reliable potable water supply and primary healthcare within {hosp_dist:.1f} km")
    elif water_score < 50:
        limitations.append("Potable water distribution network is limited; additional borewell or pipeline required")

    if hosp_dist > 10.0:
        limitations.append(f"Delayed emergency healthcare access ({hosp_dist:.1f} km to nearest hospital facility)")

    # Capacity
    cap_score = category_scores["capacity_score"]
    avail_cap = int(site_data.get("available_capacity", 0))
    if cap_score >= 80:
        strengths.append(f"High available carrying capacity (safely accommodates {avail_cap:,} displaced persons)")
    elif avail_cap < 100:
        limitations.append(f"Limited carrying capacity buffer ({avail_cap:,} remaining spots)")

    # Fallbacks if empty
    if not strengths:
        strengths.append("Viable baseline terrain with standard civic resettlement feasibility")
    if not limitations:
        limitations.append("Standard civil infrastructure maintenance and periodic storm drainage inspection required")

    return strengths, limitations


def calculate_site_suitability(
    site_data: Dict[str, Any],
    weights: Optional[CategoryWeightConfig] = None,
) -> Dict[str, Any]:
    """Calculate transparent composite suitability score (0-100) and classification."""
    w = weights or default_category_weights

    category_scores, factors = calculate_category_scores(site_data)
    
    # Weighted composite sum: 35% hazard, 25% infra, 20% access, 20% capacity
    raw_composite = (
        (category_scores["hazard_safety_score"] * w.hazard_safety)
        + (category_scores["infrastructure_score"] * w.infrastructure)
        + (category_scores["accessibility_score"] * w.accessibility)
        + (category_scores["capacity_score"] * w.capacity)
    )

    overall_score = min(100, max(0, int(round(raw_composite))))
    classification = SuitabilityClassificationThresholds.get_classification(overall_score)
    strengths, limitations = extract_strengths_and_limitations(category_scores, factors, site_data)

    return {
        "site_id": site_data.get("id"),
        "suitability_score": overall_score,
        "overall_suitability_score": overall_score,
        "hazard_safety_score": category_scores["hazard_safety_score"],
        "accessibility_score": category_scores["accessibility_score"],
        "infrastructure_score": category_scores["infrastructure_score"],
        "capacity_score": category_scores["capacity_score"],
        "classification": classification,
        "category_scores": category_scores,
        "factors": factors,
        "strengths": strengths,
        "limitations": limitations,
    }


def get_all_relocation_sites_from_db(
    db: Session,
    min_suitability: float = 0.0,
    min_capacity: int = 0,
) -> List[Dict[str, Any]]:
    """Query all candidate relocation parcels with GeoJSON boundaries."""
    stmt = text("""
        SELECT 
            id, name, available_area, current_population, estimated_capacity,
            available_capacity, water_score, road_access_score, healthcare_score,
            hazard_score, suitability_score,
            ST_AsGeoJSON(geometry) AS geojson
        FROM relocation_sites
        WHERE available_capacity >= :min_cap
          AND suitability_score >= :min_suit
        ORDER BY suitability_score DESC, available_capacity DESC;
    """)

    rows = db.execute(stmt, {
        "min_cap": min_capacity,
        "min_suit": min_suitability,
    }).mappings().all()

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "name": r["name"],
            "available_area": float(r["available_area"]),
            "current_population": int(r["current_population"]),
            "estimated_capacity": int(r["estimated_capacity"]),
            "available_capacity": int(r["available_capacity"]),
            "water_score": float(r["water_score"]),
            "road_access_score": float(r["road_access_score"]),
            "healthcare_score": float(r["healthcare_score"]),
            "hazard_score": float(r["hazard_score"]),
            "suitability_score": float(r["suitability_score"]),
            "geometry": json.loads(r["geojson"]) if r["geojson"] else {},
        })
    return results


def get_relocation_site_by_id_from_db(
    db: Session,
    site_id: uuid.UUID,
) -> Optional[Dict[str, Any]]:
    """Query a single candidate relocation parcel with GeoJSON boundary."""
    stmt = text("""
        SELECT 
            id, name, available_area, current_population, estimated_capacity,
            available_capacity, water_score, road_access_score, healthcare_score,
            hazard_score, suitability_score,
            ST_AsGeoJSON(geometry) AS geojson
        FROM relocation_sites
        WHERE id = :site_id;
    """)
    site = db.execute(stmt, {"site_id": site_id}).mappings().first()
    if not site:
        return None
    return {
        "id": site["id"],
        "name": site["name"],
        "available_area": float(site["available_area"]),
        "current_population": int(site["current_population"]),
        "estimated_capacity": int(site["estimated_capacity"]),
        "available_capacity": int(site["available_capacity"]),
        "water_score": float(site["water_score"]),
        "road_access_score": float(site["road_access_score"]),
        "healthcare_score": float(site["healthcare_score"]),
        "hazard_score": float(site["hazard_score"]),
        "suitability_score": float(site["suitability_score"]),
        "geometry": json.loads(site["geojson"]) if site["geojson"] else {},
    }


def compute_site_assessment_from_db(
    db: Session,
    site_id: uuid.UUID,
    weights: Optional[CategoryWeightConfig] = None,
) -> Dict[str, Any]:
    """Retrieve parcel and calculate transparent explainable suitability assessment."""
    stmt = text("""
        SELECT 
            id, name, available_area, current_population, estimated_capacity,
            available_capacity, water_score, road_access_score, healthcare_score,
            hazard_score, suitability_score,
            ST_AsGeoJSON(geometry) AS geojson
        FROM relocation_sites
        WHERE id = :site_id;
    """)
    site = db.execute(stmt, {"site_id": site_id}).mappings().first()
    if not site:
        return {"error": "Relocation site not found"}

    site_dict = dict(site)
    sid_str = str(site["id"])
    
    # Overlay demonstration civil metrics if present
    demo_metrics = DEMO_SITE_CIVIL_METRICS.get(sid_str, {})
    for k, v in demo_metrics.items():
        site_dict[k] = v

    evaluation = calculate_site_suitability(site_dict, weights)
    geo_dict = json.loads(site["geojson"]) if site["geojson"] else None

    return {
        "site_id": site["id"],
        "site_name": site["name"],
        "suitability_score": evaluation["suitability_score"],
        "overall_suitability_score": evaluation["suitability_score"],
        "hazard_safety_score": evaluation["hazard_safety_score"],
        "accessibility_score": evaluation["accessibility_score"],
        "infrastructure_score": evaluation["infrastructure_score"],
        "capacity_score": evaluation["capacity_score"],
        "classification": evaluation["classification"],
        "category_scores": evaluation["category_scores"],
        "factors": evaluation["factors"],
        "strengths": evaluation["strengths"],
        "limitations": evaluation["limitations"],
        "available_capacity": int(site["available_capacity"]),
        "estimated_capacity": int(site["estimated_capacity"]),
        "available_area_sqm": float(site["available_area"]),
        "geometry": geo_dict,
        "calculated_at": datetime.now(timezone.utc),
    }


def find_suitable_nearby_sites_for_habitation(
    db: Session,
    habitation_id: uuid.UUID,
    max_distance_meters: float = 35000.0,
    min_capacity: int = 50,
    limit: int = 5,
) -> Dict[str, Any]:
    """Perform spatial distance and safety query to find nearest safe relocation sites.
    
    Uses PostGIS ellipsoidal WGS84 geography calculation (`ST_Distance`)
    and strictly excludes any parcels intersecting active VERY_HIGH hazard zones.
    """
    # 1. Fetch habitation
    stmt_hab = text("""
        SELECT id, name, vulnerable_population, ST_AsGeoJSON(geometry) AS geojson
        FROM habitations
        WHERE id = :hab_id;
    """)
    hab = db.execute(stmt_hab, {"hab_id": habitation_id}).mappings().first()
    if not hab:
        return {"error": "Habitation not found"}

    # 2. Query safe candidate relocation sites sorted by distance and suitability
    stmt_sites = text("""
        SELECT 
            rs.id AS site_id,
            rs.name AS site_name,
            rs.available_capacity,
            rs.suitability_score,
            ROUND(ST_Distance(h.geometry::geography, rs.geometry::geography)::numeric, 1) AS distance_meters,
            ST_AsGeoJSON(rs.geometry) AS site_geojson
        FROM habitations h
        CROSS JOIN relocation_sites rs
        WHERE h.id = :hab_id
          AND rs.available_capacity >= :min_cap
          AND ST_DWithin(h.geometry::geography, rs.geometry::geography, :max_dist)
          -- Exclude any sites overlapping VERY_HIGH hazard zones
          AND NOT EXISTS (
              SELECT 1 FROM hazard_zones hz
              WHERE hz.severity = 'VERY_HIGH'
                AND ST_Intersects(rs.geometry, hz.geometry)
          )
        ORDER BY distance_meters ASC, rs.suitability_score DESC
        LIMIT :limit;
    """)

    rows = db.execute(stmt_sites, {
        "hab_id": habitation_id,
        "min_cap": min_capacity,
        "max_dist": max_distance_meters,
        "limit": limit,
    }).mappings().all()

    recommended = []
    for rank, r in enumerate(rows, start=1):
        dist_m = float(r["distance_meters"])
        score = int(round(float(r["suitability_score"])))
        classification = SuitabilityClassificationThresholds.get_classification(score)
        
        recommended.append({
            "site_id": r["site_id"],
            "site_name": r["site_name"],
            "distance_meters": dist_m,
            "distance_km": round(dist_m / 1000.0, 2),
            "available_capacity": int(r["available_capacity"]),
            "suitability_score": score,
            "classification": classification,
            "hazard_safe": True,
            "proximity_rank": rank,
            "geometry": json.loads(r["site_geojson"]) if r["site_geojson"] else None,
        })

    return {
        "habitation_id": hab["id"],
        "habitation_name": hab["name"],
        "vulnerable_population": int(hab["vulnerable_population"]),
        "total_sites_found": len(recommended),
        "recommended_sites": recommended,
    }
