# API Specification — SIH 2026 Problem Statement 26191
## Hazard Risk & Relocation Assessment REST API

Base URLs:
- `/api/v1` (Standard versioned prefix)
- `/api` (Direct alias prefix)

---

## 📌 Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health check, database ping & PostGIS status |
| `GET` | `/api/v1/ping` | Lightweight liveness probe |
| `GET` | `/api/hazards` | List all active hazard red zones with GeoJSON geometry |
| `GET` | `/api/hazards/{id}` | Retrieve specific hazard zone by UUID |
| `GET` | `/api/habitations/{id}/risk` | Transparent 0–100 hazard risk score and factor breakdown |
| `GET` | `/api/risk/summary` | Multi-habitation risk summary, ranking and severity breakdown |
| `GET` | `/api/vulnerability/{habitation_id}` | Transparent 0–100 population vulnerability score & demographics |
| `GET` | `/api/vulnerability/summary` | Multi-habitation population vulnerability summary & rankings |
| `GET` | `/api/relocation-sites` | List candidate resettlement sites with available area & capacity |
| `GET` | `/api/relocation-sites/{id}` | Detailed candidate relocation parcel profile & geometry |
| `GET` | `/api/relocation-sites/{id}/assessment` | Explainable 0–100 suitability score, category sub-scores & factors |
| `GET` | `/api/relocation-sites/nearby/{habitation_id}` | Spatial query finding safe relocation sites near affected habitation |

---

## 🔍 Hazard Risk Scoring Engine Specification

### Prototype Factors Evaluated (0–100 Scale)
1. **Rainfall Intensity (`rainfall`)**: Automated Weather Station (AWS) precipitation within 20km (weight: 20%).
2. **Hazard Zone Overlap (`hazard_overlap`)**: Spatial boundary intersection percentage with active red zones (weight: 20%).
3. **Landslide Susceptibility (`landslide`)**: Geological survey slope instability zones and severity (weight: 15%).
4. **Flood Exposure (`flood_exposure`)**: River gauge danger level exceedance and flood contours (weight: 15%).
5. **Elevation / Slope (`elevation_slope`)**: Terrain gradient accelerating runoff and mass movement (weight: 10%).
6. **Drainage Proximity (`drainage_proximity`)**: Distance to riverbeds and drainage corridors (weight: 10%).
7. **Historical Disaster Frequency (`historical_events`)**: Disaster occurrences recorded in vicinity (weight: 10%).

### Prototype Classification Thresholds
- **`0 – 30`**: `LOW`
- **`31 – 60`**: `MODERATE`
- **`61 – 80`**: `HIGH`
- **`81 – 100`**: `CRITICAL`

---

## 📖 Endpoint Details

### 1. Habitation Risk Assessment
**`GET /api/habitations/{id}/risk`**

#### Response Example (`200 OK`):
```json
{
  "habitation_id": "11111111-1111-4111-8111-111111111111",
  "habitation_name": "Mundakkai Settlement",
  "district": "Wayanad",
  "state": "Kerala",
  "population": 2180,
  "vulnerable_population": 1450,
  "overall_score": 88,
  "severity": "CRITICAL",
  "factors": {
    "rainfall": 98,
    "flood_exposure": 78,
    "landslide": 98,
    "elevation_slope": 81,
    "historical_events": 90,
    "drainage_proximity": 79,
    "hazard_overlap": 96
  },
  "explanation": [
    "High rainfall intensity (382.5 mm recorded)",
    "Critical spatial overlap (92.0%) with designated hazard red zones",
    "Habitation overlaps flood-prone area with critical hydrometric alerts",
    "High landslide susceptibility on steep unstable slopes",
    "High historical disaster frequency (2 past major events in sector)",
    "Immediate proximity to river/drainage channel (340 m)",
    "Steep terrain gradient accelerates rapid runoff and mass movement"
  ],
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [76.130, 11.545],
        [76.142, 11.545],
        [76.142, 11.556],
        [76.130, 11.556],
        [76.130, 11.545]
      ]
    ]
  },
  "calculated_at": "2026-09-25T08:45:00.000000Z"
}
```

---

### 2. System-Wide Risk Summary
**`GET /api/risk/summary`**

