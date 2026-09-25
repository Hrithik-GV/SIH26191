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
  MapPin,
  Waves,
  Navigation,
  School,
  HeartPulse,
  CloudRain,
  ShieldAlert,
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
          Click on any habitation, candidate relocation parcel, river, road, hospital, school, or hazard zone to inspect situational telemetry.
        </p>
      </div>
    );
  }

  const { type, data } = selectedEntity;

  // 1. Habitation Profile
  // Required fields: Name, Population, Hazard score, Vulnerability score, Priority, Main risk factors, Recommended relocation site
  if (type === 'habitation') {
    const isImmediate = data.priority === 'IMMEDIATE' || (data.hazard_score || data.risk_score || 0) >= 81;
    const isHigh = data.priority === 'SHORT_TERM' || ((data.hazard_score || data.risk_score || 0) >= 61 && (data.hazard_score || data.risk_score || 0) <= 80);

    const hazardScore = data.hazard_score ?? data.risk_score ?? data.overall_score ?? 88;
    const vulnScore = data.vulnerability_score ?? 82;
    const priority = data.priority || (isImmediate ? 'IMMEDIATE' : 'SHORT_TERM');
    const population = (data.population || 2180).toLocaleString();
    const vulnerablePop = (data.vulnerable_population || 1450).toLocaleString();
    const recommendedSite = data.recommended_relocation_site || data.recommended_site_name || 'Meppadi Safe Plateau Zone A';

    const riskFactors = data.main_risk_factors || data.explanations || [
      'Slope gradient > 28° within severe runoff corridor',
      'Torrential rainfall saturation index > 92%',
      'Kutcha dwellings proportion exceeds 65%',
    ];

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

          {/* Core Telemetry Grid (Name, Population, Hazard score, Vulnerability score, Priority) */}
          <div className="grid grid-cols-2 gap-2 my-3">
            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Priority Status</span>
              <div className="mt-1">
                <span
                  className={`inline-block px-2 py-0.5 rounded font-mono font-bold text-[11px] border ${
                    priority === 'IMMEDIATE'
                      ? 'bg-rose-950/80 text-rose-300 border-rose-700'
                      : priority === 'SHORT_TERM'
                      ? 'bg-amber-950/80 text-amber-300 border-amber-700'
                      : 'bg-sky-950/80 text-sky-300 border-sky-700'
                  }`}
                >
                  {priority}
                </span>
              </div>
            </div>

            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Hazard Score</span>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-lg font-black font-mono text-rose-400">
                  {hazardScore}
                </span>
                <span className="text-[10px] text-slate-500">/100</span>
              </div>
            </div>

            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Vulnerability Score</span>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-lg font-black font-mono text-amber-400">
                  {vulnScore}
                </span>
                <span className="text-[10px] text-slate-500">/100</span>
              </div>
            </div>

            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Total Population</span>
              <div className="mt-1 text-base font-bold font-mono text-slate-100">
                {population}
                <span className="block text-[10px] font-normal text-amber-400">
                  ({vulnerablePop} at risk)
                </span>
              </div>
            </div>
          </div>

          {/* Main Risk Factors */}
          <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-800/90 mb-3 space-y-1.5">
            <p className="text-[10px] uppercase font-bold text-rose-400 tracking-wider flex items-center gap-1.5">
              <Flame className="w-3.5 h-3.5" />
              Main Risk Factors
            </p>
            <ul className="space-y-1 text-[11px] text-slate-300">
              {riskFactors.map((factor, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <span className="text-rose-500 font-bold">•</span>
                  <span>{factor}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Recommended Relocation Site */}
          <div className="bg-emerald-950/30 p-2.5 rounded-lg border border-emerald-800/40 text-[11px]">
            <span className="text-[10px] uppercase font-bold text-emerald-400 tracking-wider flex items-center gap-1 mb-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              Recommended Relocation Site
            </span>
            <div className="font-semibold text-emerald-200">
              {recommendedSite}
            </div>
            <p className="text-[10px] text-emerald-400/80 mt-0.5">
              Designated reception zone with safe geology and available civil infrastructure.
            </p>
          </div>
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
  // Required fields: Site name, Suitability score, Carrying capacity, Current population, Available capacity, Infrastructure, Distance to nearest affected habitation
  if (type === 'relocation_site') {
    const siteName = data.site_name || data.name || 'Candidate Relocation Parcel';
    const suitabilityScore = data.suitability_score ?? data.overall_suitability_score ?? 89;
    const carryingCapacity = (data.carrying_capacity ?? data.estimated_capacity ?? data.estimated_carrying_capacity ?? 3500).toLocaleString();
    const currentPopulation = (data.current_population ?? data.current_occupancy ?? 700).toLocaleString();
    const availableCapacity = (data.available_capacity ?? 2800).toLocaleString();
    const infrastructure = data.infrastructure || 'Paved 2-lane road (0.4 km) | Community Health Centre (3.2 km) | Water Supply Grid';
    const distanceToNearest = data.distance_to_nearest_habitation || data.distance_to_nearest_affected_habitation || '3.8 km to Chooralmala / 4.2 km to Mundakkai';

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
                <h3 className="text-sm font-bold text-white leading-tight">{siteName}</h3>
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

          {/* Core Metrics Grid */}
          <div className="grid grid-cols-2 gap-2 my-3">
            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Suitability Score</span>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-lg font-black font-mono text-emerald-400">
                  {suitabilityScore}
                </span>
                <span className="text-[10px] text-slate-500">/100</span>
              </div>
            </div>

            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Available Capacity</span>
              <div className="mt-1 text-base font-bold font-mono text-emerald-400">
                {availableCapacity}
                <span className="block text-[10px] font-normal text-slate-400">persons</span>
              </div>
            </div>

            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Carrying Capacity</span>
              <div className="mt-1 text-base font-bold font-mono text-slate-100">
                {carryingCapacity}
              </div>
            </div>

            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Current Population</span>
              <div className="mt-1 text-base font-bold font-mono text-slate-300">
                {currentPopulation}
              </div>
            </div>
          </div>

          {/* Infrastructure Breakdown */}
          <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-800/90 mb-2.5">
            <span className="text-[10px] uppercase font-bold text-sky-400 tracking-wider flex items-center gap-1.5 mb-1">
              <Building2 className="w-3.5 h-3.5" />
              Available Infrastructure
            </span>
            <p className="text-[11px] text-slate-300 leading-relaxed font-mono">
              {infrastructure}
            </p>
          </div>

          {/* Distance to Nearest Affected Habitation */}
          <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-800/90 mb-3">
            <span className="text-[10px] uppercase font-bold text-amber-400 tracking-wider flex items-center gap-1.5 mb-1">
              <Navigation className="w-3.5 h-3.5" />
              Distance to Nearest Affected Habitation
            </span>
            <p className="text-[11px] font-semibold text-slate-200">
              {distanceToNearest}
            </p>
          </div>
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

  // 3. Hospital Profile
  if (type === 'hospital') {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-slate-200 text-xs flex flex-col justify-between h-full shadow-xl">
        <div>
          <div className="flex items-start justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-rose-950/80 border border-rose-800/80 flex items-center justify-center text-rose-400">
                <HeartPulse className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                  Healthcare Facility
                </span>
                <h3 className="text-sm font-bold text-white leading-tight">{data.name}</h3>
              </div>
            </div>
            {onClose && (
              <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <div className="grid grid-cols-2 gap-2 my-3">
            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Total Beds</span>
              <div className="mt-1 text-base font-bold font-mono text-slate-100">{data.total_beds || 60}</div>
            </div>
            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Emergency Beds</span>
              <div className="mt-1 text-base font-bold font-mono text-rose-400">{data.emergency_beds || 20}</div>
            </div>
          </div>

          <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-800 text-[11px] space-y-1.5">
            <div className="flex justify-between">
              <span className="text-slate-400">Type:</span>
              <span className="font-semibold text-slate-200">{data.facility_type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">ICU Facilities:</span>
              <span className={data.icu_available ? 'text-emerald-400 font-bold' : 'text-amber-400'}>
                {data.icu_available ? 'Available' : 'Field Level'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Distance to Mundakkai:</span>
              <span className="font-mono text-sky-400">{data.distance_to_mundakkai_km} km</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Operational Status:</span>
              <span className="text-emerald-400 font-mono text-[10px]">{data.status}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 4. School / Shelter Profile
  if (type === 'school') {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-slate-200 text-xs flex flex-col justify-between h-full shadow-xl">
        <div>
          <div className="flex items-start justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-amber-950/80 border border-amber-800/80 flex items-center justify-center text-amber-400">
                <School className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                  Relief & Shelter Facility
                </span>
                <h3 className="text-sm font-bold text-white leading-tight">{data.name}</h3>
              </div>
            </div>
            {onClose && (
              <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <div className="grid grid-cols-2 gap-2 my-3">
            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Shelter Capacity</span>
              <div className="mt-1 text-base font-bold font-mono text-amber-400">{data.shelter_capacity || 500}</div>
            </div>
            <div className="bg-slate-950/70 p-2.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase">Current Evacuees</span>
              <div className="mt-1 text-base font-bold font-mono text-slate-100">{data.current_evacuees || 0}</div>
            </div>
          </div>

          <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-800 text-[11px] space-y-1.5">
            <div className="flex justify-between">
              <span className="text-slate-400">Designation:</span>
              <span className="font-semibold text-slate-200">{data.facility_type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Potable Water:</span>
              <span className="text-emerald-400 font-bold">{data.potable_water ? 'Operational' : 'Tanker Required'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Sanitation Units:</span>
              <span className="font-mono text-slate-200">{data.sanitation_units} blocks</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Distance to Epicenter:</span>
              <span className="font-mono text-amber-400">{data.distance_to_mundakkai_km} km</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 5. River / Drainage Channel Profile
  if (type === 'river') {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-slate-200 text-xs flex flex-col justify-between h-full shadow-xl">
        <div>
          <div className="flex items-start justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-sky-950/80 border border-sky-800/80 flex items-center justify-center text-sky-400">
                <Waves className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                  Hydrographic Network
                </span>
                <h3 className="text-sm font-bold text-white leading-tight">{data.name}</h3>
              </div>
            </div>
            {onClose && (
              <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <div className="my-3 space-y-2 bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-400">River Basin:</span>
              <span className="font-semibold text-slate-200">{data.basin}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Channel Width:</span>
              <span className="font-mono text-slate-100">{data.width_m} meters</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Flash Flood Susceptibility:</span>
              <span className="px-1.5 py-0.5 rounded font-mono font-bold bg-rose-950 text-rose-300 border border-rose-800">
                {data.flood_prone ? 'CRITICAL RISK' : 'LOW RISK'}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 6. Road / Evacuation Corridor Profile
  if (type === 'road') {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-slate-200 text-xs flex flex-col justify-between h-full shadow-xl">
        <div>
          <div className="flex items-start justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-amber-400">
                <Navigation className="w-4 h-4" />
              </div>
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                  Transportation Corridor
                </span>
                <h3 className="text-sm font-bold text-white leading-tight">{data.name}</h3>
              </div>
            </div>
            {onClose && (
              <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-slate-800">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <div className="my-3 space-y-2 bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-[11px]">
            <div className="flex justify-between">
              <span className="text-slate-400">Category:</span>
              <span className="font-semibold text-slate-200">{data.category}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Lanes:</span>
              <span className="font-mono text-slate-100">{data.lanes} Lane(s)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Evacuation Route:</span>
              <span className={data.evacuation_route ? 'text-emerald-400 font-bold' : 'text-slate-400'}>
                {data.evacuation_route ? 'Designated Evacuation Corridor' : 'Secondary Access'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Status:</span>
              <span className="text-amber-400 font-mono text-[10px] font-semibold">{data.status}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 7. Hazard Zone Profile
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
                <h3 className="text-sm font-bold text-white capitalize">{data.hazard_type || data.name || 'Hazard Zone'}</h3>
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

  // 8. Alert Profile
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
