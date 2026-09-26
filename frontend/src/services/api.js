import axios from 'axios';
import {
  FALLBACK_DASHBOARD,
  FALLBACK_HABITATIONS,
  FALLBACK_HAZARDS,
  FALLBACK_RELOCATION_SITES,
  FALLBACK_ALERTS,
  FALLBACK_ANALYTICS,
  FALLBACK_DATA_SOURCES,
} from '../data/fallbackData';
import {
  MULTI_HAZARD_GEOJSON,
  FLOOD_ZONES_GEOJSON,
  LANDSLIDE_ZONES_GEOJSON,
  HEAVY_RAINFALL_GEOJSON,
  HABITATIONS_GEOJSON,
  RELOCATION_SITES_GEOJSON,
  RIVERS_GEOJSON,
  ROADS_GEOJSON,
  HOSPITALS_GEOJSON,
  SCHOOLS_GEOJSON,
} from '../data/gisLayersData';

// Base API configuration (proxied via Vite or direct)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
export const BACKEND_ROOT_URL = API_BASE_URL.replace(/\/api(\/v1)?\/?$/, '');

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.warn('[API Warning]', error?.config?.url, error?.message);
    return Promise.reject(error);
  }
);

// Diagnostic Health Check
export const checkSystemHealth = async () => {
  const startTime = performance.now();
  try {
    const res = await axios.get('/health', { timeout: 4000 });
    return {
      success: true,
      data: res.data,
      latency: Math.round(performance.now() - startTime),
      error: null,
    };
  } catch (err) {
    return {
      success: false,
      data: { status: 'offline', version: '1.0.0', project: 'SIH26191', database: 'disconnected' },
      latency: Math.round(performance.now() - startTime),
      error: err.message,
    };
  }
};

// 1. Dashboard API
export const getDashboardData = async () => {
  try {
    const res = await apiClient.get('/dashboard');
    return { isLive: true, data: res.data };
  } catch (err) {
    return { isLive: false, data: FALLBACK_DASHBOARD };
  }
};

// 2. Hazards API
export const getHazards = async (params = {}) => {
  try {
    const res = await apiClient.get('/hazards', { params });
    return { isLive: true, data: res.data };
  } catch (err) {
    return {
      isLive: false,
      data: {
        total: FALLBACK_HAZARDS.length,
        page: 1,
        page_size: 20,
        total_pages: 1,
        items: FALLBACK_HAZARDS,
      },
    };
  }
};

export const getHazardsGeoJSON = async () => {
  try {
    const res = await apiClient.get('/hazards/geojson');
    return { isLive: true, data: res.data };
  } catch (err) {
    return {
      isLive: false,
      data: {
        type: 'FeatureCollection',
        features: FALLBACK_HAZARDS.map((h) => ({
          type: 'Feature',
          geometry: h.geometry,
          properties: {
            id: h.id,
            hazard_type: h.hazard_type,
            severity: h.severity,
            risk_score: h.risk_score,
            source: h.source,
          },
        })),
      },
    };
  }
};

export const getHazardById = async (id) => {
  try {
    const res = await apiClient.get(`/hazards/${id}`);
    return { isLive: true, data: res.data };
  } catch (err) {
    const found = FALLBACK_HAZARDS.find((h) => h.id === id) || FALLBACK_HAZARDS[0];
    return { isLive: false, data: found };
  }
};

// 3. Habitations API
export const getHabitations = async (params = {}) => {
  try {
    const res = await apiClient.get('/habitations', { params });
    return { isLive: true, data: res.data };
  } catch (err) {
    let items = [...FALLBACK_HABITATIONS];
    if (params.search) {
      const q = params.search.toLowerCase();
      items = items.filter((h) => h.name.toLowerCase().includes(q) || h.district.toLowerCase().includes(q));
    }
    return {
      isLive: false,
      data: {
        total: items.length,
        page: params.page || 1,
        page_size: params.page_size || 20,
        total_pages: 1,
        items,
      },
    };
  }
};

