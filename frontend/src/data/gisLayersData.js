/**
 * Spatial GIS Layers GeoJSON Specification for Wayanad Disaster Sector (RFC 7946).
 * Covers all 10 GIS Layers with precise coordinates, topological connectivity, and required attributes.
 */

// 1. Multi-hazard risk (composite hazard envelope)
export const MULTI_HAZARD_GEOJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'multi-hazard-composite-1',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.115, 11.510],
            [76.185, 11.510],
            [76.185, 11.570],
            [76.115, 11.570],
            [76.115, 11.510],
          ],
        ],
      },
      properties: {
        id: 'multi-hazard-composite-1',
        name: 'Vythiri High-Exposure Multi-Hazard Envelope',
        hazard_type: 'multi_hazard',
        severity: 'CRITICAL',
        risk_score: 94.0,
        intersecting_hazards: 'Landslide + Flash Flood + Cloudburst Runoff',
        source: 'Multi-Criteria Decision Matrix (ISRO/GSI/CWC)',
      },
    },
    {
      type: 'Feature',
      id: 'multi-hazard-composite-2',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.090, 11.485],
            [76.140, 11.485],
            [76.140, 11.525],
            [76.090, 11.525],
            [76.090, 11.485],
          ],
        ],
      },
      properties: {
        id: 'multi-hazard-composite-2',
        name: 'Vellarimala Southwestern Convergence Zone',
        hazard_type: 'multi_hazard',
        severity: 'HIGH',
        risk_score: 82.0,
        intersecting_hazards: 'Slope Creep + Drainage Blockage',
        source: 'KSDMA Multi-Hazard Atlas',
      },
    },
  ],
};

// 2. Flood zones (flash flood / riverine inundation)
export const FLOOD_ZONES_GEOJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'flood-zone-chooralmala',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.135, 11.515],
            [76.175, 11.515],
            [76.178, 11.542],
            [76.138, 11.542],
            [76.135, 11.515],
          ],
        ],
      },
      properties: {
        id: 'flood-zone-chooralmala',
        name: 'Chooralmala-Iruvaipuzha Flood Plain',
        hazard_type: 'flood',
        severity: 'CRITICAL',
        risk_score: 92.0,
        inundation_depth_m: 3.8,
        water_velocity_mps: 4.5,
        source: 'CWC FFG Model / INCOIS Flood Hydrology',
      },
    },
    {
      type: 'Feature',
      id: 'flood-zone-vellarimala',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.110, 11.495],
            [76.145, 11.495],
            [76.148, 11.520],
            [76.113, 11.520],
            [76.110, 11.495],
          ],
        ],
      },
      properties: {
        id: 'flood-zone-vellarimala',
        name: 'Vellarimala Runoff Confluence Basin',
        hazard_type: 'flood',
        severity: 'HIGH',
        risk_score: 81.0,
        inundation_depth_m: 2.2,
        water_velocity_mps: 3.0,
        source: 'CWC WIMS Gauge Telemetry',
      },
    },
  ],
};

// 3. Landslide zones (slope instability / debris flow scarp)
export const LANDSLIDE_ZONES_GEOJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'landslide-zone-mundakkai',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.120, 11.530],
            [76.160, 11.530],
            [76.160, 11.565],
            [76.120, 11.565],
            [76.120, 11.530],
          ],
        ],
      },
      properties: {
        id: 'landslide-zone-mundakkai',
        name: 'Mundakkai Punchirimattam Debris Flow Scarp',
        hazard_type: 'landslide',
        severity: 'VERY_HIGH',
        risk_score: 96.0,
        slope_deg: 32.5,
        debris_volume_m3: 850000,
        source: 'GSI Geological Cell / ISRO Bhuvan High-Res DEM',
      },
    },
    {
      type: 'Feature',
      id: 'landslide-zone-attamala',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.165, 11.490],
            [76.205, 11.490],
            [76.205, 11.525],
            [76.165, 11.525],
            [76.165, 11.490],
          ],
        ],
      },
      properties: {
        id: 'landslide-zone-attamala',
        name: 'Attamala Upper Ridge Instability Zone',
        hazard_type: 'landslide',
        severity: 'HIGH',
        risk_score: 85.0,
        slope_deg: 29.0,
        debris_volume_m3: 320000,
        source: 'KSDMA Slope Stability Division',
      },
    },
  ],
};

