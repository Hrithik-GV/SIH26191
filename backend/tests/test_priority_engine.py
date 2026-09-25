"""Unit tests for Relocation Prioritization Engine and Decision Support APIs."""

import uuid
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.priority_config import (
    RelocationPriorityThresholds,
    RelocationPriorityWeightConfig,
    default_priority_weights,
    DECISION_SUPPORT_DISCLAIMER,
)
from backend.app.services.priority_engine import (
    eval_exposed_population_factor,
    eval_disaster_history_factor,
    rank_and_select_best_relocation_site,
    generate_priority_reasons,
    calculate_relocation_priority,
)
from backend.app.db.session import get_db

client = TestClient(app)


def test_priority_threshold_brackets():
    """Verify exact prototype threshold classification brackets."""
    # 81-100 = IMMEDIATE
    assert RelocationPriorityThresholds.get_priority(81) == "IMMEDIATE"
    assert RelocationPriorityThresholds.get_priority(89) == "IMMEDIATE"
    assert RelocationPriorityThresholds.get_priority(100) == "IMMEDIATE"

    # 61-80 = SHORT_TERM
    assert RelocationPriorityThresholds.get_priority(61) == "SHORT_TERM"
    assert RelocationPriorityThresholds.get_priority(75) == "SHORT_TERM"
    assert RelocationPriorityThresholds.get_priority(80) == "SHORT_TERM"

    # 31-60 = MEDIUM_TERM
    assert RelocationPriorityThresholds.get_priority(31) == "MEDIUM_TERM"
    assert RelocationPriorityThresholds.get_priority(45) == "MEDIUM_TERM"
    assert RelocationPriorityThresholds.get_priority(60) == "MEDIUM_TERM"

    # 0-30 = MONITOR
    assert RelocationPriorityThresholds.get_priority(0) == "MONITOR"
    assert RelocationPriorityThresholds.get_priority(15) == "MONITOR"
    assert RelocationPriorityThresholds.get_priority(30) == "MONITOR"


def test_default_priority_weights_validation():
    """Verify that all 7 factor weights sum strictly to 1.0 (100%)."""
    assert default_priority_weights.validate_weights() is True
    total = (
        default_priority_weights.hazard_risk
        + default_priority_weights.population_vulnerability
        + default_priority_weights.exposed_population
        + default_priority_weights.disaster_history
        + default_priority_weights.infrastructure_vulnerability
        + default_priority_weights.evacuation_difficulty
        + default_priority_weights.site_availability
    )
    assert total == pytest.approx(1.0, abs=1e-5)


def test_exposed_population_factor():
    """Verify population scale scoring across varying settlement sizes."""
    assert eval_exposed_population_factor(2000) == 100
    assert eval_exposed_population_factor(1200) == 85
    assert eval_exposed_population_factor(750) == 70
    assert eval_exposed_population_factor(350) == 55
    assert eval_exposed_population_factor(80) == 40
    assert eval_exposed_population_factor(20) == 25


def test_disaster_history_factor():
    """Verify disaster recurrence scoring."""
    assert eval_disaster_history_factor(4) == 100
    assert eval_disaster_history_factor(3) == 100
    assert eval_disaster_history_factor(2) == 80
    assert eval_disaster_history_factor(1) == 60
    assert eval_disaster_history_factor(0) == 25


def test_rank_and_select_best_relocation_site():
    """Verify spatial multi-criteria ranking (proximity + suitability + capacity)."""
    site_near = {
        "site_id": uuid.uuid4(),
        "site_name": "Nearby Safe Plateau",
        "distance_km": 4.5,
        "suitability_score": 88,
        "available_capacity": 2000,
        "classification": "HIGHLY SUITABLE",
    }
    site_far = {
        "site_id": uuid.uuid4(),
        "site_name": "Distant Municipal Reserve",
        "distance_km": 28.0,
        "suitability_score": 92,
        "available_capacity": 3000,
        "classification": "HIGHLY SUITABLE",
    }
    site_small = {
        "site_id": uuid.uuid4(),
        "site_name": "Small Constrained Parcel",
        "distance_km": 5.0,
        "suitability_score": 65,
        "available_capacity": 150,  # Insufficient for 1000 vulnerable pop
        "classification": "SUITABLE",
    }

    best, alts = rank_and_select_best_relocation_site([site_far, site_near, site_small], vulnerable_population=1000)

    assert best is not None
    assert best["site_name"] == "Nearby Safe Plateau"
    assert best["capacity_sufficient"] is True
    assert best["match_score"] > site_far["suitability_score"] * 0.35
    assert len(alts) == 2


