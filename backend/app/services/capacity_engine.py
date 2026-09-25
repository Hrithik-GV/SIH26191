"""Relocation-Site Carrying Capacity Assessment Engine for SIH 2026 Problem Statement 26191.

Calculates sustainable carrying capacity using a multi-pillar bottleneck model
(Liebig's Law of the Minimum) rather than simplistic land-area multiplication.

Pillars evaluated:
1. Usable Land Area & Safe Resettlement Density (Gross Land Capacity)
2. Potable Water Supply Yield (70 LPCD norm)
3. Sanitation & Wastewater Treatment Capacity
4. Healthcare Proximity & Hospital Beds
5. Power Grid Transmission & Transformer Headroom
6. All-Weather Road Access & Evacuation Logistics Throughput

Each limiting factor transparently caps or reduces the final carrying capacity.
"""

import math
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Union
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.core.capacity_config import (
    CapacityNormsConfig,
    default_capacity_norms,
    PROTOTYPE_CAPACITY_ASSUMPTIONS,
)


def calculate_gross_land_capacity(
    available_area_sqm: float,
    slope_degrees: float = 6.0,
    usable_area_ratio: Optional[float] = None,
    sqm_per_person_norm: Optional[float] = None,
) -> Tuple[int, float]:
    """Calculate gross population capacity supported by buildable physical land area.
    
    Adjusts available area for terrain slope and standard civic reservations (roads,
    drainage setbacks, green buffers).
    """
    norms = default_capacity_norms
    ratio = usable_area_ratio if usable_area_ratio is not None else norms.usable_area_ratio
    density_norm = sqm_per_person_norm if sqm_per_person_norm is not None else norms.sqm_per_person_norm

    # Slope penalty: gentle slopes (<=8 deg) have 100% buildable efficiency;
    # steeper slopes require significant terracing and civic exclusion buffers.
    if slope_degrees <= 8.0:
        slope_efficiency = 1.0
    elif slope_degrees <= 15.0:
        slope_efficiency = max(0.70, 1.0 - (slope_degrees - 8.0) * 0.035)
    elif slope_degrees <= 25.0:
        slope_efficiency = max(0.45, 0.70 - (slope_degrees - 15.0) * 0.025)
    else:
        slope_efficiency = max(0.20, 0.45 - (slope_degrees - 25.0) * 0.025)

    effective_usable_area = max(0.0, available_area_sqm * ratio * slope_efficiency)
    gross_capacity = int(round(effective_usable_area / density_norm))
    return gross_capacity, effective_usable_area


def calculate_water_capacity(
    gross_capacity: int,
    water_score: float,
    daily_water_litres: Optional[float] = None,
    lpcd_norm: Optional[float] = None,
) -> int:
    """Calculate sustainable population supported by potable water availability.
    
    Uses 70 LPCD (Litres Per Capita per Day) benchmark.
    If daily water yield litres is not explicitly provided, it is estimated from
    the regional water supply infrastructure rating (water_score).
    """
    norm = lpcd_norm if lpcd_norm is not None else default_capacity_norms.water_lpcd_norm
    
    if daily_water_litres is not None and daily_water_litres > 0:
        return int(math.floor(daily_water_litres / norm))
    
    # Normalize water_score to 0.0 - 1.0
    w_norm = float(water_score) / 10.0 if float(water_score) <= 10.0 else float(water_score) / 100.0
    w_norm = max(0.0, min(1.0, w_norm))
    
    # Non-linear capacity curve: severe penalty when water score is poor (<6.0)
    if w_norm >= 0.90:
        factor = 1.0
    elif w_norm >= 0.75:
        factor = 0.75 + (w_norm - 0.75) / 0.15 * 0.25
    elif w_norm >= 0.50:
        factor = 0.45 + (w_norm - 0.50) / 0.25 * 0.30
    else:
        factor = max(0.10, w_norm * 0.90)

    return int(round(gross_capacity * factor))