export const getHabitationsGeoJSON = async () => {
  try {
    const res = await apiClient.get('/habitations/geojson');
    return { isLive: true, data: res.data };
  } catch (err) {
    return {
      isLive: false,
      data: HABITATIONS_GEOJSON,
    };
  }
};

export const getHabitationById = async (id) => {
  try {
    const res = await apiClient.get(`/habitations/${id}`);
    return { isLive: true, data: res.data };
  } catch (err) {
    const found = FALLBACK_HABITATIONS.find((h) => h.id === id) || FALLBACK_HABITATIONS[0];
    return { isLive: false, data: found };
  }
};

export const getHabitationRisk = async (id) => {
  try {
    const res = await apiClient.get(`/habitations/${id}/risk`);
    return { isLive: true, data: res.data };
  } catch (err) {
    const h = FALLBACK_HABITATIONS.find((item) => item.id === id) || FALLBACK_HABITATIONS[0];
    return {
      isLive: false,
      data: {
        habitation_id: h.id,
        habitation_name: h.name,
        overall_score: h.risk_score,
        severity: h.risk_severity,
        factors: h.factors,
        explanation: h.explanations,
        geometry: h.geometry,
      },
    };
  }
};

export const getHabitationVulnerability = async (id) => {
  try {
    const res = await apiClient.get(`/habitations/${id}/vulnerability`);
    return { isLive: true, data: res.data };
  } catch (err) {
    const h = FALLBACK_HABITATIONS.find((item) => item.id === id) || FALLBACK_HABITATIONS[0];
    return {
      isLive: false,
      data: {
        habitation_id: h.id,
        habitation_name: h.name,
        vulnerability_score: h.vulnerability_score,
        severity: h.vulnerability_severity,
        factors: {
          total_population: 85,
          vulnerable_population: 88,
          population_density: 65,
          elderly_population: 74,
          children_population: 78,
          disabled_population: 70,
          housing_vulnerability: 82,
          infrastructure_vulnerability: 75,
          evacuation_accessibility: 84,
        },
        demographics: h.demographics,
        explanation: h.explanations,
        geometry: h.geometry,
      },
    };
  }
};

// 4. Vulnerability Summary API
export const getVulnerabilitySummary = async () => {
  try {
    const res = await apiClient.get('/vulnerability/summary');
    return { isLive: true, data: res.data };
  } catch (err) {
    return {
      isLive: false,
      data: {
        total_habitations: FALLBACK_HABITATIONS.length,
        severity_breakdown: { CRITICAL: 3, HIGH: 2, MODERATE: 1, LOW: 0 },
        average_vulnerability_score: 79.5,
        critical_vulnerability_count: 3,
        habitations: FALLBACK_HABITATIONS,
      },
    };
  }
};

// 5. Relocation Sites API
export const getRelocationSites = async (params = {}) => {
  try {
    const res = await apiClient.get('/relocation-sites', { params });
    return { isLive: true, data: res.data };
  } catch (err) {
    return {
      isLive: false,
      data: {
        total: FALLBACK_RELOCATION_SITES.length,
        page: 1,
        page_size: 20,
        total_pages: 1,
        items: FALLBACK_RELOCATION_SITES,
      },
    };
  }
};

export const getRelocationSitesGeoJSON = async () => {
  try {
    const res = await apiClient.get('/relocation-sites/geojson');
    return { isLive: true, data: res.data };
  } catch (err) {
    return {
      isLive: false,
      data: RELOCATION_SITES_GEOJSON,
    };
  }
};

export const getRelocationSiteById = async (id) => {
  try {
    const res = await apiClient.get(`/relocation-sites/${id}`);
    return { isLive: true, data: res.data };
  } catch (err) {
    const found = FALLBACK_RELOCATION_SITES.find((s) => s.id === id) || FALLBACK_RELOCATION_SITES[0];
    return { isLive: false, data: found };
  }
};

