"""Demonstration seed data for SIH 2026 Problem Statement 26191.

Demonstration Region: Wayanad District, Kerala (Meppadi - Chooralmala - Mundakkai)
Coordinates: WGS84 (EPSG:4326)
"""

import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement

from backend.app.db.session import SessionLocal
from backend.app.core.logging import logger
from backend.app.models.habitation import Habitation
from backend.app.models.hazard_zone import HazardZone
from backend.app.models.observation import RainfallObservation, RiverObservation
from backend.app.models.disaster_event import DisasterEvent
from backend.app.models.relocation import RelocationSite, RelocationRecommendation


# Consistent deterministic UUIDs for seed reproducibility
ID_HAB_MUNDAKKAI = uuid.UUID("11111111-1111-4111-8111-111111111111")
ID_HAB_CHOORALMALA = uuid.UUID("22222222-2222-4222-8222-222222222222")
ID_HAB_ATTAMALA = uuid.UUID("33333333-3333-4333-8333-333333333333")
ID_HAB_MEPPADI = uuid.UUID("44444444-4444-4444-8444-444444444444")

ID_SITE_MEPPADI_PLATEAU = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
ID_SITE_KALPETTA_PARK = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
ID_SITE_VYTHIRI_UPLANDS = uuid.UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc")


