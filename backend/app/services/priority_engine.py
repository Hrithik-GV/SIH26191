"""Relocation Prioritization Engine for SIH 2026 Problem Statement 26191.

Calculates a transparent 0-100 relocation priority score for vulnerable habitations,
synthesizing:
1. Hazard Risk (25%)
2. Population Vulnerability (20%)
3. Exposed Population scale (15%)
4. Disaster History (10%)
5. Infrastructure Vulnerability (10%)
6. Evacuation Difficulty (10%)
7. Relocation Site Availability & Proximity (10%)

Classifications:
  81–100 = IMMEDIATE
  61–80  = SHORT_TERM
  31–60  = MEDIUM_TERM
  0–30   = MONITOR

Identifies the best suitable relocation site using spatial distance + suitability + available capacity.

CRITICAL: Decision-support platform for authorized human officials (NDMA/SDMA/DDMA);
does not make automated executive decisions.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.core.priority_config import (
    RelocationPriorityThresholds,
    RelocationPriorityWeightConfig,
    default_priority_weights,
    DECISION_SUPPORT_DISCLAIMER,
)
from backend.app.services.risk_engine import compute_habitation_risk_from_db
from backend.app.services.vulnerability_engine import compute_habitation_vulnerability_from_db
from backend.app.services.suitability_engine import find_suitable_nearby_sites_for_habitation


def eval_exposed_population_factor(vulnerable_population: int) -> int:
    """Evaluate life-safety exposure scale (0-100)."""
    if vulnerable_population >= 1500:
        return 100
    elif vulnerable_population >= 1000:
        return 85
    elif vulnerable_population >= 500:
        return 70
    elif vulnerable_population >= 200:
        return 55
    elif vulnerable_population >= 50:
        return 40
    else:
        return 25


def eval_disaster_history_factor(events_count: int) -> int:
    """Evaluate recurrence of past critical disaster events in habitation vicinity."""
    if events_count >= 3:
        return 100
    elif events_count == 2:
        return 80
    elif events_count == 1:
        return 60
    else:
        return 25


def rank_and_select_best_relocation_site(
    candidate_sites: List[Dict[str, Any]],
    vulnerable_population: int,
) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """Rank candidate relocation parcels using spatial distance + suitability + available capacity.
    
    Composite Match Score = 40% proximity + 35% suitability + 25% capacity sufficiency.
    """
    if not candidate_sites:
        return None, []

    ranked_sites = []
    for site in candidate_sites:
        dist_km = float(site.get("distance_km", 10.0))
        dist_m = float(site.get("distance_meters", dist_km * 1000.0))
        suit_score = int(round(float(site.get("suitability_score", 70))))
        avail_cap = int(site.get("available_capacity", 0))

        # 1. Proximity Score (closer is better: <=3km -> 100, 35km -> 20)
        if dist_km <= 3.0:
            prox_score = 100.0
        elif dist_km >= 35.0:
            prox_score = max(10.0, 100.0 - (dist_km / 35.0) * 80.0)
        else:
            prox_score = 100.0 - ((dist_km - 3.0) / 32.0) * 75.0

        # 2. Capacity Sufficiency Score
        is_sufficient = avail_cap >= vulnerable_population
        if is_sufficient:
            cap_score = 100.0
        elif vulnerable_population > 0:
            cap_score = max(20.0, (avail_cap / vulnerable_population) * 90.0)
        else:
            cap_score = 100.0

        # 3. Composite Match Score
        match_score = (prox_score * 0.40) + (suit_score * 0.35) + (cap_score * 0.25)
        match_score = round(max(0.0, min(100.0, match_score)), 1)

        ranked_sites.append({
            "site_id": site.get("site_id") or site.get("id"),
            "site_name": site.get("site_name") or site.get("name", "Candidate Safe Site"),
            "distance_km": round(dist_km, 2),
            "distance_meters": round(dist_m, 1),
            "suitability_score": suit_score,
            "classification": site.get("classification", "SUITABLE"),
            "available_capacity": avail_cap,
            "capacity_sufficient": is_sufficient,
            "match_score": match_score,
            "geometry": site.get("geometry"),
        })

    # Sort descending by match score
    ranked_sites.sort(key=lambda s: s["match_score"], reverse=True)
    best_site = ranked_sites[0] if ranked_sites else None
    alternative_sites = ranked_sites[1:] if len(ranked_sites) > 1 else []

    return best_site, alternative_sites


def generate_priority_reasons(
    factors: Dict[str, int],
    vulnerable_population: int,
    best_site: Optional[Dict[str, Any]],
) -> List[str]:
    """Generate transparent human-readable explanations justifying the priority score."""
    reasons: List[str] = []

    # Hazard
    hz = factors.get("hazard_risk", 50)
    if hz >= 80:
        reasons.append("Critical multi-hazard risk (severe flood/landslide red-zone overlap and high precipitation)")
    elif hz >= 60:
        reasons.append("Elevated environmental hazard exposure in settlement perimeter")

    # Vulnerability & Population scale
    vuln = factors.get("population_vulnerability", 50)
    if vuln >= 75:
        reasons.append(f"High vulnerable population ({vulnerable_population:,} persons requiring assisted evacuation)")
    elif vuln >= 60:
        reasons.append("Significant demographic vulnerability (high elderly and dependent population)")

    # Evacuation difficulty
    evac = factors.get("evacuation_difficulty", 50)
    if evac >= 70:
        reasons.append("Poor evacuation accessibility (terrain bottlenecks and vulnerable single-corridor egress)")

    # Infrastructure
    infra = factors.get("infrastructure_vulnerability", 50)
    if infra >= 70:
        reasons.append("Severe housing and civil infrastructure fragility (high kutcha building prevalence)")

    # Disaster history
    hist = factors.get("disaster_history", 25)
    if hist >= 70:
        reasons.append("High historical disaster recurrence with recorded mass casualties or debris damage")

    # Site availability
    if best_site:
        site_name = best_site.get("site_name", "Safe parcel")
        dist_km = best_site.get("distance_km", 0.0)
        reasons.append(f"Suitable relocation site available nearby ({site_name} at {dist_km:.1f} km)")
    else:
        reasons.append("Relocation parcel search radius requires expansion; immediate regional transit planning needed")

    # Ensure at least 2 clear points
    if len(reasons) < 2:
        reasons.append("Monitored settlement undergoing scheduled disaster risk surveillance")

    return reasons


def calculate_relocation_priority(
    metrics: Dict[str, Any],
    candidate_sites: Optional[List[Dict[str, Any]]] = None,
    weights: Optional[RelocationPriorityWeightConfig] = None,
) -> Dict[str, Any]:
    """Calculate transparent 0-100 relocation priority score and classification."""
    w = weights or default_priority_weights

    hazard_score = int(round(float(metrics.get("hazard_risk", metrics.get("hazard_score", 50.0)))))
    vuln_score = int(round(float(metrics.get("population_vulnerability", metrics.get("vulnerability_score", 50.0)))))
    vuln_pop = int(metrics.get("vulnerable_population", 500))
    exposed_score = eval_exposed_population_factor(vuln_pop)
    
    events_count = int(metrics.get("disaster_events_count", metrics.get("disaster_history_count", 1)))
    history_score = eval_disaster_history_factor(events_count)
    
    infra_score = int(round(float(metrics.get("infrastructure_vulnerability", metrics.get("housing_vulnerability", 50.0)))))
    evac_score = int(round(float(metrics.get("evacuation_difficulty", metrics.get("evacuation_bottleneck", 50.0)))))

    # Evaluate best relocation site if candidate sites provided
    best_site, alternative_sites = rank_and_select_best_relocation_site(candidate_sites or [], vuln_pop)
    
    if best_site:
        site_avail_score = int(round(best_site["match_score"]))
    else:
        site_avail_score = 40

    factors = {
        "hazard_risk": hazard_score,
        "population_vulnerability": vuln_score,
        "exposed_population": exposed_score,
        "disaster_history": history_score,
        "infrastructure_vulnerability": infra_score,
        "evacuation_difficulty": evac_score,
        "site_availability": site_avail_score,
    }

    # Weighted composite sum (0-100)
    raw_composite = (
        (hazard_score * w.hazard_risk)
        + (vuln_score * w.population_vulnerability)
        + (exposed_score * w.exposed_population)
        + (history_score * w.disaster_history)
        + (infra_score * w.infrastructure_vulnerability)
        + (evac_score * w.evacuation_difficulty)
        + (site_avail_score * w.site_availability)
    )

    priority_score = min(100, max(0, int(round(raw_composite))))
    priority = RelocationPriorityThresholds.get_priority(priority_score)
    reasons = generate_priority_reasons(factors, vuln_pop, best_site)

    return {
        "priority_score": priority_score,
        "priority": priority,
        "factors": factors,
        "reasons": reasons,
        "best_suitable_site": best_site,
        "alternative_sites": alternative_sites,
        "decision_support_disclaimer": DECISION_SUPPORT_DISCLAIMER,
    }


def compute_habitation_priority_from_db(
    db: Session,
    habitation_id: uuid.UUID,
) -> Dict[str, Any]:
    """Retrieve habitation data, evaluate risk, vulnerability, nearby sites, and compute priority."""
    # 1. Fetch habitation
    stmt = text("""
        SELECT id, name, district, state, population, vulnerable_population,
               ST_AsGeoJSON(geometry) AS geojson
        FROM habitations
        WHERE id = :hab_id;
    """)
    hab = db.execute(stmt, {"hab_id": habitation_id}).mappings().first()
    if not hab:
        return {"error": "Habitation not found"}

    # 2. Compute hazard risk & vulnerability from respective engines
    risk_res = compute_habitation_risk_from_db(db, habitation_id)
    hazard_score = risk_res.get("overall_score", 50)

    vuln_res = compute_habitation_vulnerability_from_db(db, habitation_id)
    vuln_score = vuln_res.get("vulnerability_score", 50)
    vuln_factors = vuln_res.get("factors", {})

    # 3. Find candidate safe sites nearby
    nearby_res = find_suitable_nearby_sites_for_habitation(
        db, habitation_id, max_distance_meters=45000.0, min_capacity=10, limit=5
    )
    candidate_sites = nearby_res.get("recommended_sites", [])

    # 4. Count historical disaster events in vicinity (<10km)
    stmt_events = text("""
        SELECT COUNT(*) AS cnt
        FROM disaster_events de, habitations h
        WHERE h.id = :hab_id
          AND ST_DWithin(h.geometry::geography, de.geometry::geography, 10000.0);
    """)
    events_row = db.execute(stmt_events, {"hab_id": habitation_id}).mappings().first()
    events_count = 1
    if events_row:
        try:
            events_count = int(events_row["cnt"])
        except (KeyError, TypeError):
            events_count = int(events_row.get("cnt", 1)) if hasattr(events_row, "get") else 1

    metrics = {
        "hazard_risk": hazard_score,
        "population_vulnerability": vuln_score,
        "vulnerable_population": int(hab["vulnerable_population"]),
        "total_population": int(hab["population"]),
        "disaster_events_count": max(1, events_count),
        "infrastructure_vulnerability": vuln_factors.get("housing", 65),
        "evacuation_difficulty": vuln_factors.get("evacuation_accessibility", 70),
    }

    eval_result = calculate_relocation_priority(metrics, candidate_sites=candidate_sites)
    geo_dict = json.loads(hab["geojson"]) if hab["geojson"] else None

    return {
        "habitation_id": hab["id"],
        "habitation_name": hab["name"],
        "district": hab["district"],
        "state": hab["state"],
        "priority_score": eval_result["priority_score"],
        "priority": eval_result["priority"],
        "factors": eval_result["factors"],
        "reasons": eval_result["reasons"],
        "vulnerable_population": int(hab["vulnerable_population"]),
        "total_population": int(hab["population"]),
        "recommended_site": eval_result["best_suitable_site"],
        "best_suitable_site": eval_result["best_suitable_site"],
        "alternative_sites": eval_result["alternative_sites"],
        "decision_support_disclaimer": eval_result["decision_support_disclaimer"],
        "geometry": geo_dict,
        "calculated_at": datetime.now(timezone.utc),
    }


def compute_all_habitations_priorities_summary(db: Session) -> Dict[str, Any]:
    """Compile multi-habitation relocation prioritization summary and ranked priorities."""
    stmt = text("SELECT id FROM habitations ORDER BY name;")
    rows = db.execute(stmt).mappings().all()

    priorities_list = []
    immediate_c = 0
    short_term_c = 0
    medium_term_c = 0
    monitor_c = 0
    score_sum = 0

    for r in rows:
        hab_eval = compute_habitation_priority_from_db(db, r["id"])
        if "error" in hab_eval:
            continue

        p_score = hab_eval["priority_score"]
        p_tier = hab_eval["priority"]
        score_sum += p_score

        if p_tier == "IMMEDIATE":
            immediate_c += 1
        elif p_tier == "SHORT_TERM":
            short_term_c += 1
        elif p_tier == "MEDIUM_TERM":
            medium_term_c += 1
        else:
            monitor_c += 1

        best_site = hab_eval.get("recommended_site")
        priorities_list.append({
            "habitation_id": hab_eval["habitation_id"],
            "habitation_name": hab_eval["habitation_name"],
            "district": hab_eval["district"],
            "state": hab_eval["state"],
            "priority_score": p_score,
            "priority": p_tier,
            "vulnerable_population": hab_eval["vulnerable_population"],
            "total_population": hab_eval["total_population"],
            "hazard_score": hab_eval["factors"]["hazard_risk"],
            "vulnerability_score": hab_eval["factors"]["population_vulnerability"],
            "reasons": hab_eval["reasons"],
            "recommended_site_id": best_site["site_id"] if best_site else None,
            "recommended_site_name": best_site["site_name"] if best_site else None,
            "recommended_site_distance_km": best_site["distance_km"] if best_site else None,
        })

    # Sort descending by priority score
    priorities_list.sort(key=lambda x: x["priority_score"], reverse=True)
    total_hab = len(priorities_list)
    avg_score = round(score_sum / total_hab, 1) if total_hab > 0 else 0.0

    return {
        "total_habitations": total_hab,
        "immediate_count": immediate_c,
        "short_term_count": short_term_c,
        "medium_term_count": medium_term_c,
        "monitor_count": monitor_c,
        "average_priority_score": avg_score,
        "priorities": priorities_list,
        "decision_support_disclaimer": DECISION_SUPPORT_DISCLAIMER,
        "calculated_at": datetime.now(timezone.utc),
    }
