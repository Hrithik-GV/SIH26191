/**
 * High-fidelity fallback dataset for Wayanad District (Mundakkai - Meppadi - Chooralmala corridor).
 * Ensures zero UI breakage and seamless demonstration even when backend is temporarily starting.
 */

export const FALLBACK_DASHBOARD = {
  total_habitations: 18,
  habitations_in_critical_zones: 6,
  population_at_risk: 5840,
  immediate_relocation_count: 3,
  short_term_relocation_count: 3,
  medium_term_relocation_count: 7,
  monitor_relocation_count: 5,
  total_relocation_capacity: 8500,
  available_relocation_capacity: 5200,
  capacity_deficit: 0,
  active_alerts: 4,
  average_risk_score: 64.5,
  average_vulnerability_score: 68.2,
  latest_data_timestamps: {
    rainfall_telemetry: new Date().toISOString(),
    river_gauging: new Date().toISOString(),
    emergency_alerts: new Date().toISOString(),
    last_ingestion_cycle: new Date().toISOString(),
    dashboard_computed: new Date().toISOString(),
  },
  most_urgent_habitations: [
    {
      habitation_id: "11111111-1111-4111-8111-111111111111",
      habitation_name: "Mundakkai Settlement",
      district: "Wayanad",
      taluk: "Vythiri",
      priority: "IMMEDIATE",
      priority_score: 89,
      hazard_score: 92,
      vulnerability_score: 85,
      vulnerable_population: 1450,
      recommended_site_name: "Meppadi Safe Plateau Zone A",
      recommended_site_distance_km: 4.2,
    },
    {
      habitation_id: "22222222-2222-4222-8222-222222222222",
      habitation_name: "Chooralmala Hamlet",
      district: "Wayanad",
      taluk: "Vythiri",
      priority: "IMMEDIATE",
      priority_score: 86,
      hazard_score: 88,
      vulnerability_score: 83,
      vulnerable_population: 1120,
      recommended_site_name: "Meppadi Safe Plateau Zone A",
      recommended_site_distance_km: 3.8,
    },
    {
      habitation_id: "33333333-3333-4333-8333-333333333333",
      habitation_name: "Attamala Tea Estate Quarters",
      district: "Wayanad",
      taluk: "Vythiri",
      priority: "IMMEDIATE",
      priority_score: 83,
      hazard_score: 86,
      vulnerability_score: 79,
      vulnerable_population: 890,
      recommended_site_name: "Kalpetta South Ridge Parcel 3",
      recommended_site_distance_km: 7.1,
    }
  ]
};