export const getRelocationSiteAssessment = async (id) => {
  try {
    const res = await apiClient.get(`/relocation-sites/${id}/assessment`);
    return { isLive: true, data: res.data };
  } catch (err) {
    const found = FALLBACK_RELOCATION_SITES.find((s) => s.id === id) || FALLBACK_RELOCATION_SITES[0];
    return {
      isLive: false,
      data: {
        site_id: found.id,
        site_name: found.name,
        suitability_score: found.suitability_score,
        overall_suitability_score: found.overall_suitability_score,
        classification: found.classification,
        hazard_safety_score: found.hazard_safety_score,
        accessibility_score: found.accessibility_score,
        infrastructure_score: found.infrastructure_score,
        capacity_score: found.capacity_score,
        category_scores: found.category_scores,
        strengths: found.strengths,
        limitations: found.limitations,
        available_capacity: found.available_capacity,
        estimated_capacity: found.estimated_capacity,
        available_area_sqm: found.available_area,
        geometry: found.geometry,
      },
    };
  }
};

export const getRelocationSiteCapacity = async (id) => {
  try {
    const res = await apiClient.get(`/relocation-sites/${id}/capacity`);
    return { isLive: true, data: res.data };
  } catch (err) {
    const found = FALLBACK_RELOCATION_SITES.find((s) => s.id === id) || FALLBACK_RELOCATION_SITES[0];
    return {
      isLive: false,
      data: {
        site_id: found.id,
        site_name: found.name,
        gross_capacity: found.estimated_capacity,
        infrastructure_capacity: Math.round(found.estimated_capacity * 0.85),
        water_capacity: Math.round(found.estimated_capacity * 0.82),
        final_capacity: found.available_capacity + found.current_population,
        current_population: found.current_population,
        available_capacity: found.available_capacity,
        limiting_factors: found.limiting_factors,
        factor_capacities: found.factor_capacities,
      },
    };
  }
};

export const getNearbyRelocationSites = async (habitationId, params = {}) => {
  try {
    const res = await apiClient.get(`/relocation-sites/nearby/${habitationId}`, { params });
    return { isLive: true, data: res.data };
  } catch (err) {
    return {
      isLive: false,
      data: {
        habitation_id: habitationId,
        habitation_name: "Mundakkai Settlement",
        vulnerable_population: 1450,
        total_sites_found: FALLBACK_RELOCATION_SITES.length,
        recommended_sites: FALLBACK_RELOCATION_SITES.map((s, idx) => ({
          site_id: s.id,
          site_name: s.name,
          distance_km: 3.5 + idx * 2.8,
          distance_meters: (3.5 + idx * 2.8) * 1000,
          available_capacity: s.available_capacity,
          suitability_score: s.suitability_score,
          classification: s.classification,
          hazard_safe: true,
          proximity_rank: idx + 1,
          geometry: s.geometry,
        })),
      },
    };
  }
};

// 6. Relocation Prioritization API
export const getRelocationPriorities = async (params = {}) => {
  try {
    const res = await apiClient.get('/relocation/priorities', { params });
    return { isLive: true, data: res.data };
  } catch (err) {
    return {
      isLive: false,
      data: {
        total_habitations: FALLBACK_HABITATIONS.length,
        immediate_count: 3,
        short_term_count: 2,
        medium_term_count: 1,
        monitor_count: 0,
        average_priority_score: 81.2,
        priorities: FALLBACK_HABITATIONS.map((h, i) => ({
          habitation_id: h.id,
          habitation_name: h.name,
          district: h.district,
          state: h.state,
          priority: h.priority,
          priority_score: h.priority_score,
          hazard_score: h.risk_score,
          vulnerability_score: h.vulnerability_score,
          vulnerable_population: h.vulnerable_population,
          total_population: h.population,
          reasons: h.explanations,
          recommended_site_id: FALLBACK_RELOCATION_SITES[i % FALLBACK_RELOCATION_SITES.length].id,
          recommended_site_name: FALLBACK_RELOCATION_SITES[i % FALLBACK_RELOCATION_SITES.length].name,
          recommended_site_distance_km: 3.8 + i * 1.5,
        })),
        decision_support_disclaimer: "PROTOTYPE DECISION SUPPORT SYSTEM: For official evaluation by NDMA/SDMA/DDMA authorities.",
      },
    };
  }
};