def calculate_sanitation_capacity(
    gross_capacity: int,
    sanitation_score: float,
    sanitation_units: Optional[int] = None,
    persons_per_unit: Optional[int] = None,
) -> int:
    """Calculate population sustainable by decentralized sanitation and sewage absorption."""
    unit_norm = persons_per_unit or default_capacity_norms.sanitation_persons_per_core
    
    if sanitation_units is not None and sanitation_units > 0:
        return int(sanitation_units * unit_norm)

    s_norm = float(sanitation_score) / 10.0 if float(sanitation_score) <= 10.0 else float(sanitation_score) / 100.0
    s_norm = max(0.0, min(1.0, s_norm))

    if s_norm >= 0.85:
        factor = 1.0
    else:
        factor = max(0.20, s_norm)

    return int(round(gross_capacity * factor))


def calculate_healthcare_capacity(
    gross_capacity: int,
    healthcare_score: float,
    distance_to_hospital_km: float = 3.0,
    hospital_beds: Optional[int] = None,
) -> int:
    """Calculate population sustainable by primary healthcare clinics and hospital beds."""
    if hospital_beds is not None and hospital_beds > 0:
        return int(hospital_beds * default_capacity_norms.healthcare_persons_per_bed)

    h_norm = float(healthcare_score) / 10.0 if float(healthcare_score) <= 10.0 else float(healthcare_score) / 100.0
    h_norm = max(0.0, min(1.0, h_norm))

    # Distance attenuation: delayed emergency care reduces intake capacity
    if distance_to_hospital_km <= 3.0:
        dist_factor = 1.0
    elif distance_to_hospital_km <= 7.0:
        dist_factor = 0.88
    elif distance_to_hospital_km <= 15.0:
        dist_factor = 0.70
    else:
        dist_factor = 0.50

    if h_norm >= 0.90:
        h_factor = 1.0
    elif h_norm >= 0.75:
        h_factor = 0.80 + (h_norm - 0.75) / 0.15 * 0.20
    else:
        h_factor = max(0.20, h_norm)

    factor = min(1.0, h_factor * dist_factor)
    return int(round(gross_capacity * factor))


def calculate_electricity_capacity(
    gross_capacity: int,
    electricity_score: float,
    grid_capacity_kw: Optional[float] = None,
) -> int:
    """Calculate population sustainable by local electrical distribution grid."""
    if grid_capacity_kw is not None and grid_capacity_kw > 0:
        return int(math.floor(grid_capacity_kw / default_capacity_norms.electricity_kw_per_person))

    e_norm = float(electricity_score) / 10.0 if float(electricity_score) <= 10.0 else float(electricity_score) / 100.0
    e_norm = max(0.0, min(1.0, e_norm))

    if e_norm >= 0.85:
        factor = 1.0
    else:
        factor = max(0.25, e_norm)

    return int(math.floor(gross_capacity * factor))


def calculate_road_access_capacity(
    gross_capacity: int,
    road_access_score: float,
) -> int:
    """Calculate evacuation convoy and daily supply logistics capacity supported by access roads."""
    r_norm = float(road_access_score) / 10.0 if float(road_access_score) <= 10.0 else float(road_access_score) / 100.0
    r_norm = max(0.0, min(1.0, r_norm))

    if r_norm >= 0.80:
        factor = 1.0
    elif r_norm >= 0.60:
        factor = 0.80 + (r_norm - 0.60) / 0.20 * 0.20
    else:
        factor = max(0.30, r_norm)

    return int(math.floor(gross_capacity * factor))


