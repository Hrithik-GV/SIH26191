import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  Home,
  ShieldAlert,
  AlertTriangle,
  Building2,
  Users,
  Compass,
  MapPin,
  CheckCircle2,
  Flame,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';
import {
  getHabitationById,
  getHabitationRisk,
  getHabitationVulnerability,
  getNearbyRelocationSites,
} from '../services/api';

export default function HabitationDetailPage({
  habitationId,
  onBack,
  onSelectRelocationSite,
}) {
  const [habitation, setHabitation] = useState(null);
  const [riskData, setRiskData] = useState(null);
  const [vulnData, setVulnData] = useState(null);
  const [nearbySites, setNearbySites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDetail() {
      try {
        const [habRes, riskRes, vulnRes, nearRes] = await Promise.all([
          getHabitationById(habitationId),
          getHabitationRisk(habitationId),
          getHabitationVulnerability(habitationId),
          getNearbyRelocationSites(habitationId),
        ]);

        setHabitation(habRes.data);
        setRiskData(riskRes.data);
        setVulnData(vulnRes.data);
        setNearbySites(nearRes.data.recommended_sites || []);
      } catch (err) {
        console.error('Error loading habitation details:', err);
      } finally {
        setLoading(false);
      }
    }

    if (habitationId) {
      loadDetail();
    }
  }, [habitationId]);

  if (loading || !habitation) {
    return (
      <div className="flex items-center justify-center p-12 text-slate-400 text-xs">
        <Compass className="w-6 h-6 animate-spin mr-2 text-amber-400" />
        <span>Loading habitation assessment telemetry...</span>
      </div>
    );
  }

  const isImmediate = habitation.priority === 'IMMEDIATE' || (habitation.risk_score || 0) >= 81;
  const isHigh = habitation.priority === 'SHORT_TERM' || ((habitation.risk_score || 0) >= 61 && (habitation.risk_score || 0) <= 80);

  const factors = vulnData?.factors || {
    total_population: 85,
    vulnerable_population: 88,
    population_density: 65,
    elderly_population: 74,
    children_population: 78,
    disabled_population: 70,
    housing_vulnerability: 82,
    infrastructure_vulnerability: 75,
    evacuation_accessibility: 84,
  };

  return (
    <div className="space-y-4">
      {/* Top Header with Back Navigation */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm text-xs">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <button
              onClick={onBack}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-black text-white tracking-tight">{habitation.name}</h1>
                <span
                  className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] border ${
                    isImmediate
                      ? 'bg-rose-950 text-rose-300 border-rose-700'
                      : isHigh
                      ? 'bg-amber-950 text-amber-300 border-amber-700'
                      : 'bg-sky-950 text-sky-300 border-sky-700'
                  }`}
                >
                  {habitation.priority || 'IMMEDIATE'} ACTION
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                {habitation.taluk || 'Vythiri'} Taluk • {habitation.district || 'Wayanad'}, {habitation.state || 'Kerala'} •{' '}
                <span className="font-mono text-slate-300">ID: {habitation.id}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono px-2 py-1 rounded bg-slate-950 text-slate-300 border border-slate-800">
              DEMO SYNTHESIS PROXY DATA
            </span>
          </div>
        </div>
      </div>

      {/* 4 Score Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <div className="bg-slate-900 border border-rose-500/30 p-4 rounded-xl shadow-lg">
          <span className="text-[11px] font-semibold uppercase text-slate-400">Multi-Hazard Risk</span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-black font-mono text-rose-400">
              {riskData?.overall_score || habitation.risk_score || 88}
            </span>
            <span className="text-xs text-slate-500">/100</span>
          </div>
          <span className="text-[10px] text-rose-300 font-mono mt-1 inline-block">
            {riskData?.severity || 'CRITICAL'} SEVERITY
          </span>
        </div>

        <div className="bg-slate-900 border border-amber-500/30 p-4 rounded-xl shadow-lg">
          <span className="text-[11px] font-semibold uppercase text-slate-400">Vulnerability Score</span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-black font-mono text-amber-400">
              {vulnData?.vulnerability_score || habitation.vulnerability_score || 82}
            </span>
            <span className="text-xs text-slate-500">/100</span>
          </div>
          <span className="text-[10px] text-amber-300 font-mono mt-1 inline-block">
            9 Demographic Indicators
          </span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-lg">
          <span className="text-[11px] font-semibold uppercase text-slate-400">Vulnerable Population</span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-black font-mono text-slate-100">
              {(habitation.vulnerable_population || 1450).toLocaleString()}
            </span>
            <span className="text-xs text-slate-400">
              / {(habitation.population || 2180).toLocaleString()}
            </span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono mt-1 inline-block">
            {Math.round(((habitation.vulnerable_population || 1450) / (habitation.population || 2180)) * 100)}% of total residents
          </span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-lg">
          <span className="text-[11px] font-semibold uppercase text-slate-400">Kutcha Housing Fragility</span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-black font-mono text-rose-400">
              {habitation.demographics?.kutcha_houses_pct || 72}%
            </span>
          </div>
          <span className="text-[10px] text-slate-400 font-mono mt-1 inline-block">
            High structural damage risk
          </span>
        </div>
      </div>

      {/* Main Grid: Vulnerability Factors + Transparent Risk Explanations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left: 9 Demographic Vulnerability Factors */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg text-xs">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-3 border-b border-slate-800 pb-2">
            9 Socio-Demographic Vulnerability Factors
          </h3>

          <div className="space-y-2.5">
            {Object.entries(factors).map(([key, val]) => {
              const label = key
                .split('_')
                .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                .join(' ');
              const numVal = typeof val === 'number' ? val : 75;

              return (
                <div key={key}>
                  <div className="flex justify-between text-[11px] text-slate-300 mb-1">
                    <span>{label}</span>
                    <span className="font-mono font-bold text-amber-400">{numVal}/100</span>
                  </div>
                  <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                    <div
                      className={`h-full rounded-full ${
                        numVal >= 80 ? 'bg-rose-500' : numVal >= 60 ? 'bg-amber-500' : 'bg-sky-500'
                      }`}
                      style={{ width: `${numVal}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Transparent Hazard Risk Triggers & Explanations */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg text-xs flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-3 border-b border-slate-800 pb-2 flex items-center justify-between">
              <span>Transparent Risk Trigger Factors</span>
              <span className="text-[10px] font-mono text-emerald-400">NON-BLACK-BOX MODEL</span>
            </h3>

            <div className="space-y-2 mb-4">
              {(riskData?.explanation || [
                "Heavy rainfall intensity (382 mm in 24 hours recorded within 15 km)",
                "Critical 92% spatial overlap with designated GSI/ISRO landslide red zones",
                "High slope gradient (> 28 degrees) accelerating saturated soil slippage",
                "Historical disaster records show recurring mass movements in 2019 and 2024",
                "Immediate proximity to river drainage corridor (under 250 meters)"
              ]).map((exp, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 flex items-start gap-2 text-slate-200">
                  <Flame className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                  <span className="text-[11px] leading-relaxed">{exp}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-800/40 text-[11px] text-amber-300/90 leading-relaxed">
            <strong>Advisory Directive:</strong> Immediate supervised evacuation protocol recommended. Priority score indicates critical threat to human life within 24 hours of heavy rainfall threshold exceedance.
          </div>
        </div>
      </div>

      {/* Ranked Candidate Relocation Parcels Nearby */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg text-xs">
        <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Ranked Safe Candidate Relocation Parcels
            </h3>
            <p className="text-[11px] text-slate-400">
              Evaluated by PostGIS geodesic distance, 4-pillar suitability, and carrying capacity sufficiency
            </p>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
            0% Hazard Red Zone Clearance
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {nearbySites.map((site, idx) => (
            <div
              key={site.site_id || idx}
              onClick={() => onSelectRelocationSite(site.site_id)}
              className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 hover:border-emerald-500/50 cursor-pointer transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-start justify-between">
                  <span className="px-1.5 py-0.5 rounded bg-slate-900 text-amber-400 font-mono font-bold text-[10px] border border-slate-800">
                    Rank #{site.proximity_rank || idx + 1}
                  </span>
                  <span className="text-emerald-400 font-mono font-bold text-xs">
                    {site.suitability_score || 88}/100
                  </span>
                </div>

                <h4 className="font-bold text-slate-100 text-xs mt-2 group-hover:text-emerald-400 transition-colors">
                  {site.site_name}
                </h4>

                <div className="my-2 space-y-1 text-[11px] text-slate-400">
                  <div className="flex justify-between">
                    <span>Geodesic Distance:</span>
                    <span className="font-mono text-slate-200">{(site.distance_km || 4.2).toFixed(1)} km</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Available Capacity:</span>
                    <span className="font-mono text-emerald-400 font-bold">
                      {(site.available_capacity || 2800).toLocaleString()} persons
                    </span>
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-900 flex justify-between items-center text-[10px] text-emerald-400 font-medium">
                <span>View Full Capacity Profile</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
