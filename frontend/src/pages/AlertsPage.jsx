import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  Flame,
  Radio,
  Clock,
  Filter,
  ShieldAlert,
  Search,
  MapPin,
  CheckCircle2,
} from 'lucide-react';
import { getAlerts } from '../services/api';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAlerts() {
      try {
        const res = await getAlerts({ page_size: 50 });
        setAlerts(res.data.items || []);
      } catch (err) {
        console.error('Error fetching alerts:', err);
      } finally {
        setLoading(false);
      }
    }
    loadAlerts();
  }, []);

  const filteredAlerts = alerts.filter((a) => {
    if (filterSeverity !== 'ALL' && a.severity !== filterSeverity) return false;
    if (search && !a.description?.toLowerCase().includes(search.toLowerCase()) && !a.disaster_type?.toLowerCase().includes(search.toLowerCase())) {
      return false;
    }
    return true;
  });

  return (
    <div className="space-y-4">
      {/* Top Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm text-xs">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-tight">
                Emergency Alerts & Disaster Warnings Feed
              </h2>
              <p className="text-[11px] text-slate-400">
                NDMA SACHET Common Alerting Protocol (CAP v1.2) & State EOC Incident Dispatches
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono px-2 py-1 rounded bg-rose-950 text-rose-300 border border-rose-800 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
              <span>LIVE INCIDENT STREAM</span>
            </span>
          </div>
        </div>

        {/* Filter Strip */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-2 border-t border-slate-800">
          <div className="relative">
            <input
              type="text"
              placeholder="Search alert keywords or location..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 font-mono"
            />
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
          </div>

          <div>
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500 font-mono"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">CRITICAL Warnings Only</option>
              <option value="HIGH">HIGH Severity Alerts</option>
              <option value="MODERATE">MODERATE Advisories</option>
            </select>
          </div>
        </div>
      </div>

      {/* Alerts Feed Cards */}
      <div className="space-y-3">
        {filteredAlerts.map((alert) => {
          const isCrit = alert.severity === 'CRITICAL';
          const isHigh = alert.severity === 'HIGH';

          return (
            <div
              key={alert.id}
              className={`p-4 rounded-xl border transition-all text-xs ${
                isCrit
                  ? 'bg-rose-950/20 border-rose-500/40 shadow-lg shadow-rose-950/20'
                  : isHigh
                  ? 'bg-amber-950/20 border-amber-500/40 shadow-lg shadow-amber-950/20'
                  : 'bg-slate-900 border-slate-800'
              }`}
            >
              <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold ${
                      isCrit
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                        : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                    }`}
                  >
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="font-mono text-[10px] text-slate-400 uppercase tracking-wider block">
                      {alert.source || 'NDMA SACHET CAP'}
                    </span>
                    <h3 className="font-bold text-slate-100 text-xs uppercase tracking-wide">
                      {alert.disaster_type || 'EMERGENCY DISPATCH'}
                    </h3>
                  </div>
                </div>

                <div className="flex items-center gap-2 font-mono text-[11px]">
                  <span
                    className={`px-2 py-0.5 rounded font-bold text-[10px] border ${
                      isCrit
                        ? 'bg-rose-950 text-rose-300 border-rose-700'
                        : 'bg-amber-950 text-amber-300 border-amber-700'
                    }`}
                  >
                    {alert.severity}
                  </span>
                  <span className="text-slate-400 flex items-center gap-1">
                    <Clock className="w-3 h-3 text-slate-500" />
                    {new Date(alert.event_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>

              <p className="text-slate-300 leading-relaxed text-[11px] pl-9">
                {alert.description || 'Active hydrometeorological emergency in effect.'}
              </p>

              {alert.geometry && (
                <div className="mt-3 pt-2 pl-9 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                  <span>Coordinates: {alert.geometry.coordinates?.join(', ') || 'Sector Polygon'}</span>
                  <span className="text-emerald-400 font-semibold">PostGIS Broadcast</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
