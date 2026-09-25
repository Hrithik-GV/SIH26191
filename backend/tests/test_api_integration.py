"""Automated Integration Tests for all 9 API Groups and Cross-Cutting Features."""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.session import get_db
from backend.app.schemas.risk import HabitationRiskResponse, RiskSummaryResponse
from backend.app.schemas.vulnerability import VulnerabilitySummaryResponse, HabitationVulnerabilityResponse
from backend.app.schemas.priority import HabitationPrioritiesSummaryResponse, HabitationPriorityResponse

client = TestClient(app)

TEST_HAB_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
TEST_SITE_ID = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
TEST_HAZARD_ID = uuid.UUID("99999999-9999-4999-8999-999999999999")
TEST_ALERT_ID = uuid.UUID("88888888-8888-4888-8888-888888888888")


@pytest.fixture(autouse=True)
def setup_mock_db():
    """Provides a comprehensive mock database session for all endpoint tests."""
    mock_session = MagicMock()

    # Sample mock objects
    mock_hab = MagicMock()
    mock_hab.id = TEST_HAB_ID
    mock_hab.name = "Mundakkai Settlement"
    mock_hab.district = "Wayanad"
    mock_hab.taluk = "Vythiri"
    mock_hab.state = "Kerala"
    mock_hab.population = 2180
    mock_hab.vulnerable_population = 1450
    mock_hab.elderly_population = 310
    mock_hab.children_population = 420
    mock_hab.disabled_population = 95
    mock_hab.kutcha_houses_pct = 72.0
    mock_hab.elevation = 920.0
    mock_hab.slope = 28.5
    mock_hab.distance_to_road = 180.0
    mock_hab.geometry = {"type": "Polygon", "coordinates": [[[76.13, 11.54], [76.15, 11.54], [76.15, 11.56], [76.13, 11.56], [76.13, 11.54]]]}

    mock_hazard = MagicMock()
    mock_hazard.id = TEST_HAZARD_ID
    mock_hazard.hazard_type = "landslide"
    mock_hazard.risk_score = 94.0
    mock_hazard.severity = "VERY_HIGH"
    mock_hazard.source = "GSI_ISRO_BHUVAN"
    mock_hazard.timestamp = datetime.now(timezone.utc)
    mock_hazard.geometry = {"type": "Polygon", "coordinates": [[[76.12, 11.54], [76.14, 11.54], [76.14, 11.56], [76.12, 11.56], [76.12, 11.54]]]}

    mock_site = MagicMock()
    mock_site.id = TEST_SITE_ID
    mock_site.name = "Meppadi Safe Plateau Zone A"
    mock_site.district = "Wayanad"
    mock_site.taluk = "Vythiri"
    mock_site.state = "Kerala"
    mock_site.usable_area_sqm = 75000.0
    mock_site.terrain_slope = 6.5
    mock_site.soil_type = "STABLE_LATERITE"
    mock_site.water_availability_lpcd = 90.0
    mock_site.electricity_available = True
    mock_site.road_access = True
    mock_site.distance_to_hospital_km = 4.2
    mock_site.distance_to_school_km = 2.8
    mock_site.current_occupancy = 700
    mock_site.estimated_carrying_capacity = 2100
    mock_site.hazard_safety_score = 95
    mock_site.accessibility_score = 88
    mock_site.infrastructure_score = 85
    mock_site.capacity_score = 86
    mock_site.overall_suitability_score = 89
    mock_site.classification = "HIGHLY SUITABLE"
    mock_site.geometry = {"type": "Polygon", "coordinates": [[[76.11, 11.54], [76.13, 11.54], [76.13, 11.56], [76.11, 11.56], [76.11, 11.54]]]}

    mock_alert = MagicMock()
    mock_alert.id = TEST_ALERT_ID
    mock_alert.disaster_type = "landslide"
    mock_alert.severity = "CRITICAL"
    mock_alert.event_time = datetime.now(timezone.utc)
    mock_alert.source = "KSDMA_EOC"
    mock_alert.geometry = {"type": "Point", "coordinates": [76.14, 11.55]}

    # Configure query dispatcher
    def query_dispatcher(*entities, **kwargs):
        q = MagicMock()
        model_str = " ".join([getattr(e, "__name__", str(e)) for e in entities])
        if "sum" in model_str.lower():
            q.count.return_value = 1
            q.scalar.return_value = 2180
            q.all.return_value = []
            q.first.return_value = None
            q.filter.return_value = q
            q.order_by.return_value = q
            q.offset.return_value = q
            q.limit.return_value = q
        elif "max" in model_str.lower() or "observation_time" in model_str or "event_time" in model_str:
            q.count.return_value = 1
            q.scalar.return_value = datetime.now(timezone.utc)
            q.all.return_value = []
            q.first.return_value = None
            q.filter.return_value = q
            q.order_by.return_value = q
            q.offset.return_value = q
            q.limit.return_value = q
        elif "Habitation" in model_str:
            q.count.return_value = 1
            q.all.return_value = [mock_hab]
            q.first.return_value = mock_hab
            q.filter.return_value = q
            q.order_by.return_value = q
            q.offset.return_value = q
            q.limit.return_value = q
        elif "HazardZone" in model_str:
            q.count.return_value = 1
            q.all.return_value = [mock_hazard]
            q.first.return_value = mock_hazard
            q.filter.return_value = q
            q.order_by.return_value = q
            q.offset.return_value = q
            q.limit.return_value = q
        elif "RelocationSite" in model_str:
            q.count.return_value = 1
            q.all.return_value = [mock_site]
            q.first.return_value = mock_site
            q.filter.return_value = q
            q.order_by.return_value = q
            q.offset.return_value = q
            q.limit.return_value = q
        elif "DisasterEvent" in model_str:
            q.count.return_value = 1
            q.all.return_value = [mock_alert]
            q.first.return_value = mock_alert
            q.filter.return_value = q
            q.order_by.return_value = q
            q.offset.return_value = q
            q.limit.return_value = q
        else:
            q.count.return_value = 1
            q.scalar.return_value = 2180
            q.all.return_value = []
            q.first.return_value = None
            q.filter.return_value = q
            q.order_by.return_value = q
            q.offset.return_value = q
            q.limit.return_value = q
        return q

    mock_session.query.side_effect = query_dispatcher

    app.dependency_overrides[get_db] = lambda: mock_session
    yield mock_session
    app.dependency_overrides.pop(get_db, None)