export const getRelocationRecommendation = async (habitationId) => {
  try {
    const res = await apiClient.get(`/relocation/recommendation/${habitationId}`);
    return { isLive: true, data: res.data };
  } catch (err) {
    const h = FALLBACK_HABITATIONS.find((item) => item.id === habitationId) || FALLBACK_HABITATIONS[0];
    const bestSite = FALLBACK_RELOCATION_SITES[0];
    return {
      isLive: false,
      data: {
        habitation_id: h.id,
        habitation_name: h.name,
        priority: h.priority,
        priority_score: h.priority_score,
        vulnerable_population: h.vulnerable_population,
        total_population: h.population,
        reasons: h.explanations,
        best_suitable_site: {
          site_id: bestSite.id,
          site_name: bestSite.name,
          distance_km: 4.2,
          distance_meters: 4200.0,
          suitability_score: bestSite.suitability_score,
          classification: bestSite.classification,
          available_capacity: bestSite.available_capacity,
          capacity_sufficient: bestSite.available_capacity >= h.vulnerable_population,
          match_score: 91.5,
        },
        alternative_sites: FALLBACK_RELOCATION_SITES.slice(1).map((s, idx) => ({
          site_id: s.id,
          site_name: s.name,
          distance_km: 6.8 + idx * 3.0,
          suitability_score: s.suitability_score,
          available_capacity: s.available_capacity,
          capacity_sufficient: s.available_capacity >= h.vulnerable_population,
        })),
        decision_support_disclaimer: "PROTOTYPE DECISION SUPPORT SYSTEM: Strictly advisory for disaster response authorities.",
      },
    };
  }
};

// 7. Alerts API
export const getAlerts = async (params = {}) => {
  try {
    const res = await apiClient.get('/alerts', { params });
    return { isLive: true, data: res.data };
  } catch (err) {
    return {
      isLive: false,
      data: {
        total: FALLBACK_ALERTS.length,
        page: 1,
        page_size: 20,
        total_pages: 1,
        items: FALLBACK_ALERTS,
      },
    };
  }
};

export const getAlertsGeoJSON = async () => {
  try {
    const res = await apiClient.get('/alerts/geojson');
    return { isLive: true, data: res.data };
  } catch (err) {
    return {
      isLive: false,
      data: {
        type: 'FeatureCollection',
        features: FALLBACK_ALERTS.map((a) => ({
          type: 'Feature',
          geometry: a.geometry,
          properties: {
            id: a.id,
            disaster_type: a.disaster_type,
            severity: a.severity,
            event_time: a.event_time,
            source: a.source,
            description: a.description,
          },
        })),
      },
    };
  }
};

// 8. Data Sources & Real-Time Ingestion
export const getDataSourcesStatus = async () => {
  try {
    const res = await apiClient.get('/data-sources/status');
    return { isLive: true, data: res.data };
  } catch (err) {
    return { isLive: false, data: FALLBACK_DATA_SOURCES };
  }
};

export const triggerDataIngestion = async (sourceId = null) => {
  try {
    const url = sourceId ? `/data-sources/trigger?source_id=${sourceId}` : '/data-sources/trigger';
    const res = await apiClient.post(url);
    return { success: true, data: res.data };
  } catch (err) {
    return {
      success: true,
      data: {
        message: "Trigger completed in local demonstration cache",
        source_id: sourceId || "all",
        status: "SUCCESS_DEMO",
        records_ingested: 2,
        timestamp: new Date().toISOString(),
      },
    };
  }
};

// 9. Analytics API
export const getAnalyticsOverview = async () => {
  try {
    const res = await apiClient.get('/analytics');
    return { isLive: true, data: res.data };
  } catch (err) {
    return { isLive: false, data: FALLBACK_ANALYTICS };
  }
};

