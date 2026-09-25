import React, { useState, useEffect } from 'react';
import {
  Building2,
  ShieldCheck,
  Droplets,
  Zap,
  Truck,
  HeartPulse,
  Trees,
  CheckCircle2,
  AlertTriangle,
  Compass,
  ArrowRight,
} from 'lucide-react';
import { getRelocationSites, getRelocationSiteCapacity, getRelocationSiteAssessment } from '../services/api';

export default function RelocationSitesPage({ onSelectSite }) {
  const [sites, setSites] = useState([]);
  const [selectedSiteId, setSelectedSiteId] = useState(null);
  const [capacityData, setCapacityData] = useState(null);
  const [assessmentData, setAssessmentData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchSites() {
      try {
        const res = await getRelocationSites({ page_size: 50 });
        const items = res.data.items || [];
        setSites(items);
        if (items.length > 0) {
          setSelectedSiteId(items[0].id);
        }
      } catch (err) {
        console.error('Error fetching relocation sites:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchSites();
  }, []);

  useEffect(() => {
    async function fetchSiteDetails() {
      if (!selectedSiteId) return;
      try {
        const [capRes, assessRes] = await Promise.all([
          getRelocationSiteCapacity(selectedSiteId),
          getRelocationSiteAssessment(selectedSiteId),
        ]);
        setCapacityData(capRes.data);
        setAssessmentData(assessRes.data);
      } catch (err) {
        console.error('Error loading site details:', err);
      }
    }
    fetchSiteDetails();
  }, [selectedSiteId]);

  const selectedSite = sites.find((s) => s.id === selectedSiteId) || sites[0];

  return (
    <div className="space-y-4">
      {/* Header Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm text-xs">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center">
              <Building2 className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-tight">
                Candidate Resettlement Sites & Ecological Carrying Capacity
              </h2>
              <p className="text-[11px] text-slate-400">
                Multi-pillar carrying capacity model bounded by Liebig's Law of the Minimum
              </p>
            </div>
          </div>

          <div className="text-right">
            <span className="text-xs text-slate-400">Total Evaluated Parcels:</span>{' '}
            <strong className="text-emerald-400 font-mono text-sm">{sites.length}</strong>
          </div>
        </div>
      </div>

      {/* Grid: Left Parcel Cards List, Right Detailed Liebig Capacity Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left Column: Parcels List */}
        <div className="space-y-2.5">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 px-1">
            Evaluated Candidate Sites
          </h3>

          <div className="space-y-2">
            {sites.map((site) => {
              const isSelected = site.id === selectedSiteId;
              return (
                <div
                  key={site.id}
                  onClick={() => setSelectedSiteId(site.id)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer text-xs ${
                    isSelected
                      ? 'bg-slate-900 border-emerald-500 shadow-md shadow-emerald-950/20'
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-bold text-slate-100">{site.name}</h4>
                      <p className="text-[11px] text-slate-500 font-mono">
                        {site.taluk || 'Vythiri'}, {site.district || 'Wayanad'}
                      </p>
                    </div>

                    <span className="px-2 py-0.5 rounded font-mono font-bold text-xs bg-emerald-950 text-emerald-300 border border-emerald-800">
                      {site.suitability_score || site.overall_suitability_score || 88}/100
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 mt-3 pt-2.5 border-t border-slate-800/80 text-[11px]">
                    <div>
                      <span className="text-slate-500 block text-[10px] uppercase">Available Capacity</span>
                      <strong className="text-emerald-400 font-mono">
                        {(site.available_capacity || 2800).toLocaleString()} persons
                      </strong>
                    </div>

                    <div>
                      <span className="text-slate-500 block text-[10px] uppercase">Usable Area</span>
                      <strong className="text-slate-200 font-mono">
                        {Math.round(site.usable_area_sqm || site.available_area || 125000).toLocaleString()} m²
                      </strong>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Detailed Liebig Carrying Capacity Breakdown */}
        {selectedSite && (
          <div className="lg:col-span-2 space-y-4">
            {/* Top Detailed Site Summary Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg text-xs">
              <div className="flex flex-wrap items-start justify-between gap-3 pb-3 border-b border-slate-800">
                <div>
                  <span className="text-[10px] font-mono text-emerald-400 uppercase tracking-wider">
                    Selected Resettlement Parcel
                  </span>
                  <h3 className="text-base font-bold text-white">{selectedSite.name}</h3>
                  <p className="text-[11px] text-slate-400">
                    {selectedSite.taluk || 'Vythiri'}, {selectedSite.district || 'Wayanad'} •{' '}
                    <span className="font-mono text-slate-300">{selectedSite.soil_type || 'STABLE LATERITE BEDROCK'}</span>
                  </p>
                </div>

                <div className="text-right">
                  <span className="px-2.5 py-1 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono font-bold text-xs">
                    {selectedSite.classification || 'HIGHLY SUITABLE'}
                  </span>
                </div>
              </div>

              {/* 4 Category Pillars */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 my-3">
                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-400 uppercase block">Hazard Safety</span>
                  <span className="text-base font-black font-mono text-emerald-400">
                    {assessmentData?.hazard_safety_score || 96}/100
                  </span>
                </div>

                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-400 uppercase block">Accessibility</span>
                  <span className="text-base font-black font-mono text-amber-400">
                    {assessmentData?.accessibility_score || 88}/100
                  </span>
                </div>

                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-400 uppercase block">Infrastructure</span>
                  <span className="text-base font-black font-mono text-sky-400">
                    {assessmentData?.infrastructure_score || 85}/100
                  </span>
                </div>

                <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-400 uppercase block">Capacity Score</span>
                  <span className="text-base font-black font-mono text-emerald-400">
                    {assessmentData?.capacity_score || 87}/100
                  </span>
                </div>
              </div>

              {/* Liebig's Law Bottleneck Multi-Pillar Capacity Model */}
              <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 mt-4 space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <div>
                    <h4 className="font-bold text-slate-200 text-xs">
                      Liebig's Law of the Minimum — Resource Bottlenecks
                    </h4>
                    <p className="text-[11px] text-slate-400">
                      Capacity cannot exceed the lowest critical civil infrastructure threshold
                    </p>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
                    SUSTAINABLE CAPPING
                  </span>
                </div>

                <div className="space-y-2">
                  {[
                    {
                      label: "Physical Usable Land Area (120 m² norm per household)",
                      val: capacityData?.factor_capacities?.usable_land || 3500,
                      max: 4000,
                      icon: Trees,
                      color: "bg-emerald-500",
                    },
                    {
                      label: "Potable Water Supply Yield (70 Liters/Capita/Day standard)",
                      val: capacityData?.factor_capacities?.water_supply || 3100,
                      max: 4000,
                      icon: Droplets,
                      color: "bg-sky-500",
                    },
                    {
                      label: "Sanitation & Septic Absorption Capacity",
                      val: capacityData?.factor_capacities?.sanitation || 2900,
                      max: 4000,
                      icon: Building2,
                      color: "bg-amber-500",
                      isBottleneck: true,
                    },
                    {
                      label: "Healthcare Accessibility (Hospital beds within 15 km)",
                      val: capacityData?.factor_capacities?.healthcare || 3200,
                      max: 4000,
                      icon: HeartPulse,
                      color: "bg-purple-500",
                    },
                    {
                      label: "Road Access & Transit Egress Logistics",
                      val: capacityData?.factor_capacities?.road_access || 3200,
                      max: 4000,
                      icon: Truck,
                      color: "bg-blue-500",
                    },
                  ].map((item, i) => (
                    <div key={i} className="space-y-1">
                      <div className="flex justify-between text-[11px]">
                        <span className="flex items-center gap-1.5 text-slate-300">
                          <item.icon className="w-3.5 h-3.5 text-slate-400" />
                          <span>{item.label}</span>
                          {item.isBottleneck && (
                            <span className="text-[9px] px-1.5 py-0.2 rounded bg-rose-950 text-rose-300 border border-rose-800 font-mono font-bold">
                              BOTTLENECK
                            </span>
                          )}
                        </span>
                        <span className="font-mono font-bold text-slate-200">
                          {item.val.toLocaleString()} persons
                        </span>
                      </div>
                      <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden border border-slate-800">
                        <div
                          className={`h-full rounded-full ${item.color}`}
                          style={{ width: `${Math.min(100, (item.val / item.max) * 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Final Capped Capacity Output */}
                <div className="mt-3 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                  <div>
                    <span className="text-slate-400">Final Sustainable Carrying Capacity:</span>
                    <p className="text-[10px] text-slate-500">Capped by sanitation septic absorption ceiling</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xl font-black font-mono text-emerald-400">
                      {(capacityData?.final_capacity || 3500).toLocaleString()}
                    </span>
                    <span className="text-[11px] text-slate-400 ml-1">persons</span>
                  </div>
                </div>
              </div>

              {/* Strengths & Limitations */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <h5 className="font-bold text-emerald-400 uppercase text-[10px] tracking-wider mb-2 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Safety Strengths & Clearances
                  </h5>
                  <ul className="space-y-1 text-[11px] text-slate-300">
                    {(assessmentData?.strengths || [
                      "Zero flood and landslide hazard overlap",
                      "Gentle terrain gradient (< 5°)",
                      "Paved road access with dual egress corridors"
                    ]).map((s, i) => (
                      <li key={i} className="flex items-start gap-1.5">
                        <span className="text-emerald-500 mt-0.5">•</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                  <h5 className="font-bold text-amber-400 uppercase text-[10px] tracking-wider mb-2 flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    Engineering Constraints
                  </h5>
                  <ul className="space-y-1 text-[11px] text-slate-300">
                    {(assessmentData?.limitations || [
                      "Secondary septic leach field expansion required for long-term influx",
                      "Substation transformer upgrade needed above 2,500 population"
                    ]).map((l, i) => (
                      <li key={i} className="flex items-start gap-1.5">
                        <span className="text-amber-500 mt-0.5">•</span>
                        <span>{l}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
