"""Analytics Service: Situational statistical analysis, chart distributions, and capacity vs need."""

from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.habitation import Habitation
from backend.app.models.hazard_zone import HazardZone
from backend.app.models.relocation import RelocationSite
from backend.app.schemas.analytics import (
    AnalyticsOverviewResponse,
    RiskDistributionItem,
    VulnerabilityFactorComparison,
    CapacityVsNeedItem,
    HazardExposureItem,
)
from backend.app.services.risk_engine import compute_all_habitations_risk_summary
from backend.app.services.vulnerability_engine import compute_all_habitations_vulnerability_summary
from backend.app.services.priority_engine import compute_all_habitations_priorities_summary


class AnalyticsService:
    """Computes chart-ready aggregates for frontend data visualizations."""

    @staticmethod
    def get_risk_distribution(db: Session) -> List[RiskDistributionItem]:
        """Calculates population and settlement distribution across 4 risk brackets."""
        risk_summary = compute_all_habitations_risk_summary(db)

        tier_buckets = {
            "LOW": {"count": 0, "population": 0, "vulnerable": 0, "bracket": "0-30 (LOW)"},
            "MODERATE": {"count": 0, "population": 0, "vulnerable": 0, "bracket": "31-60 (MODERATE)"},
            "HIGH": {"count": 0, "population": 0, "vulnerable": 0, "bracket": "61-80 (HIGH)"},
            "CRITICAL": {"count": 0, "population": 0, "vulnerable": 0, "bracket": "81-100 (CRITICAL)"},
        }

        for hab in risk_summary.habitations:
            sev = hab.severity if hab.severity in tier_buckets else "LOW"
            tier_buckets[sev]["count"] += 1
            tier_buckets[sev]["population"] += hab.population
            tier_buckets[sev]["vulnerable"] += hab.vulnerable_population

        return [
            RiskDistributionItem(
                bracket=data["bracket"],
                count=data["count"],
                population=data["population"],
                vulnerable_population=data["vulnerable"],
            )
            for tier, data in tier_buckets.items()
        ]

    @staticmethod
    def get_vulnerability_breakdown(db: Session) -> List[VulnerabilityFactorComparison]:
        """Analyzes demographic factors across habitations."""
        vuln_summary = compute_all_habitations_vulnerability_summary(db)
        habitations = vuln_summary.habitations

        factors = [
            ("total_population", "Total Population"),
            ("vulnerable_population", "Vulnerable Population Share"),
            ("population_density", "Population Density"),
            ("elderly_population", "Elderly Population Proportion"),
            ("children_population", "Children Proportion"),
            ("disabled_population", "Persons with Disabilities"),
            ("housing_vulnerability", "Kutcha Housing Fragility"),
            ("infrastructure_vulnerability", "Infrastructure Vulnerability"),
            ("evacuation_accessibility", "Evacuation Route Difficulty"),
        ]

        results = []
        for factor_key, factor_name in factors:
            scores = [h.factors.get(factor_key, 0) for h in habitations]
            avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

            # Find habitation with highest score
            highest_hab = max(habitations, key=lambda h: h.factors.get(factor_key, 0), default=None)
            highest_name = highest_hab.habitation_name if highest_hab else "N/A"
            critical_count = sum(1 for s in scores if s >= 80)

            results.append(
                VulnerabilityFactorComparison(
                    factor=factor_name,
                    average_score=avg_score,
                    highest_habitation=highest_name,
                    critical_habitations_count=critical_count,
                )
            )

        return results

    @staticmethod
    def get_capacity_vs_need(db: Session) -> List[CapacityVsNeedItem]:
        """Evaluates relocation intake capacity against matched vulnerable demand."""
        sites = db.query(RelocationSite).all()
        priority_summary = compute_all_habitations_priorities_summary(db)

        # Map demand to recommended sites
        site_demand: Dict[str, int] = {}
        for p in priority_summary.get("priorities", []):
            if p.get("recommended_site_id"):
                s_id = str(p["recommended_site_id"])
                site_demand[s_id] = site_demand.get(s_id, 0) + p.get("vulnerable_population", 0)

        results = []
        for s in sites:
            s_id = str(s.id)
            demand = site_demand.get(s_id, 0)
            avail = max(0, (s.estimated_carrying_capacity or 0) - (s.current_occupancy or 0))
            balance = avail - demand
            status = "SURPLUS" if balance > 0 else ("BALANCED" if balance == 0 else "DEFICIT")

            results.append(
                CapacityVsNeedItem(
                    site_id=s_id,
                    site_name=s.name,
                    usable_area_sqm=float(s.usable_area_sqm),
                    total_capacity=s.estimated_carrying_capacity or 0,
                    available_capacity=avail,
                    matched_demand_population=demand,
                    balance=balance,
                    status=status,
                )
            )

        return results

    @staticmethod
    def get_hazard_exposure(db: Session) -> List[HazardExposureItem]:
        """Analyzes affected population per hazard type."""
        from backend.app.db.spatial_queries import get_habitations_in_hazard_zones

        types = ["flood", "landslide", "cloudburst", "debris_flow"]
        results = []

        for ht in types:
            intersections = get_habitations_in_hazard_zones(db, hazard_type=ht)
            hab_ids = set()
            total_pop = 0
            severe_count = 0

            for row in intersections:
                hab_id = row["habitation_id"]
                if hab_id not in hab_ids:
                    hab_ids.add(hab_id)
                    total_pop += row.get("population", 0)
                if row.get("severity") in ("VERY_HIGH", "CRITICAL"):
                    severe_count += 1

            results.append(
                HazardExposureItem(
                    hazard_type=ht,
                    affected_habitations=len(hab_ids),
                    affected_population=total_pop,
                    critical_overlap_count=severe_count,
                )
            )

        return results

    @classmethod
    def get_analytics_overview(cls, db: Session) -> AnalyticsOverviewResponse:
        """Returns comprehensive analytics overview."""
        hab_count = db.query(Habitation).count()
        raw_pop = db.query(func.sum(Habitation.population)).scalar()
        raw_vuln = db.query(func.sum(Habitation.vulnerable_population)).scalar()
        total_pop = int(raw_pop) if isinstance(raw_pop, (int, float)) else 0
        total_vuln = int(raw_vuln) if isinstance(raw_vuln, (int, float)) else 0

        sites = db.query(RelocationSite).all()
        total_safe_capacity = sum(
            max(0, (s.estimated_carrying_capacity or 0) - (s.current_occupancy or 0))
            for s in sites
        )
        regional_net_balance = total_safe_capacity - total_vuln

        return AnalyticsOverviewResponse(
            total_habitations=hab_count,
            total_population=total_pop,
            total_vulnerable_population=total_vuln,
            total_safe_capacity=total_safe_capacity,
            regional_net_balance=regional_net_balance,
            risk_distribution=cls.get_risk_distribution(db),
            vulnerability_factors=cls.get_vulnerability_breakdown(db),
            capacity_vs_need=cls.get_capacity_vs_need(db),
            hazard_exposures=cls.get_hazard_exposure(db),
        )