// 4. Heavy rainfall (isohyet precipitation contours)
export const HEAVY_RAINFALL_GEOJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'rainfall-isohyet-400',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.120, 11.530],
            [76.165, 11.530],
            [76.170, 11.565],
            [76.125, 11.565],
            [76.120, 11.530],
          ],
        ],
      },
      properties: {
        id: 'rainfall-isohyet-400',
        name: 'Torrential Precipitation Isohyet (> 400 mm/24h)',
        intensity_mm: 420.0,
        isohyet_label: '> 400 mm / 24h',
        alert_tier: 'RED_ALERT',
        source: 'IMD Automated Weather Station / MOSDAC Doppler',
      },
    },
    {
      type: 'Feature',
      id: 'rainfall-isohyet-300',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.100, 11.515],
            [76.180, 11.515],
            [76.185, 11.580],
            [76.105, 11.580],
            [76.100, 11.515],
          ],
        ],
      },
      properties: {
        id: 'rainfall-isohyet-300',
        name: 'Severe Precipitation Isohyet (300-400 mm/24h)',
        intensity_mm: 330.0,
        isohyet_label: '300 - 400 mm / 24h',
        alert_tier: 'ORANGE_ALERT',
        source: 'IMD AWS Radar Ingestion',
      },
    },
    {
      type: 'Feature',
      id: 'rainfall-isohyet-200',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.080, 11.500],
            [76.200, 11.500],
            [76.205, 11.600],
            [76.085, 11.600],
            [76.080, 11.500],
          ],
        ],
      },
      properties: {
        id: 'rainfall-isohyet-200',
        name: 'Heavy Rainfall Isohyet (200-300 mm/24h)',
        intensity_mm: 240.0,
        isohyet_label: '200 - 300 mm / 24h',
        alert_tier: 'YELLOW_ALERT',
        source: 'IMD Regional Meteorological Centre',
      },
    },
  ],
};

