# Project Status & Execution Log
## SIH 2026 — Problem Statement 26191
**Intelligent Identification of Hazard-Based Red Zones, Carrying Capacity Assessment, and Immediate Relocation Needs for Vulnerable Habitations**

> **Note**: This file tracks development progress and roadmap execution across phases.

---

## 📊 Overall Phase Roadmap

| Phase | Description | Status | Completion Date |
|---|---|---|---|
| **Phase 1** | **Monorepo Foundation, Architecture & Environment Setup** | **Completed** | 2026-09-25 |
| **Phase 2** | **PostgreSQL + PostGIS Spatial Schema & Data Modeling** | **Completed** | 2026-09-25 |
| **Phase 3** | **Hazard Risk Scoring Engine (Prototype v1) & Risk APIs** | **Completed** | 2026-09-25 |
| **Phase 3.5** | **GIS Processing Engine (GeoPandas, Shapely, Rasterio)** | **Completed** | 2026-09-25 |
| **Phase 3.6** | **Population Vulnerability Assessment Engine & APIs** | **Completed** | 2026-09-25 |
| **Phase 3.7** | **Relocation-Site Suitability Assessment Engine & APIs** | **Completed** | 2026-09-25 |
| **Phase 4** | AI/ML Carrying Capacity & Urgency Prioritization Engine | Pending / Next | — |
| **Phase 5** | Interactive MapLibre GL Frontend & Analytics Visualization | Pending | — |
| **Phase 6** | End-to-End Integration, Validation & Hackathon Hardening | Pending | — |

---

## ✅ Phase 3.7: Detailed Accomplishments (Relocation Site Suitability Engine)

### 1. Transparent 12-Factor Suitability Model
- [x] Defined non-black-box multi-category civil and environmental scoring configuration in `backend/app/core/suitability_config.py`:
  - **Hazard Safety (35%)**: Clearance from active flood zones (35%), landslide red zones (35%), construction slope angle (15%), flood-datum elevation (15%).
  - **Infrastructure (25%)**: Potable water networks (30%), electricity transmission (25%), hospital proximity (25%), school proximity (20%).
  - **Accessibility (20%)**: All-weather arterial highway connection (60%), multi-vehicle evacuation transit egress (40%).
  - **Capacity (20%)**: Immediate intake capacity buffer (40%), usable land parcel area in sqm (35%), occupancy ratio (25%).

### 2. Separate Category Scores & Prototype Classification
- [x] Generates 4 separate 0–100 category sub-scores alongside overall composite suitability score:
  - `hazard_safety_score`
  - `accessibility_score`
  - `infrastructure_score`
  - `capacity_score`
  - `overall_suitability_score`
- [x] Prototype classification brackets:
  - `80 – 100` = **HIGHLY SUITABLE**
  - `60 – 79` = **SUITABLE**
  - `40 – 59` = **CONDITIONALLY SUITABLE**
  - `0 – 39` = **UNSUITABLE**

### 3. Human-Readable Explainable Output
- [x] Generates dynamic civil `strengths` and engineering `limitations` (e.g. *"Zero active flood or landslide red-zone overlap (>500m safety clearance buffer)"*, *"Ideal gentle terrain topography (4.5°) with minimal earthwork requirements"*, *"Delayed emergency healthcare access (12.5 km to nearest hospital facility)"*).

### 4. REST API Endpoints with GeoJSON Geometries
- [x] Registered routes in both `/api` and `/api/v1`:
  - `GET /api/relocation-sites`: Lists candidate resettlement parcels with available area, capacity figures, and GeoJSON polygon geometry.
  - `GET /api/relocation-sites/{id}`: Detailed candidate relocation parcel profile and boundary.
  - `GET /api/relocation-sites/{id}/assessment`: Calculates transparent 0–100 suitability assessment with category sub-scores, dynamic strengths, limitations, and classification bracket.
  - `GET /api/relocation-sites/nearby/{habitation_id}`: Spatial proximity query ranking nearest safe relocation sites for an affected habitation using PostGIS ellipsoidal geography calculation (`ST_Distance`) with strict exclusion of parcels overlapping active `VERY_HIGH` hazard zones.

### 5. Automated Unit Tests & Documentation
- [x] Implemented dedicated test suite in `backend/tests/test_suitability_engine.py` (10 tests).
- [x] Pytest suite: **58/58 tests passing** (GIS engine, database, health, risk engine, vulnerability engine, suitability engine).
- [x] Documented complete API contracts and schemas in `docs/api-specification.md`.

---

## ✅ Phase 3.6: Detailed Accomplishments (Population Vulnerability Engine)

