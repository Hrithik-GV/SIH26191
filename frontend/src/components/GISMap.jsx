import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import maplibregl from 'maplibre-gl';
import {
  Layers,
  Search,
  Compass,
  Eye,
  EyeOff,
  Flame,
  Home,
  ShieldCheck,
  AlertCircle,
  Maximize2,
  Minimize2,
  ZoomIn,
  ZoomOut,
  Waves,
  Navigation,
  School,
  HeartPulse,
  CloudRain,
  MapPin,
  ChevronDown,
  ChevronUp,
  X,
  Filter,
  Check,
  Layers as LayersIcon,
  Crosshair,
  Info,
} from 'lucide-react';

import {
  getGISMultiHazardGeoJSON,
  getGISFloodZonesGeoJSON,
  getGISLandslideZonesGeoJSON,
  getGISRainfallGeoJSON,
  getGISRiversGeoJSON,
  getGISRoadsGeoJSON,
  getGISHospitalsGeoJSON,
  getGISSchoolsGeoJSON,
  getHabitationsGeoJSON,
  getRelocationSitesGeoJSON,
} from '../services/api';

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

// Wayanad Disaster Sector Center
const WAYANAD_COORDS = [76.14, 11.545];

// Sector Quick-Jump Locations
const SECTOR_BOOKMARKS = [
  {
    id: 'wayanad-overview',
    name: 'Wayanad Sector Overview',
    coords: [76.14, 11.545],
    zoom: 11.8,
    pitch: 25,
    bearing: -5,
    desc: 'Entire disaster monitoring perimeter',
  },
  {
    id: 'mundakkai',
    name: 'Mundakkai Ground Zero',
    coords: [76.14, 11.548],
    zoom: 14.5,
    pitch: 45,
    bearing: -15,
    desc: 'Debris flow origin & punchirimattam scarp',
  },
  {
    id: 'chooralmala',
    name: 'Chooralmala River Basin',
    coords: [76.16, 11.530],
    zoom: 14.5,
    pitch: 40,
    bearing: 10,
    desc: 'Iruvaipuzha flash flood & Bailey Bridge crossing',
  },
  {
    id: 'attamala',
    name: 'Attamala Mountain Ridge',
    coords: [76.18, 11.510],
    zoom: 14.2,
    pitch: 45,
    bearing: -20,
    desc: 'Upper tea estate slopes & restricted access road',
  },
  {
    id: 'meppadi',
    name: 'Meppadi Safe Plateau',
    coords: [76.12, 11.565],
    zoom: 14.0,
    pitch: 35,
    bearing: 5,
    desc: 'Primary safe relocation haven & CHC triage hub',
  },
  {
    id: 'kalpetta',
    name: 'Kalpetta District EOC HQ',
    coords: [76.085, 11.605],
    zoom: 13.8,
    pitch: 25,
    bearing: 0,
    desc: 'District administrative headquarters & referral hospital',
  },
];

// Dark tactical raster basemap
const DARK_TACTICAL_STYLE = {
  version: 8,
  sources: {
    'carto-dark': {
      type: 'raster',
      tiles: [
        'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
        'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
        'https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
      ],
      tileSize: 256,
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    },
  },
  layers: [
    {
      id: 'carto-dark-layer',
      type: 'raster',
      source: 'carto-dark',
      minzoom: 0,
      maxzoom: 19,
    },
  ],
};