#### Response Example (`200 OK`):
```json
{
  "total_habitations": 4,
  "severity_breakdown": {
    "CRITICAL": 2,
    "HIGH": 1,
    "MODERATE": 1,
    "LOW": 0
  },
  "average_risk_score": 74.5,
  "critical_habitations_count": 2,
  "habitations": [
    {
      "habitation_id": "11111111-1111-4111-8111-111111111111",
      "habitation_name": "Mundakkai Settlement",
      "overall_score": 88,
      "severity": "CRITICAL",
      "population": 2180,
      "vulnerable_population": 1450,
      "factors": { "..." : 0 },
      "explanation": ["..."],
      "geometry": { "type": "Polygon", "coordinates": [...] }
    }
  ]
}
```

---

### 3. List Hazard Red Zones
**`GET /api/hazards`**

#### Query Parameters:
- `hazard_type` (optional): Filter by `landslide`, `flash_flood`, etc.
- `severity` (optional): Filter by `VERY_HIGH`, `HIGH`, `MODERATE`, `LOW`

#### Response Example (`200 OK`):
```json
[
  {
    "id": "f5e3687b-40eb-40fc-8097-40989f6d1948",
    "hazard_type": "landslide",
    "risk_score": 0.94,
    "severity": "VERY_HIGH",
    "source": "GSI_ISRO_BHUVAN",
    "timestamp": "2026-09-25T06:00:00Z",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
          [76.125, 11.540],
          [76.148, 11.540],
          [76.148, 11.565],
          [76.125, 11.565],
          [76.125, 11.540]
        ]
      ]
    }
  }
]
```

---

## 👥 Population Vulnerability Assessment Engine Specification

### 9 Factors Evaluated (0–100 Scale)
1. **Vulnerable Population Ratio (`vulnerable_ratio`)**: Dependent, marginalized, high-need demographic share (weight: 18%).
2. **Housing Vulnerability (`housing`)**: Prevalence of kutcha, mud-thatch, non-engineered dwellings (weight: 15%).
3. **Evacuation Accessibility (`evacuation_accessibility`)**: Single-bridge bottleneck, narrow tracks, egress isolation (weight: 15%).
4. **Elderly Population (`elderly`)**: Senior citizens aged 60+ (weight: 12%).
5. **Children Population (`children`)**: Infants and children under 14 (weight: 10%).
6. **Persons with Disabilities (`disabilities`)**: Mobility-impaired / chronic illness residents (weight: 10%).
7. **Settlement Density (`population_density`)**: Concentration in people/km² (weight: 8%).
8. **Infrastructure Fragility (`infrastructure`)**: Fragility of power, water lines, delayed emergency medical aid (weight: 7%).
9. **Total Population Scale (`total_population`)**: Total human exposure volume (weight: 5%).

### Demonstration Data Provenance
Where field census data is absent, clearly marked synthetic demonstration proxies (`DEMO_SYNTHESIS_CENSUS_PROXY`) modeled on Wayanad tea-estate and riverfront settlement patterns are utilized.

### 4. Habitation Vulnerability Assessment
**`GET /api/vulnerability/{habitation_id}`**

#### Response Example (`200 OK`):
```json
{
  "habitation_id": "22222222-2222-4222-8222-222222222222",
  "habitation_name": "Chooralmala Village",
  "district": "Wayanad",
  "state": "Kerala",
  "vulnerability_score": 78,
  "severity": "HIGH",
  "factors": {
    "vulnerable_ratio": 78,
    "housing": 68,
    "evacuation_accessibility": 80,
    "elderly": 68,
    "children": 71,
    "disabilities": 77,
    "population_density": 85,
    "infrastructure": 65,
    "total_population": 70
  },
  "explanation": [
    "High vulnerable population proportion (52.8%, 1820 individuals)",
    "Elevated concentration of persons with disabilities (118 individuals with mobility constraints)",
    "Significant prevalence of non-engineered housing (68.0%)",
    "Critical evacuation constraint (single bridge egress / terrain bottleneck)"
  ],
  "demographics": {
    "total_population": 3450,
    "vulnerable_population": 1820,
    "elderly_population": 480,
    "children_population": 690,
    "disabled_population": 118,
    "population_density_per_sqkm": 2875.0,
    "kutcha_housing_pct": 68.0,
    "infrastructure_fragility_pct": 65.0,
    "is_demonstration_data": true,
    "data_source": "DEMO_SYNTHESIS_CENSUS_PROXY (Wayanad Riverfront Township)"
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[76.145, 11.530], [76.160, 11.530], [76.160, 11.542], [76.145, 11.542], [76.145, 11.530]]]
  },
  "calculated_at": "2026-09-25T17:15:00Z"
}
```

