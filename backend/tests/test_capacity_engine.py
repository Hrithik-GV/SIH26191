"""Unit tests for Relocation-Site Carrying Capacity Assessment Engine and API."""

import uuid
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.capacity_config import (
    CapacityNormsConfig,
    default_capacity_norms,
    PROTOTYPE_CAPACITY_ASSUMPTIONS,
)
from backend.app.services.capacity_engine import (
    calculate_gross_land_capacity,
    calculate_water_capacity,
    calculate_sanitation_capacity,
    calculate_healthcare_capacity,
    calculate_electricity_capacity,
    calculate_road_access_capacity,
    evaluate_site_carrying_capacity,
)
from backend.app.db.session import get_db

client = TestClient(app)


def test_gross_land_capacity_calculation():
    """Verify gross land capacity adheres to 35 sqm/person and 75% usable area norms."""
    # 70,000 sqm parcel, flat/gentle slope (5 deg)
    # Net usable area: 70,000 * 0.75 = 52,500 sqm
    # Gross capacity: 52,500 / 35 = 1,500 persons
    gross_cap, usable_area = calculate_gross_land_capacity(
        available_area_sqm=70000.0,
        slope_degrees=5.0,
        usable_area_ratio=0.75,
        sqm_per_person_norm=35.0,
    )
    assert gross_cap == 1500
    assert usable_area == pytest.approx(52500.0, abs=0.1)


def test_gross_land_capacity_slope_penalty():
    """Verify that steep terrain penalizes buildable area efficiency."""
    area = 100000.0
    cap_gentle, area_gentle = calculate_gross_land_capacity(area, slope_degrees=6.0)
    cap_steep, area_steep = calculate_gross_land_capacity(area, slope_degrees=22.0)

    assert cap_gentle > cap_steep
    assert area_gentle > area_steep
    # Steep slope (22 deg) must reduce buildable efficiency below 70%
    assert cap_steep < cap_gentle * 0.75


def test_water_capacity_calculation():
    """Verify water capacity strictly adheres to 70 LPCD benchmark."""
    # Explicit daily yield: 105,000 litres / 70 LPCD = 1,500 persons
    water_cap = calculate_water_capacity(
        gross_capacity=2000,
        water_score=8.5,
        daily_water_litres=105000.0,
        lpcd_norm=70.0,
    )
    assert water_cap == 1500

    # Score-based estimation when daily litres unmeasured
    # Excellent water (9.5/10) supports full gross capacity
    cap_high = calculate_water_capacity(gross_capacity=2000, water_score=9.5)
    assert cap_high == 2000

    # Poor water (4.0/10) severely bottlenecks capacity
    cap_low = calculate_water_capacity(gross_capacity=2000, water_score=4.0)
    assert cap_low <= 1000


def test_infrastructure_capacities_individual():
    """Verify individual civil utility capacity evaluations."""
    gross = 2000

    # Sanitation
    san_cap = calculate_sanitation_capacity(gross, sanitation_score=8.0)
    assert 1400 <= san_cap <= 2000

    # Healthcare (delayed distance attenuates surge capacity)
    hosp_near = calculate_healthcare_capacity(gross, healthcare_score=8.5, distance_to_hospital_km=2.0)
    hosp_far = calculate_healthcare_capacity(gross, healthcare_score=8.5, distance_to_hospital_km=16.0)
    assert hosp_near > hosp_far

    # Electricity
    elec_cap = calculate_electricity_capacity(gross, electricity_score=9.0)
    assert elec_cap == 2000

    # Road access
    road_cap = calculate_road_access_capacity(gross, road_access_score=8.5)
    assert road_cap == 2000