export default function GISMap({
  onSelectEntity,
  selectedEntity,
  className = '',
  height = '560px',
  focusCoords = null,
}) {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const popupRef = useRef(null);

  // High performance: Store large GeoJSON FeatureCollections in a ref cache rather than React state
  const geoJsonCacheRef = useRef({
    multiHazard: MULTI_HAZARD_GEOJSON,
    floodZones: FLOOD_ZONES_GEOJSON,
    landslideZones: LANDSLIDE_ZONES_GEOJSON,
    heavyRainfall: HEAVY_RAINFALL_GEOJSON,
    habitations: HABITATIONS_GEOJSON,
    relocationSites: RELOCATION_SITES_GEOJSON,
    rivers: RIVERS_GEOJSON,
    roads: ROADS_GEOJSON,
    hospitals: HOSPITALS_GEOJSON,
    schools: SCHOOLS_GEOJSON,
  });

  // Flat search index maintained in ref for rapid lookup
  const searchIndexRef = useRef([]);

  const [mapLoaded, setMapLoaded] = useState(false);

  // 10 Layer Toggles State (as required by prompt)
  const [layersVisible, setLayersVisible] = useState({
    multiHazard: true,
    floodZones: true,
    landslideZones: true,
    heavyRainfall: true,
    habitations: true,
    relocationSites: true,
    rivers: true,
    roads: true,
    hospitals: true,
    schools: true,
  });

  // UI Panels State
  const [showLayerPanel, setShowLayerPanel] = useState(false);
  const [showLegend, setShowLegend] = useState(true);
  const [showQuickJump, setShowQuickJump] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [is3D, setIs3D] = useState(false);
  const [activeBookmark, setActiveBookmark] = useState('wayanad-overview');

  // Active layer count calculation
  const activeLayersCount = useMemo(() => {
    return Object.values(layersVisible).filter(Boolean).length;
  }, [layersVisible]);

  // Helper to safely update or add GeoJSON source in MapLibre
  const updateMapSource = useCallback((sourceId, geojsonData) => {
    const map = mapRef.current;
    if (!map) return;
    const source = map.getSource(sourceId);
    if (source) {
      source.setData(geojsonData);
    } else {
      map.addSource(sourceId, {
        type: 'geojson',
        data: geojsonData,
      });
    }
  }, []);

  // Highlight selected feature with glowing halo
  const highlightSelectedFeature = useCallback((geometry) => {
    const map = mapRef.current;
    if (!map || !map.getSource('selected-highlight-source')) return;

    if (!geometry) {
      map.getSource('selected-highlight-source').setData({
        type: 'FeatureCollection',
        features: [],
      });
      return;
    }

    map.getSource('selected-highlight-source').setData({
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry,
          properties: {},
        },
      ],
    });
  }, []);

  // Build searchable index from cached features
  const rebuildSearchIndex = useCallback(() => {
    const items = [];

    // Habitations
    (geoJsonCacheRef.current.habitations?.features || []).forEach((f) => {
      items.push({
        id: f.id || f.properties?.id,
        name: f.properties?.name || 'Habitation',
        type: 'habitation',
        category: 'Habitation',
        priority: f.properties?.priority || 'IMMEDIATE',
        risk_score: f.properties?.hazard_score || f.properties?.risk_score || 85,
        geometry: f.geometry,
        center: getFeatureCenter(f.geometry),
        properties: f.properties,
      });
    });

    // Relocation Sites
    (geoJsonCacheRef.current.relocationSites?.features || []).forEach((f) => {
      items.push({
        id: f.id || f.properties?.id,
        name: f.properties?.site_name || f.properties?.name || 'Relocation Site',
        type: 'relocation_site',
        category: 'Relocation Haven',
        suitability_score: f.properties?.suitability_score || 88,
        geometry: f.geometry,
        center: getFeatureCenter(f.geometry),
        properties: f.properties,
      });
    });

    // Hospitals
    (geoJsonCacheRef.current.hospitals?.features || []).forEach((f) => {
      items.push({
        id: f.id || f.properties?.id,
        name: f.properties?.name || 'Hospital',
        type: 'hospital',
        category: 'Healthcare Facility',
        geometry: f.geometry,
        center: f.geometry?.coordinates || WAYANAD_COORDS,
        properties: f.properties,
      });
    });

    // Schools
    (geoJsonCacheRef.current.schools?.features || []).forEach((f) => {
      items.push({
        id: f.id || f.properties?.id,
        name: f.properties?.name || 'School',
        type: 'school',
        category: 'Shelter Hub',
        geometry: f.geometry,
        center: f.geometry?.coordinates || WAYANAD_COORDS,
        properties: f.properties,
      });
    });

    searchIndexRef.current = items;
  }, []);

  // 1. Initialize MapLibre GL instance
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: DARK_TACTICAL_STYLE,
      center: WAYANAD_COORDS,
      zoom: 11.8,
      pitch: 25,
      bearing: -5,
    });

    map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left');

    map.on('load', () => {
      mapRef.current = map;
      setupLayers(map);
      setMapLoaded(true);
    });

    return () => {
      if (popupRef.current) {
        popupRef.current.remove();
      }
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // 2. Fetch GeoJSON from FastAPI (with immediate local fallback) & populate MapLibre sources
  useEffect(() => {
    async function loadAllGeoJSON() {
      try {
        const [
          multiHazardRes,
          floodRes,
          landslideRes,
          rainfallRes,
          riversRes,
          roadsRes,
          hospitalsRes,
          schoolsRes,
          habitationsRes,
          relocationRes,
        ] = await Promise.all([
          getGISMultiHazardGeoJSON(),
          getGISFloodZonesGeoJSON(),
          getGISLandslideZonesGeoJSON(),
          getGISRainfallGeoJSON(),
          getGISRiversGeoJSON(),
          getGISRoadsGeoJSON(),
          getGISHospitalsGeoJSON(),
          getGISSchoolsGeoJSON(),
          getHabitationsGeoJSON(),
          getRelocationSitesGeoJSON(),
        ]);

        // Directly store in cache ref (avoids putting huge datasets into React state)
        if (multiHazardRes?.data?.features) geoJsonCacheRef.current.multiHazard = multiHazardRes.data;
        if (floodRes?.data?.features) geoJsonCacheRef.current.floodZones = floodRes.data;
        if (landslideRes?.data?.features) geoJsonCacheRef.current.landslideZones = landslideRes.data;
        if (rainfallRes?.data?.features) geoJsonCacheRef.current.heavyRainfall = rainfallRes.data;
        if (riversRes?.data?.features) geoJsonCacheRef.current.rivers = riversRes.data;
        if (roadsRes?.data?.features) geoJsonCacheRef.current.roads = roadsRes.data;
        if (hospitalsRes?.data?.features) geoJsonCacheRef.current.hospitals = hospitalsRes.data;
        if (schoolsRes?.data?.features) geoJsonCacheRef.current.schools = schoolsRes.data;
        if (habitationsRes?.data?.features) geoJsonCacheRef.current.habitations = habitationsRes.data;
        if (relocationRes?.data?.features) geoJsonCacheRef.current.relocationSites = relocationRes.data;

        rebuildSearchIndex();

        // If map is already loaded, update all MapLibre sources
        const map = mapRef.current;
        if (map && mapLoaded) {
          updateMapSource('multi-hazard-source', geoJsonCacheRef.current.multiHazard);
          updateMapSource('flood-zones-source', geoJsonCacheRef.current.floodZones);
          updateMapSource('landslide-zones-source', geoJsonCacheRef.current.landslideZones);
          updateMapSource('heavy-rainfall-source', geoJsonCacheRef.current.heavyRainfall);
          updateMapSource('rivers-source', geoJsonCacheRef.current.rivers);
          updateMapSource('roads-source', geoJsonCacheRef.current.roads);
          updateMapSource('hospitals-source', geoJsonCacheRef.current.hospitals);
          updateMapSource('schools-source', geoJsonCacheRef.current.schools);
          updateMapSource('habitations-source', geoJsonCacheRef.current.habitations);
          updateMapSource('relocation-sites-source', geoJsonCacheRef.current.relocationSites);
        }
      } catch (err) {
        console.error('Error fetching GeoJSON from FastAPI:', err);
      }
    }

    loadAllGeoJSON();
  }, [mapLoaded, updateMapSource, rebuildSearchIndex]);

  // 3. Setup All 10 Layers in MapLibre with intuitive visual hierarchy
  const setupLayers = (map) => {
    // A. Selected Feature Glowing Highlight Source & Layers (at top z-order)
    map.addSource('selected-highlight-source', {
      type: 'geojson',
      data: { type: 'FeatureCollection', features: [] },
    });

    map.addLayer({
      id: 'selected-highlight-fill',
      type: 'fill',
      source: 'selected-highlight-source',
      paint: {
        'fill-color': '#38bdf8',
        'fill-opacity': 0.18,
      },
    });

    map.addLayer({
      id: 'selected-highlight-line',
      type: 'line',
      source: 'selected-highlight-source',
      paint: {
        'line-color': '#38bdf8',
        'line-width': 4,
        'line-blur': 2,
      },
    });

    map.addLayer({
      id: 'selected-highlight-circle',
      type: 'circle',
      source: 'selected-highlight-source',
      paint: {
        'circle-radius': 14,
        'circle-color': 'transparent',
        'circle-stroke-color': '#38bdf8',
        'circle-stroke-width': 3.5,
      },
    });

    // 1. Heavy Rainfall Isohyets Layer (Lowest polygon layer)
    map.addSource('heavy-rainfall-source', {
      type: 'geojson',
      data: geoJsonCacheRef.current.heavyRainfall,
    });

    map.addLayer({
      id: 'heavy-rainfall-fill',
      type: 'fill',
      source: 'heavy-rainfall-source',
      paint: {
        'fill-color': [
          'match',
          ['get', 'alert_tier'],
          'RED_ALERT',
          '#4338ca',
          'ORANGE_ALERT',
          '#3b82f6',
          '#60a5fa',
        ],
        'fill-opacity': 0.22,
      },
    });

    map.addLayer({
      id: 'heavy-rainfall-line',
      type: 'line',
      source: 'heavy-rainfall-source',
      paint: {
        'line-color': '#60a5fa',
        'line-width': 1.5,
        'line-dasharray': [3, 2],
      },
    });

    // 2. Multi-Hazard Risk Layer (Composite envelope)
    map.addSource('multi-hazard-source', {
      type: 'geojson',
      data: geoJsonCacheRef.current.multiHazard,
    });

    map.addLayer({
      id: 'multi-hazard-fill',
      type: 'fill',
      source: 'multi-hazard-source',
      paint: {
        'fill-color': '#be123c',
        'fill-opacity': 0.28,
      },
    });

    map.addLayer({
      id: 'multi-hazard-line',
      type: 'line',
      source: 'multi-hazard-source',
      paint: {
        'line-color': '#f43f5e',
        'line-width': 2.5,
        'line-dasharray': [4, 2],
      },
    });

    // 3. Flood Zones Layer (Riverine inundation)
    map.addSource('flood-zones-source', {
      type: 'geojson',
      data: geoJsonCacheRef.current.floodZones,
    });

    map.addLayer({
      id: 'flood-zones-fill',
      type: 'fill',
      source: 'flood-zones-source',
      paint: {
        'fill-color': '#0284c7',
        'fill-opacity': 0.35,
      },
    });

    map.addLayer({
      id: 'flood-zones-line',
      type: 'line',
      source: 'flood-zones-source',
      paint: {
        'line-color': '#38bdf8',
        'line-width': 2,
      },
    });

    // 4. Landslide Zones Layer (Slope instability & debris scarps)
    map.addSource('landslide-zones-source', {
      type: 'geojson',
      data: geoJsonCacheRef.current.landslideZones,
    });

    map.addLayer({
      id: 'landslide-zones-fill',
      type: 'fill',
      source: 'landslide-zones-source',
      paint: {
        'fill-color': '#dc2626',
        'fill-opacity': 0.38,
      },
    });

    map.addLayer({
      id: 'landslide-zones-line',
      type: 'line',
      source: 'landslide-zones-source',
      paint: {
        'line-color': '#ef4444',
        'line-width': 2.5,
        'line-dasharray': [2, 1],
      },
    });

    // 5. Relocation Sites Layer (Safe reception parcels)
    map.addSource('relocation-sites-source', {
      type: 'geojson',
      data: geoJsonCacheRef.current.relocationSites,
    });

    map.addLayer({
      id: 'relocation-sites-fill',
      type: 'fill',
      source: 'relocation-sites-source',
      paint: {
        'fill-color': '#10b981',
        'fill-opacity': 0.42,
      },
    });

    map.addLayer({
      id: 'relocation-sites-line',
      type: 'line',
      source: 'relocation-sites-source',
      paint: {
        'line-color': '#34d399',
        'line-width': 2.5,
      },
    });

    // 6. Vulnerable Habitations Layer (Settlement boundaries styled by priority)
    map.addSource('habitations-source', {
      type: 'geojson',
      data: geoJsonCacheRef.current.habitations,
    });

    map.addLayer({
      id: 'habitations-fill',
      type: 'fill',
      source: 'habitations-source',
      paint: {
        'fill-color': [
          'match',
          ['get', 'priority'],
          'IMMEDIATE',
          '#dc2626',
          'SHORT_TERM',
          '#ea580c',
          'MEDIUM_TERM',
          '#d97706',
          'MONITOR',
          '#0284c7',
          '#dc2626',
        ],
        'fill-opacity': 0.52,
      },
    });

    map.addLayer({
      id: 'habitations-line',
      type: 'line',
      source: 'habitations-source',
      paint: {
        'line-color': '#ffffff',
        'line-width': 1.5,
        'line-opacity': 0.7,
      },
    });

    // 7. Rivers Layer (Hydrographic lines)
    map.addSource('rivers-source', {
      type: 'geojson',
      data: geoJsonCacheRef.current.rivers,
    });

    map.addLayer({
      id: 'rivers-line',
      type: 'line',
      source: 'rivers-source',
      paint: {
        'line-color': '#38bdf8',
        'line-width': [
          'case',
          ['==', ['get', 'flood_prone'], true],
          3.5,
          2.0,
        ],
      },
    });

    // 8. Roads Layer (Corridors & evacuation routes)
    map.addSource('roads-source', {
      type: 'geojson',
      data: geoJsonCacheRef.current.roads,
    });

    // Road casing
    map.addLayer({
      id: 'roads-casing',
      type: 'line',
      source: 'roads-source',
      paint: {
        'line-color': '#090d16',
        'line-width': 4.5,
      },
    });

    map.addLayer({
      id: 'roads-line',
      type: 'line',
      source: 'roads-source',
      paint: {
        'line-color': [
          'case',
          ['==', ['get', 'evacuation_route'], true],
          '#f59e0b',
          '#94a3b8',
        ],
        'line-width': 2.5,
      },
    });

    // 9. Hospitals Layer (Healthcare points)
    map.addSource('hospitals-source', {
      type: 'geojson',
      data: geoJsonCacheRef.current.hospitals,
    });

    map.addLayer({
      id: 'hospitals-circle',
      type: 'circle',
      source: 'hospitals-source',
      paint: {
        'circle-radius': 8,
        'circle-color': '#ef4444',
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': 2.5,
      },
    });

    // 10. Schools Layer (Emergency relief shelters)
    map.addSource('schools-source', {
      type: 'geojson',
      data: geoJsonCacheRef.current.schools,
    });

    map.addLayer({
      id: 'schools-circle',
      type: 'circle',
      source: 'schools-source',
      paint: {
        'circle-radius': 7.5,
        'circle-color': '#f59e0b',
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': 2.5,
      },
    });

    // Attach Click Events for Interactive Inspection
    registerClickHandlers(map);
  };

  // Register interactive click handlers for features
  const registerClickHandlers = (map) => {
    // Helper to setup pointer cursor on hover
    const setCursorHover = (layerId) => {
      map.on('mouseenter', layerId, () => {
        map.getCanvas().style.cursor = 'pointer';
      });
      map.on('mouseleave', layerId, () => {
        map.getCanvas().style.cursor = '';
      });
    };

    // A. Habitation Click (Required: Name, Population, Hazard score, Vulnerability score, Priority, Main risk factors, Recommended relocation site)
    setCursorHover('habitations-fill');
    map.on('click', 'habitations-fill', (e) => {
      if (!e.features || !e.features[0]) return;
      const feat = e.features[0];
      const props = feat.properties;

      // Extract required fields
      const name = props.name || 'Habitation Settlement';
      const population = props.population || 2180;
      const hazardScore = props.hazard_score ?? props.risk_score ?? 88;
      const vulnScore = props.vulnerability_score ?? 82;
      const priority = props.priority || 'IMMEDIATE';
      const mainRiskFactors = Array.isArray(props.main_risk_factors)
        ? props.main_risk_factors
        : typeof props.main_risk_factors === 'string'
        ? JSON.parse(props.main_risk_factors)
        : [
            'Steep slope gradient (> 28°)',
            'Extreme rainfall saturation (> 380 mm)',
            'Kutcha dwellings proportion > 65%',
          ];
      const recommendedSite = props.recommended_relocation_site || 'Meppadi Safe Plateau Zone A';

      // Highlight geometry
      highlightSelectedFeature(feat.geometry);

      // Render tactical popup
      const riskListHtml = mainRiskFactors
        .slice(0, 3)
        .map((f) => `<li class="text-[10px] text-slate-300 flex items-start gap-1"><span class="text-rose-400 font-bold">•</span>${f}</li>`)
        .join('');

      const popupHtml = `
        <div class="p-3 bg-slate-950 text-slate-200 rounded-lg font-sans max-w-[270px] shadow-2xl border border-slate-700">
          <div class="flex items-center justify-between pb-1.5 border-b border-slate-800">
            <span class="text-[9px] font-mono uppercase text-slate-400">Vulnerable Habitation</span>
            <span class="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold ${
              priority === 'IMMEDIATE'
                ? 'bg-rose-950 text-rose-300 border border-rose-700'
                : 'bg-amber-950 text-amber-300 border border-amber-700'
            }">${priority}</span>
          </div>
          <h4 class="text-sm font-bold text-white mt-1 leading-snug">${name}</h4>
          
          <div class="grid grid-cols-2 gap-1.5 my-2">
            <div class="bg-slate-900 p-1.5 rounded border border-slate-800">
              <span class="text-[9px] text-slate-400 uppercase">Population</span>
              <p class="text-xs font-bold font-mono text-slate-100">${Number(population).toLocaleString()}</p>
            </div>
            <div class="bg-slate-900 p-1.5 rounded border border-slate-800">
              <span class="text-[9px] text-slate-400 uppercase">Hazard / Vuln</span>
              <p class="text-xs font-bold font-mono text-rose-400">${hazardScore} <span class="text-slate-500 font-normal">|</span> <span class="text-amber-400">${vulnScore}</span></p>
            </div>
          </div>

          <div class="bg-slate-900/80 p-2 rounded border border-slate-800 mb-2">
            <p class="text-[9px] uppercase font-bold text-rose-400 mb-1">Main Risk Factors:</p>
            <ul class="space-y-0.5">${riskListHtml}</ul>
          </div>

          <div class="bg-emerald-950/40 p-2 rounded border border-emerald-800/40 text-[10px]">
            <p class="text-[9px] uppercase font-bold text-emerald-400 mb-0.5">Recommended Relocation Site:</p>
            <p class="font-semibold text-emerald-200">${recommendedSite}</p>
          </div>
        </div>
      `;

      if (popupRef.current) popupRef.current.remove();
      popupRef.current = new maplibregl.Popup({ offset: 12, closeButton: true, className: 'tactical-popup' })
        .setLngLat(e.lngLat)
        .setHTML(popupHtml)
        .addTo(map);

      // Notify parent callback
      if (onSelectEntity) {
        onSelectEntity({
          type: 'habitation',
          data: {
            ...props,
            id: props.id || feat.id,
            name,
            population: Number(population),
            hazard_score: hazardScore,
            vulnerability_score: vulnScore,
            priority,
            main_risk_factors: mainRiskFactors,
            recommended_relocation_site: recommendedSite,
            geometry: feat.geometry,
          },
        });
      }
    });

    // B. Relocation Site Click (Required: Site name, Suitability score, Carrying capacity, Current population, Available capacity, Infrastructure, Distance to nearest affected habitation)
    setCursorHover('relocation-sites-fill');
    map.on('click', 'relocation-sites-fill', (e) => {
      if (!e.features || !e.features[0]) return;
      const feat = e.features[0];
      const props = feat.properties;

      const siteName = props.site_name || props.name || 'Candidate Relocation Parcel';
      const suitabilityScore = props.suitability_score ?? 89;
      const carryingCapacity = props.carrying_capacity ?? props.estimated_capacity ?? 3500;
      const currentPopulation = props.current_population ?? props.current_occupancy ?? 700;
      const availableCapacity = props.available_capacity ?? (carryingCapacity - currentPopulation);
      const infrastructure = props.infrastructure || 'Paved Road (0.4 km) | Community Health Centre (3.2 km)';
      const distanceToNearest = props.distance_to_nearest_habitation || '3.8 km to Chooralmala / 4.2 km to Mundakkai';

      highlightSelectedFeature(feat.geometry);

      const popupHtml = `
        <div class="p-3 bg-slate-950 text-slate-200 rounded-lg font-sans max-w-[270px] shadow-2xl border border-emerald-900/60">
          <div class="flex items-center justify-between pb-1.5 border-b border-slate-800">
            <span class="text-[9px] font-mono uppercase text-emerald-400">Relocation Haven</span>
            <span class="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-700">
              ${props.classification || 'SUITABLE'}
            </span>
          </div>
          <h4 class="text-sm font-bold text-white mt-1 leading-snug">${siteName}</h4>

          <div class="grid grid-cols-2 gap-1.5 my-2">
            <div class="bg-slate-900 p-1.5 rounded border border-slate-800">
              <span class="text-[9px] text-slate-400 uppercase">Suitability</span>
              <p class="text-sm font-bold font-mono text-emerald-400">${suitabilityScore}<span class="text-[9px] text-slate-500">/100</span></p>
            </div>
            <div class="bg-slate-900 p-1.5 rounded border border-slate-800">
              <span class="text-[9px] text-slate-400 uppercase">Avail Intake</span>
              <p class="text-sm font-bold font-mono text-emerald-300">${Number(availableCapacity).toLocaleString()}</p>
            </div>
            <div class="bg-slate-900 p-1.5 rounded border border-slate-800">
              <span class="text-[9px] text-slate-400 uppercase">Carrying Cap</span>
              <p class="text-xs font-bold font-mono text-slate-200">${Number(carryingCapacity).toLocaleString()}</p>
            </div>
            <div class="bg-slate-900 p-1.5 rounded border border-slate-800">
              <span class="text-[9px] text-slate-400 uppercase">Current Pop</span>
              <p class="text-xs font-bold font-mono text-slate-400">${Number(currentPopulation).toLocaleString()}</p>
            </div>
          </div>

          <div class="bg-slate-900/80 p-2 rounded border border-slate-800 mb-1.5 text-[10px]">
            <p class="text-[9px] uppercase font-bold text-sky-400 mb-0.5">Infrastructure:</p>
            <p class="text-slate-300 font-mono text-[10px] leading-tight">${infrastructure}</p>
          </div>

          <div class="bg-slate-900/80 p-2 rounded border border-slate-800 text-[10px]">
            <p class="text-[9px] uppercase font-bold text-amber-400 mb-0.5">Distance to Nearest Habitation:</p>
            <p class="text-slate-200 font-semibold leading-tight">${distanceToNearest}</p>
          </div>
        </div>
      `;

      if (popupRef.current) popupRef.current.remove();
      popupRef.current = new maplibregl.Popup({ offset: 12, closeButton: true, className: 'tactical-popup' })
        .setLngLat(e.lngLat)
        .setHTML(popupHtml)
        .addTo(map);

      if (onSelectEntity) {
        onSelectEntity({
          type: 'relocation_site',
          data: {
            ...props,
            id: props.id || feat.id,
            site_name: siteName,
            name: siteName,
            suitability_score: suitabilityScore,
            carrying_capacity: Number(carryingCapacity),
            current_population: Number(currentPopulation),
            available_capacity: Number(availableCapacity),
            infrastructure,
            distance_to_nearest_habitation: distanceToNearest,
            geometry: feat.geometry,
          },
        });
      }
    });

    // C. Hospital Click
    setCursorHover('hospitals-circle');
    map.on('click', 'hospitals-circle', (e) => {
      if (!e.features || !e.features[0]) return;
      const feat = e.features[0];
      const props = feat.properties;

      highlightSelectedFeature(feat.geometry);

      const popupHtml = `
        <div class="p-2.5 bg-slate-950 text-slate-200 rounded-lg max-w-[240px] border border-rose-900/80">
          <span class="text-[9px] font-mono uppercase text-rose-400">Healthcare Facility</span>
          <h4 class="text-xs font-bold text-white mt-0.5">${props.name}</h4>
          <p class="text-[10px] text-slate-400 mb-2">${props.facility_type}</p>
          <div class="flex justify-between text-[10px] bg-slate-900 p-1.5 rounded mb-1">
            <span>Total Beds: <strong class="text-white">${props.total_beds}</strong></span>
            <span>Emergency: <strong class="text-rose-400">${props.emergency_beds}</strong></span>
          </div>
          <div class="text-[10px] text-slate-400 flex justify-between">
            <span>ICU: <strong class="${props.icu_available ? 'text-emerald-400' : 'text-slate-500'}">${props.icu_available ? 'Available' : 'No'}</strong></span>
            <span>Dist: <strong class="text-sky-400">${props.distance_to_mundakkai_km} km</strong></span>
          </div>
        </div>
      `;

      if (popupRef.current) popupRef.current.remove();
      popupRef.current = new maplibregl.Popup({ offset: 10, closeButton: true })
        .setLngLat(e.lngLat)
        .setHTML(popupHtml)
        .addTo(map);

      if (onSelectEntity) {
        onSelectEntity({ type: 'hospital', data: props });
      }
    });

    // D. School Click
    setCursorHover('schools-circle');
    map.on('click', 'schools-circle', (e) => {
      if (!e.features || !e.features[0]) return;
      const feat = e.features[0];
      const props = feat.properties;

      highlightSelectedFeature(feat.geometry);

      const popupHtml = `
        <div class="p-2.5 bg-slate-950 text-slate-200 rounded-lg max-w-[240px] border border-amber-900/80">
          <span class="text-[9px] font-mono uppercase text-amber-400">Designated Relief Shelter</span>
          <h4 class="text-xs font-bold text-white mt-0.5">${props.name}</h4>
          <p class="text-[10px] text-slate-400 mb-2">${props.facility_type}</p>
          <div class="flex justify-between text-[10px] bg-slate-900 p-1.5 rounded mb-1">
            <span>Capacity: <strong class="text-amber-400">${props.shelter_capacity}</strong></span>
            <span>Current: <strong class="text-white">${props.current_evacuees || 0}</strong></span>
          </div>
          <div class="text-[10px] text-slate-400 flex justify-between">
            <span>Water: <strong class="text-emerald-400">${props.potable_water ? 'Yes' : 'Tanker'}</strong></span>
            <span>Dist: <strong class="text-sky-400">${props.distance_to_mundakkai_km} km</strong></span>
          </div>
        </div>
      `;

      if (popupRef.current) popupRef.current.remove();
      popupRef.current = new maplibregl.Popup({ offset: 10, closeButton: true })
        .setLngLat(e.lngLat)
        .setHTML(popupHtml)
        .addTo(map);

      if (onSelectEntity) {
        onSelectEntity({ type: 'school', data: props });
      }
    });

    // E. River Click
    setCursorHover('rivers-line');
    map.on('click', 'rivers-line', (e) => {
      if (!e.features || !e.features[0]) return;
      const props = e.features[0].properties;
      highlightSelectedFeature(e.features[0].geometry);

      const popupHtml = `
        <div class="p-2 bg-slate-950 text-slate-200 rounded max-w-[220px] border border-sky-900">
          <span class="text-[9px] font-mono uppercase text-sky-400">Drainage Channel</span>
          <h4 class="text-xs font-bold text-white">${props.name}</h4>
          <p class="text-[10px] text-slate-400 mt-1">Basin: ${props.basin} | Width: ${props.width_m}m</p>
          <p class="text-[10px] ${props.flood_prone ? 'text-rose-400 font-semibold' : 'text-slate-400'} mt-0.5">
            ${props.flood_prone ? '⚠ Flash Flood Inundation Corridor' : 'Stable Stream Flow'}
          </p>
        </div>
      `;
      if (popupRef.current) popupRef.current.remove();
      popupRef.current = new maplibregl.Popup({ offset: 10, closeButton: true })
        .setLngLat(e.lngLat)
        .setHTML(popupHtml)
        .addTo(map);

      if (onSelectEntity) onSelectEntity({ type: 'river', data: props });
    });

    // F. Road Click
    setCursorHover('roads-line');
    map.on('click', 'roads-line', (e) => {
      if (!e.features || !e.features[0]) return;
      const props = e.features[0].properties;
      highlightSelectedFeature(e.features[0].geometry);

      const popupHtml = `
        <div class="p-2 bg-slate-950 text-slate-200 rounded max-w-[220px] border border-amber-900">
          <span class="text-[9px] font-mono uppercase text-amber-400">Transportation Corridor</span>
          <h4 class="text-xs font-bold text-white">${props.name}</h4>
          <p class="text-[10px] text-slate-400 mt-1">${props.category} (${props.lanes} Lane)</p>
          <p class="text-[10px] font-mono text-emerald-400 mt-0.5">${props.status || 'PASSABLE'}</p>
        </div>
      `;
      if (popupRef.current) popupRef.current.remove();
      popupRef.current = new maplibregl.Popup({ offset: 10, closeButton: true })
        .setLngLat(e.lngLat)
        .setHTML(popupHtml)
        .addTo(map);

      if (onSelectEntity) onSelectEntity({ type: 'road', data: props });
    });
  };

  // 4. Handle Layer Visibility Toggles (Smooth show/hide via MapLibre layout properties)
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    const setVisibility = (layers, isVisible) => {
      layers.forEach((layerId) => {
        if (map.getLayer(layerId)) {
          map.setLayoutProperty(layerId, 'visibility', isVisible ? 'visible' : 'none');
        }
      });
    };

    setVisibility(['multi-hazard-fill', 'multi-hazard-line'], layersVisible.multiHazard);
    setVisibility(['flood-zones-fill', 'flood-zones-line'], layersVisible.floodZones);
    setVisibility(['landslide-zones-fill', 'landslide-zones-line'], layersVisible.landslideZones);
    setVisibility(['heavy-rainfall-fill', 'heavy-rainfall-line'], layersVisible.heavyRainfall);
    setVisibility(['habitations-fill', 'habitations-line'], layersVisible.habitations);
    setVisibility(['relocation-sites-fill', 'relocation-sites-line'], layersVisible.relocationSites);
    setVisibility(['rivers-line'], layersVisible.rivers);
    setVisibility(['roads-casing', 'roads-line'], layersVisible.roads);
    setVisibility(['hospitals-circle'], layersVisible.hospitals);
    setVisibility(['schools-circle'], layersVisible.schools);
  }, [layersVisible, mapLoaded]);

  // 5. Handle external Focus Coords or External Entity Selection
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !focusCoords) return;

    map.flyTo({
      center: focusCoords,
      zoom: 14.2,
      duration: 1200,
      essential: true,
    });
  }, [focusCoords]);

  useEffect(() => {
    if (!selectedEntity || !mapLoaded) return;
    if (selectedEntity.data?.geometry) {
      highlightSelectedFeature(selectedEntity.data.geometry);
    }
  }, [selectedEntity, mapLoaded, highlightSelectedFeature]);

  // Search input handler
  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);

    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    const q = query.toLowerCase();
    const matches = searchIndexRef.current
      .filter((item) => item.name.toLowerCase().includes(q) || item.category.toLowerCase().includes(q))
      .slice(0, 8);

    setSearchResults(matches);
  };

  // Search item selection handler
  const handleSelectSearchResult = (item) => {
    setSearchQuery(item.name);
    setSearchResults([]);

    const map = mapRef.current;
    if (!map) return;

    if (item.center) {
      map.flyTo({
        center: item.center,
        zoom: 14.5,
        duration: 1400,
        essential: true,
      });
    }

    if (item.geometry) {
      highlightSelectedFeature(item.geometry);
    }

    if (onSelectEntity) {
      onSelectEntity({ type: item.type, data: item.properties || item });
    }
  };

  // Toggle single layer
  const toggleLayer = (layerKey) => {
    setLayersVisible((prev) => ({
      ...prev,
      [layerKey]: !prev[layerKey],
    }));
  };

  // Presets: Select all / Clear all
  const setAllLayers = (status) => {
    setLayersVisible({
      multiHazard: status,
      floodZones: status,
      landslideZones: status,
      heavyRainfall: status,
      habitations: status,
      relocationSites: status,
      rivers: status,
      roads: status,
      hospitals: status,
      schools: status,
    });
  };

  // Sector jump handler
  const jumpToSector = (bookmark) => {
    setActiveBookmark(bookmark.id);
    setShowQuickJump(false);
    const map = mapRef.current;
    if (!map) return;

    map.flyTo({
      center: bookmark.coords,
      zoom: bookmark.zoom,
      pitch: bookmark.pitch,
      bearing: bookmark.bearing,
      duration: 1500,
      essential: true,
    });
  };

  // Zoom controls
  const handleZoomIn = () => {
    if (mapRef.current) mapRef.current.zoomIn();
  };

  const handleZoomOut = () => {
    if (mapRef.current) mapRef.current.zoomOut();
  };

  const toggle3DPerspective = () => {
    const map = mapRef.current;
    if (!map) return;

    const next3D = !is3D;
    setIs3D(next3D);
    map.easeTo({
      pitch: next3D ? 50 : 0,
      bearing: next3D ? -15 : 0,
      duration: 1000,
    });
  };

  const resetBearing = () => {
    const map = mapRef.current;
    if (!map) return;
    map.resetNorthPitch({ duration: 800 });
    setIs3D(false);
  };

  return (
    <div
      className={`relative w-full rounded-xl overflow-hidden border border-slate-800 bg-slate-950 font-sans shadow-2xl ${className}`}
      style={{ height }}
    >
      {/* MapLibre DOM Node */}
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* TOP LEFT: Quick-Jump Sector Navigator & Search Bar */}
      <div className="absolute top-3 left-3 z-20 flex flex-col sm:flex-row items-start sm:items-center gap-2 max-w-[calc(100%-120px)]">
        {/* Sector Quick Jump Menu */}
        <div className="relative">
          <button
            onClick={() => setShowQuickJump(!showQuickJump)}
            className="bg-slate-900/90 hover:bg-slate-800 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700/80 shadow-lg text-xs font-mono flex items-center gap-2 text-slate-200 transition-colors"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="font-semibold truncate max-w-[140px] sm:max-w-[190px]">
              {SECTOR_BOOKMARKS.find((b) => b.id === activeBookmark)?.name || 'Wayanad Sector'}
            </span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {showQuickJump && (
            <div className="absolute left-0 top-10 w-64 bg-slate-900/95 backdrop-blur-md border border-slate-700 rounded-lg shadow-2xl p-2 z-30 space-y-1">
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 px-2 py-1 border-b border-slate-800">
                Location Navigation Bookmarks
              </p>
              {SECTOR_BOOKMARKS.map((b) => (
                <button
                  key={b.id}
                  onClick={() => jumpToSector(b)}
                  className={`w-full text-left px-2.5 py-1.5 rounded text-xs flex flex-col transition-colors ${
                    activeBookmark === b.id
                      ? 'bg-amber-600/30 text-amber-200 border border-amber-500/40'
                      : 'hover:bg-slate-800 text-slate-300'
                  }`}
                >
                  <span className="font-semibold">{b.name}</span>
                  <span className="text-[10px] text-slate-400 font-normal">{b.desc}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Global GIS Map Search Bar */}
        <div className="relative w-48 sm:w-60">
          <div className="relative">
            <input
              type="text"
              placeholder="Search GIS layers..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="w-full bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-lg pl-8 pr-7 py-1.5 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-sky-500 font-mono shadow-lg transition-colors"
            />
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            {searchQuery && (
              <button
                onClick={() => {
                  setSearchQuery('');
                  setSearchResults([]);
                }}
                className="absolute right-2 top-2 text-slate-400 hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Autocomplete Results Dropdown */}
          {searchResults.length > 0 && (
            <div className="absolute left-0 right-0 top-10 bg-slate-900/95 backdrop-blur-md border border-slate-700 rounded-lg shadow-2xl max-h-56 overflow-y-auto z-30 p-1 space-y-0.5">
              {searchResults.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleSelectSearchResult(item)}
                  className="w-full text-left px-2.5 py-1.5 rounded hover:bg-slate-800 text-xs flex items-center justify-between transition-colors text-slate-200"
                >
                  <div className="truncate pr-2">
                    <p className="font-semibold leading-tight truncate">{item.name}</p>
                    <p className="text-[10px] text-slate-400">{item.category}</p>
                  </div>
                  {item.priority && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded font-mono font-bold bg-rose-950 text-rose-300 border border-rose-800 shrink-0">
                      {item.priority}
                    </span>
                  )}
                  {item.suitability_score && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded font-mono font-bold bg-emerald-950 text-emerald-300 border border-emerald-800 shrink-0">
                      {item.suitability_score}
                    </span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* TOP RIGHT: Layer Controls Toggle Button */}
      <div className="absolute top-3 right-3 z-20 flex items-center gap-2">
        <button
          onClick={() => setShowLayerPanel(!showLayerPanel)}
          className={`bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-lg border text-xs font-medium flex items-center gap-2 shadow-lg transition-colors ${
            showLayerPanel
              ? 'border-amber-500 text-amber-300 bg-slate-800'
              : 'border-slate-700/80 text-slate-200 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Layers className="w-4 h-4 text-amber-400" />
          <span>Layers</span>
          <span className="px-1.5 py-0.2 rounded font-mono text-[10px] bg-slate-800 border border-slate-700 text-amber-300">
            {activeLayersCount}/10
          </span>
        </button>
      </div>

      {/* FLOATING GIS LAYER CONTROLS MODAL/PANEL (10 Layer Checkboxes as required) */}
      {showLayerPanel && (
        <div className="absolute top-12 right-3 w-72 bg-slate-900/95 backdrop-blur-md border border-slate-700 rounded-xl shadow-2xl p-3 z-30 text-xs space-y-2 max-h-[calc(100%-80px)] overflow-y-auto">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div className="flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-amber-400" />
              <span className="font-bold text-slate-100 uppercase tracking-wider text-[11px]">
                GIS Layer Controls
              </span>
            </div>
            <button
              onClick={() => setShowLayerPanel(false)}
              className="text-slate-400 hover:text-white p-0.5 rounded hover:bg-slate-800"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Quick Preset Buttons */}
          <div className="flex items-center justify-between pt-0.5 text-[11px]">
            <button
              onClick={() => setAllLayers(true)}
              className="text-sky-400 hover:text-sky-300 font-mono font-medium"
            >
              ☑ Select All (10)
            </button>
            <span className="text-slate-600">|</span>
            <button
              onClick={() => setAllLayers(false)}
              className="text-slate-400 hover:text-slate-300 font-mono"
            >
              ☐ Clear All
            </button>
          </div>

          <div className="space-y-1 pt-1">
            {/* 1. Multi-hazard risk */}
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-slate-800/80 cursor-pointer transition-colors">
              <span className="flex items-center gap-2 text-rose-300 font-medium">
                <span className="w-3 h-3 rounded-xs bg-rose-700/80 border border-rose-500"></span>
                Multi-Hazard Risk
              </span>
              <input
                type="checkbox"
                checked={layersVisible.multiHazard}
                onChange={() => toggleLayer('multiHazard')}
                className="w-4 h-4 rounded text-rose-600 focus:ring-0 bg-slate-950 border-slate-600 cursor-pointer"
              />
            </label>

            {/* 2. Flood zones */}
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-slate-800/80 cursor-pointer transition-colors">
              <span className="flex items-center gap-2 text-sky-300 font-medium">
                <span className="w-3 h-3 rounded-xs bg-sky-600/80 border border-sky-400"></span>
                Flood Zones
              </span>
              <input
                type="checkbox"
                checked={layersVisible.floodZones}
                onChange={() => toggleLayer('floodZones')}
                className="w-4 h-4 rounded text-sky-600 focus:ring-0 bg-slate-950 border-slate-600 cursor-pointer"
              />
            </label>

            {/* 3. Landslide zones */}
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-slate-800/80 cursor-pointer transition-colors">
              <span className="flex items-center gap-2 text-red-400 font-medium">
                <span className="w-3 h-3 rounded-xs bg-red-700/80 border border-red-500"></span>
                Landslide Zones
              </span>
              <input
                type="checkbox"
                checked={layersVisible.landslideZones}
                onChange={() => toggleLayer('landslideZones')}
                className="w-4 h-4 rounded text-red-600 focus:ring-0 bg-slate-950 border-slate-600 cursor-pointer"
              />
            </label>

            {/* 4. Heavy rainfall */}
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-slate-800/80 cursor-pointer transition-colors">
              <span className="flex items-center gap-2 text-blue-300 font-medium">
                <span className="w-3 h-3 rounded-xs bg-indigo-600/80 border border-indigo-400"></span>
                Heavy Rainfall Isohyets
              </span>
              <input
                type="checkbox"
                checked={layersVisible.heavyRainfall}
                onChange={() => toggleLayer('heavyRainfall')}
                className="w-4 h-4 rounded text-indigo-600 focus:ring-0 bg-slate-950 border-slate-600 cursor-pointer"
              />
            </label>

            {/* 5. Vulnerable habitations */}
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-slate-800/80 cursor-pointer transition-colors">
              <span className="flex items-center gap-2 text-amber-300 font-medium">
                <span className="w-3 h-3 rounded-xs bg-amber-600/80 border border-amber-400"></span>
                Vulnerable Habitations
              </span>
              <input
                type="checkbox"
                checked={layersVisible.habitations}
                onChange={() => toggleLayer('habitations')}
                className="w-4 h-4 rounded text-amber-600 focus:ring-0 bg-slate-950 border-slate-600 cursor-pointer"
              />
            </label>

            {/* 6. Relocation sites */}
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-slate-800/80 cursor-pointer transition-colors">
              <span className="flex items-center gap-2 text-emerald-300 font-medium">
                <span className="w-3 h-3 rounded-xs bg-emerald-600/80 border border-emerald-400"></span>
                Relocation Sites
              </span>
              <input
                type="checkbox"
                checked={layersVisible.relocationSites}
                onChange={() => toggleLayer('relocationSites')}
                className="w-4 h-4 rounded text-emerald-600 focus:ring-0 bg-slate-950 border-slate-600 cursor-pointer"
              />
            </label>

            {/* 7. Rivers */}
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-slate-800/80 cursor-pointer transition-colors">
              <span className="flex items-center gap-2 text-cyan-300 font-medium">
                <span className="w-4 h-1 bg-cyan-400 rounded-full"></span>
                Rivers & Drainage
              </span>
              <input
                type="checkbox"
                checked={layersVisible.rivers}
                onChange={() => toggleLayer('rivers')}
                className="w-4 h-4 rounded text-cyan-600 focus:ring-0 bg-slate-950 border-slate-600 cursor-pointer"
              />
            </label>

            {/* 8. Roads */}
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-slate-800/80 cursor-pointer transition-colors">
              <span className="flex items-center gap-2 text-slate-300 font-medium">
                <span className="w-4 h-1 bg-amber-500 rounded-full"></span>
                Roads & Evacuation Routes
              </span>
              <input
                type="checkbox"
                checked={layersVisible.roads}
                onChange={() => toggleLayer('roads')}
                className="w-4 h-4 rounded text-amber-600 focus:ring-0 bg-slate-950 border-slate-600 cursor-pointer"
              />
            </label>

            {/* 9. Hospitals */}
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-slate-800/80 cursor-pointer transition-colors">
              <span className="flex items-center gap-2 text-rose-300 font-medium">
                <span className="w-3 h-3 rounded-full bg-red-600 border border-white"></span>
                Hospitals & Trauma
              </span>
              <input
                type="checkbox"
                checked={layersVisible.hospitals}
                onChange={() => toggleLayer('hospitals')}
                className="w-4 h-4 rounded text-red-600 focus:ring-0 bg-slate-950 border-slate-600 cursor-pointer"
              />
            </label>

            {/* 10. Schools */}
            <label className="flex items-center justify-between p-1.5 rounded hover:bg-slate-800/80 cursor-pointer transition-colors">
              <span className="flex items-center gap-2 text-amber-200 font-medium">
                <span className="w-3 h-3 rounded-full bg-amber-500 border border-white"></span>
                Schools & Relief Shelters
              </span>
              <input
                type="checkbox"
                checked={layersVisible.schools}
                onChange={() => toggleLayer('schools')}
                className="w-4 h-4 rounded text-amber-600 focus:ring-0 bg-slate-950 border-slate-600 cursor-pointer"
              />
            </label>
          </div>
        </div>
      )}

      {/* RIGHT SIDEBAR: Tactical Zoom & 3D Orientation Controls */}
      <div className="absolute right-3 top-14 z-10 flex flex-col gap-1.5">
        <button
          onClick={handleZoomIn}
          title="Zoom In"
          className="bg-slate-900/90 hover:bg-slate-800 backdrop-blur-md p-2 rounded-lg border border-slate-700/80 text-slate-300 hover:text-white shadow-lg transition-colors"
        >
          <ZoomIn className="w-4 h-4" />
        </button>

        <button
          onClick={handleZoomOut}
          title="Zoom Out"
          className="bg-slate-900/90 hover:bg-slate-800 backdrop-blur-md p-2 rounded-lg border border-slate-700/80 text-slate-300 hover:text-white shadow-lg transition-colors"
        >
          <ZoomOut className="w-4 h-4" />
        </button>

        <button
          onClick={toggle3DPerspective}
          title="Toggle 3D Terrain Perspective (45° Tilt)"
          className={`p-2 rounded-lg border shadow-lg backdrop-blur-md text-xs font-mono font-bold transition-colors ${
            is3D
              ? 'bg-amber-600 text-white border-amber-400 shadow-amber-500/20'
              : 'bg-slate-900/90 hover:bg-slate-800 border-slate-700/80 text-slate-300 hover:text-white'
          }`}
        >
          3D
        </button>

        <button
          onClick={resetBearing}
          title="Reset North Orientation"
          className="bg-slate-900/90 hover:bg-slate-800 backdrop-blur-md p-2 rounded-lg border border-slate-700/80 text-sky-400 hover:text-sky-300 shadow-lg transition-colors"
        >
          <Compass className="w-4 h-4" />
        </button>

        <button
          onClick={() => setShowLegend(!showLegend)}
          title="Toggle Map Legend"
          className={`p-2 rounded-lg border shadow-lg backdrop-blur-md text-xs transition-colors ${
            showLegend
              ? 'bg-slate-800 text-amber-300 border-amber-500/60'
              : 'bg-slate-900/90 hover:bg-slate-800 border-slate-700/80 text-slate-300 hover:text-white'
          }`}
        >
          <Info className="w-4 h-4" />
        </button>
      </div>

      {/* BOTTOM RIGHT: Expandable & Collapsible Comprehensive Map Legend */}
      {showLegend && (
        <div className="absolute bottom-6 right-3 z-10 bg-slate-900/95 backdrop-blur-md p-3 rounded-xl border border-slate-700 shadow-2xl text-[11px] text-slate-300 max-w-[240px] max-h-[340px] overflow-y-auto hidden md:block">
          <div className="flex items-center justify-between pb-1.5 border-b border-slate-800 mb-2">
            <span className="font-bold text-[10px] uppercase text-slate-400 tracking-wider">
              GIS Map Legend
            </span>
            <button
              onClick={() => setShowLegend(false)}
              className="text-slate-400 hover:text-white text-xs"
            >
              ✕
            </button>
          </div>

          <div className="space-y-2">
            {/* Hazards Group */}
            <div>
              <p className="text-[9px] uppercase font-bold text-slate-500 mb-1">Hazard Overlays</p>
              <div className="space-y-1 text-[10px]">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-xs bg-rose-700/80 border border-rose-500"></span>
                  <span>Multi-Hazard Red Zone</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-xs bg-sky-600/80 border border-sky-400"></span>
                  <span>Riverine Flood Inundation</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-xs bg-red-700/80 border border-red-500"></span>
                  <span>Landslide Debris Scarp</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-xs bg-indigo-600/80 border border-indigo-400"></span>
                  <span>Torrential Rainfall (&gt;400mm)</span>
                </div>
              </div>
            </div>

            {/* Habitation & Relocation Group */}
            <div className="pt-1 border-t border-slate-800">
              <p className="text-[9px] uppercase font-bold text-slate-500 mb-1">Habitations & Relocation</p>
              <div className="space-y-1 text-[10px]">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-xs bg-red-600 border border-red-400"></span>
                  <span>Immediate Urgency Habitation</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-xs bg-amber-600 border border-amber-400"></span>
                  <span>Short-Term Urgency Habitation</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-xs bg-emerald-600 border border-emerald-400"></span>
                  <span>Safe Relocation Reception Parcel</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-xs border-2 border-sky-400 bg-sky-400/20"></span>
                  <span>Selected Feature Highlight</span>
                </div>
              </div>
            </div>

            {/* Critical Infrastructure Group */}
            <div className="pt-1 border-t border-slate-800">
              <p className="text-[9px] uppercase font-bold text-slate-500 mb-1">Infrastructure</p>
              <div className="space-y-1 text-[10px]">
                <div className="flex items-center gap-2">
                  <span className="w-4 h-0.5 bg-cyan-400"></span>
                  <span>Iruvaipuzha River Network</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-4 h-0.5 bg-amber-500"></span>
                  <span>Emergency Evacuation Road</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-600 border border-white"></span>
                  <span>Hospital / Trauma Facility</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500 border border-white"></span>
                  <span>School / Relief Shelter</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* BOTTOM LEFT: Coordinate Bar & Map Projection Status */}
      <div className="absolute bottom-3 left-3 z-10 hidden sm:flex items-center gap-2 text-[10px] font-mono text-slate-400 bg-slate-900/80 backdrop-blur-md px-2.5 py-1 rounded border border-slate-800">
        <span className="text-slate-300 font-semibold">EPSG:4326</span>
        <span className="text-slate-600">|</span>
        <span>MapLibre GL v5.2</span>
        <span className="text-slate-600">|</span>
        <span className="text-emerald-400">FastAPI GeoJSON Layer</span>
      </div>
    </div>
  );
}

// Utility to calculate centroid of simple polygon or return coordinate
function getFeatureCenter(geometry) {
  if (!geometry) return WAYANAD_COORDS;
  if (geometry.type === 'Point') {
    return geometry.coordinates;
  }
  if (geometry.type === 'Polygon' && geometry.coordinates?.[0]?.length) {
    const coords = geometry.coordinates[0];
    let sumLng = 0;
    let sumLat = 0;
    coords.forEach(([lng, lat]) => {
      sumLng += lng;
      sumLat += lat;
    });
    return [sumLng / coords.length, sumLat / coords.length];
  }
  return WAYANAD_COORDS;
}