### 1. Transparent 9-Factor Vulnerability Model
- [x] Defined non-black-box socio-demographic scoring configuration in `backend/app/core/vulnerability_config.py`:
  - **Vulnerable Ratio (18%)**: Proportion of vulnerable population to total.
  - **Housing Vulnerability (15%)**: Kutcha / fragile non-engineered dwellings prevalence.
  - **Evacuation Accessibility (15%)**: Single-bridge bottleneck, narrow tracks, isolation.
  - **Elderly Population (12%)**: Senior citizens (age 60+) proportion.
  - **Children (10%)**: Dependent infants and children (age 0-14).
  - **Persons with Disabilities (10%)**: Mobility-impaired / chronic illness residents.
  - **Population Density (8%)**: Settlement concentration (people / km²).
  - **Infrastructure Fragility (7%)**: Fragile utilities and delayed medical aid access.
  - **Total Population Scale (5%)**: Total human lives exposed.
- [x] Classification brackets: `0–30` = LOW, `31–60` = MODERATE, `61–80` = HIGH, `81–100` = CRITICAL.

### 2. Demonstration Data Provenance Integrity
- [x] Clearly marked synthetic demonstration proxies (`DEMO_SYNTHESIS_CENSUS_PROXY`) modeled on Wayanad plantation hamlets and riverfront settlements:
  - Each demographic record contains explicit flags: `is_demonstration_data: true`, `data_source: "DEMO_SYNTHESIS_CENSUS_PROXY (...)"`.
  - Zero invented real-world records.

### 3. REST API Endpoints with GeoJSON Geometries
- [x] Registered routes in both `/api` and `/api/v1`:
  - `GET /api/vulnerability/{habitation_id}`: Transparent score, 9-factor breakdown, dynamic human-readable explanations, demographic profile, and GeoJSON geometry.
  - `GET /api/vulnerability/summary`: Multi-habitation aggregate summary, average score, severity breakdown, and prioritized rankings with GeoJSON geometries.

### 4. Automated Unit Tests & Documentation
- [x] Implemented comprehensive test suite in `backend/tests/test_vulnerability_engine.py`:
  - Tested classification brackets, weight summation to 1.0, 9 factor evaluation functions, composite calculation, low-vulnerability baselines, and synthetic proxy provenance.
  - Tested FastAPI `/api/vulnerability/summary` and `/api/vulnerability/{id}` endpoints.
- [x] Full backend test suite: **48/48 tests passing**.
- [x] Documented endpoints and models in `docs/api-specification.md`.

---

## ✅ Phase 3.5: Detailed Accomplishments (GIS Processing Engine)

### 1. Geospatial Stack & Decoupled Engine Architecture
- [x] Integrated `geopandas==1.1.4`, `shapely==2.1.2`, `rasterio==1.5.1`, and `pyproj==3.8.0`.
- [x] Implemented decoupled GIS module hierarchy in `backend/app/gis/` completely independent of FastAPI routes and database sessions:
  - `backend/app/gis/crs.py`: Metric CRS projection management, automatic UTM zone detection (e.g. UTM 43N / `EPSG:32643` for Wayanad), and CRS compatibility validation with `CRSCompatibilityError`.
  - `backend/app/gis/geometry_utils.py`: OGC geometry validation, automated self-intersection bowtie repair using `shapely.make_valid`, null/empty geometry filtering, and true metric area calculation (`calculate_area_sqm`).
  - `backend/app/gis/buffers.py`: Metric buffer generation (`create_buffer`) with strict meter-unit projection enforcement, resolution, cap/join styles, and dissolve capability.
  - `backend/app/gis/intersection.py`: Strict CRS-harmonized spatial intersections (`spatial_intersection`) and precise polygon overlap area/percentage calculations (`calculate_polygon_overlap`).
  - `backend/app/gis/distance.py`: Pairwise Euclidean distance matrices (`calculate_pairwise_distances`) and boundary proximity evaluations (`calculate_distance_to_hazard`).
  - `backend/app/gis/pip.py`: Point-in-polygon checks (`points_in_polygons`) and asset density aggregations (`count_points_in_polygons`) preserving source column identities.
  - `backend/app/gis/exposure.py`: Settlement hazard exposure engine (`calculate_hazard_exposure`, `calculate_habitation_exposure`) for Flood, Landslide, Rainfall, and Multi-hazard co-occurrence with 0-100 normalized scoring.
  - `backend/app/gis/accessibility.py`: Transport accessibility analysis (`calculate_site_accessibility`) computing road network distance, catchment buffer road density, and 0-100 accessibility scores.
  - `backend/app/gis/proximity.py`: Relocation-site screening (`filter_safe_relocation_sites`, `calculate_relocation_proximity`) strictly excluding parcels overlapping hazard zones and ranking safe sites by capacity and distance.
  - `backend/app/gis/raster_dem.py`: Raster DEM processing using Rasterio (`calculate_slope`, `extract_habitation_terrain_stats`), implementing Horn's 3x3 gradient algorithm to output terrain slope in degrees [0°-90°] and zonal statistics across habitation polygons.
  - `backend/app/gis/hazard_combination.py`: Multi-hazard layer synthesis (`combine_hazard_layers`) merging vector layers with compound synergy amplification and classification.
  - `backend/app/gis/engine.py`: Unified `GISEngine` facade interface exporting all functions.