# ==============================================================================
# 1. EXECUTIVE DASHBOARD API (/api/dashboard)
# ==============================================================================

def test_dashboard_endpoint():
    """Verify GET /api/dashboard returns all required KPIs and telemetry timestamps."""
    with patch("backend.app.services.dashboard_service.compute_all_habitations_risk_summary") as mock_risk, \
         patch("backend.app.services.dashboard_service.compute_all_habitations_vulnerability_summary") as mock_vuln, \
         patch("backend.app.services.dashboard_service.compute_all_habitations_priorities_summary") as mock_prio:

        mock_risk.return_value = MagicMock(
            critical_habitations_count=1,
            average_risk_score=85.0,
            habitations=[
                MagicMock(habitation_id=TEST_HAB_ID, severity="CRITICAL", vulnerable_population=1450)
            ],
        )
        mock_vuln.return_value = MagicMock(average_vulnerability_score=78.0)
        mock_prio.return_value = {
            "immediate_count": 1,
            "short_term_count": 0,
            "medium_term_count": 0,
            "monitor_count": 0,
            "priorities": [
                {
                    "habitation_id": TEST_HAB_ID,
                    "habitation_name": "Mundakkai Settlement",
                    "district": "Wayanad",
                    "priority": "IMMEDIATE",
                    "priority_score": 89,
                    "hazard_score": 92,
                    "vulnerability_score": 85,
                    "vulnerable_population": 1450,
                    "recommended_site_name": "Meppadi Safe Plateau Zone A",
                    "recommended_site_distance_km": 4.2,
                }
            ],
        }

        response = client.get("/api/dashboard")
        assert response.status_code == 200
        data = response.json()

        # Check all required prompt fields
        assert data["total_habitations"] >= 1
        assert data["habitations_in_critical_zones"] >= 1
        assert data["population_at_risk"] >= 1000
        assert data["immediate_relocation_count"] >= 1
        assert "short_term_relocation_count" in data
        assert "medium_term_relocation_count" in data
        assert data["total_relocation_capacity"] >= 2000
        assert data["available_relocation_capacity"] >= 1000
        assert "active_alerts" in data
        assert "latest_data_timestamps" in data
        assert "rainfall_telemetry" in data["latest_data_timestamps"]
        assert "river_gauging" in data["latest_data_timestamps"]
        assert "emergency_alerts" in data["latest_data_timestamps"]


