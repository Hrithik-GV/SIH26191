import React, { useState } from 'react';
import {
  ShieldAlert,
  Lock,
  User,
  KeyRound,
  ShieldCheck,
  Building,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Terminal,
} from 'lucide-react';
import { useAuth, PRESET_USERS } from '../context/AuthContext';

export default function LoginPage({ onLoginSuccess }) {
  const { login } = useAuth();
  const [selectedUser, setSelectedUser] = useState(PRESET_USERS[0]);
  const [password, setPassword] = useState('GovAdmin@2026');
  const [rememberMe, setRememberMe] = useState(true);

  const handleSubmit = (e) => {
    e.preventDefault();
    login(selectedUser);
    if (onLoginSuccess) {
      onLoginSuccess();
    }
  };

  const handleQuickSelect = (preset) => {
    setSelectedUser(preset);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between font-sans relative overflow-hidden">
      {/* Background GIS Grid Accents */}
      <div className="absolute inset-0 opacity-10 bg-[linear-gradient(to_right,#334155_1px,transparent_1px),linear-gradient(to_bottom,#334155_1px,transparent_1px)] bg-[size:4rem_4rem] pointer-events-none"></div>

      {/* Top Government Strip */}
      <header className="px-6 py-4 border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-linear-to-br from-amber-500 to-rose-600 flex items-center justify-center font-bold text-white shadow-lg shadow-amber-950/40">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-100 tracking-tight flex items-center gap-2">
              DISASTER MANAGEMENT AUTHORITY (NDMA / KSDMA)
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                OFFICIAL PORTAL
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              Smart India Hackathon 2026 • Problem Statement 26191
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-xs font-mono text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>EOC SECURE NETWORK ONLINE</span>
        </div>
      </header>

      {/* Center Auth Card */}
      <main className="flex-1 flex items-center justify-center p-4 z-10">
        <div className="w-full max-w-md bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl">
          <div className="text-center mb-6">
            <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 mx-auto flex items-center justify-center mb-3 shadow-inner">
              <Lock className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-black text-white tracking-tight">
              Crisis Command Sign-In
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Authorized EOC & Disaster Rehabilitation Personnel Only
            </p>
          </div>

          {/* Quick Preset Selector for Demonstration */}
          <div className="mb-5">
            <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Select Official Role (Demo Profiles):
            </label>
            <div className="grid grid-cols-2 gap-2">
              {PRESET_USERS.map((preset) => {
                const isSelected = selectedUser.id === preset.id;
                return (
                  <button
                    key={preset.id}
                    type="button"
                    onClick={() => handleQuickSelect(preset)}
                    className={`p-2 rounded-lg text-left text-xs transition-all border ${
                      isSelected
                        ? 'bg-amber-500/15 border-amber-500 text-white shadow-xs'
                        : 'bg-slate-950/70 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-300'
                    }`}
                  >
                    <div className="font-semibold text-slate-200 truncate">{preset.name.split(',')[0]}</div>
                    <div className="text-[10px] text-amber-400/90 truncate">{preset.badge}</div>
                  </button>
                );
              })}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Designated Officer
              </label>
              <div className="relative">
                <input
                  type="text"
                  readOnly
                  value={selectedUser.name}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-200 font-mono focus:outline-none"
                />
                <ShieldCheck className="w-4 h-4 text-emerald-400 absolute right-3 top-2.5" />
              </div>
              <p className="text-[10px] text-slate-400 mt-1">{selectedUser.agency}</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Security Password / Token
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter authorized credential"
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-200 font-mono focus:border-amber-500 focus:outline-none"
                />
                <KeyRound className="w-4 h-4 text-slate-500 absolute right-3 top-2.5" />
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-400">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded text-amber-500 focus:ring-0"
                />
                <span>Persist EOC session</span>
              </label>
              <span className="text-emerald-400 font-mono text-[11px]">Clearance: {selectedUser.clearance}</span>
            </div>

            <button
              type="submit"
              className="w-full py-2.5 px-4 bg-linear-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold text-xs rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg shadow-amber-950/50 mt-2"
            >
              <span>Authenticate & Enter Crisis Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Security Notice */}
          <div className="mt-5 pt-4 border-t border-slate-800 text-[10px] text-slate-500 text-center leading-relaxed">
            <span className="text-amber-400 font-semibold">SECURITY NOTICE:</span> This portal interfaces with live satellite telemetry and PostGIS hazard red-zone systems. All queries are audited under NDMA guidelines.
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-6 py-3 border-t border-slate-800/80 bg-slate-900/40 text-center text-xs text-slate-500 z-10">
        SIH 2026 Problem Statement 26191 • Multi-Hazard Red Zones & Relocation Carrying Capacity Prototype
      </footer>
    </div>
  );
}
