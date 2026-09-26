import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  Lock,
  User,
  Building,
  FileSpreadsheet,
  FileDown,
  Plus,
  Pencil,
  Trash2,
  AlertTriangle,
  Compass,
  Layers,
  Activity,
  History,
  CheckCircle2,
  RefreshCw,
  Search,
  Filter,
  Eye,
  Info,
  MapPin,
  Users,
  ChevronRight,
  Download,
  FileText,
  AlertOctagon,
  Clock,
  Sparkles,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import {
  getHabitations,
  getRelocationSites,
  getAlerts,
  fetchAuditLogs,
  fetchDecisionSupportSummary,
  exportExecutiveReport,
  adminCreateHabitation,
  adminUpdateHabitation,
  adminDeleteHabitation,
  adminCreateRelocationSite,
  adminUpdateRelocationSite,
  adminDeleteRelocationSite,
} from '../services/api';


export default function AdminConsolePage() {
  const { user, isAdmin, isAuthorityViewer, canEditData } = useAuth();

  // Active console tab
  const [activeTab, setActiveTab] = useState(isAuthorityViewer ? 'decision_support' : 'decision_support');

  // Global loading and message states
  const [loading, setLoading] = useState(true);
  const [actionSuccess, setActionSuccess] = useState(null);
  const [actionError, setActionError] = useState(null);

  // Data states
  const [decisionSummary, setDecisionSummary] = useState(null);
  const [habitations, setHabitations] = useState([]);
  const [relocationSites, setRelocationSites] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [auditTotal, setAuditTotal] = useState(0);
  const [auditPage, setAuditPage] = useState(1);
  const [auditFilterAction, setAuditFilterAction] = useState('');

  // Modals & form states
  const [showHabModal, setShowHabModal] = useState(false);
  const [editingHab, setEditingHab] = useState(null);
  const [habForm, setHabForm] = useState({
    name: '',
    district: 'Wayanad',
    taluk: 'Vythiri',
    state: 'Kerala',
    population: 1500,
    vulnerable_population: 600,
    latitude: 11.55,
    longitude: 76.13,
  });

  const [showSiteModal, setShowSiteModal] = useState(false);
  const [editingSite, setEditingSite] = useState(null);
  const [siteForm, setSiteForm] = useState({
    name: '',
    available_area: 50000,
    estimated_capacity: 2500,
    current_population: 100,
    water_score: 8.5,
    road_access_score: 9.0,
    healthcare_score: 8.0,
    hazard_score: 0.5,
    suitability_score: 88,
    latitude: 11.58,
    longitude: 76.12,
  });

  // Report Export Form
  const [exportFormat, setExportFormat] = useState('json');
  const [exportNotes, setExportNotes] = useState('');
  const [exporting, setExporting] = useState(false);
  const [exportedJsonPreview, setExportedJsonPreview] = useState(null);

  // Search & filter states
  const [habSearch, setHabSearch] = useState('');
  const [siteSearch, setSiteSearch] = useState('');

  // Load initial console data
  const loadConsoleData = async () => {
    setLoading(true);
    setActionError(null);
    try {
      const [sumRes, habRes, siteRes, alertRes] = await Promise.allSettled([
        fetchDecisionSupportSummary(),
        getHabitations({ page_size: 50 }),
        getRelocationSites({ page_size: 50 }),
        getAlerts({ page_size: 50 }),
      ]);

      if (sumRes.status === 'fulfilled') setDecisionSummary(sumRes.value);
      if (habRes.status === 'fulfilled') {
        const d = habRes.value?.data || {};
        const items = d.items || (Array.isArray(d) ? d : []);
        setHabitations(items);
      }
      if (siteRes.status === 'fulfilled') {
        const d = siteRes.value?.data || {};
        const items = d.items || (Array.isArray(d) ? d : []);
        setRelocationSites(items);
      }
      if (alertRes.status === 'fulfilled') {
        const d = alertRes.value?.data || {};
        const items = d.items || (Array.isArray(d) ? d : []);
        setAlerts(items);
      }


      // If user is Admin, also load audit logs
      if (isAdmin) {
        try {
          const auditRes = await fetchAuditLogs({ page: auditPage, pageSize: 25, action: auditFilterAction || undefined });
          setAuditLogs(auditRes?.items || []);
          setAuditTotal(auditRes?.total || 0);
        } catch (e) {
          console.warn('[Audit Log fetch error]', e);
        }
      }
    } catch (err) {
      setActionError('Failed to load some authority data: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConsoleData();
  }, [isAdmin, auditPage, auditFilterAction]);

  const showNotification = (msg, isErr = false) => {
    if (isErr) {
      setActionError(msg);
      setTimeout(() => setActionError(null), 6000);
    } else {
      setActionSuccess(msg);
      setTimeout(() => setActionSuccess(null), 5000);
    }
  };

  // --- Habitation Actions (ADMIN Only) ---
  const handleOpenAddHab = () => {
    setEditingHab(null);
    setHabForm({
      name: 'Demonstration Settlement ' + (habitations.length + 1),
      district: 'Wayanad',
      taluk: 'Vythiri',
      state: 'Kerala',
      population: 1200,
      vulnerable_population: 450,
      latitude: 11.554,
      longitude: 76.138,
    });
    setShowHabModal(true);
  };

  const handleOpenEditHab = (hab) => {
    setEditingHab(hab);
    setHabForm({
      name: hab.name || '',
      district: hab.district || 'Wayanad',
      taluk: hab.taluk || 'Vythiri',
      state: hab.state || 'Kerala',
      population: hab.population || 0,
      vulnerable_population: hab.vulnerable_population || 0,
      latitude: hab.geometry?.coordinates?.[0]?.[0]?.[1] || 11.55,
      longitude: hab.geometry?.coordinates?.[0]?.[0]?.[0] || 76.13,
    });
    setShowHabModal(true);
  };

  const handleSaveHabitation = async (e) => {
    e.preventDefault();
    try {
      if (editingHab) {
        await adminUpdateHabitation(editingHab.id, habForm);
        showNotification(`Settlement '${habForm.name}' updated successfully.`);
      } else {
        await adminCreateHabitation(habForm);
        showNotification(`Demonstration settlement '${habForm.name}' created.`);
      }
      setShowHabModal(false);
      loadConsoleData();
    } catch (err) {
      showNotification(err?.response?.data?.error?.message || err.message, true);
    }
  };

  const handleDeleteHabitation = async (hab) => {
    if (!window.confirm(`Are you sure you want to delete demonstration settlement '${hab.name}'?`)) return;
    try {
      await adminDeleteHabitation(hab.id);
      showNotification(`Settlement '${hab.name}' deleted.`);
      loadConsoleData();
    } catch (err) {
      showNotification(err?.response?.data?.error?.message || err.message, true);
    }
  };

  // --- Relocation Site Actions (ADMIN Only) ---
  const handleOpenAddSite = () => {
    setEditingSite(null);
    setSiteForm({
      name: 'Candidate Safe Parcel ' + String.fromCharCode(65 + relocationSites.length),
      available_area: 45000,
      estimated_capacity: 2200,
      current_population: 80,
      water_score: 8.5,
      road_access_score: 9.0,
      healthcare_score: 8.0,
      hazard_score: 0.4,
      suitability_score: 89,
      latitude: 11.59,
      longitude: 76.09,
    });
    setShowSiteModal(true);
  };

  const handleOpenEditSite = (site) => {
    setEditingSite(site);
    setSiteForm({
      name: site.name || '',
      available_area: site.available_area || 40000,
      estimated_capacity: site.estimated_capacity || 2000,
      current_population: site.current_population || 0,
      water_score: site.water_score || 8.0,
      road_access_score: site.road_access_score || 8.5,
      healthcare_score: site.healthcare_score || 8.0,
      hazard_score: site.hazard_score || 0.5,
      suitability_score: site.suitability_score || 85,
      latitude: site.geometry?.coordinates?.[0]?.[0]?.[1] || 11.59,
      longitude: site.geometry?.coordinates?.[0]?.[0]?.[0] || 76.09,
    });
    setShowSiteModal(true);
  };

  const handleSaveSite = async (e) => {
    e.preventDefault();
    try {
      if (editingSite) {
        await adminUpdateRelocationSite(editingSite.id, siteForm);
        showNotification(`Relocation site '${siteForm.name}' updated.`);
      } else {
        await adminCreateRelocationSite(siteForm);
        showNotification(`Candidate relocation site '${siteForm.name}' registered.`);
      }
      setShowSiteModal(false);
      loadConsoleData();
    } catch (err) {
      showNotification(err?.response?.data?.error?.message || err.message, true);
    }
  };

  const handleDeleteSite = async (site) => {
    if (!window.confirm(`Are you sure you want to delete relocation site '${site.name}'?`)) return;
    try {
      await adminDeleteRelocationSite(site.id);
      showNotification(`Relocation site '${site.name}' deleted.`);
      loadConsoleData();
    } catch (err) {
      showNotification(err?.response?.data?.error?.message || err.message, true);
    }
  };

  // --- Executive Report Export ---
  const handleExportReport = async () => {
    setExporting(true);
    setExportedJsonPreview(null);
    try {
      if (exportFormat === 'csv') {
        const blob = await exportExecutiveReport({
          format: 'csv',
          officerNotes: exportNotes,
        });
        const url = window.URL.createObjectURL(new Blob([blob]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `sih26_disaster_report_${new Date().toISOString().slice(0,10)}.csv`);
        document.body.appendChild(link);
        link.click();
        link.parentNode.removeChild(link);
        showNotification('Official CSV report exported and downloaded.');
      } else {
        const data = await exportExecutiveReport({
          format: 'json',
          officerNotes: exportNotes,
        });
        setExportedJsonPreview(data);
        showNotification('Executive Decision-Support Report generated.');
      }
      // Refresh audit logs if admin
      if (isAdmin) {
        const auditRes = await fetchAuditLogs({ page: 1, pageSize: 25 });
        setAuditLogs(auditRes?.items || []);
        setAuditTotal(auditRes?.total || 0);
      }
    } catch (err) {
      showNotification('Report export error: ' + (err?.response?.data?.error?.message || err.message), true);
    } finally {
      setExporting(false);
    }
  };

  const filteredHabitations = habitations.filter((h) =>
    (h.name || '').toLowerCase().includes(habSearch.toLowerCase()) ||
    (h.district || '').toLowerCase().includes(habSearch.toLowerCase())
  );

  const filteredSites = relocationSites.filter((s) =>
    (s.name || '').toLowerCase().includes(siteSearch.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans pb-16">
      {/* Top Officer Profile Strip */}
      <section className="bg-slate-900/90 border-b border-slate-800/80 px-4 sm:px-8 py-5">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-lg shadow-lg ${
              isAdmin
                ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40 shadow-rose-950/40'
                : 'bg-sky-500/20 text-sky-400 border border-sky-500/40 shadow-sky-950/40'
            }`}>
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-black text-white tracking-tight">
                  Authority & Administrative Command
                </h1>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                  isAdmin
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    : 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                }`}>
                  {user?.role || 'OFFICIAL'}
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30">
                  {user?.clearance || 'LEVEL_1'}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                <span className="text-slate-200 font-semibold">{user?.name}</span> • {user?.designation} • {user?.station}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={loadConsoleData}
              className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700/80 text-xs font-medium flex items-center gap-1.5 transition-all"
              title="Refresh telemetry"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-amber-400' : ''}`} />
              <span>Refresh Telemetry</span>
            </button>
            <div className="text-[11px] font-mono px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>JWT AUTHENTICATED</span>
            </div>
          </div>
        </div>

        {/* Global Notifications */}
        {actionSuccess && (
          <div className="max-w-7xl mx-auto mt-3 p-3 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{actionSuccess}</span>
          </div>
        )}
        {actionError && (
          <div className="max-w-7xl mx-auto mt-3 p-3 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{actionError}</span>
          </div>
        )}
      </section>

      {/* Navigation Tabs */}
      <div className="border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-md px-4 sm:px-8">
        <div className="max-w-7xl mx-auto flex overflow-x-auto space-x-2 py-2.5">
          <button
            onClick={() => setActiveTab('decision_support')}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all whitespace-nowrap ${
              activeTab === 'decision_support'
                ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-950/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Compass className="w-4 h-4" />
            <span>Decision Support & Risk Intelligence</span>
          </button>

          <button
            onClick={() => setActiveTab('habitations')}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all whitespace-nowrap ${
              activeTab === 'habitations'
                ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-950/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Building className="w-4 h-4" />
            <span>Demonstration Settlements ({habitations.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('relocation_sites')}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all whitespace-nowrap ${
              activeTab === 'relocation_sites'
                ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-950/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <MapPin className="w-4 h-4" />
            <span>Candidate Relocation Sites ({relocationSites.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('export_report')}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all whitespace-nowrap ${
              activeTab === 'export_report'
                ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-950/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <FileSpreadsheet className="w-4 h-4" />
            <span>Executive Report Export</span>
          </button>

          {isAdmin && (
            <button
              onClick={() => setActiveTab('audit_trail')}
              className={`px-3.5 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all whitespace-nowrap ${
                activeTab === 'audit_trail'
                  ? 'bg-rose-500 text-white font-bold shadow-md shadow-rose-950/40'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <History className="w-4 h-4" />
              <span>Audit Trail Log</span>
              {auditTotal > 0 && (
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-slate-800 text-rose-300 font-mono">
                  {auditTotal}
                </span>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-8 py-6">
        {/* =========================================================================
            TAB 1: DECISION SUPPORT & RISK INTELLIGENCE (Primary Authority View)
           ========================================================================= */}
        {activeTab === 'decision_support' && (
          <div className="space-y-6">
            {/* Statutory Compliance Notice Banner */}
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3 shadow-lg">
              <Info className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div className="text-xs text-slate-300 space-y-1">
                <div className="font-bold text-amber-300 flex items-center gap-2">
                  <span>STATUTORY DECISION-SUPPORT TELEMETRY NOTICE</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-200">
                    ADVISORY ONLY
                  </span>
                </div>
                <p>
                  Relocation urgency rankings, multi-hazard red zone exposures, and carrying-capacity evaluations are advisory decision-support analytics developed under SIH 26191.
                  <strong> Automatic relocation orders are strictly prohibited.</strong> All resettlement actions require ground validation and executive orders by the District Disaster Management Authority under the Disaster Management Act, 2005.
                </p>
              </div>
            </div>

            {/* KPI Executive Telemetry Grid */}
            {decisionSummary && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <div className="text-xs text-slate-400 font-semibold mb-1">Total Habitations Monitored</div>
                  <div className="text-2xl font-black text-white font-mono">
                    {decisionSummary.kpi_metrics?.total_habitations || habitations.length}
                  </div>
                  <div className="text-[11px] text-slate-500 mt-1">Surveyed settlement polygons</div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900 border border-rose-900/40 bg-rose-950/10">
                  <div className="text-xs text-rose-300 font-semibold mb-1">In Critical Hazard Zones</div>
                  <div className="text-2xl font-black text-rose-400 font-mono">
                    {decisionSummary.kpi_metrics?.habitations_in_critical_zones || 0}
                  </div>
                  <div className="text-[11px] text-rose-300/70 mt-1">High landslide & flood exposure</div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900 border border-amber-900/40 bg-amber-950/10">
                  <div className="text-xs text-amber-300 font-semibold mb-1">Immediate Relocation Priority</div>
                  <div className="text-2xl font-black text-amber-400 font-mono">
                    {decisionSummary.kpi_metrics?.immediate_relocation_count || 0}
                  </div>
                  <div className="text-[11px] text-amber-300/70 mt-1">Score &gt; 80 / 100</div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900 border border-emerald-900/40 bg-emerald-950/10">
                  <div className="text-xs text-emerald-300 font-semibold mb-1">Available Safe Capacity</div>
                  <div className="text-2xl font-black text-emerald-400 font-mono">
                    {decisionSummary.kpi_metrics?.available_relocation_capacity || 0}
                  </div>
                  <div className="text-[11px] text-emerald-300/70 mt-1">Safe parcel carrying buffer</div>
                </div>
              </div>
            )}

            {/* Critical Habitations & Relocation Recommendations Inspection */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <AlertOctagon className="w-5 h-5 text-amber-400" />
                    <span>Vulnerable Habitation Risk Explanations & Relocation Allocations</span>
                  </h2>
                  <p className="text-xs text-slate-400">
                    Transparent breakdown of hazard triggers, exposed demographics, and designated candidate relocation parcels.
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                {decisionSummary?.urgent_habitations?.map((item, idx) => (
                  <div
                    key={item.habitation_id || idx}
                    className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 hover:border-slate-700 transition-all"
                  >
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-2">
                      <div className="flex items-center gap-3">
                        <span className="w-6 h-6 rounded-full bg-slate-800 text-slate-300 text-xs font-mono font-bold flex items-center justify-center">
                          {idx + 1}
                        </span>
                        <div>
                          <div className="text-sm font-bold text-slate-100">{item.habitation_name}</div>
                          <div className="text-[11px] text-slate-400 font-mono">
                            Priority Score: <span className="text-amber-400 font-bold">{item.priority_score}/100</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                          item.priority === 'IMMEDIATE'
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            : item.priority === 'SHORT_TERM'
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                        }`}>
                          {item.priority}
                        </span>
                        {item.recommended_site && (
                          <span className="text-[11px] font-mono px-2.5 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                            → {item.recommended_site} ({item.distance_km} km)
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Risk Explanations Justification List */}
                    <div className="mt-3 pt-3 border-t border-slate-800/80">
                      <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                        Multi-Hazard Risk Explanations & Urgency Justifications:
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {item.reasons?.map((reason, rIdx) => (
                          <span
                            key={rIdx}
                            className="text-xs px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300 flex items-center gap-1.5"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                            <span>{reason}</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Active Disaster Alerts Feed */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <Activity className="w-5 h-5 text-rose-400" />
                    <span>Real-Time Disaster Telemetry & Warnings</span>
                  </h2>
                  <p className="text-xs text-slate-400">
                    Live meteorological, hydrological, and geotechnical early warning events.
                  </p>
                </div>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {alerts.length} Active Triggers
                </span>
              </div>

              {alerts.length === 0 ? (
                <div className="text-center py-8 text-xs text-slate-500">
                  No active red alerts in the monitored jurisdiction at this moment.
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {alerts.slice(0, 6).map((al, idx) => (
                    <div
                      key={al.id || idx}
                      className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800 flex items-start gap-3"
                    >
                      <div className={`p-2 rounded-lg mt-0.5 ${
                        al.severity === 'CRITICAL'
                          ? 'bg-rose-500/20 text-rose-400'
                          : 'bg-amber-500/20 text-amber-400'
                      }`}>
                        <AlertTriangle className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-1">
                          <span className="text-xs font-bold text-slate-200 capitalize">
                            {al.disaster_type} Warning
                          </span>
                          <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                            al.severity === 'CRITICAL'
                              ? 'bg-rose-500/20 text-rose-300'
                              : 'bg-amber-500/20 text-amber-300'
                          }`}>
                            {al.severity}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                          Source: {al.source || 'IMD / KSDMA Central Monitoring'}
                        </p>
                        <div className="text-[10px] text-slate-500 font-mono mt-1">
                          Observed: {new Date(al.event_time || Date.now()).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 2: DEMONSTRATION HABITATIONS (CRUD for Admin, Read-Only for Viewer)
           ========================================================================= */}
        {activeTab === 'habitations' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-black text-white flex items-center gap-2">
                  <Building className="w-5 h-5 text-amber-400" />
                  <span>Demonstration Settlement Demographics</span>
                </h2>
                <p className="text-xs text-slate-400">
                  {canEditData
                    ? 'Admin clearance: Add, edit, or adjust demonstration habitations and vulnerable populations.'
                    : 'Authority Viewer clearance: View-only decision support access. Administrative edits restricted to System Admin.'}
                </p>
              </div>

              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    value={habSearch}
                    onChange={(e) => setHabSearch(e.target.value)}
                    placeholder="Search habitations..."
                    className="bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 font-mono focus:border-amber-500 focus:outline-none"
                  />
                </div>

                {canEditData && (
                  <button
                    onClick={handleOpenAddHab}
                    className="px-3 py-1.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-lg flex items-center gap-1.5 transition-all shadow-md shadow-amber-950/40"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Add Demo Settlement</span>
                  </button>
                )}
              </div>
            </div>

            {/* Habitation Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Settlement Name</th>
                      <th className="px-4 py-3">Jurisdiction</th>
                      <th className="px-4 py-3 font-mono">Total Pop.</th>
                      <th className="px-4 py-3 font-mono">Vulnerable Pop.</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {filteredHabitations.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="px-4 py-8 text-center text-slate-500">
                          No settlements found matching query.
                        </td>
                      </tr>
                    ) : (
                      filteredHabitations.map((hab) => (
                        <tr key={hab.id} className="hover:bg-slate-800/40 transition-colors">
                          <td className="px-4 py-3 font-bold text-slate-100">{hab.name}</td>
                          <td className="px-4 py-3 text-slate-400">{hab.district}, {hab.taluk || 'Vythiri'}</td>
                          <td className="px-4 py-3 font-mono">{hab.population?.toLocaleString()}</td>
                          <td className="px-4 py-3 font-mono text-amber-400 font-semibold">
                            {hab.vulnerable_population?.toLocaleString()}
                          </td>
                          <td className="px-4 py-3">
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/30">
                              DEMO PARCEL
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right">
                            {canEditData ? (
                              <div className="flex items-center justify-end gap-1.5">
                                <button
                                  onClick={() => handleOpenEditHab(hab)}
                                  className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-amber-400 transition-colors"
                                  title="Edit Settlement"
                                >
                                  <Pencil className="w-3.5 h-3.5" />
                                </button>
                                <button
                                  onClick={() => handleDeleteHabitation(hab)}
                                  className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-rose-400 transition-colors"
                                  title="Delete Settlement"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            ) : (
                              <span className="text-[11px] text-slate-500 font-mono">View Only</span>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 3: CANDIDATE RELOCATION SITES (CRUD for Admin, Read-Only for Viewer)
           ========================================================================= */}
        {activeTab === 'relocation_sites' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-black text-white flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-emerald-400" />
                  <span>Candidate Relocation Sites & Carrying Capacity</span>
                </h2>
                <p className="text-xs text-slate-400">
                  {canEditData
                    ? 'Admin clearance: Add, edit, or adjust relocation parcels, carrying capacity, and suitability factors.'
                    : 'Authority Viewer clearance: View-only decision support access. Administrative edits restricted to System Admin.'}
                </p>
              </div>

              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    value={siteSearch}
                    onChange={(e) => setSiteSearch(e.target.value)}
                    placeholder="Search relocation sites..."
                    className="bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 font-mono focus:border-amber-500 focus:outline-none"
                  />
                </div>

                {canEditData && (
                  <button
                    onClick={handleOpenAddSite}
                    className="px-3 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs rounded-lg flex items-center gap-1.5 transition-all shadow-md shadow-emerald-950/40"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Register Candidate Site</span>
                  </button>
                )}
              </div>
            </div>

            {/* Sites Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Parcel Name</th>
                      <th className="px-4 py-3 font-mono">Area (m²)</th>
                      <th className="px-4 py-3 font-mono">Max Capacity</th>
                      <th className="px-4 py-3 font-mono">Available Buffer</th>
                      <th className="px-4 py-3 font-mono">Suitability</th>
                      <th className="px-4 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {filteredSites.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="px-4 py-8 text-center text-slate-500">
                          No candidate sites found matching query.
                        </td>
                      </tr>
                    ) : (
                      filteredSites.map((site) => (
                        <tr key={site.id} className="hover:bg-slate-800/40 transition-colors">
                          <td className="px-4 py-3 font-bold text-slate-100">{site.name}</td>
                          <td className="px-4 py-3 font-mono">{site.available_area?.toLocaleString()}</td>
                          <td className="px-4 py-3 font-mono">{site.estimated_capacity?.toLocaleString()}</td>
                          <td className="px-4 py-3 font-mono text-emerald-400 font-bold">
                            {site.available_capacity?.toLocaleString()}
                          </td>
                          <td className="px-4 py-3">
                            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                              {site.suitability_score?.toFixed(1) || 85}/100
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right">
                            {canEditData ? (
                              <div className="flex items-center justify-end gap-1.5">
                                <button
                                  onClick={() => handleOpenEditSite(site)}
                                  className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-amber-400 transition-colors"
                                  title="Edit Parcel"
                                >
                                  <Pencil className="w-3.5 h-3.5" />
                                </button>
                                <button
                                  onClick={() => handleDeleteSite(site)}
                                  className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-rose-400 transition-colors"
                                  title="Delete Parcel"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            ) : (
                              <span className="text-[11px] text-slate-500 font-mono">View Only</span>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* =========================================================================
            TAB 4: EXECUTIVE REPORT EXPORT (Accessible to ADMIN & AUTHORITY_VIEWER)
           ========================================================================= */}
        {activeTab === 'export_report' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl max-w-3xl">
              <h2 className="text-lg font-black text-white flex items-center gap-2 mb-1">
                <FileSpreadsheet className="w-5 h-5 text-amber-400" />
                <span>Executive Decision-Support Report Generator</span>
              </h2>
              <p className="text-xs text-slate-400 mb-6">
                Exports official disaster management briefings with multi-hazard risk explanations, relocation prioritization rankings, and statutory compliance blocks.
              </p>

              <div className="space-y-5">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                    Report Export Format:
                  </label>
                  <div className="grid grid-cols-2 gap-3 max-w-md">
                    <button
                      type="button"
                      onClick={() => setExportFormat('json')}
                      className={`p-3 rounded-lg border text-left text-xs transition-all ${
                        exportFormat === 'json'
                          ? 'bg-amber-500/15 border-amber-500 text-white'
                          : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      <div className="font-bold text-slate-200">JSON Format</div>
                      <div className="text-[11px] text-slate-400 mt-0.5">Structured for command APIs & archival</div>
                    </button>

                    <button
                      type="button"
                      onClick={() => setExportFormat('csv')}
                      className={`p-3 rounded-lg border text-left text-xs transition-all ${
                        exportFormat === 'csv'
                          ? 'bg-amber-500/15 border-amber-500 text-white'
                          : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      <div className="font-bold text-slate-200">CSV Spreadsheet</div>
                      <div className="text-[11px] text-slate-400 mt-0.5">Tabular format for Excel & briefing decks</div>
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Commanding Officer Remarks / Directive Notes:
                  </label>
                  <textarea
                    rows="3"
                    value={exportNotes}
                    onChange={(e) => setExportNotes(e.target.value)}
                    placeholder="Enter executive briefing notes, monsoon directives, or evacuation priority remarks..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:border-amber-500 focus:outline-none"
                  ></textarea>
                </div>

                <div className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800/80 text-[11px] text-slate-400 space-y-1">
                  <div className="font-bold text-slate-300">Generated Report Contents:</div>
                  <ul className="list-disc list-inside space-y-0.5 text-slate-400">
                    <li>Jurisdiction KPIs & Population at Risk</li>
                    <li>Transparent 7-factor Multi-Hazard Risk Explanations</li>
                    <li>Prioritized Relocation Recommendations with Safe Carrying Capacity</li>
                    <li>Active Early Warning Alerts (IMD/CWC/NDMA)</li>
                    <li>Official Officer Signoff & Disaster Management Act 2005 Advisory Block</li>
                  </ul>
                </div>

                <button
                  type="button"
                  onClick={handleExportReport}
                  disabled={exporting}
                  className="px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-lg flex items-center gap-2 transition-all shadow-lg shadow-amber-950/50 disabled:opacity-50"
                >
                  <Download className="w-4 h-4" />
                  <span>{exporting ? 'Compiling Official Report...' : 'Generate & Download Executive Report'}</span>
                </button>
              </div>
            </div>

            {/* JSON Output Preview if generated */}
            {exportedJsonPreview && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                    Report Preview ({exportedJsonPreview.report_id})
                  </h3>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400">
                    GENERATED & AUDITED
                  </span>
                </div>
                <pre className="p-4 bg-slate-950 rounded-lg text-[11px] font-mono text-slate-300 overflow-x-auto max-h-96 border border-slate-800">
                  {JSON.stringify(exportedJsonPreview, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}

        {/* =========================================================================
            TAB 5: AUDIT TRAIL LOG (ADMIN Exclusively)
           ========================================================================= */}
        {activeTab === 'audit_trail' && isAdmin && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-black text-white flex items-center gap-2">
                  <History className="w-5 h-5 text-rose-400" />
                  <span>Administrative Audit Trail & Access Logs</span>
                </h2>
                <p className="text-xs text-slate-400">
                  Chronological tamper-evident record of official logins, data edits, deletions, and report exports.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <select
                  value={auditFilterAction}
                  onChange={(e) => {
                    setAuditFilterAction(e.target.value);
                    setAuditPage(1);
                  }}
                  className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-mono focus:border-amber-500 focus:outline-none"
                >
                  <option value="">All Actions</option>
                  <option value="LOGIN_SUCCESS">LOGIN_SUCCESS</option>
                  <option value="ADD_DEMO_HABITATION">ADD_DEMO_HABITATION</option>
                  <option value="UPDATE_DEMO_HABITATION">UPDATE_DEMO_HABITATION</option>
                  <option value="DELETE_DEMO_HABITATION">DELETE_DEMO_HABITATION</option>
                  <option value="ADD_RELOCATION_SITE">ADD_RELOCATION_SITE</option>
                  <option value="UPDATE_RELOCATION_SITE">UPDATE_RELOCATION_SITE</option>
                  <option value="EXPORT_REPORT">EXPORT_REPORT</option>
                </select>
              </div>
            </div>

            {/* Audit Log Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Timestamp (UTC)</th>
                      <th className="px-4 py-3">Official User</th>
                      <th className="px-4 py-3">Role</th>
                      <th className="px-4 py-3">Action</th>
                      <th className="px-4 py-3">Resource Target</th>
                      <th className="px-4 py-3">Details</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {auditLogs.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="px-4 py-8 text-center text-slate-500">
                          No audit log entries recorded.
                        </td>
                      </tr>
                    ) : (
                      auditLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                          <td className="px-4 py-3 text-slate-400 text-[11px] whitespace-nowrap">
                            {new Date(log.timestamp).toLocaleString()}
                          </td>
                          <td className="px-4 py-3 font-bold text-slate-200">
                            {log.user_name || log.user_id}
                          </td>
                          <td className="px-4 py-3">
                            <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                              log.user_role === 'ADMIN'
                                ? 'bg-rose-500/20 text-rose-300'
                                : 'bg-sky-500/20 text-sky-300'
                            }`}>
                              {log.user_role}
                            </span>
                          </td>
                          <td className="px-4 py-3 font-bold text-amber-400">
                            {log.action}
                          </td>
                          <td className="px-4 py-3 text-slate-300 text-[11px]">
                            {log.resource_type}:{log.resource_id ? log.resource_id.slice(0, 8) + '...' : '-'}
                          </td>
                          <td className="px-4 py-3 text-[11px] text-slate-400 max-w-xs truncate">
                            {JSON.stringify(log.details || {})}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* =========================================================================
          MODAL: ADD / EDIT HABITATION (ADMIN ONLY)
         ========================================================================= */}
      {showHabModal && canEditData && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-base font-bold text-white mb-4">
              {editingHab ? 'Edit Demonstration Settlement' : 'Add Demonstration Settlement'}
            </h3>
            <form onSubmit={handleSaveHabitation} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Settlement Name</label>
                <input
                  type="text"
                  required
                  value={habForm.name}
                  onChange={(e) => setHabForm({ ...habForm, name: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 focus:border-amber-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1">District</label>
                  <input
                    type="text"
                    required
                    value={habForm.district}
                    onChange={(e) => setHabForm({ ...habForm, district: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 focus:border-amber-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Taluk</label>
                  <input
                    type="text"
                    required
                    value={habForm.taluk}
                    onChange={(e) => setHabForm({ ...habForm, taluk: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 focus:border-amber-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1">Total Population</label>
                  <input
                    type="number"
                    required
                    min="0"
                    value={habForm.population}
                    onChange={(e) => setHabForm({ ...habForm, population: parseInt(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 focus:border-amber-500 focus:outline-none font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Vulnerable Population</label>
                  <input
                    type="number"
                    required
                    min="0"
                    value={habForm.vulnerable_population}
                    onChange={(e) => setHabForm({ ...habForm, vulnerable_population: parseInt(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 focus:border-amber-500 focus:outline-none font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1">Latitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    required
                    value={habForm.latitude}
                    onChange={(e) => setHabForm({ ...habForm, latitude: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 focus:border-amber-500 focus:outline-none font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    required
                    value={habForm.longitude}
                    onChange={(e) => setHabForm({ ...habForm, longitude: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 focus:border-amber-500 focus:outline-none font-mono"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowHabModal(false)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold"
                >
                  Save Settlement
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* =========================================================================
          MODAL: ADD / EDIT RELOCATION SITE (ADMIN ONLY)
         ========================================================================= */}
      {showSiteModal && canEditData && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-base font-bold text-white mb-4">
              {editingSite ? 'Edit Candidate Relocation Parcel' : 'Register Candidate Relocation Parcel'}
            </h3>
            <form onSubmit={handleSaveSite} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Parcel Name</label>
                <input
                  type="text"
                  required
                  value={siteForm.name}
                  onChange={(e) => setSiteForm({ ...siteForm, name: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 focus:border-amber-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1">Usable Area (m²)</label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={siteForm.available_area}
                    onChange={(e) => setSiteForm({ ...siteForm, available_area: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Estimated Capacity</label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={siteForm.estimated_capacity}
                    onChange={(e) => setSiteForm({ ...siteForm, estimated_capacity: parseInt(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1">Current Occupancy</label>
                  <input
                    type="number"
                    min="0"
                    value={siteForm.current_population}
                    onChange={(e) => setSiteForm({ ...siteForm, current_population: parseInt(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Suitability Score (0-100)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    value={siteForm.suitability_score}
                    onChange={(e) => setSiteForm({ ...siteForm, suitability_score: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 font-mono text-emerald-400 font-bold"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1">Latitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    required
                    value={siteForm.latitude}
                    onChange={(e) => setSiteForm({ ...siteForm, latitude: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Longitude</label>
                  <input
                    type="number"
                    step="0.0001"
                    required
                    value={siteForm.longitude}
                    onChange={(e) => setSiteForm({ ...siteForm, longitude: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 font-mono"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowSiteModal(false)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold"
                >
                  Save Relocation Site
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