# ==============================================================================
# 2. HAZARDS API GROUP (/api/hazards)
# ==============================================================================

def test_hazards_endpoints():
    """Verify /api/hazards listing, pagination, filtering, and GeoJSON."""
    # Paginated list
    res = client.get("/api/hazards?page=1&page_size=10&sort_by=risk_score&order=desc")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "items" in data
    assert len(data["items"]) >= 1
    assert data["items"][0]["severity"] == "VERY_HIGH"
    assert data["items"][0]["geometry"]["type"] == "Polygon"

    # GeoJSON FeatureCollection
    res_geo = client.get("/api/hazards/geojson")
    assert res_geo.status_code == 200
    geo_data = res_geo.json()
    assert geo_data["type"] == "FeatureCollection"
    assert len(geo_data["features"]) >= 1

    # Single hazard
    res_single = client.get(f"/api/hazards/{TEST_HAZARD_ID}")
    assert res_single.status_code == 200
    assert res_single.json()["id"] == str(TEST_HAZARD_ID)


# ==============================================================================
# 3. HABITATIONS API GROUP (/api/habitations)
# ==============================================================================

def test_habitations_endpoints():
    """Verify /api/habitations listing, GeoJSON, single, risk, and vulnerability."""
    # List
    res = client.get("/api/habitations?page=1&page_size=10&sort_by=name&order=asc")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert data["items"][0]["name"] == "Mundakkai Settlement"
    assert data["items"][0]["geometry"]["type"] == "Polygon"

    # GeoJSON
    res_geo = client.get("/api/habitations/geojson")
    assert res_geo.status_code == 200
    assert res_geo.json()["type"] == "FeatureCollection"

    # Single
    res_single = client.get(f"/api/habitations/{TEST_HAB_ID}")
    assert res_single.status_code == 200
    assert res_single.json()["name"] == "Mundakkai Settlement"

    # Risk route
    with patch("backend.app.api.v1.endpoints.habitations.compute_habitation_risk_from_db") as mock_r:
        mock_r.return_value = {
            "habitation_id": TEST_HAB_ID,
            "habitation_name": "Mundakkai Settlement",
            "district": "Wayanad",
            "state": "Kerala",
            "population": 2180,
            "vulnerable_population": 1450,
            "overall_score": 88,
            "severity": "CRITICAL",
            "factors": {"rainfall": 90, "flood_exposure": 85},
            "explanation": ["High rainfall intensity"],
            "geometry": {"type": "Polygon", "coordinates": [[[76.13, 11.54], [76.15, 11.54], [76.15, 11.56], [76.13, 11.56], [76.13, 11.54]]]},
            "calculated_at": datetime.now(timezone.utc),
        }
        res_risk = client.get(f"/api/habitations/{TEST_HAB_ID}/risk")
        assert res_risk.status_code == 200
        assert res_risk.json()["overall_score"] == 88

    # Vulnerability route
    with patch("backend.app.api.v1.endpoints.habitations.compute_habitation_vulnerability_from_db") as mock_v:
        mock_v.return_value = {
            "habitation_id": TEST_HAB_ID,
            "habitation_name": "Mundakkai Settlement",
            "district": "Wayanad",
            "state": "Kerala",
            "vulnerability_score": 82,
            "severity": "CRITICAL",
            "factors": {"housing": 75, "elderly": 80},
            "explanation": ["Fragile housing"],
            "demographics": {
                "total_population": 2180,
                "vulnerable_population": 1450,
                "elderly_population": 310,
                "children_population": 420,
                "disabled_population": 95,
                "population_density_per_sqkm": 420.0,
                "kutcha_housing_pct": 72.0,
                "infrastructure_fragility_pct": 65.0,
                "is_demonstration_data": True,
                "data_source": "DEMO_SYNTHESIS_CENSUS_PROXY",
            },
            "geometry": {"type": "Polygon", "coordinates": [[[76.13, 11.54], [76.15, 11.54], [76.15, 11.56], [76.13, 11.56], [76.13, 11.54]]]},
            "calculated_at": datetime.now(timezone.utc),
        }
        res_vuln = client.get(f"/api/habitations/{TEST_HAB_ID}/vulnerability")
        assert res_vuln.status_code == 200
        assert res_vuln.json()["vulnerability_score"] == 82


