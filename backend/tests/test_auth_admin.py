"""Unit & Integration Tests for Auth, RBAC, Admin Module, Audit Logging, and Report Export."""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.session import get_db
from backend.app.services.audit_service import AuditService

client = TestClient(app)

TEST_HAB_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
TEST_SITE_ID = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")


@pytest.fixture(autouse=True)
def setup_mock_db():
    """Provides a mock database session for admin endpoints."""
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

    def query_dispatcher(*entities, **kwargs):
        q = MagicMock()
        model_str = " ".join([getattr(e, "__name__", str(e)) for e in entities])
        if "sum" in model_str.lower():
            q.scalar.return_value = 2180
        elif "max" in model_str.lower():
            q.scalar.return_value = datetime.now(timezone.utc)
        elif "Habitation" in model_str:
            q.count.return_value = 1
            q.all.return_value = [mock_hab]
            q.first.return_value = mock_hab
        elif "RelocationSite" in model_str:
            q.count.return_value = 1
            q.all.return_value = [mock_site]
            q.first.return_value = mock_site
        elif "HazardZone" in model_str:
            mock_hazard = MagicMock()
            mock_hazard.id = uuid.uuid4()
            mock_hazard.hazard_type = "landslide"
            mock_hazard.risk_score = 0.94
            mock_hazard.severity = "VERY_HIGH"
            q.count.return_value = 1
            q.all.return_value = [mock_hazard]
            q.first.return_value = mock_hazard
        elif "DisasterEvent" in model_str:
            mock_event = MagicMock()
            mock_event.id = uuid.uuid4()
            mock_event.disaster_type = "landslide"
            mock_event.severity = "CRITICAL"
            mock_event.event_time = datetime.now(timezone.utc)
            q.count.return_value = 1
            q.all.return_value = [mock_event]
            q.first.return_value = mock_event
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


def get_token(username: str = "admin", password: str = "GovAdmin@2026") -> str:
    """Helper to authenticate and return a valid JWT token."""
    res = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200, f"Login failed for {username}: {res.text}"
    return res.json()["access_token"]


# --- Auth Tests ---

def test_login_success_admin():
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "GovAdmin@2026"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "ADMIN"
    assert data["user"]["username"] == "admin"


def test_login_success_authority_viewer():
    res = client.post("/api/v1/auth/login", json={"username": "collector", "password": "GovAdmin@2026"})
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["role"] == "AUTHORITY_VIEWER"
    assert "District Collector" in data["user"]["designation"]


def test_login_invalid_credentials():
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "WrongPassword"})
    assert res.status_code == 401
    data = res.json()
    err_msg = data.get("error", {}).get("message", "") or data.get("detail", "")
    assert "Invalid username or password" in err_msg


def test_auth_me_authenticated():
    token = get_token("admin")
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["username"] == "admin"
    assert res.json()["role"] == "ADMIN"


def test_auth_me_unauthorized():
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


# --- Audit Log RBAC Tests ---

def test_admin_can_view_audit_logs():
    token = get_token("admin")
    res = client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


def test_authority_viewer_forbidden_from_audit_logs():
    token = get_token("collector")
    res = client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    data = res.json()
    err_msg = data.get("error", {}).get("message", "") or data.get("detail", "")
    assert "Access forbidden" in err_msg


# --- Habitation Management RBAC Tests ---