export const FALLBACK_HABITATIONS = [
  {
    id: "11111111-1111-4111-8111-111111111111",
    name: "Mundakkai Settlement",
    district: "Wayanad",
    taluk: "Vythiri",
    state: "Kerala",
    population: 2180,
    vulnerable_population: 1450,
    area_sqm: 480000,
    risk_score: 92,
    risk_severity: "CRITICAL",
    vulnerability_score: 85,
    vulnerability_severity: "CRITICAL",
    priority: "IMMEDIATE",
    priority_score: 89,
    geometry: {
      type: "Polygon",
      coordinates: [[[76.13, 11.54], [76.15, 11.54], [76.15, 11.56], [76.13, 11.56], [76.13, 11.54]]]
    },
    factors: {
      rainfall: 96,
      flood_exposure: 88,
      landslide: 94,
      elevation_slope: 82,
      historical_events: 90,
      drainage_proximity: 85,
      hazard_overlap: 92
    },
    explanations: [
      "Extremely heavy rainfall (382 mm recorded within 24h)",
      "High landslide susceptibility index on slope > 28°",
      "92% spatial overlap with GSI/ISRO Landslide Red Zone",
      "Kutcha dwellings proportion exceeds 72%"
    ],
    demographics: {
      total_population: 2180,
      vulnerable_population: 1450,
      elderly_population: 310,
      children_population: 420,
      disabled_population: 95,
      kutcha_houses_pct: 72.0,
      infrastructure_fragility_pct: 68.0,
      is_demonstration_data: true,
      data_source: "DEMO_SYNTHESIS_CENSUS_PROXY"
    }
  },
  {
    id: "22222222-2222-4222-8222-222222222222",
    name: "Chooralmala Hamlet",
    district: "Wayanad",
    taluk: "Vythiri",
    state: "Kerala",
    population: 1850,
    vulnerable_population: 1120,
    area_sqm: 390000,
    risk_score: 88,
    risk_severity: "CRITICAL",
    vulnerability_score: 83,
    vulnerability_severity: "CRITICAL",
    priority: "IMMEDIATE",
    priority_score: 86,
    geometry: {
      type: "Polygon",
      coordinates: [[[76.15, 11.52], [76.17, 11.52], [76.17, 11.54], [76.15, 11.54], [76.15, 11.52]]]
    },
    factors: {
      rainfall: 94,
      flood_exposure: 92,
      landslide: 86,
      elevation_slope: 78,
      historical_events: 85,
      drainage_proximity: 90,
      hazard_overlap: 85
    },
    explanations: [
      "Severe flash flood risk along Iruvaipuzha river corridor",
      "Bridge access bottleneck limits emergency evacuation",
      "High concentration of women and children in river basin dwellings"
    ],
    demographics: {
      total_population: 1850,
      vulnerable_population: 1120,
      elderly_population: 240,
      children_population: 360,
      disabled_population: 75,
      kutcha_houses_pct: 65.0,
      infrastructure_fragility_pct: 62.0,
      is_demonstration_data: true,
      data_source: "DEMO_SYNTHESIS_CENSUS_PROXY"
    }
  },
  {
    id: "33333333-3333-4333-8333-333333333333",
    name: "Attamala Tea Estate Quarters",
    district: "Wayanad",
    taluk: "Vythiri",
    state: "Kerala",
    population: 1240,
    vulnerable_population: 890,
    area_sqm: 290000,
    risk_score: 86,
    risk_severity: "CRITICAL",
    vulnerability_score: 79,
    vulnerability_severity: "HIGH",
    priority: "IMMEDIATE",
    priority_score: 83,
    geometry: {
      type: "Polygon",
      coordinates: [[[76.17, 11.50], [76.19, 11.50], [76.19, 11.52], [76.17, 11.52], [76.17, 11.50]]]
    },
    factors: {
      rainfall: 92,
      flood_exposure: 74,
      landslide: 95,
      elevation_slope: 88,
      historical_events: 80,
      drainage_proximity: 70,
      hazard_overlap: 88
    },
    explanations: [
      "Steep gradient terrain prone to debris flows during cloudbursts",
      "Estate line houses located directly below unstable scarp slopes"
    ],
    demographics: {
      total_population: 1240,
      vulnerable_population: 890,
      elderly_population: 180,
      children_population: 290,
      disabled_population: 60,
      kutcha_houses_pct: 58.0,
      infrastructure_fragility_pct: 60.0,
      is_demonstration_data: true,
      data_source: "DEMO_SYNTHESIS_CENSUS_PROXY"
    }
  },
  {
    id: "44444444-4444-4444-8444-444444444444",
    name: "Punchirimattam Ridge",
    district: "Wayanad",
    taluk: "Vythiri",
    state: "Kerala",
    population: 890,
    vulnerable_population: 620,
    area_sqm: 210000,
    risk_score: 79,
    risk_severity: "HIGH",
    vulnerability_score: 75,
    vulnerability_severity: "HIGH",
    priority: "SHORT_TERM",
    priority_score: 78,
    geometry: {
      type: "Polygon",
      coordinates: [[[76.11, 11.53], [76.13, 11.53], [76.13, 11.55], [76.11, 11.55], [76.11, 11.53]]]
    },
    factors: {
      rainfall: 90,
      flood_exposure: 65,
      landslide: 84,
      elevation_slope: 85,
      historical_events: 75,
      drainage_proximity: 60,
      hazard_overlap: 72
    },
    explanations: [
      "Moderate to high slope instability with soil creep signs",
      "Narrow single-lane road egress susceptible to blockages"
    ],
    demographics: {
      total_population: 890,
      vulnerable_population: 620,
      elderly_population: 110,
      children_population: 190,
      disabled_population: 40,
      kutcha_houses_pct: 52.0,
      infrastructure_fragility_pct: 55.0,
      is_demonstration_data: true,
      data_source: "DEMO_SYNTHESIS_CENSUS_PROXY"
    }
  },
  {
    id: "55555555-5555-4555-8555-555555555555",
    name: "Vellarimala Foothills",
    district: "Wayanad",
    taluk: "Vythiri",
    state: "Kerala",
    population: 1420,
    vulnerable_population: 910,
    area_sqm: 340000,
    risk_score: 74,
    risk_severity: "HIGH",
    vulnerability_score: 72,
    vulnerability_severity: "HIGH",
    priority: "SHORT_TERM",
    priority_score: 73,
    geometry: {
      type: "Polygon",
      coordinates: [[[76.10, 11.50], [76.12, 11.50], [76.12, 11.52], [76.10, 11.52], [76.10, 11.50]]]
    },
    factors: {
      rainfall: 88,
      flood_exposure: 70,
      landslide: 76,
      elevation_slope: 72,
      historical_events: 68,
      drainage_proximity: 75,
      hazard_overlap: 68
    },
    explanations: [
      "Runoff accumulation zone receiving mountain drainage",
      "Intermittent flash flood inundation of agricultural pathways"
    ],
    demographics: {
      total_population: 1420,
      vulnerable_population: 910,
      elderly_population: 170,
      children_population: 310,
      disabled_population: 50,
      kutcha_houses_pct: 48.0,
      infrastructure_fragility_pct: 50.0,
      is_demonstration_data: true,
      data_source: "DEMO_SYNTHESIS_CENSUS_PROXY"
    }
  },
  {
    id: "66666666-6666-4666-8666-666666666666",
    name: "Meppadi Bazaar Ward",
    district: "Wayanad",
    taluk: "Vythiri",
    state: "Kerala",
    population: 3400,
    vulnerable_population: 1200,
    area_sqm: 650000,
    risk_score: 48,
    risk_severity: "MODERATE",
    vulnerability_score: 55,
    vulnerability_severity: "MODERATE",
    priority: "MEDIUM_TERM",
    priority_score: 52,
    geometry: {
      type: "Polygon",
      coordinates: [[[76.12, 11.55], [76.14, 11.55], [76.14, 11.57], [76.12, 11.57], [76.12, 11.55]]]
    },
    factors: {
      rainfall: 80,
      flood_exposure: 52,
      landslide: 40,
      elevation_slope: 35,
      historical_events: 45,
      drainage_proximity: 50,
      hazard_overlap: 30
    },
    explanations: [
      "Moderate localized urban waterlogging during torrential spells",
      "Stable geology and good connectivity to state highway"
    ],
    demographics: {
      total_population: 3400,
      vulnerable_population: 1200,
      elderly_population: 380,
      children_population: 620,
      disabled_population: 90,
      kutcha_houses_pct: 22.0,
      infrastructure_fragility_pct: 30.0,
      is_demonstration_data: true,
      data_source: "DEMO_SYNTHESIS_CENSUS_PROXY"
    }
  }
];

