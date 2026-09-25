import React, { useState, useEffect } from 'react';
import {
  Map,
  Layers,
  Search,
  Compass,
  AlertTriangle,
  Flame,
  Home,
  ShieldCheck,
  Info,
  Maximize2,
} from 'lucide-react';
import GISMap from '../components/GISMap';
import SidePanel from '../components/SidePanel';
import { getHabitations, getHazards, getRelocationSites, getAlerts } from '../services/api';

export default function RiskMapPage({ onSelectHabitation, onSelectRelocationSite }) {
  const [habitations, setHabitations] = useState([]);
  const [hazards, setHazards] = useState([]);
  const [relocationSites, setRelocationSites] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [focusCoords, setFocusCoords] = useState(null);

  useEffect(() => {
    async function fetchData() {
      const [habRes, hazRes, sitesRes, alertsRes] = await Promise.all([
        getHabitations({ page_size: 100 }),
        getHazards(),
        getRelocationSites({ page_size: 100 }),
        getAlerts(),
      ]);

      setHabitations(habRes.data.items || []);
      setHazards(hazRes.data.items || []);
      setRelocationSites(sitesRes.data.items || []);
      setAlerts(alertsRes.data.items || []);

      if (habRes.data.items && habRes.data.items.length > 0) {
        setSelectedEntity({ type: 'habitation', data: habRes.data.items[0] });
      }
    }
    fetchData();
  }, []);

  const handleSearchSelect = (hab) => {
    setSelectedEntity({ type: 'habitation', data: hab });
    if (hab.geometry?.coordinates) {
      // Find center coordinate
      const coords = hab.geometry.coordinates[0][0];
      setFocusCoords(coords);
    }
  };

  const filteredHabitations = habitations.filter((h) =>
    h.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-4">
      {/* Top Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 shadow-sm text-xs">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center justify-center">
            <Map className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight">
              Wayanad Sector GIS Risk Mapping Lab
            </h2>
            <p className="text-[11px] text-slate-400">
              Interactive multi-layer geospatial engine with PostGIS hazard polygons & safe buffers
            </p>
          </div>
        </div>

        {/* Search quick settlement jump */}
        <div className="relative w-64">
          <input
            type="text"
            placeholder="Jump to habitation..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
          />
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />

          {searchQuery && filteredHabitations.length > 0 && (
            <div className="absolute left-0 right-0 top-9 bg-slate-900 border border-slate-700 rounded-lg shadow-xl max-h-48 overflow-y-auto z-30">
              {filteredHabitations.map((h) => (
                <button
                  key={h.id}
                  onClick={() => {
                    handleSearchSelect(h);
                    setSearchQuery('');
                  }}
                  className="w-full text-left px-3 py-1.5 text-xs hover:bg-slate-800 flex items-center justify-between text-slate-300"
                >
                  <span className="font-semibold">{h.name}</span>
                  <span className="text-[10px] text-rose-400 font-mono">Risk: {h.risk_score}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Main Map View + Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-3">
          <GISMap
            habitations={habitations}
            hazards={hazards}
            relocationSites={relocationSites}
            alerts={alerts}
            onSelectEntity={(entity) => setSelectedEntity(entity)}
            selectedEntity={selectedEntity}
            height="620px"
            focusCoords={focusCoords}
          />
        </div>

        <div>
          <SidePanel
            selectedEntity={selectedEntity}
            onClose={() => setSelectedEntity(null)}
            onViewHabitationDetail={(id) => onSelectHabitation(id)}
            onViewRelocationDetail={(id) => onSelectRelocationSite(id)}
          />
        </div>
      </div>
    </div>
  );
}