def test_admin_can_create_habitation():
    token = get_token("admin")
    payload = {
        "name": "Demonstration Highland Colony",
        "district": "Wayanad",
        "taluk": "Vythiri",
        "state": "Kerala",
        "population": 1200,
        "vulnerable_population": 450,
        "latitude": 11.56,
        "longitude": 76.14,
        "is_demo": True,
    }
    res = client.post("/api/v1/admin/habitations", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "success"
    assert data["name"] == "Demonstration Highland Colony"
    assert "id" in data


def test_authority_viewer_cannot_create_habitation():
    token = get_token("collector")
    payload = {
        "name": "Unauthorized Settlement",
        "district": "Wayanad",
        "population": 500,
        "vulnerable_population": 200,
        "latitude": 11.55,
        "longitude": 76.13,
    }
    res = client.post("/api/v1/admin/habitations", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_admin_can_update_habitation():
    token = get_token("admin")
    payload = {
        "name": "Updated Mundakkai Colony",
        "population": 2500,
    }
    res = client.put(f"/api/v1/admin/habitations/{TEST_HAB_ID}", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_admin_can_delete_habitation():
    token = get_token("admin")
    res = client.delete(f"/api/v1/admin/habitations/{TEST_HAB_ID}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "success"


# --- Relocation Site Management RBAC Tests ---

def test_admin_can_create_relocation_site():
    token = get_token("admin")
    payload = {
        "name": "Kalpetta South Safe Plateau Parcel B",
        "available_area": 55000.0,
        "estimated_capacity": 3000,
        "current_population": 200,
        "water_score": 9.0,
        "road_access_score": 9.5,
        "healthcare_score": 8.0,
        "hazard_score": 0.2,
        "suitability_score": 92.0,
        "latitude": 11.61,
        "longitude": 76.08,
    }
    res = client.post("/api/v1/admin/relocation-sites", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "success"
    assert data["available_capacity"] == 2800  # 3000 - 200


def test_authority_viewer_cannot_create_relocation_site():
    token = get_token("collector")
    payload = {
        "name": "Unauthorized Site",
        "available_area": 10000.0,
        "estimated_capacity": 500,
        "latitude": 11.55,
        "longitude": 76.10,
    }
    res = client.post("/api/v1/admin/relocation-sites", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_admin_can_update_relocation_site():
    token = get_token("admin")
    payload = {
        "name": "Upgraded Safe Plateau Parcel",
        "estimated_capacity": 3500,
    }
    res = client.put(f"/api/v1/admin/relocation-sites/{TEST_SITE_ID}", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_admin_can_delete_relocation_site():
    token = get_token("admin")
    res = client.delete(f"/api/v1/admin/relocation-sites/{TEST_SITE_ID}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "success"


# --- Decision Support & Report Export Tests ---

def _get_mock_kpis():
    kpis = MagicMock()
    kpis.total_habitations = 4
    kpis.habitations_in_critical_zones = 2
    kpis.population_at_risk = 4200
    kpis.immediate_relocation_count = 1
    kpis.short_term_relocation_count = 1
    kpis.medium_term_relocation_count = 1
    kpis.total_relocation_capacity = 4500
    kpis.available_relocation_capacity = 3800
    kpis.active_alerts = 2
    kpis.model_dump.return_value = {
        "total_habitations": 4,
        "habitations_in_critical_zones": 2,
        "population_at_risk": 4200,
        "immediate_relocation_count": 1,
        "short_term_relocation_count": 1,
        "medium_term_relocation_count": 1,
        "total_relocation_capacity": 4500,
        "available_relocation_capacity": 3800,
        "active_alerts": 2,
    }
    return kpis


def _get_mock_priorities():
    p = MagicMock()
    p.priority_distribution = {"IMMEDIATE": 1, "SHORT_TERM": 1, "MEDIUM_TERM": 1, "MONITOR": 1}
    item = MagicMock()
    item.habitation_id = TEST_HAB_ID
    item.habitation_name = "Mundakkai Settlement"
    item.priority = "IMMEDIATE"
    item.priority_score = 89
    item.recommended_site = {"site_name": "Meppadi Safe Plateau Zone A", "distance_km": 4.2, "available_capacity": 2350}
    item.reasons = ["Critical landslide zone overlap", "High vulnerable population count"]
    p.priorities = [item]
    return p


def test_decision_support_summary_available_to_both_roles():
    with patch("backend.app.api.v1.endpoints.admin.DashboardService.get_dashboard_summary", return_value=_get_mock_kpis()), \
         patch("backend.app.api.v1.endpoints.admin.compute_all_habitations_priorities_summary", return_value=_get_mock_priorities()):
        admin_token = get_token("admin")
        res_admin = client.get("/api/v1/admin/decision-support-summary", headers={"Authorization": f"Bearer {admin_token}"})
        assert res_admin.status_code == 200
        data = res_admin.json()
        assert "kpi_metrics" in data
        assert "priority_distribution" in data
        assert "statutory_notice" in data

        viewer_token = get_token("collector")
        res_viewer = client.get("/api/v1/admin/decision-support-summary", headers={"Authorization": f"Bearer {viewer_token}"})
        assert res_viewer.status_code == 200
        assert res_viewer.json()["user_profile"]["role"] == "AUTHORITY_VIEWER"


def test_export_report_json():
    with patch("backend.app.api.v1.endpoints.admin.DashboardService.get_dashboard_summary", return_value=_get_mock_kpis()), \
         patch("backend.app.api.v1.endpoints.admin.compute_all_habitations_priorities_summary", return_value=_get_mock_priorities()):
        token = get_token("collector")
        payload = {
            "format": "json",
            "include_risk_explanations": True,
            "include_relocation_recommendations": True,
            "officer_notes": "Urgent review requested before monsoon peak.",
        }
        res = client.post("/api/v1/admin/export-report", json=payload, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert "report_id" in data
        assert "kpi_metrics" in data
        assert "habitations_assessment" in data
        assert data["statutory_compliance"]["ground_validation_required"] is True
        assert data["officer"]["role"] == "AUTHORITY_VIEWER"


def test_export_report_csv():
    with patch("backend.app.api.v1.endpoints.admin.DashboardService.get_dashboard_summary", return_value=_get_mock_kpis()), \
         patch("backend.app.api.v1.endpoints.admin.compute_all_habitations_priorities_summary", return_value=_get_mock_priorities()):
        token = get_token("admin")
        payload = {
            "format": "csv",
            "include_risk_explanations": True,
            "include_relocation_recommendations": True,
            "officer_notes": "District Emergency Operations Centre review.",
        }
        res = client.post("/api/v1/admin/export-report", json=payload, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]
        assert "attachment; filename=" in res.headers["content-disposition"]
        csv_text = res.text
        assert "NATIONAL DISASTER MANAGEMENT PLATFORM" in csv_text
        assert "KEY PERFORMANCE INDICATORS" in csv_text
        assert "VULNERABLE HABITATIONS & RELOCATION RECOMMENDATIONS" in csv_text
        assert "COMPLIANCE NOTICE" in csv_text


def test_audit_log_captures_all_events():
    """Verify that user actions have populated the audit log."""
    logs, total = AuditService.get_logs(page=1, page_size=50)
    assert total >= 5
    actions = [log["action"] for log in logs]
    assert "LOGIN_SUCCESS" in actions
    assert "ADD_DEMO_HABITATION" in actions
    assert "EXPORT_REPORT" in actions