export const FALLBACK_HAZARDS = [
  {
    id: "99999999-9999-4999-8999-999999999991",
    hazard_type: "landslide",
    severity: "VERY_HIGH",
    risk_score: 94.0,
    source: "GSI_ISRO_BHUVAN",
    timestamp: new Date().toISOString(),
    geometry: {
      type: "Polygon",
      coordinates: [[[76.12, 11.53], [76.16, 11.53], [76.16, 11.57], [76.12, 11.57], [76.12, 11.53]]]
    }
  },
  {
    id: "99999999-9999-4999-8999-999999999992",
    hazard_type: "flash_flood",
    severity: "CRITICAL",
    risk_score: 91.0,
    source: "CWC_FFG_INCOIS",
    timestamp: new Date().toISOString(),
    geometry: {
      type: "Polygon",
      coordinates: [[[76.14, 11.51], [76.18, 11.51], [76.18, 11.54], [76.14, 11.54], [76.14, 11.51]]]
    }
  },
  {
    id: "99999999-9999-4999-8999-999999999993",
    hazard_type: "debris_flow",
    severity: "HIGH",
    risk_score: 79.0,
    source: "KSDMA_GEOLOGICAL_CELL",
    timestamp: new Date().toISOString(),
    geometry: {
      type: "Polygon",
      coordinates: [[[76.16, 11.49], [76.20, 11.49], [76.20, 11.52], [76.16, 11.52], [76.16, 11.49]]]
    }
  }
];

