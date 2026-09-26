import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import LoginPage from './pages/LoginPage';
import MainDashboard from './pages/MainDashboard';
import RiskMapPage from './pages/RiskMapPage';
import HabitationListPage from './pages/HabitationListPage';
import HabitationDetailPage from './pages/HabitationDetailPage';
import RelocationSitesPage from './pages/RelocationSitesPage';
import RelocationRecommendationsPage from './pages/RelocationRecommendationsPage';
import AlertsPage from './pages/AlertsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import DataSourcesPage from './pages/DataSourcesPage';
import AdminConsolePage from './pages/AdminConsolePage';
import { checkSystemHealth, getAlerts } from './services/api';


function AppContent() {
  const { isAuthenticated } = useAuth();
  const [activeView, setActiveView] = useState('dashboard');
  const [selectedHabitationId, setSelectedHabitationId] = useState(null);
  const [selectedRelocationSiteId, setSelectedRelocationSiteId] = useState(null);
  const [isBackendLive, setIsBackendLive] = useState(false);
  const [activeAlertsCount, setActiveAlertsCount] = useState(4);

  // Monitor backend health
  useEffect(() => {
    async function checkHealth() {
      const res = await checkSystemHealth();
      setIsBackendLive(res.success && res.data?.status === 'healthy');
    }
    checkHealth();
    const interval = setInterval(checkHealth, 20000);
    return () => clearInterval(interval);
  }, []);

  // Fetch active alerts count
  useEffect(() => {
    async function loadAlertsCount() {
      try {
        const res = await getAlerts({ page_size: 10 });
        setActiveAlertsCount(res.data.items?.length || 4);
      } catch (e) {
        setActiveAlertsCount(4);
      }
    }
    loadAlertsCount();
  }, []);

  // If user is not authenticated, render Login Page
  if (!isAuthenticated) {
    return <LoginPage onLoginSuccess={() => setActiveView('dashboard')} />;
  }

  // Navigation handlers
  const handleSelectHabitation = (id) => {
    setSelectedHabitationId(id);
    setActiveView('habitation-detail');
  };

  const handleSelectRelocationSite = (id) => {
    setSelectedRelocationSiteId(id);
    setActiveView('relocation-sites');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-amber-500 selection:text-slate-950">
      {/* Top Government Navigation Bar */}
      <Navbar
        activeView={activeView}
        setActiveView={(view) => {
          setActiveView(view);
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }}
        isBackendLive={isBackendLive}
        activeAlertsCount={activeAlertsCount}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-3 sm:px-6 lg:px-8 py-5">
        {activeView === 'dashboard' && (
          <MainDashboard
            onNavigate={(view) => setActiveView(view)}
            onSelectHabitation={handleSelectHabitation}
            onSelectRelocationSite={handleSelectRelocationSite}
          />
        )}

        {activeView === 'risk-map' && (
          <RiskMapPage
            onSelectHabitation={handleSelectHabitation}
            onSelectRelocationSite={handleSelectRelocationSite}
          />
        )}

        {activeView === 'habitations' && (
          <HabitationListPage
            onSelectHabitation={handleSelectHabitation}
          />
        )}

        {activeView === 'habitation-detail' && (
          <HabitationDetailPage
            habitationId={selectedHabitationId || "11111111-1111-4111-8111-111111111111"}
            onBack={() => setActiveView('habitations')}
            onSelectRelocationSite={handleSelectRelocationSite}
          />
        )}

        {activeView === 'relocation-sites' && (
          <RelocationSitesPage
            onSelectSite={handleSelectRelocationSite}
          />
        )}

        {activeView === 'relocation-recommendations' && (
          <RelocationRecommendationsPage
            onSelectHabitation={handleSelectHabitation}
            onSelectRelocationSite={handleSelectRelocationSite}
          />
        )}

        {activeView === 'alerts' && <AlertsPage />}

        {activeView === 'analytics' && <AnalyticsPage />}

        {activeView === 'data-sources' && <DataSourcesPage />}

        {activeView === 'admin-console' && <AdminConsolePage />}
      </main>


      {/* Official Government Footer */}
      <footer className="bg-slate-900/80 border-t border-slate-800/80 py-4 px-4 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-400">SIH 2026 Problem Statement 26191</span>
            <span>•</span>
            <span>Government Disaster Management Decision-Support Portal</span>
          </div>

          <div className="font-mono text-[11px] text-slate-400 flex items-center gap-4">
            <span>React 19 • Vite • MapLibre GL • Recharts • PostGIS</span>
            <span className="text-emerald-400">All Systems Operational</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
