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
