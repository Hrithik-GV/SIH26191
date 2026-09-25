import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const DEFAULT_USER = {
  name: "Dr. A. K. Nambiar, IAS",
  designation: "District Collector & Chairman, DDMA Wayanad",
  role: "DISTRICT_COLLECTOR",
  clearance: "LEVEL_1_COMMAND",
  agency: "Kerala State Disaster Management Authority (KSDMA) / NDMA",
  station: "District Emergency Operations Centre (DEOC), Kalpetta",
  avatar: "AN",
};

export const PRESET_USERS = [
  {
    id: "collector",
    name: "Dr. A. K. Nambiar, IAS",
    designation: "District Collector & Chairman, DDMA",
    role: "DISTRICT_COLLECTOR",
    clearance: "LEVEL_1_COMMAND",
    agency: "District Emergency Operations Centre, Wayanad",
    station: "DEOC Kalpetta",
    badge: "Executive Chairman",
  },
  {
    id: "relief_comm",
    name: "Smt. Meera Varma, IAS",
    designation: "Principal Secretary & State Relief Commissioner",
    role: "RELIEF_COMMISSIONER",
    clearance: "LEVEL_1_COMMAND",
    agency: "Kerala State Disaster Management Authority (KSDMA)",
    station: "State EOC Thiruvananthapuram",
    badge: "State Command",
  },
  {
    id: "gis_analyst",
    name: "Dr. Rajesh K. Pillai",
    designation: "Chief Remote Sensing & GIS Scientist",
    role: "GIS_ANALYST",
    clearance: "LEVEL_2_ANALYST",
    agency: "GSI / ISRO Disaster Management Support Group",
    station: "Space Applications Centre & KSDMA GIS Cell",
    badge: "Spatial Specialist",
  },
  {
    id: "capacity_engineer",
    name: "Er. Joseph Mathew",
    designation: "Superintending Engineer (Civil & Resettlement Planning)",
    role: "CIVIL_ENGINEER",
    clearance: "LEVEL_2_ANALYST",
    agency: "Kerala Public Works & Water Resources Dept",
    station: "Wayanad Special Rehabilitation Project",
    badge: "Relocation Engineer",
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

  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem('sih26_authenticated') === 'true';
  });

  const login = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
    localStorage.setItem('sih26_auth_user', JSON.stringify(userData));
    localStorage.setItem('sih26_authenticated', 'true');
  };

  const logout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('sih26_authenticated');
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout, PRESET_USERS }}>
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
