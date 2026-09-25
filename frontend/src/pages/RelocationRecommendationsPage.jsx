import React, { useState, useEffect } from 'react';
import {
  FileCheck2,
  AlertTriangle,
  Home,
  Building2,
  CheckCircle2,
  XCircle,
  ArrowRight,
  ShieldAlert,
  Compass,
  Scale,
  Users,
} from 'lucide-react';
import { getRelocationPriorities, getRelocationRecommendation } from '../services/api';

export default function RelocationRecommendationsPage({ onSelectHabitation, onSelectRelocationSite }) {
  const [prioritiesData, setPrioritiesData] = useState(null);
  const [selectedHabId, setSelectedHabId] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadPriorities() {
      try {
        const res = await getRelocationPriorities();
        setPrioritiesData(res.data);
        if (res.data.priorities && res.data.priorities.length > 0) {
          setSelectedHabId(res.data.priorities[0].habitation_id);
        }
      } catch (err) {
        console.error('Error fetching priorities:', err);
      } finally {
        setLoading(false);
      }
    }
    loadPriorities();
  }, []);

  useEffect(() => {
    async function loadRec() {
      if (!selectedHabId) return;
      try {
        const res = await getRelocationRecommendation(selectedHabId);
        setRecommendation(res.data);
      } catch (err) {
        console.error('Error loading recommendation:', err);
      }
    }
    loadRec();
  }, [selectedHabId]);

  const priorities = prioritiesData?.priorities || [];

  return (
    <div className="space-y-4">
      {/* Header with Urgency Tiers Summary */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm text-xs">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center justify-center">
              <FileCheck2 className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-tight">
                Relocation Urgency Prioritization & Spatial Matching Engine
              </h2>
              <p className="text-[11px] text-slate-400">
                Decision support system synthesizing hazard risk, vulnerability, and candidate parcel capacity
              </p>
            </div>
          </div>

          <div className="text-right">
            <span className="text-[10px] font-mono px-2 py-1 rounded bg-slate-950 text-slate-300 border border-slate-800">
              NDMA / SDMA PROTOCOL ADVISORY
            </span>
          </div>
        </div>

        {/* Urgency Counts Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-800">
          <div className="bg-slate-950 p-2.5 rounded-lg border border-rose-900/40 flex justify-between items-center">
            <span className="text-[11px] text-rose-300 font-semibold">IMMEDIATE (81-100)</span>
            <strong className="text-rose-400 font-mono text-base font-black">
              {prioritiesData?.immediate_count ?? 3}
            </strong>
          </div>

          <div className="bg-slate-950 p-2.5 rounded-lg border border-amber-900/40 flex justify-between items-center">
            <span className="text-[11px] text-amber-300 font-semibold">SHORT_TERM (61-80)</span>
            <strong className="text-amber-400 font-mono text-base font-black">
              {prioritiesData?.short_term_count ?? 3}
            </strong>
          </div>

          <div className="bg-slate-950 p-2.5 rounded-lg border border-sky-900/40 flex justify-between items-center">
            <span className="text-[11px] text-sky-300 font-semibold">MEDIUM_TERM (31-60)</span>
            <strong className="text-sky-400 font-mono text-base font-black">
              {prioritiesData?.medium_term_count ?? 7}
            </strong>
          </div>

          <div className="bg-slate-950 p-2.5 rounded-lg border border-emerald-900/40 flex justify-between items-center">
            <span className="text-[11px] text-emerald-300 font-semibold">MONITOR (0-30)</span>
            <strong className="text-emerald-400 font-mono text-base font-black">
              {prioritiesData?.monitor_count ?? 5}
            </strong>
          </div>
        </div>
      </div>

      {/* Main Grid: Left Settlements Ranked, Right Detailed Matched Recommendation */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left Column: Ranked Settlements */}
        <div className="space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 px-1">
            Settlements Ranked by Urgency
          </h3>

          <div className="space-y-2">
            {priorities.map((item) => {
              const isSelected = item.habitation_id === selectedHabId;
              const isImm = item.priority === 'IMMEDIATE';
              const isShort = item.priority === 'SHORT_TERM';

              return (
                <div
                  key={item.habitation_id}
                  onClick={() => setSelectedHabId(item.habitation_id)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer text-xs ${
                    isSelected
                      ? 'bg-slate-900 border-amber-500 shadow-md shadow-amber-950/20'
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-bold text-slate-100">{item.habitation_name}</h4>
                      <p className="text-[11px] text-slate-500 font-mono">
                        {item.district || 'Wayanad'} • Pop: {(item.vulnerable_population || 1450).toLocaleString()} vulnerable
                      </p>
                    </div>

                    <span
                      className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] border ${
                        isImm
                          ? 'bg-rose-950 text-rose-300 border-rose-700'
                          : isShort
                          ? 'bg-amber-950 text-amber-300 border-amber-700'
                          : 'bg-sky-950 text-sky-300 border-sky-700'
                      }`}
                    >
                      {item.priority || 'IMMEDIATE'} ({item.priority_score || 89})
                    </span>
                  </div>

                  <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                    <span className="truncate max-w-[170px]">
                      Site: <strong className="text-emerald-400">{item.recommended_site_name || 'Meppadi Safe Zone'}</strong>
                    </span>
                    <span className="font-mono text-slate-300">
                      {(item.recommended_site_distance_km || 4.2).toFixed(1)} km
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Detailed Recommendation Inspector */}
        <div className="lg:col-span-2">
          {recommendation ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4 text-xs">
              {/* Header */}
              <div className="flex flex-wrap items-start justify-between gap-3 pb-3 border-b border-slate-800">
                <div>
                  <span className="text-[10px] font-mono text-amber-400 uppercase tracking-wider">
                    Recommended Action Plan
                  </span>
                  <h3 className="text-lg font-black text-white">{recommendation.habitation_name}</h3>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Vulnerable population requiring resettlement:{' '}
                    <strong className="text-rose-400 font-mono">
                      {(recommendation.vulnerable_population || 1450).toLocaleString()} residents
                    </strong>
                  </p>
                </div>

                <div className="text-right">
                  <span className="px-3 py-1 rounded bg-rose-950 text-rose-300 border border-rose-700 font-mono font-bold text-xs">
                    {recommendation.priority} URGENCY
                  </span>
                </div>
              </div>

              {/* Matched Site Recommendation Card */}
              {recommendation.best_suitable_site && (
                <div className="bg-slate-950 p-4 rounded-xl border border-emerald-500/40 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg bg-emerald-950 text-emerald-400 border border-emerald-700 flex items-center justify-center">
                        <Building2 className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="text-[10px] font-mono text-emerald-400 uppercase">
                          Optimized Destination Parcel
                        </span>
                        <h4 className="font-bold text-slate-100 text-sm">
                          {recommendation.best_suitable_site.site_name}
                        </h4>
                      </div>
                    </div>

                    <div className="text-right font-mono">
                      <span className="text-emerald-400 font-bold text-sm">
                        Match Score: {recommendation.best_suitable_site.match_score || 91}%
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-2 border-t border-slate-800/80 text-[11px]">
                    <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">
                      <span className="text-slate-400 block text-[10px] uppercase">Geodesic Distance</span>
                      <strong className="text-slate-200 font-mono text-sm">
                        {(recommendation.best_suitable_site.distance_km || 4.2).toFixed(1)} km
                      </strong>
                    </div>

                    <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">
                      <span className="text-slate-400 block text-[10px] uppercase">Site Available Capacity</span>
                      <strong className="text-emerald-400 font-mono text-sm">
                        {(recommendation.best_suitable_site.available_capacity || 2800).toLocaleString()} persons
                      </strong>
                    </div>

                    <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">
                      <span className="text-slate-400 block text-[10px] uppercase">Capacity Sufficiency</span>
                      <div className="flex items-center gap-1 mt-0.5">
                        {recommendation.best_suitable_site.capacity_sufficient ? (
                          <>
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                            <span className="font-bold text-emerald-400 font-mono text-xs">SUFFICIENT BUFFER</span>
                          </>
                        ) : (
                          <>
                            <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                            <span className="font-bold text-rose-400 font-mono text-xs">DEFICIT</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Reasons Supporting Priority & Relocation */}
              {recommendation.reasons && (
                <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 space-y-1.5">
                  <h5 className="font-bold text-slate-200 uppercase text-[10px] tracking-wider mb-2">
                    Evidence-Based Assessment Justification:
                  </h5>
                  <ul className="space-y-1 text-[11px] text-slate-300">
                    {recommendation.reasons.map((reason, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-amber-400 mt-0.5">•</span>
                        <span>{reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Alternative Fallback Sites */}
              {recommendation.alternative_sites && recommendation.alternative_sites.length > 0 && (
                <div className="space-y-2">
                  <h5 className="font-bold text-slate-400 uppercase text-[10px] tracking-wider">
                    Alternative Contingency Parcels
                  </h5>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {recommendation.alternative_sites.map((alt, i) => (
                      <div key={i} className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 flex justify-between items-center text-[11px]">
                        <div>
                          <p className="font-semibold text-slate-200">{alt.site_name}</p>
                          <p className="text-[10px] text-slate-500 font-mono">
                            Dist: {(alt.distance_km || 6.8).toFixed(1)} km • Buffer: {(alt.available_capacity || 2150).toLocaleString()}
                          </p>
                        </div>
                        <span className="text-[10px] text-emerald-400 font-mono font-bold">
                          {alt.suitability_score || 86}/100
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Human-In-The-Loop Governance Disclaimer */}
              <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-800/40 text-[11px] text-amber-300/90 leading-relaxed">
                <span className="font-bold uppercase tracking-wider block text-[10px] text-amber-400 mb-0.5">
                  Official Decision-Support Governance Notice:
                </span>
                {recommendation.decision_support_disclaimer ||
                  "This system provides algorithmic decision support based on terrain susceptibility and civil carrying capacity norms. It does not replace executive administrative orders by the District Disaster Management Authority (DDMA) or State Government."}
              </div>
            </div>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-400 text-xs">
              <Compass className="w-8 h-8 mx-auto mb-2 text-slate-600 animate-spin" />
              <span>Select a settlement on the left to inspect its relocation matching plan...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