# ==============================================================================
# 4. VULNERABILITY API GROUP (/api/vulnerability)
# ==============================================================================

def test_vulnerability_group_endpoints():
    """Verify /api/vulnerability summary, geojson, and by-id."""
    with patch("backend.app.api.v1.endpoints.vulnerability.compute_all_habitations_vulnerability_summary") as mock_sum, \
         patch("backend.app.api.v1.endpoints.vulnerability.compute_habitation_vulnerability_from_db") as mock_single:

        mock_item = HabitationVulnerabilityResponse(
            habitation_id=TEST_HAB_ID,
            habitation_name="Mundakkai Settlement",
            district="Wayanad",
            state="Kerala",
            vulnerability_score=82,
            severity="CRITICAL",
            factors={"housing": 75},
            explanation=["High vulnerability"],
            demographics={
                "total_population": 2180,
                "vulnerable_population": 1450,
                "elderly_population": 310,
                "children_population": 420,
                "disabled_population": 95,
                "population_density_per_sqkm": 420.0,
                "kutcha_housing_pct": 72.0,
                "infrastructure_fragility_pct": 65.0,
                "is_demonstration_data": True,
                "data_source": "DEMO_SYNTHESIS_CENSUS_PROXY",
            },
            geometry={"type": "Polygon", "coordinates": [[[76.13, 11.54], [76.15, 11.54], [76.15, 11.56], [76.13, 11.56], [76.13, 11.54]]]},
            calculated_at=datetime.now(timezone.utc),
        )

        mock_sum.return_value = VulnerabilitySummaryResponse(
            total_habitations=1,
            severity_breakdown={"CRITICAL": 1, "HIGH": 0, "MODERATE": 0, "LOW": 0},
            average_vulnerability_score=82.0,
            critical_vulnerability_count=1,
            habitations=[mock_item],
            calculated_at=datetime.now(timezone.utc),
        )
        mock_single.return_value = mock_item

        # Summary
        res_sum = client.get("/api/vulnerability/summary")
        assert res_sum.status_code == 200
        assert res_sum.json()["total_habitations"] == 1

        # GeoJSON
        res_geo = client.get("/api/vulnerability/geojson")
        assert res_geo.status_code == 200
        assert res_geo.json()["type"] == "FeatureCollection"

        # By ID
        res_single = client.get(f"/api/vulnerability/{TEST_HAB_ID}")
        assert res_single.status_code == 200
        assert res_single.json()["vulnerability_score"] == 82


# ==============================================================================
# 5. RELOCATION-SITES API GROUP (/api/relocation-sites)
# ==============================================================================