---

### 5. Multi-Habitation Vulnerability Summary
**`GET /api/vulnerability/summary`**

#### Response Example (`200 OK`):
```json
{
  "total_habitations": 4,
  "average_vulnerability_score": 74.2,
  "severity_breakdown": {
    "CRITICAL": 1,
    "HIGH": 2,
    "MODERATE": 1,
    "LOW": 0
  },
  "critical_vulnerability_count": 1,
  "habitations": [ ... ]
}
```

---

## 🏗️ Relocation-Site Suitability Assessment Engine Specification

### Prototype Factors Evaluated (0–100 Scale)
The engine calculates transparent 0–100 suitability scores across 4 key evaluation categories comprising 12 granular factors:

1. **Hazard Safety Category (Weight: 35%)**:
   - `flood_risk`: Proximity and clearance from active flood inundation zones (sub-weight: 35%).
   - `landslide_risk`: Clearance from high-risk mass movement and debris flow zones (sub-weight: 35%).
   - `slope`: Topographical gradient; gentle slopes (2°–8°) ideal, steep terrain (>25°) penalized (sub-weight: 15%).
   - `elevation`: Elevation above flood datum ensuring adequate gravity stormwater drainage (sub-weight: 15%).

2. **Infrastructure Category (Weight: 25%)**:
   - `water_availability`: Proximity to potable water supply pipelines, reservoirs, or viable aquifers (sub-weight: 30%).
   - `electricity_availability`: Grid proximity, high-voltage transmission access, transformer capacity (sub-weight: 25%).
   - `hospital_proximity`: Travel distance and emergency transit time to primary health centers or hospitals (sub-weight: 25%).
   - `school_proximity`: Safe pedestrian/bus distance to primary and secondary educational institutions (sub-weight: 20%).

3. **Accessibility Category (Weight: 20%)**:
   - `road_accessibility`: Proximity to all-weather paved highways, heavy vehicle load capacity (sub-weight: 60%).
   - `transit_connectivity`: Public transport arterial access, evacuation corridor redundancy (sub-weight: 40%).

4. **Capacity Category (Weight: 20%)**:
   - `available_capacity_buffer`: Unoccupied capacity margin for immediate resettlement intake (sub-weight: 40%).
   - `available_land`: Total usable continuous land parcel area in square meters (sub-weight: 35%).
   - `occupancy_ratio`: Current occupancy vs. maximum ecological and civil carrying capacity (sub-weight: 25%).

### Prototype Classification Thresholds
- **`80 – 100`**: `HIGHLY SUITABLE` (Immediate priority parcel; optimal safety and infrastructure clearances)
- **`60 – 79`**: `SUITABLE` (Viable parcel; minor civil infrastructure development needed)
- **`40 – 59`**: `CONDITIONALLY SUITABLE` (Conditional parcel; requires active engineering mitigation or slope terracing)
- **`0 – 39`**: `UNSUITABLE` (Constrained parcel; severe residual hazard risk or critical civic deficiency)

---

### 6. List Candidate Relocation Sites
**`GET /api/relocation-sites`**

#### Query Parameters:
- `min_suitability` *(float, optional, default: 0.0)*: Minimum suitability filter threshold.
- `min_capacity` *(integer, optional, default: 0)*: Minimum available capacity filter.

#### Response Example (`200 OK`):
```json
[
  {
    "id": "22222222-2222-4222-8222-222222222222",
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
    "geometry": {
      "type": "Polygon",
      "coordinates": [[[76.12, 11.55], [76.14, 11.55], [76.14, 11.57], [76.12, 11.57], [76.12, 11.55]]]
    }
  }
]
```

---