export const FALLBACK_RELOCATION_SITES = [
  {
    id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
    name: "Meppadi Safe Plateau Zone A",
    district: "Wayanad",
    taluk: "Vythiri",
    state: "Kerala",
    available_area: 125000.0,
    usable_area_sqm: 125000.0,
    current_population: 700,
    current_occupancy: 700,
    estimated_capacity: 3500,
    estimated_carrying_capacity: 3500,
    available_capacity: 2800,
    water_score: 9.2,
    road_access_score: 8.8,
    healthcare_score: 8.5,
    hazard_score: 1.2,
    suitability_score: 89.0,
    overall_suitability_score: 89,
    classification: "HIGHLY SUITABLE",
    hazard_safety_score: 96,
    accessibility_score: 88,
    infrastructure_score: 85,
    capacity_score: 87,
    category_scores: {
      hazard_safety_score: 96,
      accessibility_score: 88,
      infrastructure_score: 85,
      capacity_score: 87
    },
    factor_capacities: {
      usable_land: 3500,
      water_supply: 3100,
      sanitation: 2900,
      healthcare: 3200,
      electricity: 3400,
      road_access: 3200
    },
    limiting_factors: [
      "Sanitation septic absorption field bounds capacity to 2,900 persons",
      "Piped water booster required above 2,500 population"
    ],
    strengths: [
      "Zero flood and landslide hazard overlap",
      "Gentle terrain gradient (< 5°)",
      "Proximity to Meppadi Community Health Centre (3.2 km)",
      "Dedicated two-lane paved road access"
    ],
    limitations: [
      "Sanitation leach line capacity expansion required for long-term influx"
    ],
    geometry: {
      type: "Polygon",
      coordinates: [[[76.11, 11.56], [76.13, 11.56], [76.13, 11.58], [76.11, 11.58], [76.11, 11.56]]]
    }
  },
  {
    id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
    name: "Kalpetta South Ridge Parcel 3",
    district: "Wayanad",
    taluk: "Vythiri",
    state: "Kerala",
    available_area: 95000.0,
    usable_area_sqm: 95000.0,
    current_population: 450,
    current_occupancy: 450,
    estimated_capacity: 2600,
    estimated_carrying_capacity: 2600,
    available_capacity: 2150,
    water_score: 8.5,
    road_access_score: 9.0,
    healthcare_score: 9.2,
    hazard_score: 1.0,
    suitability_score: 86.0,
    overall_suitability_score: 86,
    classification: "HIGHLY SUITABLE",
    hazard_safety_score: 95,
    accessibility_score: 90,
    infrastructure_score: 88,
    capacity_score: 80,
    category_scores: {
      hazard_safety_score: 95,
      accessibility_score: 90,
      infrastructure_score: 88,
      capacity_score: 80
    },
    factor_capacities: {
      usable_land: 2600,
      water_supply: 2400,
      sanitation: 2300,
      healthcare: 3000,
      electricity: 2800,
      road_access: 2900
    },
    limiting_factors: [
      "Municipal water feeder limit (2,400 persons)"
    ],
    strengths: [
      "Direct National Highway access (NH-766)",
      "Proximity to Wayanad District General Hospital (4.5 km)",
      "Solid bedrock foundation with no seismic risk"
    ],
    limitations: [
      "Moderate land acquisition buffer required on southern boundary"
    ],
    geometry: {
      type: "Polygon",
      coordinates: [[[76.08, 11.59], [76.10, 11.59], [76.10, 11.61], [76.08, 11.61], [76.08, 11.59]]]
    }
  },
  {
    id: "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
    name: "Muttil North Safe Terrace",
    district: "Wayanad",
    taluk: "Vythiri",
    state: "Kerala",
    available_area: 45000.0,
    usable_area_sqm: 45000.0,
    current_population: 200,
    current_occupancy: 200,
    estimated_capacity: 1200,
    estimated_carrying_capacity: 1200,
    available_capacity: 1000,
    water_score: 7.8,
    road_access_score: 8.0,
    healthcare_score: 7.5,
    hazard_score: 1.8,
    suitability_score: 76.0,
    overall_suitability_score: 76,
    classification: "SUITABLE",
    hazard_safety_score: 90,
    accessibility_score: 78,
    infrastructure_score: 74,
    capacity_score: 70,
    category_scores: {
      hazard_safety_score: 90,
      accessibility_score: 78,
      infrastructure_score: 74,
      capacity_score: 70
    },
    factor_capacities: {
      usable_land: 1200,
      water_supply: 1100,
      sanitation: 1050,
      healthcare: 1200,
      electricity: 1300,
      road_access: 1150
    },
    limiting_factors: [
      "Groundwater recharge rate limits intake to 1,050 persons"
    ],
    strengths: [
      "Elevated natural plateau unaffected by flooding",
      "Immediate municipal power grid tie-in"
    ],
    limitations: [
      "Secondary approach road needs surface widening"
    ],
    geometry: {
      type: "Polygon",
      coordinates: [[[76.12, 11.62], [76.14, 11.62], [76.14, 11.64], [76.12, 11.64], [76.12, 11.62]]]
    }
  }
];

