"""Dashboard Service: Aggregates KPIs across all hazard, vulnerability, and relocation engines."""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.models.habitation import Habitation
from backend.app.models.hazard_zone import HazardZone
from backend.app.models.observation import RainfallObservation, RiverObservation
from backend.app.models.disaster_event import DisasterEvent
from backend.app.models.relocation import RelocationSite
from backend.app.schemas.dashboard import DashboardResponse, DashboardUrgentHabitation
from backend.app.services.risk_engine import compute_all_habitations_risk_summary
from backend.app.services.vulnerability_engine import compute_all_habitations_vulnerability_summary
from backend.app.services.priority_engine import compute_all_habitations_priorities_summary
from backend.app.ingestion.status_registry import source_registry


class DashboardService:
    """Computes executive KPIs for emergency disaster management leadership."""

    @staticmethod
    def get_dashboard_summary(db: Session) -> DashboardResponse:
        """
        Gathers comprehensive situational metrics:
        - total habitations
        - habitations in critical zones
        - population at risk
        - immediate relocation count
        - short-term relocation count
        - medium-term relocation count
        - total relocation capacity
        - available relocation capacity
        - active alerts
        - latest data timestamps
        """
        # 1. Total habitations
        total_habitations = db.query(Habitation).count()

        # 2. Risk & Vulnerability Assessments
        risk_summary = compute_all_habitations_risk_summary(db)
        vuln_summary = compute_all_habitations_vulnerability_summary(db)
        priority_summary = compute_all_habitations_priorities_summary(db)

        # 3. Critical Zone Counts & Population At Risk
        critical_hab_ids = {
            h.habitation_id
            for h in risk_summary.habitations
            if h.severity in ("CRITICAL", "HIGH")
        }
        habitations_in_critical_zones = len(critical_hab_ids)

        population_at_risk = sum(
            h.vulnerable_population
            for h in risk_summary.habitations
            if h.habitation_id in critical_hab_ids
        )

        # 4. Relocation Urgency Counts
        immediate_count = priority_summary.get("immediate_count", 0)
        short_term_count = priority_summary.get("short_term_count", 0)
        medium_term_count = priority_summary.get("medium_term_count", 0)
        monitor_count = priority_summary.get("monitor_count", 0)

        # 5. Relocation Capacity Metrics
        sites = db.query(RelocationSite).all()
        total_relocation_capacity = sum(s.estimated_carrying_capacity or 0 for s in sites)
        available_relocation_capacity = sum(
            max(0, (s.estimated_carrying_capacity or 0) - (s.current_occupancy or 0))
            for s in sites
        )

        urgent_pop_demand = sum(
            p.get("vulnerable_population", 0)
            for p in priority_summary.get("priorities", [])
            if p.get("priority") in ("IMMEDIATE", "SHORT_TERM")
        )
        capacity_deficit = max(0, urgent_pop_demand - available_relocation_capacity)

        # 6. Active Alerts Count
        active_alerts_count = db.query(DisasterEvent).count()

        # 7. Latest Data Timestamps
        latest_rainfall = db.query(func.max(RainfallObservation.observation_time)).scalar()
        latest_river = db.query(func.max(RiverObservation.observation_time)).scalar()
        latest_alert = db.query(func.max(DisasterEvent.event_time)).scalar()

        all_sources = source_registry.get_all_statuses()
        latest_ingestion = None
        for src in all_sources:
            if src.last_update and (latest_ingestion is None or src.last_update > latest_ingestion):
                latest_ingestion = src.last_update

        timestamps: Dict[str, Optional[datetime]] = {
            "rainfall_telemetry": latest_rainfall,
            "river_gauging": latest_river,
            "emergency_alerts": latest_alert,
            "last_ingestion_cycle": latest_ingestion,
            "dashboard_computed": datetime.now(timezone.utc),
        }

        # 8. Top Urgent Habitations Preview
        priorities_list = priority_summary.get("priorities", [])
        top_urgent: List[DashboardUrgentHabitation] = [
            DashboardUrgentHabitation(
                habitation_id=str(p["habitation_id"]),
                habitation_name=p["habitation_name"],
                district=p["district"],
                priority=p["priority"],
                priority_score=p["priority_score"],
                hazard_score=p["hazard_score"],
                vulnerability_score=p["vulnerability_score"],
                vulnerable_population=p["vulnerable_population"],
                recommended_site_name=p.get("recommended_site_name"),
                recommended_site_distance_km=p.get("recommended_site_distance_km"),
            )
            for p in priorities_list[:5]
        ]

        return DashboardResponse(
            total_habitations=total_habitations,
            habitations_in_critical_zones=habitations_in_critical_zones,
            population_at_risk=population_at_risk,
            immediate_relocation_count=immediate_count,
            short_term_relocation_count=short_term_count,
            medium_term_relocation_count=medium_term_count,
            monitor_relocation_count=monitor_count,
            total_relocation_capacity=total_relocation_capacity,
            available_relocation_capacity=available_relocation_capacity,
            active_alerts=active_alerts_count,
            latest_data_timestamps=timestamps,
            average_risk_score=risk_summary.average_risk_score,
            average_vulnerability_score=vuln_summary.average_vulnerability_score,
            capacity_deficit=capacity_deficit,
            top_urgent_habitations=top_urgent,
            generated_at=datetime.now(timezone.utc),
        )