### 7. Get Candidate Relocation Site Profile
**`GET /api/relocation-sites/{id}`**

#### Response Example (`200 OK`):
```json
{
  "id": "22222222-2222-4222-8222-222222222222",
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
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[76.12, 11.55], [76.14, 11.55], [76.14, 11.57], [76.12, 11.57], [76.12, 11.55]]]
  }
}
```

---

### 8. Explainable Relocation Site Assessment
**`GET /api/relocation-sites/{id}/assessment`**

#### Response Example (`200 OK`):
```json
{
  "site_id": "22222222-2222-4222-8222-222222222222",
  "site_name": "Meppadi Green Plateau",
  "suitability_score": 86,
  "overall_suitability_score": 86,
  "hazard_safety_score": 92,
  "accessibility_score": 85,
  "infrastructure_score": 88,
  "capacity_score": 84,
  "classification": "HIGHLY SUITABLE",
  "category_scores": {
    "hazard_safety_score": 92,
    "accessibility_score": 85,
    "infrastructure_score": 88,
    "capacity_score": 84
  },
  "factors": {
    "flood_risk": 95,
    "landslide_risk": 90,
    "slope": 95,
    "elevation": 90,
    "water_availability": 90,
    "electricity_availability": 88,
    "hospital_proximity": 86,
    "school_proximity": 85,
    "road_accessibility": 85,
    "available_land": 85,
    "capacity_buffer": 98,
    "occupancy_ratio": 98
  },
  "strengths": [
    "Zero active flood or landslide red-zone overlap (>500m safety clearance buffer)",
    "Ideal gentle terrain topography (4.5°) with minimal earthwork requirements",
    "High all-weather arterial highway connection and multi-vehicle transport egress",
    "Reliable potable water supply and primary healthcare within 2.5 km",
    "High available carrying capacity (safely accommodates 2,160 displaced persons)"
  ],
  "limitations": [
    "Standard civil infrastructure maintenance and periodic storm drainage inspection required"
  ],
  "available_capacity": 2160,
  "estimated_capacity": 2200,
  "available_area_sqm": 125000.0,
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[76.12, 11.55], [76.14, 11.55], [76.14, 11.57], [76.12, 11.57], [76.12, 11.55]]]
  },
  "calculated_at": "2026-09-25T17:30:00Z"
}
```

---

### 9. Spatial Proximity Search for Relocation Sites Near Affected Habitation
**`GET /api/relocation-sites/nearby/{habitation_id}`**

#### Query Parameters:
- `max_distance_km` *(float, optional, default: 35.0)*: Maximum search radius in kilometers.
- `min_capacity` *(integer, optional, default: 50)*: Minimum remaining capacity buffer.
- `limit` *(integer, optional, default: 5)*: Maximum candidate parcels to rank.

#### Safety Filter:
Strictly excludes any sites intersecting active `VERY_HIGH` hazard zones using PostGIS spatial intersection.

#### Response Example (`200 OK`):
```json
{
  "habitation_id": "11111111-1111-4111-8111-111111111111",
  "habitation_name": "Chooralmala Settlement",
  "vulnerable_population": 450,
  "total_sites_found": 2,
  "recommended_sites": [
    {
      "site_id": "22222222-2222-4222-8222-222222222222",
      "site_name": "Meppadi Safe Plateau",
      "distance_km": 4.2,
      "distance_meters": 4200.5,
      "available_capacity": 1500,
      "suitability_score": 86,
      "classification": "HIGHLY SUITABLE",
      "hazard_safe": true,
      "proximity_rank": 1,
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[76.12, 11.55], [76.14, 11.55], [76.14, 11.57], [76.12, 11.57], [76.12, 11.55]]]
      }
    },
    {
      "site_id": "33333333-3333-4333-8333-333333333333",
      "site_name": "Kalpetta South Ridge",
      "distance_km": 8.9,
      "distance_meters": 8900.0,
      "available_capacity": 900,
      "suitability_score": 78,
      "classification": "SUITABLE",
      "hazard_safe": true,
      "proximity_rank": 2,
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[76.08, 11.60], [76.10, 11.60], [76.10, 11.62], [76.08, 11.62], [76.08, 11.60]]]
      }
    }
  ]
}
```