export const FALLBACK_ALERTS = [
  {
    id: "88888888-8888-4888-8888-888888888881",
    disaster_type: "landslide",
    severity: "CRITICAL",
    event_time: new Date().toISOString(),
    source: "NDMA_SACHET_CAP",
    description: "IMMEDIATE EVACUATION: Landslide danger level crossed in Mundakkai-Chooralmala slopes following 380mm rainfall in 24 hours.",
    geometry: {
      type: "Point",
      coordinates: [76.14, 11.55]
    }
  },
  {
    id: "88888888-8888-4888-8888-888888888882",
    disaster_type: "flash_flood",
    severity: "HIGH",
    event_time: new Date(Date.now() - 3600000).toISOString(),
    source: "CWC_WIMS",
    description: "River Iruvaipuzha at Chooralmala gauge exceeded Danger Mark (+1.42m). Flood surge expected along low-lying tea estate banks.",
    geometry: {
      type: "Point",
      coordinates: [76.16, 11.53]
    }
  },
  {
    id: "88888888-8888-4888-8888-888888888883",
    disaster_type: "heavy_rainfall",
    severity: "HIGH",
    event_time: new Date(Date.now() - 7200000).toISOString(),
    source: "IMD_RADAR",
    description: "Extremely Heavy Rainfall (Red Alert) ongoing across Vythiri and Meppadi taluks for the next 12 hours.",
    geometry: {
      type: "Point",
      coordinates: [76.13, 11.54]
    }
  },
  {
    id: "88888888-8888-4888-8888-888888888884",
    disaster_type: "road_blockage",
    severity: "MODERATE",
    event_time: new Date(Date.now() - 10800000).toISOString(),
    source: "KSDMA_EOC",
    description: "Partial road blockage on Meppadi-Chooralmala road due to uprooted trees and localized mudslide. Egress via south bypass.",
    geometry: {
      type: "Point",
      coordinates: [76.145, 11.545]
    }
  }
];

export const FALLBACK_ANALYTICS = {
  total_habitations: 18,
  total_population: 26800,
  total_vulnerable_population: 9450,
  total_safe_capacity: 6150,
  regional_net_balance: -3300,
  risk_distribution: [
    { bracket: "0-30 (LOW)", count: 4, population: 7500, vulnerable_population: 1100 },
    { bracket: "31-60 (MODERATE)", count: 7, population: 11200, vulnerable_population: 2510 },
    { bracket: "61-80 (HIGH)", count: 4, population: 4200, vulnerable_population: 2150 },
    { bracket: "81-100 (CRITICAL)", count: 3, population: 3900, vulnerable_population: 3690 },
  ],
  vulnerability_factors: [
    { factor: "Total Population", average_score: 68.5, highest_habitation: "Mundakkai Settlement", critical_habitations_count: 5 },
    { factor: "Vulnerable Population Share", average_score: 72.1, highest_habitation: "Mundakkai Settlement", critical_habitations_count: 6 },
    { factor: "Population Density", average_score: 54.0, highest_habitation: "Meppadi Bazaar Ward", critical_habitations_count: 2 },
    { factor: "Elderly Population Proportion", average_score: 64.2, highest_habitation: "Mundakkai Settlement", critical_habitations_count: 4 },
    { factor: "Children Proportion", average_score: 66.8, highest_habitation: "Chooralmala Hamlet", critical_habitations_count: 4 },
    { factor: "Persons with Disabilities", average_score: 59.4, highest_habitation: "Mundakkai Settlement", critical_habitations_count: 3 },
    { factor: "Kutcha Housing Fragility", average_score: 78.5, highest_habitation: "Mundakkai Settlement", critical_habitations_count: 7 },
    { factor: "Infrastructure Vulnerability", average_score: 71.0, highest_habitation: "Attamala Estate Quarters", critical_habitations_count: 5 },
    { factor: "Evacuation Route Difficulty", average_score: 76.3, highest_habitation: "Attamala Estate Quarters", critical_habitations_count: 6 },
  ],
  capacity_vs_need: [
    {
      site_id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
      site_name: "Meppadi Safe Plateau Zone A",
      usable_area_sqm: 125000.0,
      total_capacity: 3500,
      available_capacity: 2800,
      matched_demand_population: 2570,
      balance: 230,
      status: "SURPLUS"
    },
    {
      site_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
      site_name: "Kalpetta South Ridge Parcel 3",
      usable_area_sqm: 95000.0,
      total_capacity: 2600,
      available_capacity: 2150,
      matched_demand_population: 890,
      balance: 1260,
      status: "SURPLUS"
    },
    {
      site_id: "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
      site_name: "Muttil North Safe Terrace",
      usable_area_sqm: 45000.0,
      total_capacity: 1200,
      available_capacity: 1000,
      matched_demand_population: 1530,
      balance: -530,
      status: "DEFICIT"
    }
  ],
  hazard_exposures: [
    { hazard_type: "landslide", affected_habitations: 7, affected_population: 9800, critical_overlap_count: 4 },
    { hazard_type: "flood", affected_habitations: 5, affected_population: 7400, critical_overlap_count: 3 },
    { hazard_type: "cloudburst", affected_habitations: 4, affected_population: 5200, critical_overlap_count: 2 },
    { hazard_type: "debris_flow", affected_habitations: 3, affected_population: 3900, critical_overlap_count: 2 },
  ]
};

