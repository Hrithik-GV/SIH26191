import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginOfficer, logoutOfficer, fetchCurrentProfile } from '../services/api';

const AuthContext = createContext();

export const DEFAULT_USER = {
  id: "usr-collector-02",
  username: "collector",
  name: "Dr. A. K. Nambiar, IAS",
  designation: "District Collector & Chairman, DDMA Wayanad",
  role: "AUTHORITY_VIEWER",
  clearance: "COMMAND_AUTHORITY",
  agency: "Kerala State Disaster Management Authority (KSDMA) / NDMA",
  station: "District Collectorate, Kalpetta",
  avatar: "AN",
};

export const PRESET_USERS = [
  {
    id: "admin",
    username: "admin",
    name: "Shri K. Harikumar",
    designation: "Executive Disaster Operations Administrator",
    role: "ADMIN",
    clearance: "LEVEL_1_ADMIN",
    agency: "District Emergency Operations Centre, Wayanad",
    station: "DEOC Kalpetta",
    badge: "Admin (Full Operations & Edits)",
    passwordHint: "GovAdmin@2026",
    description: "Can add/edit settlements, candidate relocation sites, view audit trail, and export reports.",
  },
  {
    id: "collector",
    username: "collector",
    name: "Dr. A. K. Nambiar, IAS",
    designation: "District Collector & Chairman, DDMA Wayanad",
    role: "AUTHORITY_VIEWER",
    clearance: "COMMAND_AUTHORITY",
    agency: "Kerala State Disaster Management Authority (KSDMA) / NDMA",
    station: "District Collectorate, Kalpetta",
    badge: "Authority Viewer (Decision Support)",
    passwordHint: "GovAdmin@2026",
    description: "Consumes decision-support telemetry, hazard layers, risk explanations, and exports reports.",
  },
  {
    id: "relief_commissioner",
    username: "relief_commissioner",
    name: "Smt. Meera Varma, IAS",
    designation: "Principal Secretary & State Relief Commissioner",
    role: "AUTHORITY_VIEWER",
    clearance: "STATE_COMMAND",
    agency: "Revenue & Disaster Management Dept, Govt of Kerala",
    station: "State EOC Thiruvananthapuram",
    badge: "State Authority (Decision Support)",
    passwordHint: "GovAdmin@2026",
    description: "State-level oversight of multi-hazard red zones, carrying capacity buffers, and evacuation readiness.",
  },
];

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('sih26_auth_user');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return DEFAULT_USER;
      }
    }
    return DEFAULT_USER;
  });

  const [token, setToken] = useState(() => {
    return localStorage.getItem('sih26_token') || null;
  });

  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem('sih26_authenticated') === 'true';
  });

  // Verify token on mount if present
  useEffect(() => {
    if (token) {
      fetchCurrentProfile()
        .then((profile) => {
          if (profile) {
            setUser(profile);
            localStorage.setItem('sih26_auth_user', JSON.stringify(profile));
          }
        })
        .catch(() => {
          // Token expired or invalid, keep existing offline/cached user
        });
    }
  }, [token]);

  const login = async (usernameOrPreset, password = 'GovAdmin@2026') => {
    const username = typeof usernameOrPreset === 'string'
      ? usernameOrPreset
      : usernameOrPreset?.username || usernameOrPreset?.id;

    try {
      const data = await loginOfficer(username, password);
      if (data?.user) {
        setUser(data.user);
        setToken(data.access_token);
        setIsAuthenticated(true);
        return { success: true, user: data.user };
      }
    } catch (err) {
      console.warn('[Auth Login Fallback]', err?.message);
      // Offline fallback: find matching preset
      const matched = PRESET_USERS.find(
        (p) => p.username === username || p.id === username
      ) || DEFAULT_USER;
      setUser(matched);
      setIsAuthenticated(true);
      localStorage.setItem('sih26_auth_user', JSON.stringify(matched));
      localStorage.setItem('sih26_authenticated', 'true');
      return { success: true, user: matched, offline: true };
    }
  };

  const logout = () => {
    logoutOfficer();
    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
  };

  const isAdmin = user?.role === 'ADMIN';
  const isAuthorityViewer = user?.role === 'AUTHORITY_VIEWER';
  const canEditData = isAdmin; // Authority users primarily consume decision support info

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated,
        isAdmin,
        isAuthorityViewer,
        canEditData,
        login,
        logout,
        PRESET_USERS,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