def test_multi_pillar_bottleneck_evaluation_matching_spec():
    """Verify exact evaluation output matching the prompt's carrying capacity specification."""
    # Input with limiting factors: gross=2000, infra=1600, water=1500, current=700
    site_input = {
        "site_id": 1,
        "site_name": "Meppadi Tableland Site 1",
        "gross_capacity": 2000,
        "infrastructure_capacity": 1600,
        "water_capacity": 1500,
        "current_population": 700,
    }

    result = evaluate_site_carrying_capacity(site_input)

    # Output matches required fields
    assert result["site_id"] == 1
    assert result["gross_capacity"] == 2000
    assert result["infrastructure_capacity"] == 1600
    assert result["water_capacity"] == 1500
    assert result["final_capacity"] == 1500
    assert result["current_population"] == 700
    assert result["available_capacity"] == 800

    # Limiting factors identification
    assert isinstance(result["limiting_factors"], list)
    assert len(result["limiting_factors"]) >= 1
    assert any("water" in f.lower() for f in result["limiting_factors"])
    assert any("1,500" in f or "1500" in f for f in result["limiting_factors"])


def test_limiting_factors_unconstrained_site():
    """Verify parcel where all civil utilities match or exceed gross land capacity."""
    site_input = {
        "site_id": 2,
        "available_area": 95000.0,
        "slope_degrees": 4.0,
        "water_score": 9.5,
        "healthcare_score": 9.2,
        "sanitation_score": 9.0,
        "road_access_score": 9.5,
        "electricity_score": 9.0,
        "current_population": 200,
    }

    result = evaluate_site_carrying_capacity(site_input)

    assert result["final_capacity"] == result["gross_capacity"]
    assert result["available_capacity"] == result["final_capacity"] - 200
    # No limiting bottlenecks restricting below land area
    assert result["water_capacity"] >= result["final_capacity"]
    assert result["infrastructure_capacity"] >= result["final_capacity"]


def test_prototype_assumptions_labeled():
    """Verify explicit labeling of prototype assumptions in engine output."""
    site_input = {
        "site_id": 12,
        "available_area": 45000.0,
        "water_score": 8.0,
        "road_access_score": 8.0,
        "healthcare_score": 8.0,
    }

    result = evaluate_site_carrying_capacity(site_input)

    assert "assumptions" in result
    assumptions = result["assumptions"]
    assert "spatial_density_standard" in assumptions
    assert "water_consumption_norm" in assumptions
    assert "capacity_model" in assumptions
    assert "Liebig's Law" in assumptions["capacity_model"]


# ============================================================================
# FastAPI Endpoint Integration Tests
# ============================================================================

def test_fastapi_site_capacity_not_found():
    """Test GET /api/relocation-sites/{id}/capacity returns 404 or 503 when DB offline."""
    fake_id = str(uuid.uuid4())
    for prefix in ["/api/relocation-sites", "/api/v1/relocation-sites"]:
        response = client.get(f"{prefix}/{fake_id}/capacity")
        assert response.status_code in [404, 503]


def test_fastapi_site_capacity_endpoint_mocked():
    """Verify endpoint schema validation with mock DB response."""
    mock_site_id = uuid.uuid4()
    mock_db = MagicMock()

    mock_row = {
        "id": mock_site_id,
        "name": "Meppadi Green Plateau Zone A",
        "available_area": 93333.3,  # Net usable ~70,000 sqm -> Gross ~2000
        "current_population": 700,
        "estimated_capacity": 2000,
        "available_capacity": 800,
        "water_score": 7.5,         # Bottleneck to ~1500
        "road_access_score": 8.0,
        "healthcare_score": 8.0,    # Bottleneck to ~1600
        "hazard_score": 1.0,
        "suitability_score": 85.0,
    }
    mock_db.execute.return_value.mappings.return_value.first.return_value = mock_row

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        response = client.get(f"/api/relocation-sites/{mock_site_id}/capacity")
        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert data["site_name"] == "Meppadi Green Plateau Zone A"
        assert "gross_capacity" in data
        assert "infrastructure_capacity" in data
        assert "water_capacity" in data
        assert "final_capacity" in data
        assert data["current_population"] == 700
        assert data["available_capacity"] == data["final_capacity"] - 700
        assert isinstance(data["limiting_factors"], list)
        assert "factor_capacities" in data
        assert "assumptions" in data
        assert data["assumptions"]["water_consumption_norm"] != ""
    finally:
        app.dependency_overrides.pop(get_db, None)
