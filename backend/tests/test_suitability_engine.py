"""Unit tests for Relocation-Site Suitability Assessment Engine and APIs."""

import uuid
import json
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.suitability_config import (
    SuitabilityClassificationThresholds,
    CategoryWeightConfig,
    default_category_weights,
)
from backend.app.services.suitability_engine import (
    calculate_site_suitability,
    calculate_category_scores,
    extract_strengths_and_limitations,
    eval_flood_risk_factor,
    eval_landslide_risk_factor,
    eval_slope_factor,
    eval_elevation_factor,
    eval_available_land_factor,
    eval_carrying_capacity_buffer,
    eval_distance_to_hospital_factor,
    eval_distance_to_school_factor,
    eval_water_availability_factor,
    eval_electricity_infrastructure_factor,
    eval_road_accessibility_factor,
)
from backend.app.db.session import get_db

client = TestClient(app)


def test_suitability_threshold_brackets():
    """Verify exact prototype threshold classification brackets."""
    # 80-100 = HIGHLY SUITABLE
    assert SuitabilityClassificationThresholds.get_classification(80) == "HIGHLY SUITABLE"
    assert SuitabilityClassificationThresholds.get_classification(86) == "HIGHLY SUITABLE"
    assert SuitabilityClassificationThresholds.get_classification(100) == "HIGHLY SUITABLE"

    # 60-79 = SUITABLE
    assert SuitabilityClassificationThresholds.get_classification(60) == "SUITABLE"
    assert SuitabilityClassificationThresholds.get_classification(70) == "SUITABLE"
    assert SuitabilityClassificationThresholds.get_classification(79) == "SUITABLE"

    # 40-59 = CONDITIONALLY SUITABLE
    assert SuitabilityClassificationThresholds.get_classification(40) == "CONDITIONALLY SUITABLE"
    assert SuitabilityClassificationThresholds.get_classification(50) == "CONDITIONALLY SUITABLE"
    assert SuitabilityClassificationThresholds.get_classification(59) == "CONDITIONALLY SUITABLE"

    # 0-39 = UNSUITABLE
    assert SuitabilityClassificationThresholds.get_classification(0) == "UNSUITABLE"
    assert SuitabilityClassificationThresholds.get_classification(20) == "UNSUITABLE"
    assert SuitabilityClassificationThresholds.get_classification(39) == "UNSUITABLE"


def test_default_category_weights():
    """Verify category weights sum strictly to 1.0 (100%)."""
    assert default_category_weights.validate_weights() is True
    total = (
        default_category_weights.hazard_safety
        + default_category_weights.infrastructure
        + default_category_weights.accessibility
        + default_category_weights.capacity
    )
    assert total == pytest.approx(1.0, abs=1e-5)


def test_factor_evaluations():
    """Verify discrete factor scoring behavior across civil and environmental metrics."""
    # Flood risk (0% -> 100 safe, 100% -> 0 safe)
    assert eval_flood_risk_factor(0.0) == 100
    assert eval_flood_risk_factor(80.0) == 20
    assert eval_flood_risk_factor(100.0) == 0

    # Landslide risk
    assert eval_landslide_risk_factor(0.0) == 100
    assert eval_landslide_risk_factor(100.0) == 0

    # Slope
    assert eval_slope_factor(3.0) == 95
    assert eval_slope_factor(8.0) == 95
    assert eval_slope_factor(16.0) >= 55
    assert eval_slope_factor(35.0) <= 20

    # Elevation
    assert eval_elevation_factor(750.0) == 95
    assert eval_elevation_factor(250.0) == 85
    assert eval_elevation_factor(5.0) == 15

    # Available land
    assert eval_available_land_factor(160000.0) == 95
    assert eval_available_land_factor(5000.0) <= 25

    # Carrying capacity buffer
    assert eval_carrying_capacity_buffer(1500, 1500) == 100
    assert eval_carrying_capacity_buffer(500, 1000) == 50

    # Hospital distance
    assert eval_distance_to_hospital_factor(1.5) == 100
    assert eval_distance_to_hospital_factor(4.0) == 86
    assert eval_distance_to_hospital_factor(16.0) <= 40

    # School distance
    assert eval_distance_to_school_factor(1.0) == 100
    assert eval_distance_to_school_factor(3.0) == 79
    assert eval_distance_to_school_factor(12.0) <= 40

    # Baseline scores (0-10) scaled to 0-100
    assert eval_water_availability_factor(9.0) == 90
    assert eval_electricity_infrastructure_factor(8.5) == 85
    assert eval_road_accessibility_factor(8.0) == 80