// 5. Vulnerable habitations (settlements styled with priority, including all 7 required attributes)
export const HABITATIONS_GEOJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: '11111111-1111-4111-8111-111111111111',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.13, 11.54],
            [76.15, 11.54],
            [76.15, 11.56],
            [76.13, 11.56],
            [76.13, 11.54],
          ],
        ],
      },
      properties: {
        id: '11111111-1111-4111-8111-111111111111',
        name: 'Mundakkai Settlement',
        population: 2180,
        vulnerable_population: 1450,
        hazard_score: 92,
        vulnerability_score: 85,
        priority: 'IMMEDIATE',
        main_risk_factors: [
          'Debris flow path directly through town centre',
          '382 mm extreme cloudburst rainfall within 24h',
          'Kutcha dwellings proportion exceeds 72%',
        ],
        recommended_relocation_site: 'Meppadi Safe Plateau Zone A',
        district: 'Wayanad',
        taluk: 'Vythiri',
      },
    },
    {
      type: 'Feature',
      id: '22222222-2222-4222-8222-222222222222',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.15, 11.52],
            [76.17, 11.52],
            [76.17, 11.54],
            [76.15, 11.54],
            [76.15, 11.52],
          ],
        ],
      },
      properties: {
        id: '22222222-2222-4222-8222-222222222222',
        name: 'Chooralmala Hamlet',
        population: 1850,
        vulnerable_population: 1120,
        hazard_score: 88,
        vulnerability_score: 83,
        priority: 'IMMEDIATE',
        main_risk_factors: [
          'Flash flood inundation along Iruvaipuzha riverbank',
          'Bridge access breach isolating downstream ward',
          'High concentration of elderly & infant population',
        ],
        recommended_relocation_site: 'Meppadi Safe Plateau Zone A',
        district: 'Wayanad',
        taluk: 'Vythiri',
      },
    },
    {
      type: 'Feature',
      id: '33333333-3333-4333-8333-333333333333',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.17, 11.50],
            [76.19, 11.50],
            [76.19, 11.52],
            [76.17, 11.52],
            [76.17, 11.50],
          ],
        ],
      },
      properties: {
        id: '33333333-3333-4333-8333-333333333333',
        name: 'Attamala Tea Estate Quarters',
        population: 1240,
        vulnerable_population: 890,
        hazard_score: 86,
        vulnerability_score: 79,
        priority: 'IMMEDIATE',
        main_risk_factors: [
          'Steep gradient terrain (> 29°) prone to rockfall',
          'Estate line houses situated directly beneath unstable scarp',
          'Single egress mountain road prone to tree fall blocks',
        ],
        recommended_relocation_site: 'Kalpetta South Ridge Parcel 3',
        district: 'Wayanad',
        taluk: 'Vythiri',
      },
    },
    {
      type: 'Feature',
      id: '44444444-4444-4444-8444-444444444444',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.11, 11.53],
            [76.13, 11.53],
            [76.13, 11.55],
            [76.11, 11.55],
            [76.11, 11.53],
          ],
        ],
      },
      properties: {
        id: '44444444-4444-4444-8444-444444444444',
        name: 'Punchirimattam Ridge',
        population: 890,
        vulnerable_population: 620,
        hazard_score: 79,
        vulnerability_score: 75,
        priority: 'SHORT_TERM',
        main_risk_factors: [
          'Noticeable active soil creep on upper cultivation terraces',
          'Narrow feeder lane vulnerable to localized slip',
        ],
        recommended_relocation_site: 'Meppadi Safe Plateau Zone A',
        district: 'Wayanad',
        taluk: 'Vythiri',
      },
    },
    {
      type: 'Feature',
      id: '55555555-5555-4555-8555-555555555555',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.10, 11.50],
            [76.12, 11.50],
            [76.12, 11.52],
            [76.10, 11.52],
            [76.10, 11.50],
          ],
        ],
      },
      properties: {
        id: '55555555-5555-4555-8555-555555555555',
        name: 'Vellarimala Foothills',
        population: 1420,
        vulnerable_population: 910,
        hazard_score: 74,
        vulnerability_score: 72,
        priority: 'SHORT_TERM',
        main_risk_factors: [
          'Runoff accumulation receiving mountain catchment drainage',
          'Intermittent pathway flooding during sustained downpours',
        ],
        recommended_relocation_site: 'Kalpetta South Ridge Parcel 3',
        district: 'Wayanad',
        taluk: 'Vythiri',
      },
    },
    {
      type: 'Feature',
      id: '66666666-6666-4666-8666-666666666666',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.12, 11.55],
            [76.14, 11.55],
            [76.14, 11.57],
            [76.12, 11.57],
            [76.12, 11.55],
          ],
        ],
      },
      properties: {
        id: '66666666-6666-4666-8666-666666666666',
        name: 'Meppadi Bazaar Ward',
        population: 3400,
        vulnerable_population: 1200,
        hazard_score: 48,
        vulnerability_score: 55,
        priority: 'MEDIUM_TERM',
        main_risk_factors: [
          'Localized urban stormwater clogging during monsoon peaks',
          'Stable underlying bedrock with low slope inclination',
        ],
        recommended_relocation_site: 'Meppadi Safe Plateau Zone A',
        district: 'Wayanad',
        taluk: 'Vythiri',
      },
    },
  ],
};

