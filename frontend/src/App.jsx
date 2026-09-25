import React, { useState, useEffect, useCallback } from 'react';
import {
  Server,
  Database,
  Activity,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Layers,
  Cpu,
  ShieldAlert,
  ArrowRight,
  ExternalLink,
  Code2,
  Clock,
  Terminal,
} from 'lucide-react';
import { checkSystemHealth, pingBackend, BACKEND_ROOT_URL } from './services/api';

export default function App() {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pingLoading, setPingLoading] = useState(false);
  const [lastPing, setLastPing] = useState(null);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [showRawJson, setShowRawJson] = useState(false);

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await checkSystemHealth();
      if (res.success) {
        setHealthData(res.data);
      } else {
        setError(res.error);
        setHealthData(null);
      }
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err.message || 'Failed to connect to backend service');
      setHealthData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const handlePing = async () => {
    setPingLoading(true);
    try {
      const res = await pingBackend();
      setLastPing(res);
    } catch (err) {
      setLastPing({ success: false, error: err.message, latency: null });
    } finally {
      setPingLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  const isHealthy = healthData?.status === 'healthy';
  const isDegraded = healthData?.status === 'degraded';
  const isConnected = !!healthData;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-500 text-white flex items-center justify-center font-bold text-lg shadow-sm">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight">
                  Disaster Risk & Vulnerable Habitations Assessment
                </h1>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
                  SIH 2026 • PS 26191
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                Hazard-Based Red Zones • Carrying Capacity • Immediate Relocation Needs
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Live Indicator */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border bg-white shadow-2xs">
              <span className="relative flex h-2 w-2">
                <span
                  className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                    isHealthy ? 'bg-emerald-400' : isDegraded ? 'bg-amber-400' : 'bg-red-400'
                  }`}
                />
                <span
                  className={`relative inline-flex rounded-full h-2 w-2 ${
                    isHealthy ? 'bg-emerald-500' : isDegraded ? 'bg-amber-500' : 'bg-red-500'
                  }`}
                />
              </span>
              <span className="text-slate-600">
                {isConnected
                  ? isHealthy
                    ? 'All Systems Operational'
                    : 'Backend Online (DB Degraded)'
                  : 'Backend Offline'}
              </span>
            </div>

            <button
              onClick={fetchHealth}
              disabled={loading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-colors disabled:opacity-50 cursor-pointer"
              title="Refresh health check"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-slate-500' : ''}`} />
              <span className="hidden sm:inline">Refresh</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Banner Alert if Backend Offline */}
        {!isConnected && !loading && (
          <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-red-800 flex items-start gap-3">
            <XCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            <div className="text-sm">
              <p className="font-semibold text-red-900">Backend Connection Failed</p>
              <p className="mt-0.5 text-red-700">
                Could not reach FastAPI backend at{' '}
                <code className="bg-red-100 px-1 py-0.5 rounded text-xs font-mono">{BACKEND_ROOT_URL}/health</code>.
                Ensure backend service is running locally on port 8000 or via Docker Compose.
              </p>
              {error && <p className="mt-1 text-xs text-red-600 font-mono">Error: {error}</p>}
            </div>
          </div>
        )}

        {/* Connectivity Confirmation Hero Card */}
        <section className="bg-white rounded-xl border border-slate-200 shadow-xs p-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-slate-100 text-slate-700">
                  <Activity className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-slate-900">
                    Full-Stack Connectivity & Environment Health
                  </h2>
                  <p className="text-xs text-slate-500">
                    Live telemetry confirming communication between React Frontend and FastAPI Backend
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handlePing}
                disabled={pingLoading || !isConnected}
                className="inline-flex items-center gap-2 px-3.5 py-1.5 text-xs font-medium rounded-lg text-slate-700 bg-white hover:bg-slate-50 border border-slate-300 shadow-2xs transition disabled:opacity-50 cursor-pointer"
              >
                <Terminal className="w-3.5 h-3.5 text-slate-600" />
                {pingLoading ? 'Testing ping...' : 'Ping /api/v1/ping'}
              </button>

              <a
                href={`${BACKEND_ROOT_URL}/docs`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded-lg text-white bg-slate-800 hover:bg-slate-900 shadow-2xs transition"
              >
                <span>Swagger Docs</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          {/* Quick Ping Feedback */}
          {lastPing && (
            <div className="mt-4 p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs flex items-center justify-between">
              <span className="text-slate-600">
                Ping Status:{' '}
                <strong className={lastPing.success ? 'text-emerald-700' : 'text-red-700'}>
                  {lastPing.success ? '200 OK (pong)' : 'Failed'}
                </strong>
              </span>
              <span className="font-mono text-slate-500">Latency: {lastPing.latency} ms</span>
            </div>
          )}

          {/* 3 Core Status Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5">
            {/* Card 1: FastAPI Core */}
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 hover:border-slate-300 transition">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Server className="w-3.5 h-3.5 text-slate-600" />
                  FastAPI Backend
                </span>
                {isConnected ? (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    Online
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                    <XCircle className="w-3 h-3 text-red-600" />
                    Offline
                  </span>
                )}
              </div>
              <div className="mt-3">
                <div className="text-lg font-bold text-slate-900">
                  {healthData?.version ? `v${healthData.version}` : 'Unavailable'}
                </div>
                <div className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                  <span>Env:</span>
                  <span className="font-mono text-slate-700">{healthData?.environment || 'unknown'}</span>
                </div>
              </div>
            </div>

            {/* Card 2: PostgreSQL / PostGIS */}
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 hover:border-slate-300 transition">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-slate-600" />
                  PostgreSQL / PostGIS
                </span>
                {healthData?.database?.connected ? (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    Connected
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">
                    <AlertTriangle className="w-3 h-3 text-amber-600" />
                    Standby / Disconnected
                  </span>
                )}
              </div>
              <div className="mt-3">
                <div className="text-sm font-semibold text-slate-900 truncate">
                  {healthData?.database?.connected
                    ? healthData.database.postgis_version || 'PostGIS Active'
                    : 'Awaiting Docker / DB Launch'}
                </div>
                <div className="text-xs text-slate-500 mt-1 flex items-center justify-between">
                  <span>Latency:</span>
                  <span className="font-mono text-slate-700">
                    {healthData?.database?.latency_ms !== null && healthData?.database?.latency_ms !== undefined
                      ? `${healthData.database.latency_ms} ms`
                      : 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            {/* Card 3: GIS / ML Processing Engine */}
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 hover:border-slate-300 transition">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-slate-600" />
                  GIS & ML Pipelines
                </span>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-sky-100 text-sky-800">
                  Configured
                </span>
              </div>
              <div className="mt-3">
                <div className="text-sm font-semibold text-slate-900">
                  GeoPandas & XGBoost Stack
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  Ready for red-zone raster & tabular intake
                </div>
              </div>
            </div>
          </div>

          {/* Timestamp footer */}
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              Last polled: {lastUpdated || 'Checking...'}
            </span>
            <button
              onClick={() => setShowRawJson(!showRawJson)}
              className="text-slate-600 hover:text-slate-900 font-medium inline-flex items-center gap-1 cursor-pointer"
            >
              <Code2 className="w-3.5 h-3.5" />
              {showRawJson ? 'Hide Diagnostic JSON' : 'View Diagnostic JSON'}
            </button>
          </div>

          {/* Raw Diagnostic JSON Viewer */}
          {showRawJson && (
            <div className="mt-4 p-4 rounded-lg bg-slate-900 text-slate-100 font-mono text-xs overflow-x-auto">
              <pre>{JSON.stringify(healthData || { error: error || 'No data' }, null, 2)}</pre>
            </div>
          )}
        </section>

        {/* Architectural Pipeline Grid */}
        <section className="bg-white rounded-xl border border-slate-200 shadow-xs p-6">
          <h2 className="text-base font-semibold text-slate-900">System Architecture Pipeline</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            End-to-end dataflow for Problem Statement 26191
          </p>

          <div className="mt-5 grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Step 1 */}
            <div className="p-4 rounded-lg border border-slate-200 bg-white relative">
              <div className="w-7 h-7 rounded-md bg-slate-100 text-slate-800 text-xs font-bold flex items-center justify-center mb-3">
                01
              </div>
              <h3 className="text-sm font-semibold text-slate-900">React Frontend</h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Vite + Tailwind CSS + MapLibre GL JS vector maps + Recharts demographic capacity visualizers.
              </p>
              <span className="mt-3 inline-block text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                Port 5173 / 3000
              </span>
            </div>

            {/* Step 2 */}
            <div className="p-4 rounded-lg border border-slate-200 bg-white relative">
              <div className="w-7 h-7 rounded-md bg-slate-100 text-slate-800 text-xs font-bold flex items-center justify-center mb-3">
                02
              </div>
              <h3 className="text-sm font-semibold text-slate-900">FastAPI Backend</h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Pydantic validation, SQLAlchemy 2.0 ORM, CORS security, structured logging, and health checks.
              </p>
              <span className="mt-3 inline-block text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                Port 8000
              </span>
            </div>

            {/* Step 3 */}
            <div className="p-4 rounded-lg border border-slate-200 bg-white relative">
              <div className="w-7 h-7 rounded-md bg-slate-100 text-slate-800 text-xs font-bold flex items-center justify-center mb-3">
                03
              </div>
              <h3 className="text-sm font-semibold text-slate-900">PostgreSQL + PostGIS</h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Spatial queries, GiST indices, hazard polygons, vulnerable habitations, and buffer intersections.
              </p>
              <span className="mt-3 inline-block text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                Port 5432
              </span>
            </div>

            {/* Step 4 */}
            <div className="p-4 rounded-lg border border-slate-200 bg-white relative">
              <div className="w-7 h-7 rounded-md bg-slate-100 text-slate-800 text-xs font-bold flex items-center justify-center mb-3">
                04
              </div>
              <h3 className="text-sm font-semibold text-slate-900">GIS & ML Layer</h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                GeoPandas, Shapely, Rasterio DEM processing with Scikit-learn & XGBoost relocation prioritization.
              </p>
              <span className="mt-3 inline-block text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                Processing Engine
              </span>
            </div>
          </div>
        </section>

        {/* Project Problem Statement Modules Preview */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
            <div className="w-8 h-8 rounded-lg bg-red-100 text-red-700 flex items-center justify-center mb-3">
              <Layers className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-semibold text-slate-900">1. Hazard Red Zone Mapping</h3>
            <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
              Multi-hazard risk delineation combining slope instability, flood levels, seismic sensitivity, and historical events.
            </p>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
              Module initialized • Ready for GIS layer ingestion
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
            <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center mb-3">
              <Activity className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-semibold text-slate-900">2. Carrying Capacity Assessment</h3>
            <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
              Resource and demographic threshold evaluation calculating ecological, water, and structural safety limits for habitations.
            </p>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
              Module initialized • Schema definitions prepared
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
            <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center mb-3">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-semibold text-slate-900">3. Relocation Priority Engine</h3>
            <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
              Algorithmic prioritization ranking vulnerable settlements by urgency, evacuation logistics, and safe shelter proximity.
            </p>
            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400">
              Module initialized • Pipeline structure established
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <p>
            Smart India Hackathon 2026 • Problem Statement 26191 Production Foundation
          </p>
          <div className="flex items-center gap-4">
            <a
              href="https://github.com/Hrithik-GV/SIH26191"
              target="_blank"
              rel="noreferrer"
              className="hover:text-slate-800 flex items-center gap-1"
            >
              <span>GitHub Repo</span>
              <ExternalLink className="w-3 h-3" />
            </a>
            <span className="text-slate-300">•</span>
            <span>FastAPI + React + PostGIS Monorepo</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