def test_calculate_site_suitability_ideal_site():
    """Verify high suitability parcel produces HIGHLY SUITABLE with all separate scores."""
    site_data = {
        "id": uuid.uuid4(),
        "name": "Hillside Safe Haven",
        "flood_risk_pct": 0.0,
        "landslide_susceptibility_pct": 5.0,
        "slope_degrees": 4.5,
        "elevation_meters": 220.0,
        "available_area": 120000.0,
        "road_access_score": 9.0,
        "distance_to_hospital_km": 2.5,
        "distance_to_school_km": 1.8,
        "water_score": 9.0,
        "electricity_score": 8.5,
        "current_population": 50,
        "estimated_capacity": 1500,
        "available_capacity": 1450,
    }

    result = calculate_site_suitability(site_data)

    # Required individual scores
    assert "hazard_safety_score" in result
    assert "accessibility_score" in result
    assert "infrastructure_score" in result
    assert "capacity_score" in result
    assert "overall_suitability_score" in result
    assert "suitability_score" in result

    assert result["suitability_score"] >= 80
    assert result["overall_suitability_score"] == result["suitability_score"]
    assert result["classification"] == "HIGHLY SUITABLE"
    assert result["hazard_safety_score"] >= 85
    assert result["accessibility_score"] >= 80
    assert result["infrastructure_score"] >= 80
    assert result["capacity_score"] >= 80

    # Explainability: strengths and limitations
    assert len(result["strengths"]) >= 2
    assert isinstance(result["limitations"], list)


def test_calculate_site_suitability_unsuitable_site():
    """Verify hazardous flood-prone steep site results in UNSUITABLE classification."""
    site_data = {
        "id": uuid.uuid4(),
        "name": "Hazardous Lowland Parcel",
        "flood_risk_pct": 85.0,
        "landslide_susceptibility_pct": 75.0,
        "slope_degrees": 28.0,
        "elevation_meters": 8.0,
        "available_area": 4000.0,
        "road_access_score": 2.0,
        "distance_to_hospital_km": 18.0,
        "distance_to_school_km": 14.0,
        "water_score": 2.0,
        "electricity_score": 1.5,
        "current_population": 480,
        "estimated_capacity": 500,
        "available_capacity": 20,
    }

    result = calculate_site_suitability(site_data)

    assert result["suitability_score"] <= 39
    assert result["classification"] == "UNSUITABLE"
    assert len(result["limitations"]) >= 2
    assert any("hazard" in lim.lower() for lim in result["limitations"])


def test_extract_strengths_and_limitations():
    """Test dynamic generation of explainable civic strengths and engineering limitations."""
    cat_scores = {
        "hazard_safety_score": 92,
        "accessibility_score": 40,
        "infrastructure_score": 55,
        "capacity_score": 85,
    }
    factors = {
        "water_availability": 45,
    }
    site_data = {
        "slope_degrees": 22.0,
        "distance_to_hospital_km": 12.5,
        "available_capacity": 1500,
    }

    strengths, limitations = extract_strengths_and_limitations(cat_scores, factors, site_data)

    assert any("buffer" in s.lower() or "hazard" in s.lower() for s in strengths)
    assert any("capacity" in s.lower() for s in strengths)
    assert any("slope" in l.lower() for l in limitations)
    assert any("accessibility" in l.lower() or "road" in l.lower() for l in limitations)
    assert any("water" in l.lower() for l in limitations)


# ============================================================================
# FastAPI Endpoint Integration Tests
# ============================================================================

def test_fastapi_relocation_sites_endpoint():
    """Test GET /api/relocation-sites returns HTTP 200 or 503 when DB offline."""
    for path in ["/api/relocation-sites", "/api/v1/relocation-sites"]:
        response = client.get(path)
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            sites = response.json()
            assert isinstance(sites, list)
            if sites:
                assert "available_area" in sites[0]
                assert "estimated_capacity" in sites[0]
                assert "geometry" in sites[0]


def test_fastapi_relocation_site_by_id_not_found():
    """Test GET /api/relocation-sites/{id} returns 404 or 503 when DB offline."""
    fake_id = str(uuid.uuid4())
    for prefix in ["/api/relocation-sites", "/api/v1/relocation-sites"]:
        response = client.get(f"{prefix}/{fake_id}")
        assert response.status_code in [404, 503]


