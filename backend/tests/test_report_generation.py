"""Tests for the Report-Generation Module: 13 Required Sections, Epistemic Demarcation, and PDF/CSV Export."""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.session import get_db
from backend.app.services.audit_service import AuditService

client = TestClient(app)

TEST_HAB_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
TEST_SITE_ID = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
TEST_EVENT_ID = uuid.UUID("88888888-8888-4888-8888-888888888888")


@pytest.fixture(autouse=True)
def setup_mock_db():
    """Provides a mock database session for report generation."""
    mock_session = MagicMock()

    mock_hab = MagicMock()
    mock_hab.id = TEST_HAB_ID
    mock_hab.name = "Mundakkai Settlement"
    mock_hab.district = "Wayanad"
    mock_hab.taluk = "Vythiri"
    mock_hab.state = "Kerala"
    mock_hab.population = 2180
    mock_hab.vulnerable_population = 1450
    mock_hab.geometry = {"type": "Polygon", "coordinates": [[[76.13, 11.54], [76.15, 11.54], [76.15, 11.56], [76.13, 11.56], [76.13, 11.54]]]}

    mock_site = MagicMock()
    mock_site.id = TEST_SITE_ID
    mock_site.name = "Meppadi Safe Plateau Zone A"
    mock_site.available_area = 45000.0
    mock_site.current_population = 150
    mock_site.estimated_capacity = 2500
    mock_site.available_capacity = 2350
    mock_site.water_score = 8.8
    mock_site.road_access_score = 9.2
    mock_site.healthcare_score = 8.5
    mock_site.hazard_score = 0.5
    mock_site.suitability_score = 89.0
    mock_site.geometry = {"type": "Polygon", "coordinates": [[[76.11, 11.54], [76.13, 11.54], [76.13, 11.56], [76.11, 11.56], [76.11, 11.54]]]}

    mock_event = MagicMock()
    mock_event.id = TEST_EVENT_ID
    mock_event.disaster_type = "landslide"
    mock_event.severity = "CRITICAL"
    mock_event.event_time = datetime.now(timezone.utc)
    mock_event.source = "KSDMA_EOC"
    mock_event.geometry = {"type": "Point", "coordinates": [76.14, 11.55]}

    mock_rain = MagicMock()
    mock_rain.rainfall_mm = 382.5
    mock_rain.source = "IMD_AWS_MUNDAKKAI_PEAK"
    mock_rain.latitude = 11.55
    mock_rain.longitude = 76.14
    mock_rain.observation_time = datetime.now(timezone.utc)

    mock_river = MagicMock()
    mock_river.station_name = "Iruvanjippuzha Chooralmala Bridge"
    mock_river.water_level = 8.65
    mock_river.danger_level = 6.50
    mock_river.observation_time = datetime.now(timezone.utc)

    def query_dispatcher(*entities, **kwargs):
        q = MagicMock()
        model_str = " ".join([getattr(e, "__name__", str(e)) for e in entities])
        if "Habitation" in model_str:
            q.count.return_value = 1
            q.all.return_value = [mock_hab]
            q.first.return_value = mock_hab
        elif "RelocationSite" in model_str:
            q.count.return_value = 1
            q.all.return_value = [mock_site]
            q.first.return_value = mock_site
        elif "DisasterEvent" in model_str:
            q.count.return_value = 1
            q.all.return_value = [mock_event]
            q.first.return_value = mock_event
        elif "RainfallObservation" in model_str:
            q.first.return_value = mock_rain
            q.all.return_value = [mock_rain]
        elif "RiverObservation" in model_str:
            q.first.return_value = mock_river
            q.all.return_value = [mock_river]
        else:
            q.count.return_value = 1
            q.all.return_value = []
            q.first.return_value = None

        q.filter.return_value = q
        q.order_by.return_value = q
        q.offset.return_value = q
        q.limit.return_value = q
        return q

    mock_session.query.side_effect = query_dispatcher

    def override_get_db():
        try:
            yield mock_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield mock_session
    app.dependency_overrides.pop(get_db, None)


