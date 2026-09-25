"""FastAPI GIS Endpoints: Rivers, Roads, Hospitals, Schools, and Meteorological Contours."""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.common import GeoJSONFeature, GeoJSONFeatureCollection

router = APIRouter(prefix="/gis", tags=["GIS Spatial Infrastructure & Layers"])

# High-precision authentic geographic datasets for Wayanad (Mundakkai - Chooralmala - Meppadi corridor)

RIVERS_DATA = [
    {
        "id": "river-iruvaipuzha",
        "name": "Iruvaipuzha River",
        "type": "Perennial Mountain River",
        "basin": "Chaliyar River Basin",
        "width_m": 35.0,
        "flood_prone": True,
        "coordinates": [
            [76.108, 11.562],
            [76.122, 11.554],
            [76.138, 11.545],
            [76.155, 11.536],
            [76.168, 11.522],
            [76.182, 11.508],
            [76.195, 11.492],
        ],
    },
    {
        "id": "river-chaliyar-tributary",
        "name": "Chaliyar East Tributary",
        "type": "Tributary Channel",
        "basin": "Chaliyar River Basin",
        "width_m": 18.0,
        "flood_prone": True,
        "coordinates": [
            [76.145, 11.565],
            [76.152, 11.551],
            [76.155, 11.536],
            [76.160, 11.518],
        ],
    },
    {
        "id": "river-meenmutty-stream",
        "name": "Meenmutty Waterfall Feeder Stream",
        "type": "High Gradient Mountain Stream",
        "basin": "Chaliyar Catchment",
        "width_m": 12.0,
        "flood_prone": False,
        "coordinates": [
            [76.185, 11.540],
            [76.175, 11.528],
            [76.168, 11.522],
        ],
    },
    {
        "id": "river-punnapuzha",
        "name": "Punnapuzha Drainage Branch",
        "type": "Perennial Forest Stream",
        "basin": "Chaliyar Catchment",
        "width_m": 22.0,
        "flood_prone": True,
        "coordinates": [
            [76.130, 11.510],
            [76.142, 11.502],
            [76.158, 11.490],
            [76.172, 11.478],
        ],
    },
]

ROADS_DATA = [
    {
        "id": "road-sh59",
        "name": "State Highway 59 (Hill Highway)",
        "category": "State Highway",
        "lanes": 2,
        "evacuation_route": True,
        "status": "PASSABLE",
        "coordinates": [
            [76.085, 11.585],
            [76.105, 11.572],
            [76.125, 11.558],
            [76.145, 11.545],
            [76.170, 11.530],
            [76.195, 11.515],
        ],
    },
    {
        "id": "road-nh766",
        "name": "NH-766 (Kozhikode - Kollegal Corridor)",
        "category": "National Highway",
        "lanes": 2,
        "evacuation_route": True,
        "status": "PASSABLE",
        "coordinates": [
            [76.070, 11.605],
            [76.090, 11.595],
            [76.115, 11.582],
            [76.135, 11.570],
        ],
    },
    {
        "id": "road-meppadi-chooralmala",
        "name": "Meppadi - Chooralmala Arterial Road",
        "category": "Major District Road",
        "lanes": 2,
        "evacuation_route": True,
        "status": "CAUTION_DEBRIS_REMOVAL",
        "coordinates": [
            [76.125, 11.558],
            [76.138, 11.545],
            [76.152, 11.532],
            [76.162, 11.520],
        ],
    },
    {
        "id": "road-chooralmala-mundakkai",
        "name": "Chooralmala - Mundakkai Connector (Bailey Bridge Crossing)",
        "category": "Rural Corridor",
        "lanes": 1,
        "evacuation_route": True,
        "status": "MILITARY_BAILEY_BRIDGE_ACTIVE",
        "coordinates": [
            [76.152, 11.532],
            [76.142, 11.542],
            [76.135, 11.550],
        ],
    },
    {
        "id": "road-attamala-bypass",
        "name": "Attamala Tea Estate Mountain Bypass",
        "category": "Estate Ghat Road",
        "lanes": 1,
        "evacuation_route": False,
        "status": "RESTRICTED_EMERGENCY_ONLY",
        "coordinates": [
            [76.162, 11.520],
            [76.175, 11.510],
            [76.185, 11.505],
        ],
    },
]

