import uuid
from datetime import datetime, timezone
from geoalchemy2.elements import WKTElement

from backend.app.models.habitation import Habitation
from backend.app.models.hazard_zone import HazardZone
from backend.app.models.observation import RainfallObservation, RiverObservation
from backend.app.models.disaster_event import DisasterEvent
from backend.app.models.relocation import RelocationSite, RelocationRecommendation
from backend.app.db.seeds import (
    ID_HAB_MUNDAKKAI,
    ID_HAB_CHOORALMALA,
    ID_SITE_MEPPADI_PLATEAU,
)


def test_habitation_model_instantiation():
    """Verify Habitation model correctly accepts WKT polygon and population attributes."""
    hab = Habitation(
        id=ID_HAB_MUNDAKKAI,
        name="Mundakkai Settlement",
        district="Wayanad",
        state="Kerala",
        population=2180,
        vulnerable_population=1450,
        geometry=WKTElement("POLYGON((76.130 11.545, 76.142 11.545, 76.142 11.556, 76.130 11.556, 76.130 11.545))", srid=4326),
    )
    assert hab.name == "Mundakkai Settlement"
    assert hab.district == "Wayanad"
    assert hab.population == 2180
    assert hab.vulnerable_population == 1450
    assert hab.geometry.srid == 4326
    assert "Mundakkai" in repr(hab)


def test_hazard_zone_model_instantiation():
    """Verify HazardZone model with risk score and severity."""
    now = datetime.now(timezone.utc)
    zone = HazardZone(
        id=uuid.uuid4(),
        hazard_type="landslide",
        risk_score=0.94,
        severity="VERY_HIGH",
        source="GSI_ISRO_BHUVAN",
        timestamp=now,
        geometry=WKTElement("POLYGON((76.125 11.540, 76.148 11.540, 76.148 11.565, 76.125 11.565, 76.125 11.540))", srid=4326),
    )
    assert zone.hazard_type == "landslide"
    assert zone.risk_score == 0.94
    assert zone.severity == "VERY_HIGH"
    assert zone.source == "GSI_ISRO_BHUVAN"


def test_observation_models():
    """Verify RainfallObservation and RiverObservation models."""
    now = datetime.now(timezone.utc)
    rain = RainfallObservation(
        id=uuid.uuid4(),
        latitude=11.552,
        longitude=76.135,
        rainfall_mm=382.5,
        observation_time=now,
        source="IMD_AWS_MUNDAKKAI_PEAK",
        geometry=WKTElement("POINT(76.135 11.552)", srid=4326),
    )
    assert rain.rainfall_mm == 382.5
    assert rain.latitude == 11.552

    river = RiverObservation(
        id=uuid.uuid4(),
        station_name="Iruvanjippuzha - Chooralmala Bridge",
        water_level=8.65,
        danger_level=6.50,
        observation_time=now,
        geometry=WKTElement("POINT(76.152 11.536)", srid=4326),
    )
    assert river.water_level == 8.65
    assert river.danger_level == 6.50
    assert river.water_level > river.danger_level


def test_disaster_event_model():
    """Verify DisasterEvent model."""
    event = DisasterEvent(
        id=uuid.uuid4(),
        disaster_type="landslide",
        severity="CRITICAL",
        event_time=datetime.now(timezone.utc),
        source="KSDMA_EMERGENCY_OPS",
        geometry=WKTElement("POINT(76.132 11.546)", srid=4326),
    )
    assert event.disaster_type == "landslide"
    assert event.severity == "CRITICAL"


def test_relocation_site_and_recommendation_models():
    """Verify RelocationSite capacity parameters and Recommendation linkages."""
    site = RelocationSite(
        id=ID_SITE_MEPPADI_PLATEAU,
        name="Meppadi Plateau Safe Rehabilitation Zone A",
        available_area=45000.0,
        current_population=150,
        estimated_capacity=2500,
        available_capacity=2350,
        water_score=8.8,
        road_access_score=9.2,
        healthcare_score=8.5,
        hazard_score=0.05,
        suitability_score=9.1,
        geometry=WKTElement("POLYGON((76.090 11.545, 76.105 11.545, 76.105 11.558, 76.090 11.558, 76.090 11.545))", srid=4326),
    )
    assert site.estimated_capacity == 2500
    assert site.available_capacity == 2350
    assert site.suitability_score == 9.1

    rec = RelocationRecommendation(
        id=uuid.uuid4(),
        habitation_id=ID_HAB_MUNDAKKAI,
        relocation_site_id=site.id,
        priority="CRITICAL",
        priority_score=96.5,
        reason="Extreme landslide hazard overlap",
        created_at=datetime.now(timezone.utc),
    )
    assert rec.priority == "CRITICAL"
    assert rec.priority_score == 96.5
    assert rec.habitation_id == ID_HAB_MUNDAKKAI
    assert rec.relocation_site_id == site.id