export const FALLBACK_DATA_SOURCES = {
  total_sources: 4,
  sources: [
    {
      source_id: "mosdac_isro",
      source: "ISRO MOSDAC Satellite Telemetry (INSAT-3D/3DR Hydro-Estimator)",
      category: "SATELLITE_PRECIPITATION",
      status: "DEMO_MODE",
      data_mode: "DEMONSTRATION_PROXY",
      is_mock_data: true,
      last_update: new Date().toISOString(),
      data_freshness: "12m ago",
      records_ingested_last_run: 2,
      total_records_ingested: 48,
      latency_ms: 1.25,
      last_error: null
    },
    {
      source_id: "cwc_wims",
      source: "Central Water Commission (CWC) WIMS River Stage Gauging",
      category: "HYDROLOGY",
      status: "DEMO_MODE",
      data_mode: "DEMONSTRATION_PROXY",
      is_mock_data: true,
      last_update: new Date().toISOString(),
      data_freshness: "5m ago",
      records_ingested_last_run: 2,
      total_records_ingested: 42,
      latency_ms: 0.95,
      last_error: null
    },
    {
      source_id: "ndma_sachet",
      source: "NDMA SACHET Common Alerting Protocol (CAP v1.2) Feed",
      category: "DISASTER_ALERTS",
      status: "DEMO_MODE",
      data_mode: "DEMONSTRATION_PROXY",
      is_mock_data: true,
      last_update: new Date().toISOString(),
      data_freshness: "Just now",
      records_ingested_last_run: 1,
      total_records_ingested: 26,
      latency_ms: 0.82,
      last_error: null
    },
    {
      source_id: "imd_weather",
      source: "India Meteorological Department (IMD) Automated Weather Station",
      category: "METEOROLOGY",
      status: "DEMO_MODE",
      data_mode: "DEMONSTRATION_PROXY",
      is_mock_data: true,
      last_update: new Date().toISOString(),
      data_freshness: "8m ago",
      records_ingested_last_run: 2,
      total_records_ingested: 36,
      latency_ms: 1.10,
      last_error: null
    }
  ],
  recent_logs: [
    {
      timestamp: new Date().toISOString(),
      source_id: "mosdac_isro",
      status: "SUCCESS",
      records_count: 2,
      duration_ms: 1.25,
      message: "Fetched 2 records, 2 inserted, 0 duplicates skipped"
    },
    {
      timestamp: new Date(Date.now() - 300000).toISOString(),
      source_id: "cwc_wims",
      status: "SUCCESS",
      records_count: 2,
      duration_ms: 0.95,
      message: "Fetched 2 gauge readings, 2 inserted, 0 duplicates skipped"
    }
  ]
};