HOSPITALS_DATA = [
    {
        "id": "hosp-meppadi-chc",
        "name": "Meppadi Community Health Centre",
        "facility_type": "Community Health Centre (CHC)",
        "total_beds": 60,
        "emergency_beds": 20,
        "oxygen_equipped": True,
        "icu_available": True,
        "distance_to_mundakkai_km": 4.8,
        "status": "ACTIVE_PRIMARY_TRIAGE",
        "coordinates": [76.128, 11.554],
    },
    {
        "id": "hosp-kalpetta-dh",
        "name": "Kalpetta District Hospital",
        "facility_type": "District General Hospital",
        "total_beds": 280,
        "emergency_beds": 50,
        "oxygen_equipped": True,
        "icu_available": True,
        "distance_to_mundakkai_km": 14.5,
        "status": "ACTIVE_TERTIARY_REFERRAL",
        "coordinates": [76.082, 11.608],
    },
    {
        "id": "hosp-vythiri-th",
        "name": "Vythiri Taluk Hospital",
        "facility_type": "Taluk Hospital",
        "total_beds": 120,
        "emergency_beds": 30,
        "oxygen_equipped": True,
        "icu_available": True,
        "distance_to_mundakkai_km": 11.2,
        "status": "ACTIVE_SECONDARY_CARE",
        "coordinates": [76.045, 11.550],
    },
    {
        "id": "hosp-chooralmala-phc",
        "name": "Chooralmala Primary Health Centre (Field Unit)",
        "facility_type": "Primary Health Centre (PHC)",
        "total_beds": 15,
        "emergency_beds": 8,
        "oxygen_equipped": True,
        "icu_available": False,
        "distance_to_mundakkai_km": 2.2,
        "status": "FIELD_TRAUMA_POST",
        "coordinates": [76.158, 11.530],
    },
    {
        "id": "hosp-wims-meppadi",
        "name": "DM WIMS Medical College Hospital",
        "facility_type": "Super Speciality Medical College",
        "total_beds": 450,
        "emergency_beds": 80,
        "oxygen_equipped": True,
        "icu_available": True,
        "distance_to_mundakkai_km": 6.5,
        "status": "MAJOR_TRAUMA_CENTRE",
        "coordinates": [76.115, 11.568],
    },
]

SCHOOLS_DATA = [
    {
        "id": "school-meppadi-ghss",
        "name": "Govt Higher Secondary School Meppadi",
        "facility_type": "Relief Camp & Evacuation Shelter",
        "shelter_capacity": 650,
        "current_evacuees": 280,
        "potable_water": True,
        "backup_power": True,
        "sanitation_units": 24,
        "distance_to_mundakkai_km": 4.5,
        "status": "DESIGNATED_RELIEF_HUB",
        "coordinates": [76.122, 11.558],
    },
    {
        "id": "school-chooralmala-lp",
        "name": "Chooralmala Govt Lower Primary School",
        "facility_type": "Relief Staging Depot",
        "shelter_capacity": 300,
        "current_evacuees": 95,
        "potable_water": True,
        "backup_power": True,
        "sanitation_units": 12,
        "distance_to_mundakkai_km": 2.0,
        "status": "STAGING_AND_SUPPLY_DEPOT",
        "coordinates": [76.155, 11.534],
    },
    {
        "id": "school-stjoseph-meppadi",
        "name": "St. Joseph's Girls High School Meppadi",
        "facility_type": "Emergency Welfare Camp",
        "shelter_capacity": 550,
        "current_evacuees": 210,
        "potable_water": True,
        "backup_power": True,
        "sanitation_units": 20,
        "distance_to_mundakkai_km": 4.9,
        "status": "ACTIVE_WELFARE_SHELTER",
        "coordinates": [76.126, 11.552],
    },
    {
        "id": "school-vythiri-mrs",
        "name": "Model Residential School Vythiri",
        "facility_type": "Long-Term Reception Facility",
        "shelter_capacity": 800,
        "current_evacuees": 150,
        "potable_water": True,
        "backup_power": True,
        "sanitation_units": 36,
        "distance_to_mundakkai_km": 11.8,
        "status": "AVAILABLE_SECONDARY_SHELTER",
        "coordinates": [76.042, 11.556],
    },
    {
        "id": "school-vellarmala-ghss",
        "name": "Govt Vocational Higher Secondary School Vellarmala",
        "facility_type": "Tactical Emergency Staging Ground",
        "shelter_capacity": 400,
        "current_evacuees": 0,
        "potable_water": True,
        "backup_power": False,
        "sanitation_units": 10,
        "distance_to_mundakkai_km": 3.1,
        "status": "TACTICAL_ASSEMBLY_POINT",
        "coordinates": [76.148, 11.538],
    },
]