// 6. Relocation sites (including all 7 required attributes)
export const RELOCATION_SITES_GEOJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.11, 11.56],
            [76.13, 11.56],
            [76.13, 11.58],
            [76.11, 11.58],
            [76.11, 11.56],
          ],
        ],
      },
      properties: {
        id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
        site_name: 'Meppadi Safe Plateau Zone A',
        name: 'Meppadi Safe Plateau Zone A',
        suitability_score: 89,
        carrying_capacity: 3500,
        current_population: 700,
        available_capacity: 2800,
        infrastructure: 'Paved 2-lane road (0.4 km) | Meppadi CHC (3.2 km) | GHSS School (1.8 km) | 33kV Substation',
        distance_to_nearest_habitation: '3.8 km to Chooralmala / 4.2 km to Mundakkai',
        classification: 'HIGHLY SUITABLE',
        usable_area_sqm: 125000,
        district: 'Wayanad',
        taluk: 'Vythiri',
      },
    },
    {
      type: 'Feature',
      id: 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.07, 11.59],
            [76.09, 11.59],
            [76.09, 11.61],
            [76.07, 11.61],
            [76.07, 11.59],
          ],
        ],
      },
      properties: {
        id: 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
        site_name: 'Kalpetta South Ridge Parcel 3',
        name: 'Kalpetta South Ridge Parcel 3',
        suitability_score: 86,
        carrying_capacity: 2600,
        current_population: 450,
        available_capacity: 2150,
        infrastructure: 'NH-766 Highway (0.8 km) | Kalpetta District Hospital (2.5 km) | St. Joseph High School (1.2 km)',
        distance_to_nearest_habitation: '7.1 km to Attamala / 8.5 km to Mundakkai',
        classification: 'HIGHLY SUITABLE',
        usable_area_sqm: 95000,
        district: 'Wayanad',
        taluk: 'Vythiri',
      },
    },
    {
      type: 'Feature',
      id: 'cccccccc-cccc-4ccc-8ccc-cccccccccccc',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [76.04, 11.53],
            [76.06, 11.53],
            [76.06, 11.55],
            [76.04, 11.55],
            [76.04, 11.53],
          ],
        ],
      },
      properties: {
        id: 'cccccccc-cccc-4ccc-8ccc-cccccccccccc',
        site_name: 'Vythiri North Terrace Haven',
        name: 'Vythiri North Terrace Haven',
        suitability_score: 78,
        carrying_capacity: 1800,
        current_population: 320,
        available_capacity: 1480,
        infrastructure: 'NH Corridor (1.2 km) | Vythiri Taluk Hospital (1.5 km) | Govt Residential School (0.9 km)',
        distance_to_nearest_habitation: '11.2 km to Mundakkai / 10.4 km to Chooralmala',
        classification: 'SUITABLE',
        usable_area_sqm: 68000,
        district: 'Wayanad',
        taluk: 'Vythiri',
      },
    },
  ],
};

// 7. Rivers (hydrographic line network)
export const RIVERS_GEOJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'river-iruvaipuzha',
      geometry: {
        type: 'LineString',
        coordinates: [
          [76.108, 11.562],
          [76.122, 11.554],
          [76.138, 11.545],
          [76.155, 11.536],
          [76.168, 11.522],
          [76.182, 11.508],
          [76.195, 11.492],
        ],
      },
      properties: {
        id: 'river-iruvaipuzha',
        name: 'Iruvaipuzha River (Main Drainage Channel)',
        type: 'Perennial Mountain River',
        basin: 'Chaliyar River Basin',
        width_m: 35.0,
        flood_prone: true,
        danger_level_m: 4.5,
      },
    },
    {
      type: 'Feature',
      id: 'river-chaliyar-tributary',
      geometry: {
        type: 'LineString',
        coordinates: [
          [76.145, 11.565],
          [76.152, 11.551],
          [76.155, 11.536],
          [76.160, 11.518],
        ],
      },
      properties: {
        id: 'river-chaliyar-tributary',
        name: 'Chaliyar East Tributary',
        type: 'Tributary Channel',
        basin: 'Chaliyar River Basin',
        width_m: 18.0,
        flood_prone: true,
        danger_level_m: 3.2,
      },
    },
    {
      type: 'Feature',
      id: 'river-meenmutty-stream',
      geometry: {
        type: 'LineString',
        coordinates: [
          [76.185, 11.540],
          [76.175, 11.528],
          [76.168, 11.522],
        ],
      },
      properties: {
        id: 'river-meenmutty-stream',
        name: 'Meenmutty Waterfall Feeder Stream',
        type: 'High Gradient Mountain Stream',
        basin: 'Chaliyar Catchment',
        width_m: 12.0,
        flood_prone: false,
        danger_level_m: 2.5,
      },
    },
    {
      type: 'Feature',
      id: 'river-punnapuzha',
      geometry: {
        type: 'LineString',
        coordinates: [
          [76.130, 11.510],
          [76.142, 11.502],
          [76.158, 11.490],
          [76.172, 11.478],
        ],
      },
      properties: {
        id: 'river-punnapuzha',
        name: 'Punnapuzha Forest Branch',
        type: 'Perennial Forest Stream',
        basin: 'Chaliyar Catchment',
        width_m: 22.0,
        flood_prone: true,
        danger_level_m: 3.8,
      },
    },
  ],
};

