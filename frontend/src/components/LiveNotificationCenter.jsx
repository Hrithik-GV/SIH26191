import React, { useState, useEffect, useRef } from 'react';
import {
  Bell,
  AlertTriangle,
  Flame,
  Home,
  ShieldCheck,
  CloudRain,
  Waves,
  Radio,
  X,
  ChevronDown,
  ChevronUp,
  Play,
  RotateCcw,
  CheckCircle2,
  Info,
  ShieldAlert,
  ArrowRight,
  ExternalLink,
} from 'lucide-react';

import {
  connectDisasterEventStream,
  getRecentDisasterEvents,
  simulateDisasterScenario,
} from '../services/api';

export default function LiveNotificationCenter({
  onEventReceived,
  onNavigate,
  onFocusEntity,
}) {
  const [events, setEvents] = useState([]);
  const [activeNotifications, setActiveNotifications] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showSimulateMenu, setShowSimulateMenu] = useState(false);

  // Initialize SSE connection & fetch recent history
  useEffect(() => {
    // 1. Fetch recent history
    async function loadRecent() {
      const res = await getRecentDisasterEvents(10);
      if (res.data?.events) {
        setEvents(res.data.events);
      }
    }
    loadRecent();

    // 2. Connect to Server-Sent Events (SSE)
    const cleanup = connectDisasterEventStream(
      (eventPayload) => {
        setIsConnected(true);

        if (eventPayload.event_type === 'CONNECTED') {
          return;
        }

        // Add to persistent event log
        setEvents((prev) => [eventPayload, ...prev.slice(0, 49)]);

        // Push to active toast notifications
        setActiveNotifications((prev) => [eventPayload, ...prev.slice(0, 4)]);

        // Propagate to parent (updates KPI cards, maps, etc.)
        if (onEventReceived) {
          onEventReceived(eventPayload);
        }

        // Auto dismiss toast after 9 seconds
        setTimeout(() => {
          setActiveNotifications((current) =>
            current.filter((n) => n.id !== eventPayload.id)
          );
        }, 9000);
      },
      (err) => {
        // Fallback gracefully to simulated standby
        setIsConnected(false);
      }
    );

    return () => {
      cleanup();
    };
  }, [onEventReceived]);

  // Dismiss a single toast
  const dismissToast = (id) => {
    setActiveNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  // Trigger Live Disaster Simulation
  const handleTriggerScenario = async (scenario) => {
    setIsSimulating(true);
    setShowSimulateMenu(false);

    try {
      const res = await simulateDisasterScenario(scenario);
      if (res.success && res.data?.pipeline_result) {
        // If running in local demo without live backend SSE, manually dispatch the events
        if (!isConnected) {
          const now = new Date().toISOString();
          let headline = 'Heavy rainfall alert detected';
          let evtType = 'NEW_ALERT';
          let severity = 'CRITICAL';

          if (scenario === 'river_surge') {
            headline = '12 habitations have moved to HIGH risk';
            evtType = 'HABITATION_PRIORITY_CHANGED';
          } else if (scenario === 'landslide_warning') {
            headline = '3 habitations require immediate assessment';
            evtType = 'HABITATION_PRIORITY_CHANGED';
          }

          const syntheticEvent = {
            id: `evt-sim-${Date.now()}`,
            event_type: evtType,
            headline,
            severity,
            timestamp: now,
            data: res.data.pipeline_result,
            disclaimer: (
              'Decision-support telemetry: Relocation allocations and priority classifications ' +
              'are advisory candidate assessments. Relocation actions require competent administrative authority validation.'
            ),
          };

          setEvents((prev) => [syntheticEvent, ...prev]);
          setActiveNotifications((prev) => [syntheticEvent, ...prev.slice(0, 4)]);
          if (onEventReceived) onEventReceived(syntheticEvent);
        }
      }
    } catch (err) {
      console.error('Error triggering simulation scenario:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <>
      {/* Real-Time Live Status Bar with Simulation Trigger */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl px-4 py-2.5 shadow-sm text-xs flex flex-wrap items-center justify-between gap-3 font-sans">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Radio
              className={`w-3.5 h-3.5 ${
                isConnected ? 'text-emerald-400 animate-pulse' : 'text-amber-400'
              }`}
            />
            <span className="font-semibold text-slate-200">
              {isConnected
                ? 'Server-Sent Events (SSE) Live Disaster Stream Connected'
                : 'Live Telemetry Engine Active (Autonomous Standby Mode)'}
            </span>
          </div>

          <span className="text-slate-600 hidden md:inline">|</span>

          <span className="text-[11px] text-slate-400 hidden lg:inline">
            Pipeline: 1. Store Observation → 2. Geo Buffer → 3. Recalculate Hazards → 4. Priorities → 5. Relocation Sites → 6. Dashboard
          </span>
        </div>

        {/* Right Action Controls: Scenario Trigger & Event History */}
        <div className="flex items-center gap-2">
          {/* Interactive Live Scenario Simulation Button */}
          <div className="relative">
            <button
              onClick={() => setShowSimulateMenu(!showSimulateMenu)}
              disabled={isSimulating}
              className="bg-rose-950/80 hover:bg-rose-900 text-rose-200 border border-rose-800/80 px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors shadow-sm disabled:opacity-50"
            >
              <Play className={`w-3.5 h-3.5 text-rose-400 ${isSimulating ? 'animate-spin' : ''}`} />
              <span>{isSimulating ? 'Processing Pipeline...' : 'Simulate Live Ingestion'}</span>
              <ChevronDown className="w-3.5 h-3.5 text-rose-400" />
            </button>

            {showSimulateMenu && (
              <div className="absolute right-0 top-10 w-72 bg-slate-900/95 backdrop-blur-md border border-slate-700 rounded-xl shadow-2xl p-2 z-40 space-y-1 text-xs">
                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 px-2 py-1 border-b border-slate-800">
                  Select Real-Time Ingestion Scenario
                </p>

                <button
                  onClick={() => handleTriggerScenario('heavy_rainfall')}
                  className="w-full text-left p-2 rounded hover:bg-slate-800 transition-colors flex items-start gap-2"
                >
                  <CloudRain className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-slate-200">Heavy Rainfall Cloudburst (382mm)</p>
                    <p className="text-[10px] text-slate-400">
                      Triggers: "Heavy rainfall alert detected" & escalates hazard risk to CRITICAL
                    </p>
                  </div>
                </button>

                <button
                  onClick={() => handleTriggerScenario('river_surge')}
                  className="w-full text-left p-2 rounded hover:bg-slate-800 transition-colors flex items-start gap-2"
                >
                  <Waves className="w-4 h-4 text-sky-400 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-slate-200">Iruvaipuzha River Level Surge (5.2m)</p>
                    <p className="text-[10px] text-slate-400">
                      Triggers: "12 habitations have moved to HIGH risk" following river gauge breach
                    </p>
                  </div>
                </button>

                <button
                  onClick={() => handleTriggerScenario('landslide_warning')}
                  className="w-full text-left p-2 rounded hover:bg-slate-800 transition-colors flex items-start gap-2"
                >
                  <Flame className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-slate-200">NDMA SACHET Landslide Warning</p>
                    <p className="text-[10px] text-slate-400">
                      Triggers: "3 habitations require immediate assessment" for potential assisted egress
                    </p>
                  </div>
                </button>
              </div>
            )}
          </div>

          {/* Event History Toggle Button */}
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-2.5 py-1.5 rounded-lg text-xs font-mono flex items-center gap-1.5 transition-colors"
          >
            <Bell className="w-3.5 h-3.5 text-amber-400" />
            <span>Feed ({events.length})</span>
          </button>
        </div>
      </div>

      {/* FLOATING ACTIVE TOAST NOTIFICATION STREAM (Top Right) */}
      <div className="fixed top-20 right-4 z-50 flex flex-col gap-2.5 max-w-sm pointer-events-none">
        {activeNotifications.map((notif) => {
          const isCritical = notif.severity === 'CRITICAL' || notif.event_type === 'NEW_ALERT';
          const isHigh = notif.severity === 'HIGH' || notif.event_type === 'HABITATION_PRIORITY_CHANGED';

          return (
            <div
              key={notif.id}
              className={`pointer-events-auto rounded-xl p-3.5 border shadow-2xl backdrop-blur-md transition-all transform translate-y-0 text-xs ${
                isCritical
                  ? 'bg-rose-950/95 border-rose-600/80 text-rose-100 shadow-rose-950/50'
                  : isHigh
                  ? 'bg-amber-950/95 border-amber-600/80 text-amber-100 shadow-amber-950/50'
                  : 'bg-slate-900/95 border-sky-600/80 text-slate-100 shadow-slate-950/50'
              }`}
            >
              {/* Toast Header */}
              <div className="flex items-start justify-between gap-2 pb-1.5 border-b border-white/10">
                <div className="flex items-center gap-2">
                  {notif.event_type === 'NEW_ALERT' && <AlertTriangle className="w-4 h-4 text-rose-400 animate-bounce" />}
                  {notif.event_type === 'HAZARD_UPDATED' && <Flame className="w-4 h-4 text-orange-400" />}
                  {notif.event_type === 'HABITATION_PRIORITY_CHANGED' && <Home className="w-4 h-4 text-amber-400" />}
                  {notif.event_type === 'RELOCATION_SITE_UPDATED' && <ShieldCheck className="w-4 h-4 text-emerald-400" />}

                  <span className="font-mono text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-black/40 border border-white/10">
                    {notif.event_type}
                  </span>
                </div>

                <button
                  onClick={() => dismissToast(notif.id)}
                  className="text-white/60 hover:text-white p-0.5 rounded hover:bg-black/30"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Toast Headline */}
              <div className="mt-2 font-bold text-sm leading-snug">
                {notif.headline}
              </div>

              {/* Timestamp & Affected Summary */}
              <div className="mt-1 text-[10px] text-white/70 font-mono flex items-center justify-between">
                <span>{new Date(notif.timestamp).toLocaleTimeString()} IST</span>
                {notif.data?.immediate_assessment_count !== undefined && (
                  <span className="text-rose-300 font-bold">
                    {notif.data.immediate_assessment_count} Immediate Assessment(s)
                  </span>
                )}
              </div>

              {/* Mandatory Governance Notice: No automatic relocation */}
              <div className="mt-2 pt-1.5 border-t border-white/10 text-[9px] text-white/70 leading-tight italic flex items-start gap-1">
                <Info className="w-3 h-3 text-amber-300 shrink-0 mt-0.5" />
                <span>Advisory decision support: Relocation decisions require competent administrative authority validation.</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* EVENT HISTORY DRAWER / AUDIT MODAL */}
      {showHistory && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-2xl overflow-hidden font-sans">
            {/* Modal Header */}
            <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center">
                  <Bell className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white leading-tight">
                    Live Disaster Event Stream Audit Log
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    Real-time sequential broadcast record for SIH 26191 emergency telemetry
                  </p>
                </div>
              </div>

              <button
                onClick={() => setShowHistory(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Event List */}
            <div className="p-4 overflow-y-auto space-y-2.5 text-xs flex-1">
              {events.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  <Radio className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                  <p>No telemetry events logged yet in current session.</p>
                </div>
              ) : (
                events.map((evt, idx) => (
                  <div
                    key={evt.id || idx}
                    className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex flex-col gap-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span
                          className={`px-1.5 py-0.5 rounded font-mono text-[9px] font-bold uppercase border ${
                            evt.event_type === 'NEW_ALERT'
                              ? 'bg-rose-950 text-rose-300 border-rose-800'
                              : evt.event_type === 'HABITATION_PRIORITY_CHANGED'
                              ? 'bg-amber-950 text-amber-300 border-amber-800'
                              : evt.event_type === 'RELOCATION_SITE_UPDATED'
                              ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                              : 'bg-sky-950 text-sky-300 border-sky-800'
                          }`}
                        >
                          {evt.event_type}
                        </span>
                        <span className="font-semibold text-slate-200">{evt.headline}</span>
                      </div>
                      <span className="font-mono text-[10px] text-slate-500">
                        {new Date(evt.timestamp).toLocaleTimeString()}
                      </span>
                    </div>

                    {evt.data?.raw_metrics && (
                      <div className="bg-slate-900 p-2 rounded text-[10px] font-mono text-slate-300">
                        Metrics: {JSON.stringify(evt.data.raw_metrics)}
                      </div>
                    )}

                    <div className="text-[10px] text-slate-400 italic">
                      {evt.disclaimer}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