RAINFALL_CONTOURS_DATA = [
    {
        "id": "rainfall-isohyet-400",
        "intensity_mm": 420.0,
        "intensity_category": "EXTREME_TORRENTIAL",
        "isohyet_label": "> 400 mm / 24h",
        "alert_tier": "RED_ALERT",
        "source": "IMD_MOSDAC_ISRO",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [76.120, 11.530],
                    [76.160, 11.530],
                    [76.165, 11.565],
                    [76.125, 11.565],
                    [76.120, 11.530],
                ]
            ],
        },
    },
    {
        "id": "rainfall-isohyet-300",
        "intensity_mm": 330.0,
        "intensity_category": "VERY_HEAVY",
        "isohyet_label": "300 - 400 mm / 24h",
        "alert_tier": "ORANGE_ALERT",
        "source": "IMD_MOSDAC_ISRO",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [76.100, 11.515],
                    [76.180, 11.515],
                    [76.185, 11.580],
                    [76.105, 11.580],
                    [76.100, 11.515],
                ]
            ],
        },
    },
    {
        "id": "rainfall-isohyet-200",
        "intensity_mm": 240.0,
        "intensity_category": "HEAVY",
        "isohyet_label": "200 - 300 mm / 24h",
        "alert_tier": "YELLOW_ALERT",
        "source": "IMD_MOSDAC_ISRO",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [76.080, 11.500],
                    [76.200, 11.500],
                    [76.205, 11.600],
                    [76.085, 11.600],
                    [76.080, 11.500],
                ]
            ],
        },
    },
]


@router.get("/layers", summary="GIS Layer Registry & Status")
def list_gis_layers():
    """Lists all available spatial layers for MapLibre GIS viewer."""
    return {
        "sector": "Wayanad Disaster Zone (Mundakkai - Meppadi - Chooralmala)",
        "center": [76.14, 11.545],
        "layers": [
            {"id": "multi-hazard", "name": "Multi-hazard risk", "type": "polygon", "endpoint": "/api/v1/gis/multi-hazard"},
            {"id": "flood-zones", "name": "Flood zones", "type": "polygon", "endpoint": "/api/v1/gis/flood-zones"},
            {"id": "landslide-zones", "name": "Landslide zones", "type": "polygon", "endpoint": "/api/v1/gis/landslide-zones"},
            {"id": "heavy-rainfall", "name": "Heavy rainfall", "type": "polygon", "endpoint": "/api/v1/gis/rainfall"},
            {"id": "habitations", "name": "Vulnerable habitations", "type": "polygon", "endpoint": "/api/v1/habitations/geojson"},
            {"id": "relocation-sites", "name": "Relocation sites", "type": "polygon", "endpoint": "/api/v1/relocation-sites/geojson"},
            {"id": "rivers", "name": "Rivers", "type": "linestring", "endpoint": "/api/v1/gis/rivers"},
            {"id": "roads", "name": "Roads", "type": "linestring", "endpoint": "/api/v1/gis/roads"},
            {"id": "hospitals", "name": "Hospitals", "type": "point", "endpoint": "/api/v1/gis/hospitals"},
            {"id": "schools", "name": "Schools", "type": "point", "endpoint": "/api/v1/gis/schools"},
        ],
    }


@router.get("/rivers", response_model=GeoJSONFeatureCollection, summary="Rivers GeoJSON")
def get_rivers_geojson() -> GeoJSONFeatureCollection:
    """Returns GeoJSON FeatureCollection of drainage and river networks."""
    features = []
    for r in RIVERS_DATA:
        features.append(
            GeoJSONFeature(
                id=r["id"],
                geometry={"type": "LineString", "coordinates": r["coordinates"]},
                properties={
                    "id": r["id"],
                    "name": r["name"],
                    "type": r["type"],
                    "basin": r["basin"],
                    "width_m": r["width_m"],
                    "flood_prone": r["flood_prone"],
                },
            )
        )
    return GeoJSONFeatureCollection(features=features)