def test_relocation_sites_endpoints():
    """Verify /api/relocation-sites listing, GeoJSON, assessment, capacity, nearby."""
    with patch("backend.app.api.v1.endpoints.relocation_sites.get_all_relocation_sites_from_db") as mock_all, \
         patch("backend.app.api.v1.endpoints.relocation_sites.get_relocation_site_by_id_from_db") as mock_one, \
         patch("backend.app.api.v1.endpoints.relocation_sites.compute_site_assessment_from_db") as mock_assess, \
         patch("backend.app.api.v1.endpoints.relocation_sites.compute_site_capacity_from_db") as mock_cap, \
         patch("backend.app.api.v1.endpoints.relocation_sites.find_suitable_nearby_sites_for_habitation") as mock_near:

        site_dict = {
            "id": TEST_SITE_ID,
            "name": "Meppadi Safe Plateau Zone A",
            "district": "Wayanad",
            "taluk": "Vythiri",
            "state": "Kerala",
            "available_area": 75000.0,
            "usable_area_sqm": 75000.0,
            "current_population": 700,
            "current_occupancy": 700,
            "estimated_capacity": 2100,
            "estimated_carrying_capacity": 2100,
            "available_capacity": 1400,
            "water_score": 9.0,
            "road_access_score": 8.5,
            "healthcare_score": 8.0,
            "hazard_score": 1.5,
            "suitability_score": 89.0,
            "terrain_slope": 6.5,
            "soil_type": "STABLE_LATERITE",
            "water_availability_lpcd": 90.0,
            "electricity_available": True,
            "road_access": True,
            "distance_to_hospital_km": 4.2,
            "distance_to_school_km": 2.8,
            "hazard_safety_score": 95,
            "accessibility_score": 88,
            "infrastructure_score": 85,
            "capacity_score": 86,
            "overall_suitability_score": 89,
            "classification": "HIGHLY SUITABLE",
            "geometry": {"type": "Polygon", "coordinates": [[[76.11, 11.54], [76.13, 11.54], [76.13, 11.56], [76.11, 11.56], [76.11, 11.54]]]},
        }

        mock_all.return_value = [site_dict]
        mock_one.return_value = site_dict
        mock_assess.return_value = {
            "site_id": TEST_SITE_ID,
            "site_name": "Meppadi Safe Plateau Zone A",
            "suitability_score": 89,
            "overall_suitability_score": 89,
            "classification": "HIGHLY SUITABLE",
            "hazard_safety_score": 95,
            "accessibility_score": 88,
            "infrastructure_score": 85,
            "capacity_score": 86,
            "category_scores": {
                "hazard_safety_score": 95,
                "accessibility_score": 88,
                "infrastructure_score": 85,
                "capacity_score": 86,
            },
            "factors": {"water_availability": 90, "road_access": 85},
            "strengths": ["Excellent hazard safety"],
            "limitations": [],
            "available_capacity": 1400,
            "estimated_capacity": 2100,
            "available_area_sqm": 75000.0,
            "geometry": site_dict["geometry"],
            "calculated_at": datetime.now(timezone.utc),
        }
        mock_cap.return_value = {
            "site_id": TEST_SITE_ID,
            "site_name": "Meppadi Safe Plateau Zone A",
            "gross_capacity": 2100,
            "infrastructure_capacity": 1800,
            "water_capacity": 1600,
            "final_capacity": 1600,
            "current_population": 700,
            "available_capacity": 900,
            "limiting_factors": ["Water capacity bottleneck"],
            "factor_capacities": {
                "usable_land": 2100,
                "water_supply": 1600,
                "sanitation": 1800,
                "healthcare": 2000,
                "electricity": 2000,
                "road_access": 1900,
            },
            "assumptions": {},
            "calculated_at": datetime.now(timezone.utc),
        }
        mock_near.return_value = {
            "habitation_id": TEST_HAB_ID,
            "habitation_name": "Mundakkai Settlement",
            "vulnerable_population": 1450,
            "total_sites_found": 1,
            "recommended_sites": [{
                "site_id": TEST_SITE_ID,
                "site_name": "Meppadi Safe Plateau Zone A",
                "distance_km": 4.2,
                "distance_meters": 4200.0,
                "available_capacity": 900,
                "suitability_score": 89,
                "classification": "HIGHLY SUITABLE",
                "hazard_safe": True,
                "proximity_rank": 1,
                "geometry": site_dict["geometry"],
            }],
        }

        # List
        res_list = client.get("/api/relocation-sites?page=1&page_size=10")
        assert res_list.status_code == 200
        assert res_list.json()["total"] == 1

        # GeoJSON
        res_geo = client.get("/api/relocation-sites/geojson")
        assert res_geo.status_code == 200
        assert res_geo.json()["type"] == "FeatureCollection"

        # Single
        res_single = client.get(f"/api/relocation-sites/{TEST_SITE_ID}")
        assert res_single.status_code == 200
        assert res_single.json()["name"] == "Meppadi Safe Plateau Zone A"

        # Assessment
        res_assess = client.get(f"/api/relocation-sites/{TEST_SITE_ID}/assessment")
        assert res_assess.status_code == 200
        assert res_assess.json()["overall_suitability_score"] == 89

        # Capacity
        res_cap = client.get(f"/api/relocation-sites/{TEST_SITE_ID}/capacity")
        assert res_cap.status_code == 200
        assert res_cap.json()["final_capacity"] == 1600

        # Nearby
        res_near = client.get(f"/api/relocation-sites/nearby/{TEST_HAB_ID}")
        assert res_near.status_code == 200
        assert len(res_near.json()["recommended_sites"]) == 1