def test_calculate_relocation_priority_immediate():
    """Verify critical settlement produces IMMEDIATE classification and required reasons."""
    metrics = {
        "hazard_risk": 90,
        "population_vulnerability": 88,
        "vulnerable_population": 1600,
        "disaster_events_count": 2,
        "infrastructure_vulnerability": 75,
        "evacuation_difficulty": 85,
    }

    candidate_site = {
        "site_id": uuid.uuid4(),
        "site_name": "Meppadi Tableland",
        "distance_km": 3.8,
        "suitability_score": 86,
        "available_capacity": 2200,
    }

    result = calculate_relocation_priority(metrics, candidate_sites=[candidate_site])

    assert result["priority_score"] >= 81
    assert result["priority"] == "IMMEDIATE"
    assert result["best_suitable_site"] is not None
    assert result["best_suitable_site"]["site_name"] == "Meppadi Tableland"

    # Check reasons
    reasons = result["reasons"]
    assert any("hazard" in r.lower() for r in reasons)
    assert any("vulnerable population" in r.lower() for r in reasons)
    assert any("evacuation" in r.lower() for r in reasons)
    assert any("relocation site" in r.lower() for r in reasons)

    # Check decision support disclaimer
    assert "decision_support_disclaimer" in result
    assert "decision-support" in result["decision_support_disclaimer"].lower()
    assert "NDMA" in result["decision_support_disclaimer"]


def test_calculate_relocation_priority_monitor():
    """Verify resilient low-risk settlement produces MONITOR tier."""
    metrics = {
        "hazard_risk": 20,
        "population_vulnerability": 25,
        "vulnerable_population": 40,
        "disaster_events_count": 0,
        "infrastructure_vulnerability": 25,
        "evacuation_difficulty": 20,
    }

    result = calculate_relocation_priority(metrics, candidate_sites=[])

    assert result["priority_score"] <= 30
    assert result["priority"] == "MONITOR"


def test_decision_support_disclaimer_governance():
    """Verify platform explicitly preserves human administrative authority."""
    assert "NOT make" in DECISION_SUPPORT_DISCLAIMER or "does NOT" in DECISION_SUPPORT_DISCLAIMER
    assert "authorized" in DECISION_SUPPORT_DISCLAIMER.lower()


# ============================================================================
# FastAPI Endpoint Integration Tests
# ============================================================================

def test_fastapi_relocation_priorities_summary_offline_or_online():
    """Test GET /api/relocation/priorities returns 200 or 503 when DB offline."""
    for path in ["/api/relocation/priorities", "/api/v1/relocation/priorities"]:
        response = client.get(path)
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "total_habitations" in data
            assert "immediate_count" in data
            assert "priorities" in data
            assert "decision_support_disclaimer" in data


def test_fastapi_habitation_priority_not_found():
    """Test GET /api/relocation/priorities/{id} returns 404 or 503 when DB offline."""
    fake_id = str(uuid.uuid4())
    for prefix in ["/api/relocation/priorities", "/api/v1/relocation/priorities"]:
        response = client.get(f"{prefix}/{fake_id}")
        assert response.status_code in [404, 503]