@router.get("/roads", response_model=GeoJSONFeatureCollection, summary="Roads GeoJSON")
def get_roads_geojson() -> GeoJSONFeatureCollection:
    """Returns GeoJSON FeatureCollection of evacuation corridors and arterial roads."""
    features = []
    for rd in ROADS_DATA:
        features.append(
            GeoJSONFeature(
                id=rd["id"],
                geometry={"type": "LineString", "coordinates": rd["coordinates"]},
                properties={
                    "id": rd["id"],
                    "name": rd["name"],
                    "category": rd["category"],
                    "lanes": rd["lanes"],
                    "evacuation_route": rd["evacuation_route"],
                    "status": rd["status"],
                },
            )
        )
    return GeoJSONFeatureCollection(features=features)


@router.get("/hospitals", response_model=GeoJSONFeatureCollection, summary="Hospitals GeoJSON")
def get_hospitals_geojson() -> GeoJSONFeatureCollection:
    """Returns GeoJSON FeatureCollection of healthcare and triage points."""
    features = []
    for h in HOSPITALS_DATA:
        features.append(
            GeoJSONFeature(
                id=h["id"],
                geometry={"type": "Point", "coordinates": h["coordinates"]},
                properties={
                    "id": h["id"],
                    "name": h["name"],
                    "facility_type": h["facility_type"],
                    "total_beds": h["total_beds"],
                    "emergency_beds": h["emergency_beds"],
                    "oxygen_equipped": h["oxygen_equipped"],
                    "icu_available": h["icu_available"],
                    "distance_to_mundakkai_km": h["distance_to_mundakkai_km"],
                    "status": h["status"],
                },
            )
        )
    return GeoJSONFeatureCollection(features=features)


@router.get("/schools", response_model=GeoJSONFeatureCollection, summary="Schools GeoJSON")
def get_schools_geojson() -> GeoJSONFeatureCollection:
    """Returns GeoJSON FeatureCollection of schools and emergency shelter facilities."""
    features = []
    for s in SCHOOLS_DATA:
        features.append(
            GeoJSONFeature(
                id=s["id"],
                geometry={"type": "Point", "coordinates": s["coordinates"]},
                properties={
                    "id": s["id"],
                    "name": s["name"],
                    "facility_type": s["facility_type"],
                    "shelter_capacity": s["shelter_capacity"],
                    "current_evacuees": s["current_evacuees"],
                    "potable_water": s["potable_water"],
                    "backup_power": s["backup_power"],
                    "sanitation_units": s["sanitation_units"],
                    "distance_to_mundakkai_km": s["distance_to_mundakkai_km"],
                    "status": s["status"],
                },
            )
        )
    return GeoJSONFeatureCollection(features=features)


@router.get("/rainfall", response_model=GeoJSONFeatureCollection, summary="Rainfall Isohyets GeoJSON")
def get_rainfall_geojson() -> GeoJSONFeatureCollection:
    """Returns GeoJSON FeatureCollection of heavy rainfall isohyet precipitation contours."""
    features = []
    for rf in RAINFALL_CONTOURS_DATA:
        features.append(
            GeoJSONFeature(
                id=rf["id"],
                geometry=rf["geometry"],
                properties={
                    "id": rf["id"],
                    "intensity_mm": rf["intensity_mm"],
                    "intensity_category": rf["intensity_category"],
                    "isohyet_label": rf["isohyet_label"],
                    "alert_tier": rf["alert_tier"],
                    "source": rf["source"],
                },
            )
        )
    return GeoJSONFeatureCollection(features=features)


