import React, { useEffect, useRef, useState, useCallback } from 'react';
import maplibregl from 'maplibre-gl';
import {
  Layers,
  Maximize2,
  Minimize2,
  ZoomIn,
  ZoomOut,
  Compass,
  Eye,
  EyeOff,
  Flame,
  Home,
  ShieldCheck,
  AlertCircle,
} from 'lucide-react';

const WAYANAD_COORDS = [76.14, 11.545]; // [longitude, latitude]

// High-reliability dark tactical raster basemap style
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
  habitations = [],
  hazards = [],
  relocationSites = [],
  alerts = [],
  onSelectEntity,
  selectedEntity,
  className = '',
  height = '500px',
  focusCoords = null,
}) {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Layer visibility state
  const [layersVisible, setLayersVisible] = useState({
    hazards: true,
    habitations: true,
    relocationSites: true,
    alerts: true,
  });

  const [showLayerMenu, setShowLayerMenu] = useState(false);

  // Initialize Map
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

    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right');
    map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left');

    map.on('load', () => {
      mapRef.current = map;
      setMapLoaded(true);
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Update Data Sources & Layers whenever data changes or map loads
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    // Helper to safely add or update GeoJSON source
    const updateSource = (sourceId, geojsonData) => {
      if (map.getSource(sourceId)) {
        map.getSource(sourceId).setData(geojsonData);
      } else {
        map.addSource(sourceId, {
          type: 'geojson',
          data: geojsonData,
        });
      }
    };

    // 1. Hazards Layer
    const hazardsGeoJSON = {
      type: 'FeatureCollection',
      features: (hazards || []).map((h) => ({
        type: 'Feature',
        geometry: h.geometry,
        properties: {
          id: h.id,
          hazard_type: h.hazard_type || 'Unknown Hazard',
          severity: h.severity || 'HIGH',
          risk_score: h.risk_score || 80,
          source: h.source || 'GSI/ISRO',
        },
      })),
    };
    updateSource('hazards-source', hazardsGeoJSON);

    if (!map.getLayer('hazards-fill')) {
      map.addLayer({
        id: 'hazards-fill',
        type: 'fill',
        source: 'hazards-source',
        paint: {
          'fill-color': [
            'match',
            ['get', 'severity'],
            'CRITICAL',
            '#f43f5e',
            'VERY_HIGH',
            '#e11d48',
            'HIGH',
            '#f97316',
            'MODERATE',
            '#eab308',
            '#f43f5e',
          ],
          'fill-opacity': 0.35,
        },
      });

      map.addLayer({
        id: 'hazards-line',
        type: 'line',
        source: 'hazards-source',
        paint: {
          'line-color': '#f43f5e',
          'line-width': 2,
          'line-dasharray': [2, 1],
        },
      });

      map.on('click', 'hazards-fill', (e) => {
        if (e.features && e.features[0] && onSelectEntity) {
          const props = e.features[0].properties;
          const fullObj = hazards.find((h) => String(h.id) === String(props.id)) || props;
          onSelectEntity({ type: 'hazard', data: fullObj });
        }
      });

      map.on('mouseenter', 'hazards-fill', () => {
        map.getCanvas().style.cursor = 'pointer';
      });
      map.on('mouseleave', 'hazards-fill', () => {
        map.getCanvas().style.cursor = '';
      });
    }

    // 2. Relocation Sites Layer
    const sitesGeoJSON = {
      type: 'FeatureCollection',
      features: (relocationSites || []).map((s) => ({
        type: 'Feature',
        geometry: s.geometry,
        properties: {
          id: s.id,
          name: s.name,
          suitability_score: s.suitability_score || s.overall_suitability_score || 85,
          available_capacity: s.available_capacity || 0,
          classification: s.classification || 'SUITABLE',
        },
      })),
    };
    updateSource('relocation-sites-source', sitesGeoJSON);

    if (!map.getLayer('relocation-sites-fill')) {
      map.addLayer({
        id: 'relocation-sites-fill',
        type: 'fill',
        source: 'relocation-sites-source',
        paint: {
          'fill-color': '#10b981',
          'fill-opacity': 0.38,
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

      map.on('click', 'relocation-sites-fill', (e) => {
        if (e.features && e.features[0] && onSelectEntity) {
          const props = e.features[0].properties;
          const fullObj = relocationSites.find((s) => String(s.id) === String(props.id)) || props;
          onSelectEntity({ type: 'relocation_site', data: fullObj });
        }
      });

      map.on('mouseenter', 'relocation-sites-fill', () => {
        map.getCanvas().style.cursor = 'pointer';
      });
      map.on('mouseleave', 'relocation-sites-fill', () => {
        map.getCanvas().style.cursor = '';
      });
    }

    // 3. Habitations Layer
    const habitationsGeoJSON = {
      type: 'FeatureCollection',
      features: (habitations || []).map((h) => ({
        type: 'Feature',
        geometry: h.geometry,
        properties: {
          id: h.id,
          name: h.name,
          population: h.population,
          vulnerable_population: h.vulnerable_population,
          risk_score: h.risk_score || h.overall_score || 80,
          priority: h.priority || 'IMMEDIATE',
        },
      })),
    };
    updateSource('habitations-source', habitationsGeoJSON);

    if (!map.getLayer('habitations-fill')) {
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
          'fill-opacity': 0.45,
        },
      });

      map.addLayer({
        id: 'habitations-line',
        type: 'line',
        source: 'habitations-source',
        paint: {
          'line-color': '#f87171',
          'line-width': 2,
        },
      });

      map.on('click', 'habitations-fill', (e) => {
        if (e.features && e.features[0] && onSelectEntity) {
          const props = e.features[0].properties;
          const fullObj = habitations.find((h) => String(h.id) === String(props.id)) || props;
          onSelectEntity({ type: 'habitation', data: fullObj });
        }
      });

      map.on('mouseenter', 'habitations-fill', () => {
        map.getCanvas().style.cursor = 'pointer';
      });
      map.on('mouseleave', 'habitations-fill', () => {
        map.getCanvas().style.cursor = '';
      });
    }

    // 4. Alerts Layer
    const alertsGeoJSON = {
      type: 'FeatureCollection',
      features: (alerts || []).map((a) => ({
        type: 'Feature',
        geometry: a.geometry,
        properties: {
          id: a.id,
          disaster_type: a.disaster_type,
          severity: a.severity,
          source: a.source,
          description: a.description,
        },
      })),
    };
    updateSource('alerts-source', alertsGeoJSON);

    if (!map.getLayer('alerts-circle')) {
      map.addLayer({
        id: 'alerts-circle',
        type: 'circle',
        source: 'alerts-source',
        paint: {
          'circle-radius': 9,
          'circle-color': '#f43f5e',
          'circle-stroke-width': 3,
          'circle-stroke-color': '#ffffff',
          'circle-opacity': 0.9,
        },
      });

      map.on('click', 'alerts-circle', (e) => {
        if (e.features && e.features[0] && onSelectEntity) {
          const props = e.features[0].properties;
          const fullObj = alerts.find((a) => String(a.id) === String(props.id)) || props;
          onSelectEntity({ type: 'alert', data: fullObj });
        }
      });

      map.on('mouseenter', 'alerts-circle', () => {
        map.getCanvas().style.cursor = 'pointer';
      });
      map.on('mouseleave', 'alerts-circle', () => {
        map.getCanvas().style.cursor = '';
      });
    }
  }, [mapLoaded, habitations, hazards, relocationSites, alerts, onSelectEntity]);

  // Handle Layer Visibility Toggles
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    if (map.getLayer('hazards-fill')) {
      map.setLayoutProperty('hazards-fill', 'visibility', layersVisible.hazards ? 'visible' : 'none');
      map.setLayoutProperty('hazards-line', 'visibility', layersVisible.hazards ? 'visible' : 'none');
    }
    if (map.getLayer('habitations-fill')) {
      map.setLayoutProperty('habitations-fill', 'visibility', layersVisible.habitations ? 'visible' : 'none');
      map.setLayoutProperty('habitations-line', 'visibility', layersVisible.habitations ? 'visible' : 'none');
    }
    if (map.getLayer('relocation-sites-fill')) {
      map.setLayoutProperty('relocation-sites-fill', 'visibility', layersVisible.relocationSites ? 'visible' : 'none');
      map.setLayoutProperty('relocation-sites-line', 'visibility', layersVisible.relocationSites ? 'visible' : 'none');
    }
    if (map.getLayer('alerts-circle')) {
      map.setLayoutProperty('alerts-circle', 'visibility', layersVisible.alerts ? 'visible' : 'none');
    }
  }, [layersVisible, mapLoaded]);

  // Handle Focus Coords
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !focusCoords) return;

    map.flyTo({
      center: focusCoords,
      zoom: 13.5,
      essential: true,
      duration: 1500,
    });
  }, [focusCoords]);

  const toggleLayer = (layerName) => {
    setLayersVisible((prev) => ({ ...prev, [layerName]: !prev[layerName] }));
  };

  const resetView = () => {
    if (mapRef.current) {
      mapRef.current.flyTo({
        center: WAYANAD_COORDS,
        zoom: 11.8,
        pitch: 25,
        bearing: -5,
        duration: 1000,
      });
    }
  };

  return (
    <div
      className={`relative w-full rounded-xl overflow-hidden border border-slate-800 bg-slate-950 ${className}`}
      style={{ height }}
    >
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Top Map Tactical Overlays & Tools */}
      <div className="absolute top-3 left-3 z-10 flex items-center gap-2">
        <div className="bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700/80 shadow-lg text-xs font-mono flex items-center gap-2 text-slate-200">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>WAYANAD EOC SECTOR</span>
          <span className="text-slate-500">|</span>
          <span className="text-amber-400 font-semibold">11.545°N, 76.140°E</span>
        </div>

        <button
          onClick={resetView}
          title="Reset to Sector Overview"
          className="bg-slate-900/90 backdrop-blur-md p-1.5 rounded-lg border border-slate-700/80 text-slate-300 hover:text-white hover:bg-slate-800 transition-colors shadow-lg"
        >
          <Compass className="w-4 h-4 text-sky-400" />
        </button>
      </div>

      {/* Layer Visibility Control Floating Button */}
      <div className="absolute top-3 right-14 z-10">
        <div className="relative">
          <button
            onClick={() => setShowLayerMenu(!showLayerMenu)}
            className="bg-slate-900/90 backdrop-blur-md px-2.5 py-1.5 rounded-lg border border-slate-700/80 text-xs font-medium text-slate-200 hover:text-white flex items-center gap-1.5 shadow-lg"
          >
            <Layers className="w-4 h-4 text-amber-400" />
            <span>GIS Layers</span>
          </button>

          {showLayerMenu && (
            <div className="absolute right-0 top-10 w-56 bg-slate-900/95 backdrop-blur-md border border-slate-700 rounded-lg shadow-2xl p-2.5 z-20 text-xs space-y-1.5">
              <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider px-1 pb-1 border-b border-slate-800">
                Spatial Feature Toggles
              </p>

              <label className="flex items-center justify-between px-1.5 py-1 rounded hover:bg-slate-800 cursor-pointer">
                <span className="flex items-center gap-2 text-rose-300">
                  <Flame className="w-3.5 h-3.5 text-rose-500" />
                  Hazard Red Zones
                </span>
                <input
                  type="checkbox"
                  checked={layersVisible.hazards}
                  onChange={() => toggleLayer('hazards')}
                  className="rounded text-rose-600 focus:ring-0"
                />
              </label>

              <label className="flex items-center justify-between px-1.5 py-1 rounded hover:bg-slate-800 cursor-pointer">
                <span className="flex items-center gap-2 text-amber-300">
                  <Home className="w-3.5 h-3.5 text-amber-500" />
                  Habitations & Risk
                </span>
                <input
                  type="checkbox"
                  checked={layersVisible.habitations}
                  onChange={() => toggleLayer('habitations')}
                  className="rounded text-amber-600 focus:ring-0"
                />
              </label>

              <label className="flex items-center justify-between px-1.5 py-1 rounded hover:bg-slate-800 cursor-pointer">
                <span className="flex items-center gap-2 text-emerald-300">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                  Relocation Sites
                </span>
                <input
                  type="checkbox"
                  checked={layersVisible.relocationSites}
                  onChange={() => toggleLayer('relocationSites')}
                  className="rounded text-emerald-600 focus:ring-0"
                />
              </label>

              <label className="flex items-center justify-between px-1.5 py-1 rounded hover:bg-slate-800 cursor-pointer">
                <span className="flex items-center gap-2 text-red-400">
                  <AlertCircle className="w-3.5 h-3.5 text-red-500" />
                  Active Alerts
                </span>
                <input
                  type="checkbox"
                  checked={layersVisible.alerts}
                  onChange={() => toggleLayer('alerts')}
                  className="rounded text-red-600 focus:ring-0"
                />
              </label>
            </div>
          )}
        </div>
      </div>

      {/* Map Legend Overlay */}
      <div className="absolute bottom-6 right-3 z-10 bg-slate-900/90 backdrop-blur-md p-2.5 rounded-lg border border-slate-700/80 shadow-xl text-[11px] text-slate-300 max-w-[210px] hidden sm:block">
        <p className="font-bold text-[10px] uppercase text-slate-400 tracking-wider mb-1.5">
          Map Legend
        </p>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-xs bg-rose-600/60 border border-rose-500"></span>
            <span>Critical Hazard Red Zone</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-xs bg-red-700/60 border border-red-500"></span>
            <span>Immediate Relocation Habitation</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-xs bg-amber-600/60 border border-amber-500"></span>
            <span>Short-Term Urgency Settlement</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-xs bg-emerald-500/60 border border-emerald-400"></span>
            <span>Safe Relocation Parcel</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 border border-white"></span>
            <span>Active Disaster Point Alert</span>
          </div>
        </div>
      </div>
    </div>
  );
}