def test_fastapi_habitation_priority_mocked():
    """Verify single habitation priority calculation with mock DB."""
    mock_hab_id = uuid.uuid4()
    mock_db = MagicMock()

    hab_row = {
        "id": mock_hab_id,
        "name": "Mundakkai Hamlet",
        "district": "Wayanad",
        "state": "Kerala",
        "population": 2200,
        "vulnerable_population": 1450,
        "cnt": 2,
        "geojson": '{"type": "Polygon", "coordinates": [[[76.13, 11.54], [76.15, 11.54], [76.15, 11.56], [76.13, 11.56], [76.13, 11.54]]]}',
    }

    mock_db.execute.return_value.mappings.return_value.first.return_value = hab_row

    with patch("backend.app.services.priority_engine.compute_habitation_risk_from_db") as mock_risk, \
         patch("backend.app.services.priority_engine.compute_habitation_vulnerability_from_db") as mock_vuln, \
         patch("backend.app.services.priority_engine.find_suitable_nearby_sites_for_habitation") as mock_sites:

        mock_risk.return_value = {"overall_score": 92}
        mock_vuln.return_value = {
            "vulnerability_score": 86,
            "factors": {"housing": 75, "evacuation_accessibility": 85},
        }
        mock_sites.return_value = {
            "recommended_sites": [
                {
                    "site_id": uuid.uuid4(),
                    "site_name": "Meppadi Green Plateau",
                    "distance_km": 4.2,
                    "distance_meters": 4200.0,
                    "suitability_score": 88,
                    "available_capacity": 2100,
                    "classification": "HIGHLY SUITABLE",
                }
            ]
        }

        app.dependency_overrides[get_db] = lambda: mock_db
        try:
            response = client.get(f"/api/relocation/priorities/{mock_hab_id}")
            assert response.status_code == 200
            data = response.json()

            assert data["habitation_name"] == "Mundakkai Hamlet"
            assert data["priority_score"] >= 81
            assert data["priority"] == "IMMEDIATE"
            assert "factors" in data
            assert len(data["reasons"]) >= 2
            assert data["recommended_site"] is not None
            assert data["recommended_site"]["site_name"] == "Meppadi Green Plateau"
            assert "decision_support_disclaimer" in data
        finally:
            app.dependency_overrides.pop(get_db, None)


def test_fastapi_habitation_recommendation_mocked():
    """Verify complete relocation recommendation with best suitable site and alternatives."""
    mock_hab_id = uuid.uuid4()
    mock_db = MagicMock()

    hab_row = {
        "id": mock_hab_id,
        "name": "Chooralmala Riverside",
        "district": "Wayanad",
        "state": "Kerala",
        "population": 1800,
        "vulnerable_population": 1200,
        "cnt": 2,
        "geojson": '{"type": "Polygon", "coordinates": [[[76.15, 11.52], [76.17, 11.52], [76.17, 11.54], [76.15, 11.54], [76.15, 11.52]]]}',
    }

    mock_db.execute.return_value.mappings.return_value.first.return_value = hab_row

    with patch("backend.app.services.priority_engine.compute_habitation_risk_from_db") as mock_risk, \
         patch("backend.app.services.priority_engine.compute_habitation_vulnerability_from_db") as mock_vuln, \
         patch("backend.app.services.priority_engine.find_suitable_nearby_sites_for_habitation") as mock_sites:

        mock_risk.return_value = {"overall_score": 88}
        mock_vuln.return_value = {
            "vulnerability_score": 80,
            "factors": {"housing": 70, "evacuation_accessibility": 78},
        }
        mock_sites.return_value = {
            "recommended_sites": [
                {
                    "site_id": uuid.uuid4(),
                    "site_name": "Kalpetta South Ridge",
                    "distance_km": 5.5,
                    "distance_meters": 5500.0,
                    "suitability_score": 85,
                    "available_capacity": 1500,
                    "classification": "HIGHLY SUITABLE",
                },
                {
                    "site_id": uuid.uuid4(),
                    "site_name": "Vythiri Safe Uplands",
                    "distance_km": 14.0,
                    "distance_meters": 14000.0,
                    "suitability_score": 80,
                    "available_capacity": 900,
                    "classification": "SUITABLE",
                },
            ]
        }

        app.dependency_overrides[get_db] = lambda: mock_db
        try:
            response = client.get(f"/api/relocation/recommendation/{mock_hab_id}")
            assert response.status_code == 200
            data = response.json()

            assert data["habitation_name"] == "Chooralmala Riverside"
            assert data["priority"] in ["IMMEDIATE", "SHORT_TERM"]
            assert data["best_suitable_site"] is not None
            assert data["best_suitable_site"]["site_name"] == "Kalpetta South Ridge"
            assert data["best_suitable_site"]["distance_km"] == 5.5
            assert data["best_suitable_site"]["capacity_sufficient"] is True
            assert len(data["alternative_sites"]) == 1
            assert data["alternative_sites"][0]["site_name"] == "Vythiri Safe Uplands"
            assert "decision_support_disclaimer" in data
        finally:
            app.dependency_overrides.pop(get_db, None)