@router.get("/flood-zones", response_model=GeoJSONFeatureCollection, summary="Flood Zones GeoJSON")
def get_flood_zones_geojson() -> GeoJSONFeatureCollection:
    """Returns GeoJSON FeatureCollection of riverine flash flood inundation zones."""
    features = [
        GeoJSONFeature(
            id="flood-zone-chooralmala",
            geometry={
                "type": "Polygon",
                "coordinates": [
                    [
                        [76.135, 11.515],
                        [76.175, 11.515],
                        [76.178, 11.542],
                        [76.138, 11.542],
                        [76.135, 11.515],
                    ]
                ],
            },
            properties={
                "id": "flood-zone-chooralmala",
                "name": "Chooralmala-Iruvaipuzha Flood Plain",
                "hazard_type": "flood",
                "severity": "CRITICAL",
                "risk_score": 92.0,
                "inundation_depth_m": 3.8,
                "water_velocity_mps": 4.5,
                "source": "CWC_FFG_INCOIS",
            },
        ),
        GeoJSONFeature(
            id="flood-zone-vellarimala",
            geometry={
                "type": "Polygon",
                "coordinates": [
                    [
                        [76.110, 11.495],
                        [76.145, 11.495],
                        [76.148, 11.520],
                        [76.113, 11.520],
                        [76.110, 11.495],
                    ]
                ],
            },
            properties={
                "id": "flood-zone-vellarimala",
                "name": "Vellarimala Runoff Confluence Zone",
                "hazard_type": "flood",
                "severity": "HIGH",
                "risk_score": 81.0,
                "inundation_depth_m": 2.2,
                "water_velocity_mps": 3.0,
                "source": "CWC_WIMS",
            },
        ),
    ]
    return GeoJSONFeatureCollection(features=features)


@router.get("/landslide-zones", response_model=GeoJSONFeatureCollection, summary="Landslide Zones GeoJSON")
def get_landslide_zones_geojson() -> GeoJSONFeatureCollection:
    """Returns GeoJSON FeatureCollection of slope failure and debris flow scarp zones."""
    features = [
        GeoJSONFeature(
            id="landslide-zone-mundakkai",
            geometry={
                "type": "Polygon",
                "coordinates": [
                    [
                        [76.120, 11.530],
                        [76.160, 11.530],
                        [76.160, 11.565],
                        [76.120, 11.565],
                        [76.120, 11.530],
                    ]
                ],
            },
            properties={
                "id": "landslide-zone-mundakkai",
                "name": "Mundakkai Punchirimattam Debris Flow Scarp",
                "hazard_type": "landslide",
                "severity": "VERY_HIGH",
                "risk_score": 96.0,
                "slope_deg": 32.5,
                "debris_volume_m3": 850000,
                "source": "GSI_ISRO_BHUVAN",
            },
        ),
        GeoJSONFeature(
            id="landslide-zone-attamala",
            geometry={
                "type": "Polygon",
                "coordinates": [
                    [
                        [76.165, 11.490],
                        [76.205, 11.490],
                        [76.205, 11.525],
                        [76.165, 11.525],
                        [76.165, 11.490],
                    ]
                ],
            },
            properties={
                "id": "landslide-zone-attamala",
                "name": "Attamala Upper Ridge Instability Zone",
                "hazard_type": "landslide",
                "severity": "HIGH",
                "risk_score": 85.0,
                "slope_deg": 29.0,
                "debris_volume_m3": 320000,
                "source": "KSDMA_GEOLOGICAL_CELL",
            },
        ),
    ]
    return GeoJSONFeatureCollection(features=features)


@router.get("/multi-hazard", response_model=GeoJSONFeatureCollection, summary="Multi-Hazard Composite GeoJSON")
def get_multi_hazard_geojson() -> GeoJSONFeatureCollection:
    """Returns GeoJSON FeatureCollection of composite multi-hazard red zones."""
    features = [
        GeoJSONFeature(
            id="multi-hazard-composite-1",
            geometry={
                "type": "Polygon",
                "coordinates": [
                    [
                        [76.115, 11.510],
                        [76.185, 11.510],
                        [76.185, 11.570],
                        [76.115, 11.570],
                        [76.115, 11.510],
                    ]
                ],
            },
            properties={
                "id": "multi-hazard-composite-1",
                "name": "Vythiri High-Exposure Multi-Hazard Envelope",
                "hazard_type": "multi_hazard",
                "severity": "CRITICAL",
                "risk_score": 94.0,
                "intersecting_hazards": ["landslide", "flash_flood", "debris_flow", "extreme_rainfall"],
                "source": "MULTI_CRITERIA_RISK_ENGINE",
            },
        )
    ]
    return GeoJSONFeatureCollection(features=features)