def evaluate_site_carrying_capacity(site_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute transparent multi-pillar carrying capacity assessment for a candidate parcel.
    
    Adheres strictly to the bottleneck principle (Liebig's Law of the Minimum):
    final_capacity = min(gross_capacity, water_capacity, infrastructure_capacity).
    """
    site_id = site_data.get("id") or site_data.get("site_id", 1)
    site_name = site_data.get("name") or site_data.get("site_name", "Candidate Relocation Site")
    
    # 1. Usable Land & Gross Spatial Capacity
    if "gross_capacity" in site_data:
        gross_capacity = int(site_data["gross_capacity"])
    else:
        area_sqm = float(site_data.get("available_area", site_data.get("available_area_sqm", 70000.0)))
        slope_deg = float(site_data.get("slope_degrees", site_data.get("slope", 6.0)))
        gross_capacity, _ = calculate_gross_land_capacity(area_sqm, slope_degrees=slope_deg)

    # 2. Water Capacity
    if "water_capacity" in site_data:
        water_capacity = int(site_data["water_capacity"])
    else:
        water_score = float(site_data.get("water_score", 8.5))
        water_litres = site_data.get("daily_water_yield_litres")
        water_capacity = calculate_water_capacity(gross_capacity, water_score, daily_water_litres=water_litres)

    # 3. Individual Infrastructure Components
    # Sanitation
    if "sanitation_capacity" in site_data:
        sanitation_capacity = int(site_data["sanitation_capacity"])
    else:
        san_score = float(site_data.get("sanitation_score", site_data.get("water_score", 8.5)))
        sanitation_capacity = calculate_sanitation_capacity(gross_capacity, san_score)

    # Healthcare
    if "healthcare_capacity" in site_data:
        healthcare_capacity = int(site_data["healthcare_capacity"])
    else:
        hosp_score = float(site_data.get("healthcare_score", 8.0))
        hosp_dist = float(site_data.get("distance_to_hospital_km", site_data.get("distance_to_hospitals", 3.0)))
        healthcare_capacity = calculate_healthcare_capacity(gross_capacity, hosp_score, distance_to_hospital_km=hosp_dist)

    # Electricity
    if "electricity_capacity" in site_data:
        electricity_capacity = int(site_data["electricity_capacity"])
    else:
        elec_score = float(site_data.get("electricity_score", 8.5))
        electricity_capacity = calculate_electricity_capacity(gross_capacity, elec_score)

    # Road Accessibility
    if "road_capacity" in site_data:
        road_capacity = int(site_data["road_capacity"])
    else:
        road_score = float(site_data.get("road_access_score", site_data.get("road_accessibility", 8.5)))
        road_capacity = calculate_road_access_capacity(gross_capacity, road_score)

    # Composite Infrastructure Capacity (Bottleneck of civil utilities)
    if "infrastructure_capacity" in site_data:
        infrastructure_capacity = int(site_data["infrastructure_capacity"])
    else:
        infrastructure_capacity = min(sanitation_capacity, healthcare_capacity, electricity_capacity, road_capacity)

    # 4. Final Carrying Capacity (Liebig's Law of the Minimum)
    if "final_capacity" in site_data:
        final_capacity = int(site_data["final_capacity"])
    else:
        final_capacity = min(gross_capacity, water_capacity, infrastructure_capacity)

    # 5. Existing Population & Available Capacity
    current_pop = int(site_data.get("current_population", 0))
    available_capacity = max(0, final_capacity - current_pop)

    # 6. Limiting Factors Identification
    limiting_factors: List[str] = []

    # Check water limitation
    if water_capacity < gross_capacity:
        diff = gross_capacity - water_capacity
        is_bottleneck = (water_capacity == final_capacity)
        status_tag = " (Primary Limiting Bottleneck)" if is_bottleneck else ""
        limiting_factors.append(
            f"Potable water supply yield limits capacity to {water_capacity:,} persons "
            f"({diff:,} below gross land capacity){status_tag}"
        )

    # Check healthcare limitation
    if healthcare_capacity < gross_capacity:
        diff = gross_capacity - healthcare_capacity
        is_bottleneck = (healthcare_capacity == final_capacity)
        status_tag = " (Primary Limiting Bottleneck)" if is_bottleneck else ""
        limiting_factors.append(
            f"Healthcare and clinical surge capacity limits intake to {healthcare_capacity:,} persons "
            f"({diff:,} below gross land capacity){status_tag}"
        )

    # Check sanitation limitation
    if sanitation_capacity < gross_capacity:
        diff = gross_capacity - sanitation_capacity
        is_bottleneck = (sanitation_capacity == final_capacity)
        status_tag = " (Primary Limiting Bottleneck)" if is_bottleneck else ""
        limiting_factors.append(
            f"Decentralized sanitation and wastewater absorption limits intake to {sanitation_capacity:,} persons "
            f"({diff:,} below gross land capacity){status_tag}"
        )

    # Check road access limitation
    if road_capacity < gross_capacity:
        diff = gross_capacity - road_capacity
        is_bottleneck = (road_capacity == final_capacity)
        status_tag = " (Primary Limiting Bottleneck)" if is_bottleneck else ""
        limiting_factors.append(
            f"Road accessibility and evacuation corridor throughput limits intake to {road_capacity:,} persons "
            f"({diff:,} below gross land capacity){status_tag}"
        )

    # Check electricity limitation
    if electricity_capacity < gross_capacity:
        diff = gross_capacity - electricity_capacity
        is_bottleneck = (electricity_capacity == final_capacity)
        status_tag = " (Primary Limiting Bottleneck)" if is_bottleneck else ""
        limiting_factors.append(
            f"Power grid transmission capacity limits connected population to {electricity_capacity:,} persons "
            f"({diff:,} below gross land capacity){status_tag}"
        )

    # Fallback if no individual factor is below gross capacity
    if not limiting_factors and final_capacity < gross_capacity:
        diff = gross_capacity - final_capacity
        limiting_factors.append(
            f"Composite civil infrastructure bottleneck limits capacity to {final_capacity:,} persons "
            f"({diff:,} below gross land capacity)"
        )

    factor_capacities = {
        "usable_land": gross_capacity,
        "water_supply": water_capacity,
        "sanitation": sanitation_capacity,
        "healthcare": healthcare_capacity,
        "electricity": electricity_capacity,
        "road_access": road_capacity,
    }

    return {
        "site_id": site_id,
        "site_name": site_name,
        "gross_capacity": gross_capacity,
        "infrastructure_capacity": infrastructure_capacity,
        "water_capacity": water_capacity,
        "final_capacity": final_capacity,
        "current_population": current_pop,
        "available_capacity": available_capacity,
        "limiting_factors": limiting_factors,
        "factor_capacities": factor_capacities,
        "assumptions": PROTOTYPE_CAPACITY_ASSUMPTIONS,
        "calculated_at": datetime.now(timezone.utc),
    }


def compute_site_capacity_from_db(
    db: Session,
    site_id: uuid.UUID,
) -> Dict[str, Any]:
    """Retrieve candidate relocation parcel from DB and execute multi-pillar capacity assessment."""
    stmt = text("""
        SELECT 
            id, name, available_area, current_population, estimated_capacity,
            available_capacity, water_score, road_access_score, healthcare_score,
            hazard_score, suitability_score
        FROM relocation_sites
        WHERE id = :site_id;
    """)
    site = db.execute(stmt, {"site_id": site_id}).mappings().first()
    if not site:
        return {"error": "Relocation site not found"}

    site_dict = dict(site)
    sid_str = str(site["id"])

    # Supplement with demonstration metrics (slope, electricity, hospital distances)
    from backend.app.services.suitability_engine import DEMO_SITE_CIVIL_METRICS
    demo_metrics = DEMO_SITE_CIVIL_METRICS.get(sid_str, {})
    for k, v in demo_metrics.items():
        site_dict[k] = v

    return evaluate_site_carrying_capacity(site_dict)
