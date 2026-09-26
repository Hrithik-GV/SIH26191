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
  fetchReportOptions,
  generateComprehensiveReport,
  exportComprehensiveReport,
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

  // Report Generation & Export Form
  const [exportFormat, setExportFormat] = useState('pdf');
  const [exportNotes, setExportNotes] = useState('');
  const [exporting, setExporting] = useState(false);
  const [exportedJsonPreview, setExportedJsonPreview] = useState(null);

  // Advanced Report Generation Selection States
  const [reportOptions, setReportOptions] = useState({
    districts: ['Wayanad', 'Idukki', 'Malappuram', 'Kozhikode'],
    habitations: [],
    hazard_events: [],
    relocation_sites: [],
  });
  const [reportDistrict, setReportDistrict] = useState('Wayanad');
  const [reportHabitationId, setReportHabitationId] = useState('');
  const [reportHazardEventId, setReportHazardEventId] = useState('');
  const [reportRelocationSiteId, setReportRelocationSiteId] = useState('');
  const [generatedReport, setGeneratedReport] = useState(null);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [reportViewMode, setReportViewMode] = useState('13_sections'); // '13_sections' or 'epistemic'

  // Search & filter states
  const [habSearch, setHabSearch] = useState('');
  const [siteSearch, setSiteSearch] = useState('');

  // Load initial console data
  const loadConsoleData = async () => {
    setLoading(true);
    setActionError(null);
    try {
      const [sumRes, habRes, siteRes, alertRes, optRes] = await Promise.allSettled([
        fetchDecisionSupportSummary(),
        getHabitations({ page_size: 50 }),
        getRelocationSites({ page_size: 50 }),
        getAlerts({ page_size: 50 }),
        fetchReportOptions(),
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
      if (optRes.status === 'fulfilled' && optRes.value) {
        setReportOptions(optRes.value);
        if (optRes.value.habitations?.length > 0 && !reportHabitationId) {
          setReportHabitationId(optRes.value.habitations[0].id);
        }
        if (optRes.value.hazard_events?.length > 0 && !reportHazardEventId) {
          setReportHazardEventId(optRes.value.hazard_events[0].id);
        }
        if (optRes.value.relocation_sites?.length > 0 && !reportRelocationSiteId) {
          setReportRelocationSiteId(optRes.value.relocation_sites[0].id);
        }
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

  // --- Comprehensive Report Generation & Export Handlers ---
  const handleGenerateLiveReport = async () => {
    setGeneratingReport(true);
    try {
      const payload = {
        district: reportDistrict,
        habitation_id: reportHabitationId || undefined,
        hazard_event_id: reportHazardEventId || undefined,
        relocation_site_id: reportRelocationSiteId || undefined,
        officer_notes: exportNotes,
      };
      const data = await generateComprehensiveReport(payload);
      setGeneratedReport(data);
      setExportedJsonPreview(data);
      showNotification(`Report generated for ${data.jurisdiction?.focal_habitation || 'Settlement'}.`);

      if (isAdmin) {
        const auditRes = await fetchAuditLogs({ page: 1, pageSize: 25 });
        setAuditLogs(auditRes?.items || []);
        setAuditTotal(auditRes?.total || 0);
      }
    } catch (err) {
      showNotification('Report generation failed: ' + (err?.response?.data?.error?.message || err.message), true);
    } finally {
      setGeneratingReport(false);
    }
  };

  const handleDownloadPdf = async () => {
    setExporting(true);
    try {
      const blob = await exportComprehensiveReport({
        district: reportDistrict,
        habitationId: reportHabitationId || null,
        hazardEventId: reportHazardEventId || null,
        relocationSiteId: reportRelocationSiteId || null,
        officerNotes: exportNotes,
        format: 'pdf',
      });
      const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      const focalName = (generatedReport?.jurisdiction?.focal_habitation || 'disaster').replace(/\s+/g, '_').toLowerCase();
      link.setAttribute('download', `sih26_report_${focalName}_${new Date().toISOString().slice(0, 10)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      showNotification('Official PDF report downloaded successfully.');

      if (isAdmin) {
        const auditRes = await fetchAuditLogs({ page: 1, pageSize: 25 });
        setAuditLogs(auditRes?.items || []);
        setAuditTotal(auditRes?.total || 0);
      }
    } catch (err) {
      showNotification('PDF download failed: ' + (err?.response?.data?.error?.message || err.message), true);
    } finally {
      setExporting(false);
    }
  };

  const handleDownloadCsv = async () => {
    setExporting(true);
    try {
      const blob = await exportComprehensiveReport({
        district: reportDistrict,
        habitationId: reportHabitationId || null,
        hazardEventId: reportHazardEventId || null,
        relocationSiteId: reportRelocationSiteId || null,
        officerNotes: exportNotes,
        format: 'csv',
      });
      const url = window.URL.createObjectURL(new Blob([blob], { type: 'text/csv' }));
      const link = document.createElement('a');
      link.href = url;
      const focalName = (generatedReport?.jurisdiction?.focal_habitation || 'disaster').replace(/\s+/g, '_').toLowerCase();
      link.setAttribute('download', `sih26_report_${focalName}_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      showNotification('Official CSV report downloaded successfully.');

      if (isAdmin) {
        const auditRes = await fetchAuditLogs({ page: 1, pageSize: 25 });
        setAuditLogs(auditRes?.items || []);
        setAuditTotal(auditRes?.total || 0);
      }
    } catch (err) {
      showNotification('CSV download failed: ' + (err?.response?.data?.error?.message || err.message), true);
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
            TAB 4: EXECUTIVE REPORT GENERATION & DECISION BRIEFING
           ========================================================================= */}
        {activeTab === 'export_report' && (
          <div className="space-y-6">
            {/* Report Configuration & Target Selection Panel */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
                <div>
                  <h2 className="text-lg font-black text-white flex items-center gap-2">
                    <FileSpreadsheet className="w-5 h-5 text-amber-400" />
                    <span>Executive Disaster Risk & Relocation Report Generator</span>
                  </h2>
                  <p className="text-xs text-slate-400">
                    Generate multi-criteria decision-support reports for any combination of district, settlement, hazard incident, and relocation parcel.
                  </p>
                </div>
                <div className="flex items-center gap-2 font-mono text-xs">
                  <span className="px-2.5 py-1 rounded bg-slate-950 text-slate-300 border border-slate-800">
                    13 Statutory Sections
                  </span>
                  <span className="px-2.5 py-1 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30">
                    4 Epistemic Pillars
                  </span>
                </div>
              </div>

              {/* Selection Dropdown Controls */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                {/* 1. Selected District */}
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                    1. Target District:
                  </label>
                  <select
                    value={reportDistrict}
                    onChange={(e) => setReportDistrict(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 font-mono focus:border-amber-500 focus:outline-none"
                  >
                    {reportOptions.districts?.map((d) => (
                      <option key={d} value={d}>{d} District</option>
                    ))}
                  </select>
                </div>

                {/* 2. Selected Habitation */}
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                    2. Focal Settlement:
                  </label>
                  <select
                    value={reportHabitationId}
                    onChange={(e) => setReportHabitationId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 font-mono focus:border-amber-500 focus:outline-none"
                  >
                    <option value="">All / Priority Overview</option>
                    {reportOptions.habitations?.map((h) => (
                      <option key={h.id} value={h.id}>
                        {h.name} (Pop: {h.population?.toLocaleString()})
                      </option>
                    ))}
                  </select>
                </div>

                {/* 3. Selected Hazard Event */}
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                    3. Focal Hazard Event:
                  </label>
                  <select
                    value={reportHazardEventId}
                    onChange={(e) => setReportHazardEventId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 font-mono focus:border-amber-500 focus:outline-none"
                  >
                    <option value="">Latest Active Multi-Hazard Trigger</option>
                    {reportOptions.hazard_events?.map((ev) => (
                      <option key={ev.id} value={ev.id}>
                        {ev.disaster_type?.toUpperCase()} ({ev.severity}) - {ev.source}
                      </option>
                    ))}
                  </select>
                </div>

                {/* 4. Selected Relocation Site */}
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                    4. Candidate Relocation Parcel:
                  </label>
                  <select
                    value={reportRelocationSiteId}
                    onChange={(e) => setReportRelocationSiteId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 font-mono focus:border-amber-500 focus:outline-none"
                  >
                    <option value="">Optimal Evaluated Safe Parcel</option>
                    {reportOptions.relocation_sites?.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name} (Buffer: +{s.available_capacity?.toLocaleString()})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Officer Directives / Notes */}
              <div className="mb-5">
                <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                  Commanding Officer Directives & Strategic Notes:
                </label>
                <textarea
                  rows="2"
                  value={exportNotes}
                  onChange={(e) => setExportNotes(e.target.value)}
                  placeholder="Enter executive briefing notes, monsoon contingencies, priority evacuation orders, or civil defense notes..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:border-amber-500 focus:outline-none"
                ></textarea>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={handleGenerateLiveReport}
                  disabled={generatingReport}
                  className="px-4 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-lg flex items-center gap-2 transition-all shadow-md shadow-amber-950/40 disabled:opacity-50 cursor-pointer"
                >
                  <Eye className="w-4 h-4" />
                  <span>{generatingReport ? 'Compiling 13 Sections...' : 'Generate & Inspect Live Report'}</span>
                </button>

                <button
                  type="button"
                  onClick={handleDownloadPdf}
                  disabled={exporting}
                  className="px-4 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs rounded-lg flex items-center gap-2 transition-all shadow-md shadow-rose-950/40 disabled:opacity-50 cursor-pointer"
                >
                  <FileText className="w-4 h-4" />
                  <span>{exporting ? 'Generating PDF...' : 'Download Official PDF Report'}</span>
                </button>

                <button
                  type="button"
                  onClick={handleDownloadCsv}
                  disabled={exporting}
                  className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-lg flex items-center gap-2 transition-all shadow-md shadow-emerald-950/40 disabled:opacity-50 cursor-pointer"
                >
                  <Download className="w-4 h-4" />
                  <span>{exporting ? 'Exporting CSV...' : 'Download CSV Spreadsheet'}</span>
                </button>
              </div>
            </div>

            {/* Generated Report Live Inspector */}
            {generatedReport && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl space-y-6">
                {/* Report Header & Meta Bar */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-xl bg-slate-950 border border-slate-800">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        {generatedReport.report_id}
                      </span>
                      <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {new Date(generatedReport.generated_at).toLocaleString()} UTC
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-white tracking-tight">
                      {generatedReport.title}
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Focal Target: <span className="text-slate-200 font-semibold">{generatedReport.jurisdiction?.focal_habitation}</span> ({generatedReport.jurisdiction?.district}) • Reporting Officer: <span className="text-slate-200 font-semibold">{generatedReport.officer?.name}</span> ({generatedReport.officer?.designation})
                    </p>
                  </div>

                  {/* View Mode Toggle */}
                  <div className="flex items-center gap-1.5 p-1 rounded-lg bg-slate-900 border border-slate-800">
                    <button
                      type="button"
                      onClick={() => setReportViewMode('13_sections')}
                      className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                        reportViewMode === '13_sections'
                          ? 'bg-amber-500 text-slate-950 font-bold'
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      13-Section Deep Dive
                    </button>
                    <button
                      type="button"
                      onClick={() => setReportViewMode('epistemic')}
                      className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                        reportViewMode === 'epistemic'
                          ? 'bg-amber-500 text-slate-950 font-bold'
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      Epistemic Demarcation (4 Pillars)
                    </button>
                  </div>
                </div>

                {/* VIEW 1: EPISTEMIC DEMARCATION (4 PILLARS) */}
                {reportViewMode === 'epistemic' && generatedReport.epistemic_categorization && (
                  <div className="space-y-4">
                    <div className="text-xs text-slate-400 bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                      <strong className="text-slate-200">EPISTEMIC GOVERNANCE PRINCIPLE:</strong> Scientific disaster management strictly separates ground sensor measurements from statistical models, mathematical assumptions, and executive directives to ensure transparent decision-support.
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Pillar 1: Observed Data */}
                      <div className="p-4 rounded-xl bg-blue-950/20 border border-blue-500/30">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="w-2.5 h-2.5 rounded-full bg-blue-400 animate-pulse"></span>
                          <h4 className="text-xs font-bold text-blue-300 uppercase tracking-wider font-mono">
                            [1] OBSERVED DATA (Empirical Ground Sensors)
                          </h4>
                        </div>
                        <p className="text-[11px] text-slate-400 mb-3">
                          {generatedReport.epistemic_categorization.observed_data.description}
                        </p>
                        <div className="space-y-1.5 text-xs font-mono">
                          {Object.entries(generatedReport.epistemic_categorization.observed_data.items).map(([k, v]) => (
                            <div key={k} className="flex items-center justify-between p-1.5 rounded bg-slate-950/60 border border-slate-800">
                              <span className="text-slate-400 capitalize">{k.replace(/_/g, ' ')}:</span>
                              <span className="font-bold text-blue-300">{String(v)}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Pillar 2: Model-Derived Scores */}
                      <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                          <h4 className="text-xs font-bold text-amber-300 uppercase tracking-wider font-mono">
                            [2] MODEL-DERIVED SCORES (Algorithmic Indices)
                          </h4>
                        </div>
                        <p className="text-[11px] text-slate-400 mb-3">
                          {generatedReport.epistemic_categorization.model_derived_scores.description}
                        </p>
                        <div className="space-y-1.5 text-xs font-mono">
                          {Object.entries(generatedReport.epistemic_categorization.model_derived_scores.items).map(([k, v]) => (
                            <div key={k} className="flex items-center justify-between p-1.5 rounded bg-slate-950/60 border border-slate-800">
                              <span className="text-slate-400 capitalize">{k.replace(/_/g, ' ')}:</span>
                              <span className="font-bold text-amber-300">{String(v)}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Pillar 3: Prototype Assumptions */}
                      <div className="p-4 rounded-xl bg-slate-900 border border-slate-700">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="w-2.5 h-2.5 rounded-full bg-slate-400"></span>
                          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
                            [3] PROTOTYPE ASSUMPTIONS (Engineering Norms)
                          </h4>
                        </div>
                        <p className="text-[11px] text-slate-400 mb-3">
                          {generatedReport.epistemic_categorization.prototype_assumptions.description}
                        </p>
                        <div className="space-y-1.5 text-xs font-mono">
                          {Object.entries(generatedReport.epistemic_categorization.prototype_assumptions.items).map(([k, v]) => (
                            <div key={k} className="flex items-center justify-between p-1.5 rounded bg-slate-950/60 border border-slate-800">
                              <span className="text-slate-400 capitalize">{k.replace(/_/g, ' ')}:</span>
                              <span className="font-bold text-slate-300">{String(v)}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Pillar 4: Recommendations */}
                      <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                          <h4 className="text-xs font-bold text-emerald-300 uppercase tracking-wider font-mono">
                            [4] RECOMMENDATIONS (Decision-Support Actions)
                          </h4>
                        </div>
                        <p className="text-[11px] text-slate-400 mb-3">
                          {generatedReport.epistemic_categorization.recommendations.description}
                        </p>
                        <div className="space-y-1.5 text-xs font-mono">
                          {Object.entries(generatedReport.epistemic_categorization.recommendations.items).map(([k, v]) => (
                            <div key={k} className="flex items-center justify-between p-1.5 rounded bg-slate-950/60 border border-slate-800">
                              <span className="text-slate-400 capitalize">{k.replace(/_/g, ' ')}:</span>
                              <span className="font-bold text-emerald-300 text-right">{String(v)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* VIEW 2: 13-SECTION DETAILED BREAKDOWN */}
                {reportViewMode === '13_sections' && (
                  <div className="space-y-5">
                    {/* Section 1: Situation Summary */}
                    <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                      <div className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono mb-1.5">
                        1. Situation Summary
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {generatedReport.situation_summary}
                      </p>
                    </div>

                    {/* Section 2: Hazard Assessment */}
                    <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                      <div className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono mb-2">
                        2. Hazard Assessment & Telemetry
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                          <div className="text-[11px] text-slate-400">Active Event / Trigger</div>
                          <div className="font-bold text-rose-400 mt-0.5">{generatedReport.hazard_assessment?.active_hazard_type}</div>
                          <div className="text-[10px] text-slate-500 font-mono mt-1">Severity: {generatedReport.hazard_assessment?.hazard_severity}</div>
                        </div>

                        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                          <div className="text-[11px] text-slate-400">Observed Rainfall (24h)</div>
                          <div className="text-lg font-black text-amber-300 font-mono mt-0.5">
                            {generatedReport.hazard_assessment?.rainfall_telemetry?.observed_rainfall_mm} mm
                          </div>
                          <div className="text-[10px] text-slate-500 truncate mt-1">
                            {generatedReport.hazard_assessment?.rainfall_telemetry?.station}
                          </div>
                        </div>

                        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                          <div className="text-[11px] text-slate-400">River Gauge Danger Exceedance</div>
                          <div className="text-lg font-black text-rose-400 font-mono mt-0.5">
                            +{generatedReport.hazard_assessment?.river_telemetry?.exceedance_meters} m
                          </div>
                          <div className="text-[10px] text-slate-500 truncate mt-1">
                            {generatedReport.hazard_assessment?.river_telemetry?.station_name}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Section 3: Population Vulnerability */}
                    <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                      <div className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono mb-2">
                        3. Population Vulnerability Profile
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                        <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 block">Total Population</span>
                          <span className="font-bold text-slate-100 text-sm">{generatedReport.population_vulnerability?.total_population?.toLocaleString()}</span>
                        </div>
                        <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 block">Vulnerable Count</span>
                          <span className="font-bold text-amber-400 text-sm">
                            {generatedReport.population_vulnerability?.vulnerable_population?.toLocaleString()} ({generatedReport.population_vulnerability?.vulnerable_percentage}%)
                          </span>
                        </div>
                        <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 block">Elderly / Children / Disabled</span>
                          <span className="font-bold text-slate-200 text-sm">
                            {generatedReport.population_vulnerability?.elderly_count} / {generatedReport.population_vulnerability?.children_under_10_count} / {generatedReport.population_vulnerability?.persons_with_disabilities}
                          </span>
                        </div>
                        <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 block">Kutcha Dwellings Ratio</span>
                          <span className="font-bold text-rose-300 text-sm">{generatedReport.population_vulnerability?.kutcha_housing_percentage}%</span>
                        </div>
                      </div>
                    </div>

                    {/* Section 4: Disaster History */}
                    <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                      <div className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono mb-2">
                        4. Disaster Incident History
                      </div>
                      <div className="space-y-2 text-xs">
                        {generatedReport.disaster_history?.map((h_ev, hIdx) => (
                          <div key={hIdx} className="p-2.5 rounded bg-slate-900 border border-slate-800 flex items-center justify-between gap-3">
                            <div>
                              <span className="font-bold text-slate-200 capitalize">{h_ev.type}</span> • <span className="text-slate-400">{h_ev.historical_significance}</span>
                            </div>
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-amber-300 border border-slate-700">
                              {h_ev.severity} ({h_ev.timestamp?.slice(0, 10)})
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Section 5, 6, 7: Risk, Priority & Relocation Recommendations */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Section 5: Risk Score */}
                      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                        <div className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono mb-1">
                          5. Hazard Risk Score
                        </div>
                        <div className="text-2xl font-black text-rose-400 font-mono mt-1">
                          {generatedReport.risk_score?.score} / 100
                        </div>
                        <div className="text-[10px] font-mono text-slate-400 uppercase">
                          Tier: {generatedReport.risk_score?.classification}
                        </div>
                        <div className="mt-3 space-y-1 text-[11px] font-mono">
                          {generatedReport.risk_score?.factor_sub_scores && Object.entries(generatedReport.risk_score.factor_sub_scores).map(([fk, fv]) => (
                            <div key={fk} className="flex justify-between text-slate-400">
                              <span className="capitalize">{fk.replace(/_/g, ' ')}:</span>
                              <span className="text-slate-200">{String(fv)}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Section 6: Relocation Priority */}
                      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                        <div className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono mb-1">
                          6. Relocation Urgency
                        </div>
                        <div className="text-2xl font-black text-amber-400 font-mono mt-1">
                          {generatedReport.relocation_priority?.priority}
                        </div>
                        <div className="text-[10px] font-mono text-slate-400">
                          Priority Score: {generatedReport.relocation_priority?.priority_score} / 100
                        </div>
                        <p className="text-xs text-slate-300 mt-3 italic">
                          "{generatedReport.relocation_priority?.action_urgency}"
                        </p>
                      </div>

                      {/* Section 7: Recommended Site */}
                      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                        <div className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono mb-1">
                          7. Recommended Safe Site
                        </div>
                        <div className="text-sm font-bold text-emerald-400 mt-1">
                          {generatedReport.recommended_relocation_sites?.[0]?.name}
                        </div>
                        <div className="text-[11px] font-mono text-slate-400 mt-1">
                          Distance: <span className="text-slate-200 font-bold">{generatedReport.recommended_relocation_sites?.[0]?.distance_km} km</span> • Suitability: <span className="text-emerald-300 font-bold">{generatedReport.recommended_relocation_sites?.[0]?.suitability_score}/100</span>
                        </div>
                        <div className="mt-3 space-y-1 text-[10px] text-slate-400">
                          {generatedReport.recommended_relocation_sites?.[0]?.strengths?.map((st, stIdx) => (
                            <div key={stIdx} className="flex items-center gap-1.5">
                              <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                              <span>{st}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Section 8 & 9: Carrying Capacity & Available Buffer */}
                    <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                      <div className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono mb-2">
                        8. Carrying Capacity & 9. Available Buffer (Liebig's Law Bottleneck Model)
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                        <div className="p-3 rounded bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 block">Gross Spatial Area</span>
                          <span className="font-bold text-slate-200">{generatedReport.carrying_capacity?.usable_land_area_sqm?.toLocaleString()} m²</span>
                          <span className="text-[10px] text-slate-500 block">@ 50 m²/person</span>
                        </div>
                        <div className="p-3 rounded bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 block">Sustainable Civil Capacity</span>
                          <span className="font-bold text-emerald-400 text-sm">{generatedReport.carrying_capacity?.final_ecological_civil_capacity?.toLocaleString()} persons</span>
                          <span className="text-[10px] text-slate-500 block">Bottleneck limited</span>
                        </div>
                        <div className="p-3 rounded bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 block">Available Headroom Buffer</span>
                          <span className="font-bold text-emerald-300 text-sm">+{generatedReport.available_capacity?.available_buffer?.toLocaleString()} persons</span>
                          <span className="text-[10px] text-slate-500 block">Net capacity buffer</span>
                        </div>
                        <div className="p-3 rounded bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 block">Limiting Factor</span>
                          <span className="font-bold text-amber-300 text-xs truncate block">{generatedReport.carrying_capacity?.limiting_factor}</span>
                          <span className="text-[10px] text-slate-500 block">Active constraint</span>
                        </div>
                      </div>
                    </div>

                    {/* Section 10: Key Reasons */}
                    <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                      <div className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono mb-2">
                        10. Key Reasons & Operational Justifications
                      </div>
                      <div className="space-y-1.5 text-xs">
                        {generatedReport.key_reasons?.map((rsn, idx) => (
                          <div key={idx} className="flex items-start gap-2 text-slate-300">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0"></span>
                            <span>{rsn}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Section 11, 12, 13: Data Sources, Timestamps & Assumptions */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Section 11: Data Sources */}
                      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                        <div className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono mb-2">
                          11. Data Sources
                        </div>
                        <div className="space-y-2 text-[11px]">
                          {generatedReport.data_sources?.map((ds, dsIdx) => (
                            <div key={dsIdx} className="p-2 rounded bg-slate-900 border border-slate-800">
                              <span className="font-bold text-slate-200 block">{ds.domain}</span>
                              <span className="text-slate-400">{ds.provider} ({ds.product})</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Section 12: Data Timestamps */}
                      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 font-mono">
                        <div className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2">
                          12. Observation Timestamps
                        </div>
                        <div className="space-y-2 text-[11px]">
                          {generatedReport.data_timestamps && Object.entries(generatedReport.data_timestamps).map(([tk, tv]) => (
                            <div key={tk} className="p-2 rounded bg-slate-900 border border-slate-800">
                              <span className="text-slate-400 block capitalize">{tk.replace(/_/g, ' ')}:</span>
                              <span className="text-slate-200 font-semibold">{String(tv)}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Section 13: Model Assumptions */}
                      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
                        <div className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono mb-2">
                          13. Model Assumptions
                        </div>
                        <div className="space-y-2 text-[11px]">
                          {generatedReport.model_scoring_assumptions?.map((asm, aIdx) => (
                            <div key={aIdx} className="p-2 rounded bg-slate-900 border border-slate-800">
                              <span className="font-bold text-slate-300 block">{asm.parameter}: {asm.value}</span>
                              <span className="text-slate-500 italic">{asm.basis}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Statutory Signoff Footer */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 space-y-1">
                  <div className="font-bold text-slate-300 uppercase tracking-wider font-mono">
                    Statutory Compliance Notice (Disaster Management Act, 2005):
                  </div>
                  <p className="leading-relaxed">
                    {generatedReport.statutory_signoff?.legal_disclaimer}
                  </p>
                  <p className="text-[11px] font-mono text-slate-500 pt-1">
                    Certified for executive decision-support review by {generatedReport.officer?.name}, {generatedReport.officer?.designation}.
                  </p>
                </div>
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