// 8. Roads (arterial corridors & emergency evacuation routes)
export const ROADS_GEOJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'road-sh59',
      geometry: {
        type: 'LineString',
        coordinates: [
          [76.085, 11.585],
          [76.105, 11.572],
          [76.125, 11.558],
          [76.145, 11.545],
          [76.170, 11.530],
          [76.195, 11.515],
        ],
      },
      properties: {
        id: 'road-sh59',
        name: 'State Highway 59 (Hill Highway)',
        category: 'State Highway',
        lanes: 2,
        evacuation_route: true,
        status: 'CLEAR / PASSABLE',
      },
    },
    {
      type: 'Feature',
      id: 'road-nh766',
      geometry: {
        type: 'LineString',
        coordinates: [
          [76.070, 11.605],
          [76.090, 11.595],
          [76.115, 11.582],
          [76.135, 11.570],
        ],
      },
      properties: {
        id: 'road-nh766',
        name: 'NH-766 (Kozhikode - Kollegal Heavy Corridor)',
        category: 'National Highway',
        lanes: 2,
        evacuation_route: true,
        status: 'CLEAR / PASSABLE',
      },
    },
    {
      type: 'Feature',
      id: 'road-meppadi-chooralmala',
      geometry: {
        type: 'LineString',
        coordinates: [
          [76.125, 11.558],
          [76.138, 11.545],
          [76.152, 11.532],
          [76.162, 11.520],
        ],
      },
      properties: {
        id: 'road-meppadi-chooralmala',
        name: 'Meppadi - Chooralmala Arterial Road',
        category: 'Major District Road',
        lanes: 2,
        evacuation_route: true,
        status: 'CAUTION - DEBRIS REMOVAL VEHICLES',
      },
    },
    {
      type: 'Feature',
      id: 'road-chooralmala-mundakkai',
      geometry: {
        type: 'LineString',
        coordinates: [
          [76.152, 11.532],
          [76.142, 11.542],
          [76.135, 11.550],
        ],
      },
      properties: {
        id: 'road-chooralmala-mundakkai',
        name: 'Chooralmala - Mundakkai Connector (Bailey Bridge Crossing)',
        category: 'Critical Emergency Link',
        lanes: 1,
        evacuation_route: true,
        status: 'OPERATIONAL - ARMY BAILEY BRIDGE',
      },
    },
    {
      type: 'Feature',
      id: 'road-attamala-bypass',
      geometry: {
        type: 'LineString',
        coordinates: [
          [76.162, 11.520],
          [76.175, 11.510],
          [76.185, 11.505],
        ],
      },
      properties: {
        id: 'road-attamala-bypass',
        name: 'Attamala Tea Estate Mountain Bypass',
        category: 'Estate Ghat Road',
        lanes: 1,
        evacuation_route: false,
        status: 'RESTRICTED - 4WD ONLY',
      },
    },
  ],
};

// 9. Hospitals (healthcare, trauma triage, ICU facilities)
export const HOSPITALS_GEOJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'hosp-meppadi-chc',
      geometry: {
        type: 'Point',
        coordinates: [76.128, 11.554],
      },
      properties: {
        id: 'hosp-meppadi-chc',
        name: 'Meppadi Community Health Centre',
        facility_type: 'Community Health Centre (CHC)',
        total_beds: 60,
        emergency_beds: 20,
        oxygen_equipped: true,
        icu_available: true,
        distance_to_mundakkai_km: 4.8,
        status: 'ACTIVE - PRIMARY TRIAGE HUB',
      },
    },
    {
      type: 'Feature',
      id: 'hosp-kalpetta-dh',
      geometry: {
        type: 'Point',
        coordinates: [76.082, 11.608],
      },
      properties: {
        id: 'hosp-kalpetta-dh',
        name: 'Kalpetta District Hospital',
        facility_type: 'District General Hospital',
        total_beds: 280,
        emergency_beds: 50,
        oxygen_equipped: true,
        icu_available: true,
        distance_to_mundakkai_km: 14.5,
        status: 'ACTIVE - TERTIARY REFERRAL',
      },
    },
    {
      type: 'Feature',
      id: 'hosp-vythiri-th',
      geometry: {
        type: 'Point',
        coordinates: [76.045, 11.550],
      },
      properties: {
        id: 'hosp-vythiri-th',
        name: 'Vythiri Taluk Hospital',
        facility_type: 'Taluk Hospital',
        total_beds: 120,
        emergency_beds: 30,
        oxygen_equipped: true,
        icu_available: true,
        distance_to_mundakkai_km: 11.2,
        status: 'ACTIVE - SECONDARY CARE',
      },
    },
    {
      type: 'Feature',
      id: 'hosp-chooralmala-phc',
      geometry: {
        type: 'Point',
        coordinates: [76.158, 11.530],
      },
      properties: {
        id: 'hosp-chooralmala-phc',
        name: 'Chooralmala Primary Health Centre (Field Unit)',
        facility_type: 'Primary Health Centre (PHC)',
        total_beds: 15,
        emergency_beds: 8,
        oxygen_equipped: true,
        icu_available: false,
        distance_to_mundakkai_km: 2.2,
        status: 'FIELD TRAUMA ADVANCED POST',
      },
    },
    {
      type: 'Feature',
      id: 'hosp-wims-meppadi',
      geometry: {
        type: 'Point',
        coordinates: [76.115, 11.568],
      },
      properties: {
        id: 'hosp-wims-meppadi',
        name: 'DM WIMS Medical College Hospital',
        facility_type: 'Super Speciality Medical College',
        total_beds: 450,
        emergency_beds: 80,
        oxygen_equipped: true,
        icu_available: true,
        distance_to_mundakkai_km: 6.5,
        status: 'MAJOR TRAUMA RESCUE HOSPITAL',
      },
    },
  ],
};