def seed_database(db: Session = None) -> None:
    """Populate database with demonstration disaster management spatial data."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        logger.info("Starting demonstration database seeding...")

        # 1. Clean existing seed records if present
        db.query(RelocationRecommendation).delete()
        db.query(RelocationSite).delete()
        db.query(DisasterEvent).delete()
        db.query(RiverObservation).delete()
        db.query(RainfallObservation).delete()
        db.query(HazardZone).delete()
        db.query(Habitation).delete()
        db.commit()

        now = datetime.now(timezone.utc)

        # 2. Seed Habitations (WGS84 Polygons)
        habitations = [
            Habitation(
                id=ID_HAB_MUNDAKKAI,
                name="Mundakkai Settlement",
                district="Wayanad",
                state="Kerala",
                population=2180,
                vulnerable_population=1450,
                # Polygon covering upper tea estate settlement
                geometry=WKTElement(
                    "POLYGON((76.130 11.545, 76.142 11.545, 76.142 11.556, 76.130 11.556, 76.130 11.545))",
                    srid=4326,
                ),
            ),
            Habitation(
                id=ID_HAB_CHOORALMALA,
                name="Chooralmala Village",
                district="Wayanad",
                state="Kerala",
                population=3450,
                vulnerable_population=1820,
                # Polygon covering riverfront township and bridge market
                geometry=WKTElement(
                    "POLYGON((76.145 11.530, 76.160 11.530, 76.160 11.542, 76.145 11.542, 76.145 11.530))",
                    srid=4326,
                ),
            ),
            Habitation(
                id=ID_HAB_ATTAMALA,
                name="Attamala Habitation",
                district="Wayanad",
                state="Kerala",
                population=1120,
                vulnerable_population=780,
                # Polygon covering elevated ridge-line community
                geometry=WKTElement(
                    "POLYGON((76.120 11.520, 76.135 11.520, 76.135 11.532, 76.120 11.532, 76.120 11.520))",
                    srid=4326,
                ),
            ),
            Habitation(
                id=ID_HAB_MEPPADI,
                name="Meppadi Town Hub",
                district="Wayanad",
                state="Kerala",
                population=8900,
                vulnerable_population=2100,
                # Polygon covering lower valley commercial and residential transit zone
                geometry=WKTElement(
                    "POLYGON((76.110 11.540, 76.125 11.540, 76.125 11.555, 76.110 11.555, 76.110 11.540))",
                    srid=4326,
                ),
            ),
        ]
        db.add_all(habitations)
        db.flush()

        # 3. Seed Multi-Hazard Red Zones (WGS84 Polygons)
        hazard_zones = [
            HazardZone(
                id=uuid.uuid4(),
                hazard_type="landslide",
                risk_score=0.94,
                severity="VERY_HIGH",
                source="GSI_ISRO_BHUVAN",
                timestamp=now - timedelta(hours=2),
                # Overlaps Mundakkai & upper slopes
                geometry=WKTElement(
                    "POLYGON((76.125 11.540, 76.148 11.540, 76.148 11.565, 76.125 11.565, 76.125 11.540))",
                    srid=4326,
                ),
            ),
            HazardZone(
                id=uuid.uuid4(),
                hazard_type="flash_flood",
                risk_score=0.91,
                severity="VERY_HIGH",
                source="CWC_KSDMA",
                timestamp=now - timedelta(hours=1),
                # Overlaps Chooralmala river valley
                geometry=WKTElement(
                    "POLYGON((76.140 11.525, 76.168 11.525, 76.168 11.548, 76.140 11.548, 76.140 11.525))",
                    srid=4326,
                ),
            ),
            HazardZone(
                id=uuid.uuid4(),
                hazard_type="landslide",
                risk_score=0.82,
                severity="HIGH",
                source="GSI_LANDSLIDE_EARLY_WARNING",
                timestamp=now - timedelta(hours=3),
                # Overlaps Attamala ridge
                geometry=WKTElement(
                    "POLYGON((76.115 11.515, 76.138 11.515, 76.138 11.536, 76.115 11.536, 76.115 11.515))",
                    srid=4326,
                ),
            ),
            HazardZone(
                id=uuid.uuid4(),
                hazard_type="flash_flood",
                risk_score=0.58,
                severity="MODERATE",
                source="IMD_HYDROLOGY",
                timestamp=now - timedelta(hours=4),
                # Buffer along Meppadi downstream fringe
                geometry=WKTElement(
                    "POLYGON((76.105 11.535, 76.120 11.535, 76.120 11.550, 76.105 11.550, 76.105 11.535))",
                    srid=4326,
                ),
            ),
        ]
        db.add_all(hazard_zones)

        # 4. Seed Rainfall Observations
        rainfall_data = [
            RainfallObservation(
                id=uuid.uuid4(),
                latitude=11.552,
                longitude=76.135,
                rainfall_mm=382.5,
                observation_time=now - timedelta(minutes=45),
                source="IMD_AWS_MUNDAKKAI_PEAK",
                geometry=WKTElement("POINT(76.135 11.552)", srid=4326),
            ),
            RainfallObservation(
                id=uuid.uuid4(),
                latitude=11.538,
                longitude=76.152,
                rainfall_mm=294.0,
                observation_time=now - timedelta(minutes=45),
                source="IMD_AWS_CHOORALMALA",
                geometry=WKTElement("POINT(76.152 11.538)", srid=4326),
            ),
            RainfallObservation(
                id=uuid.uuid4(),
                latitude=11.548,
                longitude=76.118,
                rainfall_mm=178.5,
                observation_time=now - timedelta(minutes=45),
                source="IMD_AWS_MEPPADI_TOWN",
                geometry=WKTElement("POINT(76.118 11.548)", srid=4326),
            ),
            RainfallObservation(
                id=uuid.uuid4(),
                latitude=11.605,
                longitude=76.082,
                rainfall_mm=112.0,
                observation_time=now - timedelta(minutes=45),
                source="IMD_AWS_KALPETTA_SOUTH",
                geometry=WKTElement("POINT(76.082 11.605)", srid=4326),
            ),
        ]
        db.add_all(rainfall_data)

        # 5. Seed River Observations
        river_data = [
            RiverObservation(
                id=uuid.uuid4(),
                station_name="Iruvanjippuzha - Chooralmala Bridge",
                water_level=8.65,
                danger_level=6.50,
                observation_time=now - timedelta(minutes=30),
                geometry=WKTElement("POINT(76.152 11.536)", srid=4326),
            ),
            RiverObservation(
                id=uuid.uuid4(),
                station_name="Chaliyar - Nilambur Confluence",
                water_level=14.20,
                danger_level=13.80,
                observation_time=now - timedelta(minutes=30),
                geometry=WKTElement("POINT(76.220 11.450)", srid=4326),
            ),
            RiverObservation(
                id=uuid.uuid4(),
                station_name="Meppadi Upstream Feeder Gauge",
                water_level=4.15,
                danger_level=5.20,
                observation_time=now - timedelta(minutes=30),
                geometry=WKTElement("POINT(76.115 11.542)", srid=4326),
            ),
        ]
        db.add_all(river_data)

        # 6. Seed Historical / Real-Time Disaster Events
        events = [
            DisasterEvent(
                id=uuid.uuid4(),
                disaster_type="landslide",
                severity="CRITICAL",
                event_time=now - timedelta(hours=2),
                source="KSDMA_EMERGENCY_OPS",
                geometry=WKTElement(
                    "POLYGON((76.132 11.546, 76.145 11.546, 76.145 11.558, 76.132 11.558, 76.132 11.546))",
                    srid=4326,
                ),
            ),
            DisasterEvent(
                id=uuid.uuid4(),
                disaster_type="flash_flood",
                severity="SEVERE",
                event_time=now - timedelta(hours=1, minutes=30),
                source="NDRF_BATTALION_04",
                geometry=WKTElement(
                    "POLYGON((76.148 11.532, 76.162 11.532, 76.162 11.544, 76.148 11.544, 76.148 11.532))",
                    srid=4326,
                ),
            ),
        ]
        db.add_all(events)

        # 7. Seed Relocation Candidate Sites (Safe carrying capacity parcels)
        relocation_sites = [
            RelocationSite(
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
                # Safe flat elevated plateau
                geometry=WKTElement(
                    "POLYGON((76.090 11.545, 76.105 11.545, 76.105 11.558, 76.090 11.558, 76.090 11.545))",
                    srid=4326,
                ),
            ),
            RelocationSite(
                id=ID_SITE_KALPETTA_PARK,
                name="Kalpetta South Municipal Relocation Park B",
                available_area=62000.0,
                current_population=400,
                estimated_capacity=3500,
                available_capacity=3100,
                water_score=9.2,
                road_access_score=9.6,
                healthcare_score=9.4,
                hazard_score=0.02,
                suitability_score=9.4,
                # Safe urban perimeter parcel
                geometry=WKTElement(
                    "POLYGON((76.070 11.595, 76.088 11.595, 76.088 11.612, 76.070 11.612, 76.070 11.595))",
                    srid=4326,
                ),
            ),
            RelocationSite(
                id=ID_SITE_VYTHIRI_UPLANDS,
                name="Vythiri Safe Uplands Parcel C",
                available_area=28000.0,
                current_population=80,
                estimated_capacity=1500,
                available_capacity=1420,
                water_score=7.6,
                road_access_score=8.1,
                healthcare_score=7.2,
                hazard_score=0.12,
                suitability_score=8.1,
                geometry=WKTElement(
                    "POLYGON((76.035 11.550, 76.050 11.550, 76.050 11.562, 76.035 11.562, 76.035 11.550))",
                    srid=4326,
                ),
            ),
        ]
        db.add_all(relocation_sites)
        db.flush()

        # 8. Seed Relocation Recommendations
        recommendations = [
            RelocationRecommendation(
                id=uuid.uuid4(),
                habitation_id=ID_HAB_MUNDAKKAI,
                relocation_site_id=ID_SITE_MEPPADI_PLATEAU,
                priority="CRITICAL",
                priority_score=96.5,
                reason=(
                    "Mundakkai Settlement has 92% spatial overlap with VERY_HIGH Landslide Red Zone. "
                    "Precipitation exceeded 382mm threshold. Immediate evacuation of 1,450 vulnerable residents required."
                ),
                created_at=now,
            ),
            RelocationRecommendation(
                id=uuid.uuid4(),
                habitation_id=ID_HAB_CHOORALMALA,
                relocation_site_id=ID_SITE_KALPETTA_PARK,
                priority="CRITICAL",
                priority_score=93.0,
                reason=(
                    "Chooralmala river gauge (8.65m) exceeds danger level (6.50m) by 2.15m. "
                    "Severe debris flow has compromised structural safety. Immediate relocation of 1,820 vulnerable residents."
                ),
                created_at=now,
            ),
            RelocationRecommendation(
                id=uuid.uuid4(),
                habitation_id=ID_HAB_ATTAMALA,
                relocation_site_id=ID_SITE_VYTHIRI_UPLANDS,
                priority="HIGH",
                priority_score=84.5,
                reason=(
                    "High slope instability risk with isolated single-lane road access vulnerable to secondary blockages."
                ),
                created_at=now,
            ),
        ]
        db.add_all(recommendations)
        db.commit()

        logger.info("Demonstration database seeding successfully completed!")
        print("Successfully seeded SIH 2026 PostGIS demonstration dataset (Wayanad, Kerala)!")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}")
        raise e
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    seed_database()