// 10. GIS Spatial Layers API (Multi-hazard, Floods, Landslides, Rainfall, Rivers, Roads, Hospitals, Schools)
export const getGISLayersOverview = async () => {
  try {
    const res = await apiClient.get('/gis/layers');
    return { isLive: true, data: res.data };
  } catch (err) {
    return {
      isLive: false,
      data: {
        sector: 'Wayanad Disaster Zone',
        layers: [
          { id: 'multi-hazard', name: 'Multi-hazard risk' },
          { id: 'flood-zones', name: 'Flood zones' },
          { id: 'landslide-zones', name: 'Landslide zones' },
          { id: 'heavy-rainfall', name: 'Heavy rainfall' },
          { id: 'habitations', name: 'Vulnerable habitations' },
          { id: 'relocation-sites', name: 'Relocation sites' },
          { id: 'rivers', name: 'Rivers' },
          { id: 'roads', name: 'Roads' },
          { id: 'hospitals', name: 'Hospitals' },
          { id: 'schools', name: 'Schools' },
        ],
      },
    };
  }
};

export const getGISMultiHazardGeoJSON = async () => {
  try {
    const res = await apiClient.get('/gis/multi-hazard');
    return { isLive: true, data: res.data };
  } catch (err) {
    return { isLive: false, data: MULTI_HAZARD_GEOJSON };
  }
};

export const getGISFloodZonesGeoJSON = async () => {
  try {
    const res = await apiClient.get('/gis/flood-zones');
    return { isLive: true, data: res.data };
  } catch (err) {
    return { isLive: false, data: FLOOD_ZONES_GEOJSON };
  }
};

export const getGISLandslideZonesGeoJSON = async () => {
  try {
    const res = await apiClient.get('/gis/landslide-zones');
    return { isLive: true, data: res.data };
  } catch (err) {
    return { isLive: false, data: LANDSLIDE_ZONES_GEOJSON };
  }
};

export const getGISRainfallGeoJSON = async () => {
  try {
    const res = await apiClient.get('/gis/rainfall');
    return { isLive: true, data: res.data };
  } catch (err) {
    return { isLive: false, data: HEAVY_RAINFALL_GEOJSON };
  }
};

export const getGISRiversGeoJSON = async () => {
  try {
    const res = await apiClient.get('/gis/rivers');
    return { isLive: true, data: res.data };
  } catch (err) {
    return { isLive: false, data: RIVERS_GEOJSON };
  }
};

export const getGISRoadsGeoJSON = async () => {
  try {
    const res = await apiClient.get('/gis/roads');
    return { isLive: true, data: res.data };
  } catch (err) {
    return { isLive: false, data: ROADS_GEOJSON };
  }
};

export const getGISHospitalsGeoJSON = async () => {
  try {
    const res = await apiClient.get('/gis/hospitals');
    return { isLive: true, data: res.data };
  } catch (err) {
    return { isLive: false, data: HOSPITALS_GEOJSON };
  }
};

export const getGISSchoolsGeoJSON = async () => {
  try {
    const res = await apiClient.get('/gis/schools');
    return { isLive: true, data: res.data };
  } catch (err) {
    return { isLive: false, data: SCHOOLS_GEOJSON };
  }
};

// 11. Live Disaster Event Streaming (Server-Sent Events) & Scenario Simulation
export const getRecentDisasterEvents = async (limit = 20) => {
  try {
    const res = await apiClient.get(`/events/recent?limit=${limit}`);
    return { isLive: true, data: res.data };
  } catch (err) {
    return {
      isLive: false,
      data: {
        total: 3,
        events: [
          {
            id: 'evt-init-1',
            event_type: 'NEW_ALERT',
            headline: 'Heavy rainfall alert detected: 382mm registered in Vythiri catchment',
            severity: 'CRITICAL',
            timestamp: new Date().toISOString(),
            data: { observation_type: 'rainfall', rainfall_mm: 382.0 },
            disclaimer: 'Advisory assessment: Relocation actions require competent administrative authority validation.',
          },
          {
            id: 'evt-init-2',
            event_type: 'HABITATION_PRIORITY_CHANGED',
            headline: '12 habitations have moved to HIGH risk',
            severity: 'HIGH',
            timestamp: new Date().toISOString(),
            data: { total_affected: 12, immediate_assessment_count: 3 },
            disclaimer: 'Advisory assessment: Relocation actions require competent administrative authority validation.',
          },
          {
            id: 'evt-init-3',
            event_type: 'HABITATION_PRIORITY_CHANGED',
            headline: '3 habitations require immediate assessment',
            severity: 'CRITICAL',
            timestamp: new Date().toISOString(),
            data: { immediate_assessment_count: 3 },
            disclaimer: 'Advisory assessment: Relocation actions require competent administrative authority validation.',
          },
        ],
      },
    };
  }
};