// 10. Schools (designated emergency relief shelter facilities)
export const SCHOOLS_GEOJSON = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'school-meppadi-ghss',
      geometry: {
        type: 'Point',
        coordinates: [76.122, 11.558],
      },
      properties: {
        id: 'school-meppadi-ghss',
        name: 'Govt Higher Secondary School Meppadi',
        facility_type: 'Relief Camp & Evacuation Shelter',
        shelter_capacity: 650,
        current_evacuees: 280,
        potable_water: true,
        backup_power: true,
        sanitation_units: 24,
        distance_to_mundakkai_km: 4.5,
        status: 'DESIGNATED SECTOR RELIEF HUB',
      },
    },
    {
      type: 'Feature',
      id: 'school-chooralmala-lp',
      geometry: {
        type: 'Point',
        coordinates: [76.155, 11.534],
      },
      properties: {
        id: 'school-chooralmala-lp',
        name: 'Chooralmala Govt Lower Primary School',
        facility_type: 'Relief Staging Depot',
        shelter_capacity: 300,
        current_evacuees: 95,
        potable_water: true,
        backup_power: true,
        sanitation_units: 12,
        distance_to_mundakkai_km: 2.0,
        status: 'STAGING & RATION DISTRIBUTION DEPOT',
      },
    },
    {
      type: 'Feature',
      id: 'school-stjoseph-meppadi',
      geometry: {
        type: 'Point',
        coordinates: [76.126, 11.552],
      },
      properties: {
        id: 'school-stjoseph-meppadi',
        name: "St. Joseph's Girls High School Meppadi",
        facility_type: 'Emergency Welfare Camp',
        shelter_capacity: 550,
        current_evacuees: 210,
        potable_water: true,
        backup_power: true,
        sanitation_units: 20,
        distance_to_mundakkai_km: 4.9,
        status: 'ACTIVE WOMEN & CHILDREN WELFARE CAMP',
      },
    },
    {
      type: 'Feature',
      id: 'school-vythiri-mrs',
      geometry: {
        type: 'Point',
        coordinates: [76.042, 11.556],
      },
      properties: {
        id: 'school-vythiri-mrs',
        name: 'Model Residential School Vythiri',
        facility_type: 'Long-Term Reception Facility',
        shelter_capacity: 800,
        current_evacuees: 150,
        potable_water: true,
        backup_power: true,
        sanitation_units: 36,
        distance_to_mundakkai_km: 11.8,
        status: 'AVAILABLE HIGH-CAPACITY RECEPTION HUB',
      },
    },
    {
      type: 'Feature',
      id: 'school-vellarmala-ghss',
      geometry: {
        type: 'Point',
        coordinates: [76.148, 11.538],
      },
      properties: {
        id: 'school-vellarmala-ghss',
        name: 'Govt Vocational Higher Secondary School Vellarmala',
        facility_type: 'Tactical Emergency Staging Ground',
        shelter_capacity: 400,
        current_evacuees: 0,
        potable_water: true,
        backup_power: false,
        sanitation_units: 10,
        distance_to_mundakkai_km: 3.1,
        status: 'TACTICAL DISASTER RESPONSE STAGING',
      },
    },
  ],
};
