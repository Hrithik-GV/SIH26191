import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  PieChart as PieIcon,
  ShieldAlert,
  Users,
  Building2,
  RefreshCw,
} from 'lucide-react';
import RiskHistogramChart from '../components/Charts/RiskHistogramChart';
import CapacityNeedChart from '../components/Charts/CapacityNeedChart';
import VulnerabilityRadarChart from '../components/Charts/VulnerabilityRadarChart';
import HazardExposurePieChart from '../components/Charts/HazardExposurePieChart';
import { getAnalyticsOverview } from '../services/api';

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const res = await getAnalyticsOverview();
        setAnalytics(res.data);
      } catch (err) {
        console.error('Error fetching analytics:', err);
      } finally {
        setLoading(false);
      }
    }
    loadAnalytics();
  }, []);

  const totalPop = analytics?.total_population || 26800;
  const totalVuln = analytics?.total_vulnerable_population || 9450;
  const totalSafeCap = analytics?.total_safe_capacity || 6150;
  const regionalNet = analytics?.regional_net_balance || -3300;

  return (
    <div className="space-y-4">
      {/* Header Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm text-xs">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 border border-sky-500/30 flex items-center justify-center">
              <BarChart3 className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-tight">
                Statistical Analytics & Decision Support Visualizations
              </h2>
              <p className="text-[11px] text-slate-400">
                Consolidated demographic vulnerability, hazard exposure, and capacity balance distributions
              </p>
            </div>
          </div>

          <div className="text-right">
            <span className="text-[10px] font-mono px-2 py-1 rounded bg-slate-950 text-slate-300 border border-slate-800">
              RECHARTS VISUALIZATION ENGINE
            </span>
          </div>
        </div>
      </div>

      {/* Top Statistical Summary KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-lg">
          <span className="text-[11px] font-semibold uppercase text-slate-400">Monitored Population</span>
          <div className="mt-2 text-2xl font-black font-mono text-slate-100">
            {totalPop.toLocaleString()}
          </div>
          <span className="text-[10px] text-slate-500 mt-1 block">Total across 18 monitored settlements</span>
        </div>

        <div className="bg-slate-900 border border-rose-500/30 p-4 rounded-xl shadow-lg">
          <span className="text-[11px] font-semibold uppercase text-slate-400">Vulnerable Lives</span>
          <div className="mt-2 text-2xl font-black font-mono text-rose-400">
            {totalVuln.toLocaleString()}
          </div>
          <span className="text-[10px] text-rose-300 font-mono mt-1 block">
            {Math.round((totalVuln / totalPop) * 100)}% of total regional residents
          </span>
        </div>

        <div className="bg-slate-900 border border-emerald-500/30 p-4 rounded-xl shadow-lg">
          <span className="text-[11px] font-semibold uppercase text-slate-400">Safe Relocation Capacity</span>
          <div className="mt-2 text-2xl font-black font-mono text-emerald-400">
            {totalSafeCap.toLocaleString()}
          </div>
          <span className="text-[10px] text-emerald-300 font-mono mt-1 block">
            Ecologically sustainable intake buffer
          </span>
        </div>

        <div className="bg-slate-900 border border-amber-500/30 p-4 rounded-xl shadow-lg">
          <span className="text-[11px] font-semibold uppercase text-slate-400">Regional Intake Balance</span>
          <div className="mt-2 text-2xl font-black font-mono text-amber-400">
            {regionalNet.toLocaleString()}
          </div>
          <span className="text-[10px] text-amber-300 font-mono mt-1 block">
            {regionalNet >= 0 ? 'Surplus Capacity' : 'Relocation Deficit (Additional Land Required)'}
          </span>
        </div>
      </div>

      {/* Grid of 4 Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Chart 1: Risk Distribution Histogram */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Risk Distribution Histogram
              </h3>
              <p className="text-[11px] text-slate-400">Settlements & population across 4 severity tiers</p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
              0-100 Model
            </span>
          </div>
          <RiskHistogramChart data={analytics?.risk_distribution} />
        </div>

        {/* Chart 2: Relocation Capacity vs Displaced Demand */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Relocation Intake Capacity vs Need Balance
              </h3>
              <p className="text-[11px] text-slate-400">Safe parcel capacity vs matched vulnerable demand</p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
              Surplus / Deficit
            </span>
          </div>
          <CapacityNeedChart data={analytics?.capacity_vs_need} />
        </div>

        {/* Chart 3: 9 Demographic Vulnerability Factors */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Demographic Vulnerability Factors Comparison
              </h3>
              <p className="text-[11px] text-slate-400">Average severity score across 9 census proxy indicators</p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
              9 Factors
            </span>
          </div>
          <VulnerabilityRadarChart data={analytics?.vulnerability_factors} />
        </div>

        {/* Chart 4: Hazard Exposure Breakdown */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Population Exposure by Hazard Type
              </h3>
              <p className="text-[11px] text-slate-400">Lives exposed to landslide, flood, cloudburst, debris</p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-950 text-sky-300 border border-sky-800">
              Disaster Types
            </span>
          </div>
          <HazardExposurePieChart data={analytics?.hazard_exposures} />
        </div>
      </div>
    </div>
  );
}