def get_auth_token(username: str = "collector", password: str = "GovAdmin@2026") -> str:
    """Helper to authenticate as authority viewer."""
    res = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_get_report_options():
    token = get_auth_token()
    res = client.get("/api/v1/reports/options", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "districts" in data
    assert "habitations" in data
    assert "hazard_events" in data
    assert "relocation_sites" in data
    assert "Wayanad" in data["districts"]
    assert len(data["habitations"]) >= 1


def test_generate_report_contains_all_13_sections():
    token = get_auth_token()
    payload = {
        "district": "Wayanad",
        "habitation_id": str(TEST_HAB_ID),
        "hazard_event_id": str(TEST_EVENT_ID),
        "relocation_site_id": str(TEST_SITE_ID),
        "officer_notes": "Urgent review prior to southwest monsoon intensification.",
    }
    res = client.post("/api/v1/reports/generate", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()

    # Verify all 13 required sections:
    # 1. Situation summary
    assert "situation_summary" in data and len(data["situation_summary"]) > 20
    # 2. Hazard assessment
    assert "hazard_assessment" in data
    assert "rainfall_telemetry" in data["hazard_assessment"]
    assert "river_telemetry" in data["hazard_assessment"]
    # 3. Population vulnerability
    assert "population_vulnerability" in data
    assert data["population_vulnerability"]["total_population"] > 0
    assert data["population_vulnerability"]["vulnerable_population"] > 0
    # 4. Disaster history
    assert "disaster_history" in data
    assert len(data["disaster_history"]) >= 1
    # 5. Risk score
    assert "risk_score" in data
    assert "score" in data["risk_score"]
    assert "factor_sub_scores" in data["risk_score"]
    # 6. Relocation priority
    assert "relocation_priority" in data
    assert data["relocation_priority"]["priority"] in ["IMMEDIATE", "SHORT_TERM", "MEDIUM_TERM", "MONITOR"]
    # 7. Recommended relocation sites
    assert "recommended_relocation_sites" in data
    assert len(data["recommended_relocation_sites"]) >= 1
    assert "distance_km" in data["recommended_relocation_sites"][0]
    # 8. Carrying capacity
    assert "carrying_capacity" in data
    assert "final_ecological_civil_capacity" in data["carrying_capacity"]
    assert "limiting_factor" in data["carrying_capacity"]
    # 9. Available capacity
    assert "available_capacity" in data
    assert "available_buffer" in data["available_capacity"]
    # 10. Key reasons
    assert "key_reasons" in data
    assert len(data["key_reasons"]) >= 1
    # 11. Data sources
    assert "data_sources" in data
    assert any("IMD" in ds["provider"] or "India Meteorological" in ds["provider"] for ds in data["data_sources"])
    # 12. Data timestamps
    assert "data_timestamps" in data
    assert "report_generated_utc" in data["data_timestamps"]
    # 13. Model/scoring assumptions
    assert "model_scoring_assumptions" in data
    assert len(data["model_scoring_assumptions"]) >= 3


def test_epistemic_demarcation():
    """Verify that observed data, model-derived scores, prototype assumptions, and recommendations are clearly distinguished."""
    token = get_auth_token()
    payload = {"district": "Wayanad"}
    res = client.post("/api/v1/reports/generate", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()

    assert "epistemic_categorization" in data
    epistemic = data["epistemic_categorization"]

    # 1. Observed data
    assert "observed_data" in epistemic
    assert "rainfall_mm" in epistemic["observed_data"]["items"]
    assert "river_level_m" in epistemic["observed_data"]["items"]
    assert "habitation_population" in epistemic["observed_data"]["items"]

    # 2. Model-derived scores
    assert "model_derived_scores" in epistemic
    assert "hazard_risk_score" in epistemic["model_derived_scores"]["items"]
    assert "relocation_priority_score" in epistemic["model_derived_scores"]["items"]
    assert "sustainable_carrying_capacity" in epistemic["model_derived_scores"]["items"]

    # 3. Prototype assumptions
    assert "prototype_assumptions" in epistemic
    assert "shelter_area_standard" in epistemic["prototype_assumptions"]["items"]
    assert "potable_water_baseline" in epistemic["prototype_assumptions"]["items"]

    # 4. Recommendations
    assert "recommendations" in epistemic
    assert "allocated_safe_resettlement_site" in epistemic["recommendations"]["items"]
    assert "statutory_mandate" in epistemic["recommendations"]["items"]


def test_export_report_csv():
    token = get_auth_token()
    payload = {
        "district": "Wayanad",
        "habitation_id": str(TEST_HAB_ID),
        "format": "csv",
        "officer_notes": "DDMA operational briefing copy.",
    }
    res = client.post("/api/v1/reports/export", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "attachment; filename=" in res.headers["content-disposition"]
    csv_text = res.text
    assert "SECTION 1: SITUATION SUMMARY" in csv_text
    assert "SECTION 2: HAZARD ASSESSMENT" in csv_text
    assert "SECTION 3: POPULATION VULNERABILITY" in csv_text
    assert "SECTION 5: RISK SCORE" in csv_text
    assert "SECTION 7: RECOMMENDED RELOCATION SITES" in csv_text
    assert "SECTION 8 & 9: CARRYING CAPACITY" in csv_text
    assert "EPISTEMIC CATEGORIZATION MAPPING" in csv_text


def test_export_report_pdf():
    token = get_auth_token()
    payload = {
        "district": "Wayanad",
        "habitation_id": str(TEST_HAB_ID),
        "format": "pdf",
        "officer_notes": "Official Command Briefing Copy.",
    }
    res = client.post("/api/v1/reports/export", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "application/pdf" in res.headers["content-type"]
    assert "attachment; filename=" in res.headers["content-disposition"]
    # PDF starts with %PDF magic bytes
    assert res.content.startswith(b"%PDF")
    assert len(res.content) > 1000


def test_report_unauthorized_without_token():
    res = client.post("/api/v1/reports/generate", json={"district": "Wayanad"})
    assert res.status_code == 401