### 2. Comprehensive Automated Testing
- [x] Implemented 21 automated unit tests in `backend/tests/test_gis_engine.py` covering all 9 modules, edge cases, in-memory Rasterio GeoTIFF processing, and CRS validation.
- [x] Total backend test suite: **39/39 passing** (21 GIS tests + 9 risk engine tests + 5 database tests + 4 health tests).

---

## ✅ Phase 3: Detailed Accomplishments (Hazard Risk Scoring Engine)

### 1. Transparent 7-Factor Scoring Model
- [x] Defined non-black-box prototype scoring configuration in `backend/app/core/risk_config.py`:
  - **Rainfall Intensity (20%)**: Telemetry from Automated Weather Stations within 20km.
  - **Hazard-Zone Overlap (20%)**: Direct geometric boundary overlap with designated red zones.
  - **Landslide Susceptibility (15%)**: Slope instability hazard zone severity (VERY_HIGH, HIGH, MODERATE).
  - **Flood Exposure (15%)**: River water levels exceeding flood warning thresholds + flood contour overlap.
  - **Elevation / Slope (10%)**: Steep terrain angles (>25°-35°) accelerating mass movement and runoff.
  - **Distance to Rivers / Drainage (10%)**: Proximity to drainage channels (severe risk <150m).
  - **Historical Disaster Frequency (10%)**: Recurrence count of critical past disaster incidents.

### 2. Prototype Severity Classification
- [x] Implemented exact bracket thresholds:
  - `0 – 30` = **LOW**
  - `31 – 60` = **MODERATE**
  - `61 – 80` = **HIGH**
  - `81 – 100` = **CRITICAL**

### 3. Human-Readable Explanation Generator
- [x] Generates dynamic transparent explanations for every score (e.g. *"High rainfall intensity (382.5 mm recorded)"*, *"Critical spatial overlap (92.0%) with designated hazard red zones"*, *"Habitation overlaps flood-prone area (river exceeds danger level by 2.15 m)"*).

### 4. REST API Endpoints with GeoJSON Geometries
- [x] Implemented and registered endpoints in both `/api` and `/api/v1` prefixes:
  - `GET /api/hazards`: Lists all active hazard red zones with GeoJSON polygons, filterable by hazard type and severity.
  - `GET /api/hazards/{id}`: Retrieves single hazard red zone details and polygon GeoJSON.
  - `GET /api/habitations/{id}/risk`: Calculates 0–100 transparent score, factor sub-scores, explanations, severity tier, and GeoJSON geometry.
  - `GET /api/risk/summary`: Aggregated multi-habitation risk summary, average risk score, severity breakdown, and ranked habitations list.

### 5. Automated Unit Tests & Documentation
- [x] Implemented comprehensive test suite in `backend/tests/test_risk_engine.py`:
  - Tested bracket thresholds (0, 30, 31, 60, 61, 80, 81, 100).
  - Tested factor evaluation functions for rainfall, flood, landslide, slope, historical events, drainage, and overlap.
  - Tested transparent composite formula and explanation generation.
  - Tested FastAPI hazard and risk endpoints.
- [x] Pytest suite: **18/18 tests passing**.
- [x] Documented complete API contracts in `docs/api-specification.md`.

---

## ✅ Phase 2: Completed Summary (Database & PostGIS Layer)
- Unified Spatial Models: Habitation, HazardZone, RainfallObservation, RiverObservation, DisasterEvent, RelocationSite, RelocationRecommendation.
- PostGIS GiST spatial indexing on all geometry columns.
- Alembic migration `0001_initial_postgis_schema.py`.
- Wayanad, Kerala demonstration seed dataset (`backend/app/db/seeds.py`).
- Spatial query utilities (`backend/app/db/spatial_queries.py`).
- Schema documentation in `docs/database-schema.md`.

---

## ✅ Phase 1: Completed Summary (Monorepo Foundation)
- Monorepo folder hierarchy & git repository setup.
- FastAPI backend with CORS, logging, exception handlers, and `/health` diagnostic endpoints.
- React 19 + Vite 6 frontend with Tailwind CSS v4 light civic theme, Axios client, and health monitor.
- Docker Compose configuration for PostGIS 16-3.4, FastAPI, and NGINX frontend.
- Root and module documentation (`README.md`, `docs/architecture.md`).

---

## 🔮 Next Phase: Phase 4 Plan (AI/ML Carrying Capacity & Prioritization)
1. **Carrying Capacity Assessment Engine**:
   - Algorithmic evaluation of relocation site ecological, civil infrastructure, and water safety limits.
2. **Relocation Urgency Prioritization (Supervised / Ranking ML)**:
   - Priority classification (CRITICAL, HIGH, MEDIUM, LOW) combining risk score, vulnerable population density, and nearest safe capacity parcel.
3. **Relocation Recommendation Generator**:
   - Automated generation of actionable, explainable relocation allocations in `relocation_recommendations`.