export const simulateDisasterScenario = async (scenario = 'heavy_rainfall') => {
  try {
    const res = await apiClient.post(`/events/simulate?scenario=${scenario}`);
    return { success: true, data: res.data };
  } catch (err) {
    // High-fidelity fallback simulation when backend is starting or offline
    const now = new Date().toISOString();
    let headline = 'Heavy rainfall alert detected';
    let severity = 'CRITICAL';
    if (scenario === 'river_surge') {
      headline = '12 habitations have moved to HIGH risk following river-level surge';
      severity = 'CRITICAL';
    } else if (scenario === 'landslide_warning') {
      headline = '3 habitations require immediate assessment for assisted egress';
      severity = 'CRITICAL';
    }

    return {
      success: true,
      data: {
        status: 'SUCCESS_DEMO',
        scenario,
        message: '6-step simulation executed in local demonstration mode.',
        pipeline_result: {
          observation_stored: true,
          affected_regions: ['Wayanad District', 'Vythiri Taluk', 'Meppadi Plateau Catchment', 'Mundakkai Slope'],
          hazards_updated: [
            { hazard_type: scenario === 'river_surge' ? 'flash_flood' : 'landslide', risk_score: 95, severity },
          ],
          priority_changes: [
            { habitation_name: 'Mundakkai Settlement', priority: 'IMMEDIATE', priority_score: 94 },
            { habitation_name: 'Chooralmala Hamlet', priority: 'IMMEDIATE', priority_score: 91 },
            { habitation_name: 'Attamala Quarters', priority: 'IMMEDIATE', priority_score: 88 },
          ],
          candidate_sites: [
            { site_name: 'Meppadi Safe Plateau Zone A', suitability_score: 89, available_capacity: 2800 },
          ],
          dashboard_summary: {
            total_habitations: 18,
            habitations_in_critical_zones: 6,
            population_at_risk: 5840,
            immediate_relocation_count: 3,
            available_relocation_capacity: 4950,
          },
        },
      },
    };
  }
};

/**
 * Connects to Server-Sent Events (SSE) live stream with automatic reconnect
 * and structured dispatch for NEW_ALERT, HAZARD_UPDATED, HABITATION_PRIORITY_CHANGED, RELOCATION_SITE_UPDATED, DASHBOARD_UPDATED.
 */
export const connectDisasterEventStream = (onEvent, onError) => {
  const sseUrl = `${BACKEND_ROOT_URL}/api/v1/events/stream`;
  let eventSource = null;

  try {
    eventSource = new EventSource(sseUrl);

    // Standard message or generic event
    eventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (onEvent) onEvent(payload);
      } catch (parseErr) {
        console.warn('[SSE Parse Error]', parseErr);
      }
    };

    // Specific event listeners for all 4 required event types + dashboard & connected
    const eventTypes = [
      'NEW_ALERT',
      'HAZARD_UPDATED',
      'HABITATION_PRIORITY_CHANGED',
      'RELOCATION_SITE_UPDATED',
      'DASHBOARD_UPDATED',
      'CONNECTED',
    ];

    eventTypes.forEach((eventType) => {
      eventSource.addEventListener(eventType, (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (onEvent) onEvent({ ...payload, event_type: eventType });
        } catch (parseErr) {
          console.warn(`[SSE ${eventType} Parse Error]`, parseErr);
        }
      });
    });

    eventSource.onerror = (err) => {
      if (onError) onError(err);
    };

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  } catch (err) {
    if (onError) onError(err);
    return () => {};
  }
};


