import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldAlert,
  Users,
  Building2,
  Truck,
  RefreshCw,
  Clock,
  Radio,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  MapPin,
  ChevronRight,
} from 'lucide-react';
import KPICard from '../components/KPICard';
import GISMap from '../components/GISMap';
import SidePanel from '../components/SidePanel';
import LiveNotificationCenter from '../components/LiveNotificationCenter';
import RiskHistogramChart from '../components/Charts/RiskHistogramChart';
import CapacityNeedChart from '../components/Charts/CapacityNeedChart';
import {
  getDashboardData,
  getHabitations,
  getHazards,
  getRelocationSites,
  getAlerts,
  getAnalyticsOverview,
} from '../services/api';

export default function MainDashboard({
  onNavigate,
  onSelectHabitation,
  onSelectRelocationSite,
}) {
  const [dashboard, setDashboard] = useState(null);
  const [habitations, setHabitations] = useState([]);
  const [hazards, setHazards] = useState([]);
  const [relocationSites, setRelocationSites] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [isLive, setIsLive] = useState(false);
  const [selectedEntity, setSelectedEntity] = useState(null);

  const loadData = useCallback(async () => {
    try {
      const [dashRes, habRes, hazRes, sitesRes, alertsRes, anaRes] = await Promise.all([
        getDashboardData(),
        getHabitations({ page_size: 50 }),
        getHazards(),
        getRelocationSites({ page_size: 50 }),
        getAlerts(),
        getAnalyticsOverview(),
      ]);

      setDashboard(dashRes.data);
      setIsLive(dashRes.isLive);
      setHabitations(habRes.data.items || []);
      setHazards(hazRes.data.items || []);
      setRelocationSites(sitesRes.data.items || []);
      setAlerts(alertsRes.data.items || []);
      setAnalytics(anaRes.data);

      // Pre-select most urgent habitation if available
      if (habRes.data.items && habRes.data.items.length > 0) {
        const topUrgent = habRes.data.items.find(
          (h) => h.priority === 'IMMEDIATE' || h.risk_score >= 80
        ) || habRes.data.items[0];
        setSelectedEntity({ type: 'habitation', data: topUrgent });
      }
    } catch (err) {
      console.error('Error fetching dashboard telemetry:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const handleLiveEvent = useCallback((event) => {
    if (event.event_type === 'DASHBOARD_UPDATED' && event.data) {
      setDashboard((prev) => ({ ...prev, ...event.data }));
    } else if (event.event_type === 'HABITATION_PRIORITY_CHANGED' && event.data) {
      if (event.data.immediate_assessment_count !== undefined) {
        setDashboard((prev) => ({
          ...prev,
          immediate_relocation_count: event.data.immediate_assessment_count,
        }));
      }
    } else if (event.event_type === 'NEW_ALERT') {
      setDashboard((prev) => ({
        ...prev,
        active_alerts: (prev?.active_alerts || 4) + 1,
      }));
    }
  }, []);

  const timestamps = dashboard?.latest_data_timestamps || {};

  return (
    <div className="space-y-4">
      {/* Live Disaster Notification Center & SSE Stream Control */}
      <LiveNotificationCenter
        onEventReceived={handleLiveEvent}
        onNavigate={onNavigate}
      />

      {/* Top 4 KPI Cards (As required by prompt) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <KPICard
          title="Critical Habitations"
          value={dashboard?.habitations_in_critical_zones ?? 6}
          subvalue={`of ${dashboard?.total_habitations ?? 18} monitored`}
          icon={ShieldAlert}
          colorScheme="rose"
          trend="Overlaps active red zones"
          trendDirection="up"
          badge="CRITICAL TIER"
          onClick={() => onNavigate('habitations')}
        />

        <KPICard
          title="Population at Risk"
          value={dashboard?.population_at_risk ?? 5840}
          subvalue="vulnerable residents"
          icon={Users}
          colorScheme="amber"
          trend="Requires assisted egress"
          badge="EXPOSED"
          onClick={() => onNavigate('habitations')}
        />

        <KPICard
          title="Immediate Relocations"
          value={dashboard?.immediate_relocation_count ?? 3}
          subvalue={`+${dashboard?.short_term_relocation_count ?? 3} short-term`}
          icon={Truck}
          colorScheme="rose"
          trend="Urgency score 81-100"
          trendDirection="up"
          badge="TIER 1 ACTION"
          onClick={() => onNavigate('relocation-recommendations')}
        />

        <KPICard
          title="Available Relocation Capacity"
          value={dashboard?.available_relocation_capacity ?? 5200}
          subvalue={`of ${dashboard?.total_relocation_capacity ?? 8500} gross`}
          icon={Building2}
          colorScheme="emerald"
          trend="Safe candidate parcels"
          trendDirection="down"
          badge="CARRYING CAPACITY"
          onClick={() => onNavigate('relocation-sites')}
        />
      </div>

      {/* Main Area: Large Interactive GIS Map & Side Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {/* Main Area: Large Interactive GIS Map */}
        <div className="lg:col-span-2 xl:col-span-3 space-y-2">
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200">
                Interactive Spatial Situational Map
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                PostGIS WGS84
              </span>
            </div>
            <button
              onClick={() => onNavigate('risk-map')}
              className="text-xs text-amber-400 hover:text-amber-300 flex items-center gap-1 font-medium transition-colors"
            >
              <span>Full Screen GIS Lab</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <GISMap
            habitations={habitations}
            hazards={hazards}
            relocationSites={relocationSites}
            alerts={alerts}
            onSelectEntity={(entity) => setSelectedEntity(entity)}
            selectedEntity={selectedEntity}
            height="460px"
          />
        </div>

        {/* Side Panel: Selected habitation/site information */}
        <div className="space-y-2">
          <div className="flex items-center justify-between px-1">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Sector Inspector
            </h2>
            {selectedEntity && (
              <span className="text-[10px] font-mono text-slate-400 uppercase">
                Active Selection
              </span>
            )}
          </div>

          <SidePanel
            selectedEntity={selectedEntity}
            onClose={() => setSelectedEntity(null)}
            onViewHabitationDetail={(id) => onSelectHabitation(id)}
            onViewRelocationDetail={(id) => onSelectRelocationSite(id)}
          />
        </div>
      </div>

      {/* Bottom: Risk and Relocation Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left Chart: Risk Severity Histogram */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Habitation Risk Severity Histogram
              </h3>
              <p className="text-[11px] text-slate-400">
                Settlements and vulnerable population distribution across risk brackets
              </p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-rose-950/60 text-rose-300 border border-rose-800/60">
              0-100 Model
            </span>
          </div>

          <RiskHistogramChart data={analytics?.risk_distribution} />
        </div>

        {/* Right Chart: Relocation Capacity vs Displaced Demand */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
          <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                Relocation Intake Capacity vs Demand Balance
              </h3>
              <p className="text-[11px] text-slate-400">
                Safe candidate parcel available buffer versus matched displaced persons
              </p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800/60">
              Liebig Bottleneck
            </span>
          </div>

          <CapacityNeedChart data={analytics?.capacity_vs_need} />
        </div>
      </div>
    </div>
  );
}
