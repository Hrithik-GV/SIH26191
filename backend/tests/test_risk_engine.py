import uuid
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.risk_config import RiskClassificationThresholds, default_risk_weights
from backend.app.services.risk_engine import (
    calculate_composite_risk,
    eval_rainfall_factor,
    eval_flood_factor,
    eval_landslide_factor,
    eval_elevation_slope_factor,
    eval_historical_events_factor,
    eval_drainage_proximity_factor,
    eval_hazard_overlap_factor,
    generate_risk_explanations,
)

client = TestClient(app)


def test_risk_threshold_classification():
    """Verify exact prototype threshold classification brackets."""
    assert RiskClassificationThresholds.get_severity(0) == "LOW"
    assert RiskClassificationThresholds.get_severity(15) == "LOW"
    assert RiskClassificationThresholds.get_severity(30) == "LOW"
    
    assert RiskClassificationThresholds.get_severity(31) == "MODERATE"
    assert RiskClassificationThresholds.get_severity(45) == "MODERATE"
    assert RiskClassificationThresholds.get_severity(60) == "MODERATE"
    
    assert RiskClassificationThresholds.get_severity(61) == "HIGH"
    assert RiskClassificationThresholds.get_severity(70) == "HIGH"
    assert RiskClassificationThresholds.get_severity(80) == "HIGH"
    
    assert RiskClassificationThresholds.get_severity(81) == "CRITICAL"
    assert RiskClassificationThresholds.get_severity(95) == "CRITICAL"
    assert RiskClassificationThresholds.get_severity(100) == "CRITICAL"


def test_default_risk_weights_validation():
    """Verify risk weights are valid, transparent, and sum precisely to 1.0 (100%)."""
    assert default_risk_weights.validate_weights() is True
    assert default_risk_weights.rainfall_intensity == 0.20
    assert default_risk_weights.hazard_zone_overlap == 0.20
    assert default_risk_weights.landslide_susceptibility == 0.15
    assert default_risk_weights.flood_exposure == 0.15
    assert default_risk_weights.elevation_slope == 0.10
    assert default_risk_weights.distance_to_rivers_drainage == 0.10
    assert default_risk_weights.historical_disaster_frequency == 0.10


def test_factor_evaluation_functions():
    """Verify individual risk factor scaling from real-world telemetry."""
    # Rainfall: 382mm cloudburst should be >= 90; 25mm should be low <= 30
    assert eval_rainfall_factor(382.5) >= 90
    assert eval_rainfall_factor(25.0) <= 30

    # Flood: Water level 8.65m vs danger 6.50m (exceedance 2.15m) should be critical
    assert eval_flood_factor(water_level=8.65, danger_level=6.50) >= 85
    assert eval_flood_factor(water_level=2.0, danger_level=5.0) <= 25

    # Landslide: VERY_HIGH zone should score >= 85
    assert eval_landslide_factor(intersects_landslide_zone=True, max_severity="VERY_HIGH", overlap_pct=80.0) >= 85
    assert eval_landslide_factor(intersects_landslide_zone=False) <= 20

    # Slope: Steep slope 32° should score >= 70; flat slope 8° should score <= 30
    assert eval_elevation_slope_factor(slope_degrees=32.0) >= 70
    assert eval_elevation_slope_factor(slope_degrees=8.0) <= 30

    # Historical Events: Multiple critical events should score >= 80
    assert eval_historical_events_factor(event_count=3, has_critical_events=True) >= 80
    assert eval_historical_events_factor(event_count=0) <= 20

    # Drainage proximity: 100m from river should score >= 90; 2000m should score <= 25
    assert eval_drainage_proximity_factor(distance_meters=100.0) >= 90
    assert eval_drainage_proximity_factor(distance_meters=2000.0) <= 25

    # Hazard Overlap: 90% overlap should score >= 90; 0% overlap should score 0
    assert eval_hazard_overlap_factor(total_overlap_pct=90.0) >= 90
    assert eval_hazard_overlap_factor(total_overlap_pct=0.0) == 0


def test_composite_risk_calculation_output_structure():
    """Verify composite risk calculation provides transparent factors and explanations."""
    factors = {
        "rainfall": 95,
        "flood_exposure": 86,
        "landslide": 76,
        "elevation_slope": 68,
        "historical_events": 70,
        "drainage_proximity": 78,
        "hazard_overlap": 90,
    }
    details = {
        "rainfall_mm": 320.0,
        "overlap_percentage": 90.0,
        "river_danger_exceedance_m": 1.8,
        "historical_event_count": 2,
        "distance_to_river_m": 180.0,
    }

    result = calculate_composite_risk(factors, details)

    assert "overall_score" in result
    assert isinstance(result["overall_score"], int)
    assert 81 <= result["overall_score"] <= 100
    assert result["severity"] == "CRITICAL"
    assert "factors" in result
    assert result["factors"]["rainfall"] == 95
    assert result["factors"]["flood_exposure"] == 86
    assert result["factors"]["landslide"] == 76
    assert result["factors"]["historical_events"] == 70

    assert "explanation" in result
    assert isinstance(result["explanation"], list)
    assert len(result["explanation"]) >= 3
    # Check that key explanations are present
    assert any("rainfall" in exp.lower() for exp in result["explanation"])
    assert any("flood" in exp.lower() for exp in result["explanation"])


def test_low_risk_composite_calculation():
    """Verify low risk factors result in LOW classification."""
    factors = {
        "rainfall": 15,
        "flood_exposure": 15,
        "landslide": 15,
        "elevation_slope": 15,
        "historical_events": 15,
        "drainage_proximity": 15,
        "hazard_overlap": 0,
    }
    result = calculate_composite_risk(factors)
    assert result["overall_score"] <= 30
    assert result["severity"] == "LOW"


def test_fastapi_hazards_endpoint():
    """Verify GET /api/hazards and /api/v1/hazards endpoints work."""
    for path in ["/api/hazards", "/api/v1/hazards"]:
        response = client.get(path)
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


def test_fastapi_hazard_by_id_not_found():
    """Verify GET /api/hazards/{id} and /api/v1/hazards/{id} handle non-existent UUID with 404."""
    random_id = uuid.uuid4()
    for prefix in ["/api/hazards", "/api/v1/hazards"]:
        response = client.get(f"{prefix}/{random_id}")
        assert response.status_code in [404, 503]


def test_fastapi_habitation_risk_not_found():
    """Verify GET /api/habitations/{id}/risk handles non-existent UUID."""
    random_id = uuid.uuid4()
    for prefix in ["/api/habitations", "/api/v1/habitations"]:
        response = client.get(f"{prefix}/{random_id}/risk")
        assert response.status_code in [404, 503]


def test_fastapi_risk_summary_endpoint():
    """Verify GET /api/risk/summary and /api/v1/risk/summary endpoint structure."""
    for path in ["/api/risk/summary", "/api/v1/risk/summary"]:
        response = client.get(path)
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "total_habitations" in data
            assert "severity_breakdown" in data
            assert "average_risk_score" in data