# ==============================================================================
# 6. RELOCATION PRIORITIZATION API GROUP (/api/relocation)
# ==============================================================================

def test_relocation_priorities_endpoints():
    """Verify /api/relocation/priorities and recommendation routes."""
    with patch("backend.app.api.v1.endpoints.relocation.compute_all_habitations_priorities_summary") as mock_sum, \
         patch("backend.app.api.v1.endpoints.relocation.compute_habitation_priority_from_db") as mock_single:

        prio_item = {
            "habitation_id": TEST_HAB_ID,
            "habitation_name": "Mundakkai Settlement",
            "district": "Wayanad",
            "state": "Kerala",
            "priority_score": 89,
            "priority": "IMMEDIATE",
            "factors": {"hazard_risk": 92, "population_vulnerability": 85},
            "reasons": ["Critical hazard risk"],
            "vulnerable_population": 1450,
            "total_population": 2180,
            "recommended_site": {
                "site_id": TEST_SITE_ID,
                "site_name": "Meppadi Safe Plateau Zone A",
                "distance_km": 4.2,
                "distance_meters": 4200.0,
                "suitability_score": 89,
                "classification": "HIGHLY SUITABLE",
                "available_capacity": 900,
                "capacity_sufficient": False,
                "match_score": 90.0,
            },
            "best_suitable_site": {
                "site_id": TEST_SITE_ID,
                "site_name": "Meppadi Safe Plateau Zone A",
                "distance_km": 4.2,
                "distance_meters": 4200.0,
                "suitability_score": 89,
                "classification": "HIGHLY SUITABLE",
                "available_capacity": 900,
                "capacity_sufficient": False,
                "match_score": 90.0,
            },
            "alternative_sites": [],
            "decision_support_disclaimer": "Decision support only",
            "calculated_at": datetime.now(timezone.utc),
        }

        mock_sum.return_value = {
            "total_habitations": 1,
            "immediate_count": 1,
            "short_term_count": 0,
            "medium_term_count": 0,
            "monitor_count": 0,
            "average_priority_score": 89.0,
            "priorities": [{
                "habitation_id": TEST_HAB_ID,
                "habitation_name": "Mundakkai Settlement",
                "district": "Wayanad",
                "state": "Kerala",
                "priority_score": 89,
                "priority": "IMMEDIATE",
                "vulnerable_population": 1450,
                "total_population": 2180,
                "hazard_score": 92,
                "vulnerability_score": 85,
                "reasons": ["Critical risk"],
                "recommended_site_id": TEST_SITE_ID,
                "recommended_site_name": "Meppadi Safe Plateau Zone A",
                "recommended_site_distance_km": 4.2,
            }],
            "decision_support_disclaimer": "Decision support only",
            "calculated_at": datetime.now(timezone.utc),
        }
        mock_single.return_value = prio_item

        # Priorities summary
        res_prio = client.get("/api/relocation/priorities")
        assert res_prio.status_code == 200
        assert res_prio.json()["immediate_count"] == 1

        # Single priority
        res_single = client.get(f"/api/relocation/priorities/{TEST_HAB_ID}")
        assert res_single.status_code == 200
        assert res_single.json()["priority_score"] == 89

        # Actionable recommendation
        res_rec = client.get(f"/api/relocation/recommendation/{TEST_HAB_ID}")
        assert res_rec.status_code == 200
        assert res_rec.json()["best_suitable_site"]["site_name"] == "Meppadi Safe Plateau Zone A"

        # Summary count
        res_sum = client.get("/api/relocation/summary")
        assert res_sum.status_code == 200
        assert res_sum.json()["immediate_count"] == 1


