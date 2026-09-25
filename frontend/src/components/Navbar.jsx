import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Map,
  Users,
  Compass,
  AlertTriangle,
  BarChart3,
  Database,
  Radio,
  Clock,
  LogOut,
  ChevronDown,
  Activity,
  Layers,
  Building2,
  FileCheck2,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ activeView, setActiveView, isBackendLive, activeAlertsCount = 0 }) {
  const { user, logout } = useAuth();
  const [timeUTC, setTimeUTC] = useState('');
  const [timeIST, setTimeIST] = useState('');
  const [userDropdown, setUserDropdown] = useState(false);

  useEffect(() => {
    const updateClocks = () => {
      const now = new Date();
      setTimeUTC(now.toUTCString().slice(17, 25) + ' UTC');
      setTimeIST(
        now.toLocaleTimeString('en-IN', {
          timeZone: 'Asia/Kolkata',
          hour12: false,
        }) + ' IST'
      );
    };
    updateClocks();
    const interval = setInterval(updateClocks, 1000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'risk-map', label: 'Risk Map', icon: Map },
    { id: 'habitations', label: 'Habitations', icon: Users },
    { id: 'relocation-sites', label: 'Relocation Sites', icon: Building2 },
    { id: 'relocation-recommendations', label: 'Prioritization', icon: FileCheck2 },
    { id: 'alerts', label: 'Alerts', icon: AlertTriangle, badge: activeAlertsCount },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'data-sources', label: 'Telemetry Feeds', icon: Database },
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50 text-slate-100 shadow-md">
      {/* Top Government Emblazon / Alert Status Bar */}
      <div className="bg-slate-950/80 px-4 py-1.5 border-b border-slate-800/80 text-xs flex flex-wrap items-center justify-between gap-3 text-slate-400">
        <div className="flex items-center gap-3">
          <span className="font-semibold tracking-wider text-slate-300 uppercase flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            NATIONAL DISASTER MANAGEMENT AUTHORITY (NDMA) • KSDMA
          </span>
          <span className="hidden md:inline text-slate-600">|</span>
          <span className="hidden md:inline text-slate-400">
            Problem Statement 26191: Hazard-Based Red Zones & Relocation Assessment
          </span>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-1 text-slate-300">
            <Clock className="w-3.5 h-3.5 text-sky-400" />
            <span>{timeIST}</span>
            <span className="text-slate-600">({timeUTC})</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                isBackendLive ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
              }`}
            ></span>
            <span className={isBackendLive ? 'text-emerald-400 font-medium' : 'text-amber-400'}>
              {isBackendLive ? 'FastAPI Connected' : 'Demo Proxy Mode'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14 gap-2">
          {/* Brand & Project Logo */}
          <div
            onClick={() => setActiveView('dashboard')}
            className="flex items-center gap-2.5 cursor-pointer group shrink-0"
          >
            <div className="w-9 h-9 rounded bg-linear-to-br from-amber-500 to-rose-600 text-white flex items-center justify-center font-bold shadow-md shadow-amber-900/30">
              <ShieldAlert className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-base font-bold tracking-tight text-white group-hover:text-amber-400 transition-colors">
                  RELO-RISK 26191
                </span>
                <span className="text-[10px] font-semibold tracking-wider bg-rose-500/20 text-rose-300 px-1.5 py-0.5 rounded border border-rose-500/30 uppercase">
                  CRISIS EOC
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden xl:block -mt-0.5">
                Intelligent Hazard Red Zones & Carrying Capacity System
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1 overflow-x-auto py-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveView(item.id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30 shadow-xs'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/80 border border-transparent'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-amber-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                  {item.badge !== undefined && item.badge > 0 && (
                    <span className="ml-1 bg-rose-600 text-white text-[10px] px-1.5 py-0.2 rounded-full font-bold">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* User Profile & Actions */}
          <div className="flex items-center gap-3 relative">
            <div
              onClick={() => setUserDropdown(!userDropdown)}
              className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-800/70 border border-slate-700/60 cursor-pointer hover:border-slate-600 transition-colors"
            >
              <div className="w-7 h-7 rounded-full bg-slate-700 border border-slate-600 flex items-center justify-center text-xs font-bold text-amber-300">
                {user?.avatar || 'AK'}
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-xs font-semibold text-slate-200 leading-tight">{user?.name}</p>
                <p className="text-[10px] text-slate-400 truncate max-w-[140px]">{user?.designation}</p>
              </div>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </div>

            {/* Dropdown Menu */}
            {userDropdown && (
              <div className="absolute right-0 top-12 w-64 bg-slate-900 border border-slate-700 rounded-lg shadow-xl py-2 z-50 text-xs">
                <div className="px-3 py-2 border-b border-slate-800">
                  <p className="font-semibold text-slate-200">{user?.name}</p>
                  <p className="text-[11px] text-slate-400">{user?.agency}</p>
                  <div className="mt-1.5 inline-block px-1.5 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/50 text-[10px] font-mono">
                    Clearance: {user?.clearance}
                  </div>
                </div>

                <div className="py-1">
                  <button
                    onClick={() => {
                      setUserDropdown(false);
                      setActiveView('data-sources');
                    }}
                    className="w-full text-left px-3 py-1.5 text-slate-300 hover:bg-slate-800 hover:text-white flex items-center gap-2"
                  >
                    <Radio className="w-3.5 h-3.5 text-sky-400" />
                    Telemetry Feeds Status
                  </button>
                  <button
                    onClick={() => {
                      setUserDropdown(false);
                      logout();
                    }}
                    className="w-full text-left px-3 py-1.5 text-rose-400 hover:bg-rose-950/40 flex items-center gap-2"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    Secure Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Navigation Strip */}
      <div className="lg:hidden border-t border-slate-800 bg-slate-900/90 overflow-x-auto px-2 py-1.5 flex gap-1.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`shrink-0 flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium ${
                isActive
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{item.label}</span>
              {item.badge !== undefined && item.badge > 0 && (
                <span className="bg-rose-600 text-white text-[9px] px-1 rounded-full font-bold">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </header>
  );
}