def test_fastapi_site_assessment_mocked():
    """Verify complete explainable assessment output matching user requirements using mock DB."""
    mock_site_id = uuid.uuid4()
    mock_db = MagicMock()

    mock_row = {
        "id": mock_site_id,
        "name": "Meppadi Green Plateau",
        "available_area": 125000.0,
        "current_population": 40,
        "estimated_capacity": 2200,
        "available_capacity": 2160,
        "water_score": 9.0,
        "road_access_score": 8.5,
        "healthcare_score": 8.0,
        "hazard_score": 1.2,
        "suitability_score": 88.0,
        "geojson": '{"type": "Polygon", "coordinates": [[[76.12, 11.55], [76.14, 11.55], [76.14, 11.57], [76.12, 11.57], [76.12, 11.55]]]}',
    }
    mock_db.execute.return_value.mappings.return_value.first.return_value = mock_row

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.get(f"/api/relocation-sites/{mock_site_id}/assessment")
        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert data["site_name"] == "Meppadi Green Plateau"
        assert 0 <= data["suitability_score"] <= 100
        assert data["overall_suitability_score"] == data["suitability_score"]
        assert data["classification"] in ["HIGHLY SUITABLE", "SUITABLE"]

        # Category scores
        assert "hazard_safety_score" in data
        assert "accessibility_score" in data
        assert "infrastructure_score" in data
        assert "capacity_score" in data
        assert "category_scores" in data

        # Explainability
        assert isinstance(data["strengths"], list)
        assert len(data["strengths"]) > 0
        assert isinstance(data["limitations"], list)
        assert "factors" in data

        # GeoJSON
        assert data["geometry"]["type"] == "Polygon"
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_fastapi_nearby_relocation_sites_mocked():
    """Verify spatial query ranking nearby safe relocation sites near a habitation."""
    mock_hab_id = uuid.uuid4()
    mock_site_1 = uuid.uuid4()
    mock_site_2 = uuid.uuid4()

    mock_db = MagicMock()

    hab_row = {
        "id": mock_hab_id,
        "name": "Chooralmala Settlement",
        "vulnerable_population": 450,
        "geojson": '{"type": "Point", "coordinates": [76.15, 11.52]}',
    }

    site_rows = [
        {
            "site_id": mock_site_1,
            "site_name": "Meppadi Safe Plateau",
            "available_capacity": 1500,
            "suitability_score": 86.0,
            "distance_meters": 4200.5,
            "site_geojson": '{"type": "Polygon", "coordinates": [[[76.12, 11.55], [76.14, 11.55], [76.14, 11.57], [76.12, 11.57], [76.12, 11.55]]]}',
        },
        {
            "site_id": mock_site_2,
            "site_name": "Kalpetta South Ridge",
            "available_capacity": 900,
            "suitability_score": 78.0,
            "distance_meters": 8900.0,
            "site_geojson": '{"type": "Polygon", "coordinates": [[[76.08, 11.60], [76.10, 11.60], [76.10, 11.62], [76.08, 11.62], [76.08, 11.60]]]}',
        },
    ]

    # Configure mock responses for sequential queries
    mock_cursor_hab = MagicMock()
    mock_cursor_hab.mappings.return_value.first.return_value = hab_row

    mock_cursor_sites = MagicMock()
    mock_cursor_sites.mappings.return_value.all.return_value = site_rows

    mock_db.execute.side_effect = [mock_cursor_hab, mock_cursor_sites]

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.get(f"/api/relocation-sites/nearby/{mock_hab_id}?max_distance_km=15&limit=2")
        assert response.status_code == 200
        data = response.json()

        assert data["habitation_name"] == "Chooralmala Settlement"
        assert data["vulnerable_population"] == 450
        assert data["total_sites_found"] == 2
        assert len(data["recommended_sites"]) == 2

        first_site = data["recommended_sites"][0]
        assert first_site["site_name"] == "Meppadi Safe Plateau"
        assert first_site["distance_km"] == pytest.approx(4.2, abs=0.1)
        assert first_site["suitability_score"] == 86
        assert first_site["classification"] == "HIGHLY SUITABLE"
        assert first_site["hazard_safe"] is True
        assert first_site["proximity_rank"] == 1
    finally:
        app.dependency_overrides.pop(get_db, None)