# ==============================================================================
# 7. ALERTS API GROUP (/api/alerts)
# ==============================================================================

def test_alerts_endpoints():
    """Verify /api/alerts listing, GeoJSON, and by-id."""
    # List
    res = client.get("/api/alerts?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert data["items"][0]["severity"] == "CRITICAL"
    assert data["items"][0]["geometry"]["type"] == "Point"

    # GeoJSON FeatureCollection
    res_geo = client.get("/api/alerts/geojson")
    assert res_geo.status_code == 200
    assert res_geo.json()["type"] == "FeatureCollection"

    # By ID
    res_single = client.get(f"/api/alerts/{TEST_ALERT_ID}")
    assert res_single.status_code == 200
    assert res_single.json()["id"] == str(TEST_ALERT_ID)


# ==============================================================================
# 8. DATA SOURCES API GROUP (/api/data-sources)
# ==============================================================================

def test_data_sources_status():
    """Verify /api/data-sources/status returns 4 telemetry feeds."""
    res = client.get("/api/data-sources/status")
    assert res.status_code == 200
    data = res.json()
    assert data["total_sources"] == 4
    src_ids = [s["source_id"] for s in data["sources"]]
    assert "mosdac_isro" in src_ids
    assert "cwc_wims" in src_ids
    assert "ndma_sachet" in src_ids
    assert "imd_weather" in src_ids


# ==============================================================================
# 9. ANALYTICS API GROUP (/api/analytics)
# ==============================================================================

def test_analytics_endpoints():
    """Verify /api/analytics package and sub-routes."""
    with patch("backend.app.services.analytics_service.compute_all_habitations_risk_summary") as mock_r, \
         patch("backend.app.services.analytics_service.compute_all_habitations_vulnerability_summary") as mock_v, \
         patch("backend.app.services.analytics_service.compute_all_habitations_priorities_summary") as mock_p, \
         patch("backend.app.db.spatial_queries.get_habitations_in_hazard_zones") as mock_spat:

        mock_r.return_value = MagicMock(
            habitations=[
                MagicMock(severity="CRITICAL", population=2180, vulnerable_population=1450)
            ]
        )
        mock_v.return_value = MagicMock(
            habitations=[
                MagicMock(
                    habitation_name="Mundakkai Settlement",
                    factors={"total_population": 85, "housing_vulnerability": 75}
                )
            ]
        )
        mock_p.return_value = {
            "priorities": [{
                "recommended_site_id": TEST_SITE_ID,
                "vulnerable_population": 1450,
            }]
        }
        mock_spat.return_value = [{"habitation_id": str(TEST_HAB_ID), "population": 2180, "severity": "VERY_HIGH"}]

        # Full overview
        res_over = client.get("/api/analytics")
        assert res_over.status_code == 200
        data = res_over.json()
        assert "risk_distribution" in data
        assert "vulnerability_factors" in data
        assert "capacity_vs_need" in data
        assert "hazard_exposures" in data

        # Risk distribution histogram
        res_hist = client.get("/api/analytics/risk-distribution")
        assert res_hist.status_code == 200
        assert len(res_hist.json()) == 4

        # Vulnerability breakdown
        res_vuln = client.get("/api/analytics/vulnerability-breakdown")
        assert res_vuln.status_code == 200
        assert len(res_vuln.json()) == 9

        # Capacity vs need
        res_cap = client.get("/api/analytics/capacity-vs-need")
        assert res_cap.status_code == 200
        assert len(res_cap.json()) >= 1


# ==============================================================================
# 10. CROSS-CUTTING: ERROR HANDLING, CORS & HEALTH
# ==============================================================================

def test_cors_and_error_handling():
    """Verify CORS preflight and 422/404 error responses."""
    # CORS
    res_cors = client.options(
        "/api/dashboard",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res_cors.status_code in (200, 204)
    assert "access-control-allow-origin" in res_cors.headers

    # 422 validation error
    res_422 = client.get("/api/habitations?page=not_a_valid_number")
    assert res_422.status_code == 422
    assert "error" in res_422.json() or "detail" in res_422.json()

    # Health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] in ["healthy", "degraded"]
