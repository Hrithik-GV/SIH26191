import React from 'react';
import {
  X,
  AlertTriangle,
  Home,
  ShieldCheck,
  Flame,
  ArrowRight,
  Users,
  Compass,
  Building2,
  Droplets,
  Activity,
  CheckCircle,
  ExternalLink,
} from 'lucide-react';

export default function SidePanel({
  selectedEntity,
  onClose,
  onViewHabitationDetail,
  onViewRelocationDetail,
}) {
  if (!selectedEntity) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-slate-400 text-xs flex flex-col justify-center items-center text-center h-full min-h-[300px]">
        <Compass className="w-8 h-8 text-slate-600 mb-2 animate-spin-slow" />
        <p className="font-semibold text-slate-300">Sector Inspector Idle</p>
        <p className="text-[11px] text-slate-500 mt-1 max-w-[200px]">
          Click on any settlement polygon, hazard zone, candidate relocation parcel, or alert marker on the GIS map to inspect situational telemetry.
        </p>
      </div>
    );
  }

  const { type, data } = selectedEntity;

  // 1. Habitation Profile
  if (type === 'habitation') {
    const isImmediate = data.priority === 'IMMEDIATE' || (data.risk_score || 0) >= 81;
    const isHigh = data.priority === 'SHORT_TERM' || ((data.risk_score || 0) >= 61 && (data.risk_score || 0) <= 80);

    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-slate-200 text-xs flex flex-col justify-between h-full shadow-xl">
        <div>
          {/* Header */}
          <div className="flex items-start justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-red-950/80 border border-red-800/80 flex items-center justify-center text-red-400">
                <Home className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                  Vulnerable Habitation
                </span>
                <h3 className="text-sm font-bold text-white leading-tight">{data.name}</h3>
              </div>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Quick Metrics Grid */}
          <div className="grid grid-cols-2 gap-2 my-3">
            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Relocation Urgency</span>
              <div className="mt-1">
                <span
                  className={`inline-block px-2 py-0.5 rounded font-mono font-bold text-[11px] border ${
                    isImmediate
                      ? 'bg-rose-950/60 text-rose-300 border-rose-700/60'
                      : isHigh
                      ? 'bg-amber-950/60 text-amber-300 border-amber-700/60'
                      : 'bg-sky-950/60 text-sky-300 border-sky-700/60'
                  }`}
                >
                  {data.priority || (isImmediate ? 'IMMEDIATE' : 'SHORT_TERM')}
                </span>
              </div>
            </div>

            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Composite Risk</span>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-lg font-black font-mono text-rose-400">
                  {data.risk_score || data.overall_score || 88}
                </span>
                <span className="text-[10px] text-slate-500">/100</span>
              </div>
            </div>

            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Total Population</span>
              <div className="mt-1 text-base font-bold font-mono text-slate-100">
                {(data.population || 2180).toLocaleString()}
              </div>
            </div>

            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Vulnerable Lives</span>
              <div className="mt-1 text-base font-bold font-mono text-amber-400">
                {(data.vulnerable_population || 1450).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Demographic Breakdown */}
          {data.demographics && (
            <div className="bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/80 mb-3 text-[11px] space-y-1">
              <div className="flex justify-between text-slate-400">
                <span>Elderly ({data.demographics.elderly_population || 310})</span>
                <span className="text-slate-200">
                  {Math.round(((data.demographics.elderly_population || 310) / (data.population || 2180)) * 100)}%
                </span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Children ({data.demographics.children_population || 420})</span>
                <span className="text-slate-200">
                  {Math.round(((data.demographics.children_population || 420) / (data.population || 2180)) * 100)}%
                </span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Kutcha Dwellings</span>
                <span className="text-rose-400 font-semibold">{data.demographics.kutcha_houses_pct || 72}%</span>
              </div>
            </div>
          )}

          {/* Key Explanations */}
          {data.explanations && data.explanations.length > 0 && (
            <div>
              <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider mb-1.5">
                Critical Hazard Triggers:
              </p>
              <ul className="space-y-1 text-[11px] text-slate-300">
                {data.explanations.slice(0, 3).map((exp, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <span className="text-rose-400 mt-0.5">•</span>
                    <span>{exp}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="pt-3 border-t border-slate-800 flex gap-2">
          {onViewHabitationDetail && (
            <button
              onClick={() => onViewHabitationDetail(data.id)}
              className="flex-1 py-1.5 px-3 bg-amber-600 hover:bg-amber-500 text-white rounded font-medium text-xs flex items-center justify-center gap-1.5 transition-colors shadow-sm"
            >
              <span>Detailed Assessment</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    );
  }

  // 2. Relocation Site Profile
  if (type === 'relocation_site') {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-slate-200 text-xs flex flex-col justify-between h-full shadow-xl">
        <div>
          {/* Header */}
          <div className="flex items-start justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-emerald-950/80 border border-emerald-800/80 flex items-center justify-center text-emerald-400">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                  Relocation Candidate Parcel
                </span>
                <h3 className="text-sm font-bold text-white leading-tight">{data.name}</h3>
              </div>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Quick Metrics Grid */}
          <div className="grid grid-cols-2 gap-2 my-3">
            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Suitability Score</span>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-lg font-black font-mono text-emerald-400">
                  {data.suitability_score || data.overall_suitability_score || 89}
                </span>
                <span className="text-[10px] text-slate-500">/100</span>
              </div>
            </div>

            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Classification</span>
              <div className="mt-1">
                <span className="inline-block px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-emerald-950/60 text-emerald-300 border border-emerald-700/60">
                  {data.classification || 'HIGHLY SUITABLE'}
                </span>
              </div>
            </div>

            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Available Land</span>
              <div className="mt-1 text-base font-bold font-mono text-slate-100">
                {Math.round(data.usable_area_sqm || data.available_area || 125000).toLocaleString()} m²
              </div>
            </div>

            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Intake Capacity</span>
              <div className="mt-1 text-base font-bold font-mono text-emerald-400">
                {(data.available_capacity || 2800).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Civil Carrying Capacity Breakdown (Liebig's Law) */}
          {data.factor_capacities && (
            <div className="bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/80 mb-3 text-[11px] space-y-1">
              <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider mb-1">
                Civil Bottlenecks (Liebig's Law):
              </p>
              <div className="flex justify-between text-slate-400">
                <span>Land Density Capacity</span>
                <span className="font-mono text-slate-200">{data.factor_capacities.usable_land?.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Potable Water Yield (70 LPCD)</span>
                <span className="font-mono text-sky-400">{data.factor_capacities.water_supply?.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Sanitation & Septic Absorption</span>
                <span className="font-mono text-amber-400">{data.factor_capacities.sanitation?.toLocaleString()}</span>
              </div>
            </div>
          )}

          {/* Strengths */}
          {data.strengths && (
            <div>
              <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider mb-1">
                Clearances & Safety Strengths:
              </p>
              <ul className="space-y-1 text-[11px] text-slate-300">
                {data.strengths.slice(0, 2).map((s, i) => (
                  <li key={i} className="flex items-start gap-1.5">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Action Button */}
        {onViewRelocationDetail && (
          <div className="pt-3 border-t border-slate-800">
            <button
              onClick={() => onViewRelocationDetail(data.id)}
              className="w-full py-1.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-medium text-xs flex items-center justify-center gap-1.5 transition-colors"
            >
              <span>Capacity & Allocation View</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    );
  }

  // 3. Hazard Zone Profile
  if (type === 'hazard') {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-slate-200 text-xs flex flex-col justify-between h-full shadow-xl">
        <div>
          <div className="flex items-start justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-rose-950/80 border border-rose-800/80 flex items-center justify-center text-rose-400">
                <Flame className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                  Hazard Red Zone
                </span>
                <h3 className="text-sm font-bold text-white capitalize">{data.hazard_type || 'Landslide Zone'}</h3>
              </div>
            </div>
            {onClose && (
              <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <div className="my-3 space-y-2">
            <div className="flex justify-between items-center bg-slate-950 p-2 rounded border border-slate-800">
              <span className="text-slate-400">Severity Tier:</span>
              <span className="px-2 py-0.5 rounded font-mono font-bold bg-rose-950 text-rose-300 border border-rose-700">
                {data.severity || 'CRITICAL'}
              </span>
            </div>

            <div className="flex justify-between items-center bg-slate-950 p-2 rounded border border-slate-800">
              <span className="text-slate-400">Risk Score:</span>
              <span className="font-mono font-bold text-rose-400 text-sm">
                {data.risk_score || 94}/100
              </span>
            </div>

            <div className="flex justify-between items-center bg-slate-950 p-2 rounded border border-slate-800">
              <span className="text-slate-400">Originating Source:</span>
              <span className="font-mono text-slate-200">{data.source || 'GSI / ISRO Bhuvan'}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 4. Alert Profile
  if (type === 'alert') {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-slate-200 text-xs flex flex-col justify-between h-full shadow-xl">
        <div>
          <div className="flex items-start justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-rose-950/80 border border-rose-800/80 flex items-center justify-center text-rose-400">
                <AlertTriangle className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                  Emergency Alert
                </span>
                <h3 className="text-sm font-bold text-white uppercase">{data.disaster_type || 'EMERGENCY WARNING'}</h3>
              </div>
            </div>
            {onClose && (
              <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <div className="my-3 space-y-2">
            <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-[11px] leading-relaxed text-slate-300">
              {data.description || 'Immediate emergency response protocol active in this spatial sector.'}
            </div>

            <div className="flex justify-between items-center text-[11px] text-slate-400 pt-1">
              <span>Source: <strong className="text-slate-200">{data.source || 'NDMA SACHET CAP'}</strong></span>
              <span className="px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 font-mono font-bold text-[10px]">
                {data.severity || 'CRITICAL'}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
