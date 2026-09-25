import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  Filter,
  ArrowUpDown,
  Home,
  ShieldAlert,
  ArrowRight,
  MapPin,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { getHabitations } from '../services/api';

export default function HabitationListPage({ onSelectHabitation }) {
  const [habitations, setHabitations] = useState([]);
  const [search, setSearch] = useState('');
  const [filterPriority, setFilterPriority] = useState('ALL');
  const [sortBy, setSortBy] = useState('risk_score');
  const [order, setOrder] = useState('desc');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    async function fetchHabitations() {
      const res = await getHabitations({
        page,
        page_size: 20,
        search,
        sort_by: sortBy,
        order,
      });
      setHabitations(res.data.items || []);
      setTotal(res.data.total || 0);
    }
    fetchHabitations();
  }, [page, search, sortBy, order]);

  const filteredItems = habitations.filter((h) => {
    if (filterPriority === 'ALL') return true;
    return h.priority === filterPriority;
  });

  return (
    <div className="space-y-4">
      {/* Header and Filter Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm text-xs">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center">
              <Users className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white tracking-tight">
                Vulnerable Habitations & Settlements Directory
              </h2>
              <p className="text-[11px] text-slate-400">
                Monitored human settlements with 9-factor socio-demographic vulnerability profiles
              </p>
            </div>
          </div>

          <div className="text-right">
            <span className="text-xs text-slate-400">Total Registered Habitations:</span>{' '}
            <strong className="text-amber-400 font-mono text-sm">{total}</strong>
          </div>
        </div>

        {/* Filter Strip */}
        <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
          <div className="relative">
            <input
              type="text"
              placeholder="Search settlement name..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500"
            />
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
          </div>

          <div>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500 font-mono"
            >
              <option value="ALL">All Urgency Tiers</option>
              <option value="IMMEDIATE">IMMEDIATE Urgency (81-100)</option>
              <option value="SHORT_TERM">SHORT_TERM Urgency (61-80)</option>
              <option value="MEDIUM_TERM">MEDIUM_TERM Urgency (31-60)</option>
              <option value="MONITOR">MONITOR (0-30)</option>
            </select>
          </div>

          <div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500 font-mono"
            >
              <option value="risk_score">Sort: Hazard Risk Score</option>
              <option value="vulnerability_score">Sort: Vulnerability Score</option>
              <option value="vulnerable_population">Sort: Vulnerable Population</option>
              <option value="population">Sort: Total Population</option>
              <option value="name">Sort: Settlement Name</option>
            </select>
          </div>

          <div>
            <button
              onClick={() => setOrder(order === 'desc' ? 'asc' : 'desc')}
              className="w-full bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-lg px-3 py-1.5 text-xs font-mono flex items-center justify-center gap-1.5 transition-colors"
            >
              <ArrowUpDown className="w-3.5 h-3.5 text-amber-400" />
              <span>Order: {order.toUpperCase()}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Settlements Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] font-mono border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Settlement & Location</th>
                <th className="py-3 px-3">Hazard Risk</th>
                <th className="py-3 px-3">Vulnerability</th>
                <th className="py-3 px-3">Population</th>
                <th className="py-3 px-3">Vulnerable Lives</th>
                <th className="py-3 px-3">Urgency Action</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {filteredItems.map((hab) => {
                const isImmediate = hab.priority === 'IMMEDIATE' || (hab.risk_score || 0) >= 81;
                const isHigh = hab.priority === 'SHORT_TERM' || ((hab.risk_score || 0) >= 61 && (hab.risk_score || 0) <= 80);

                return (
                  <tr
                    key={hab.id}
                    onClick={() => onSelectHabitation(hab.id)}
                    className="hover:bg-slate-800/50 cursor-pointer transition-colors group"
                  >
                    <td className="py-3 px-4">
                      <div className="font-bold text-slate-100 group-hover:text-amber-400 transition-colors">
                        {hab.name}
                      </div>
                      <div className="text-[11px] text-slate-500 font-mono">
                        {hab.taluk || 'Vythiri'}, {hab.district || 'Wayanad'}
                      </div>
                    </td>

                    <td className="py-3 px-3 font-mono">
                      <span
                        className={`inline-block px-2 py-0.5 rounded font-bold text-[11px] ${
                          (hab.risk_score || 80) >= 80
                            ? 'bg-rose-950/60 text-rose-400 border border-rose-800'
                            : 'bg-amber-950/60 text-amber-400 border border-amber-800'
                        }`}
                      >
                        {hab.risk_score || hab.overall_score || 85}/100
                      </span>
                    </td>

                    <td className="py-3 px-3 font-mono">
                      <span className="inline-block px-2 py-0.5 rounded bg-slate-950 text-slate-300 border border-slate-700 font-bold text-[11px]">
                        {hab.vulnerability_score || 78}/100
                      </span>
                    </td>

                    <td className="py-3 px-3 font-mono text-slate-300">
                      {(hab.population || 2180).toLocaleString()}
                    </td>

                    <td className="py-3 px-3 font-mono font-bold text-rose-400">
                      {(hab.vulnerable_population || 1450).toLocaleString()}
                    </td>

                    <td className="py-3 px-3">
                      <span
                        className={`inline-block px-2 py-0.5 rounded font-mono font-bold text-[10px] border ${
                          isImmediate
                            ? 'bg-rose-950 text-rose-300 border-rose-700'
                            : isHigh
                            ? 'bg-amber-950 text-amber-300 border-amber-700'
                            : 'bg-sky-950 text-sky-300 border-sky-700'
                        }`}
                      >
                        {hab.priority || 'IMMEDIATE'}
                      </span>
                    </td>

                    <td className="py-3 px-4 text-right">
                      <button className="text-slate-400 group-hover:text-amber-400 p-1.5 rounded-lg group-hover:bg-slate-700 transition-colors">
                        <ArrowRight className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="bg-slate-950 px-4 py-2.5 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>Showing {filteredItems.length} settlements</span>
          <div className="flex items-center gap-2">
            <button
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
              className="p-1.5 rounded bg-slate-900 border border-slate-800 disabled:opacity-40 hover:bg-slate-800 text-slate-300"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-slate-200">Page {page}</span>
            <button
              disabled={filteredItems.length < 20}
              onClick={() => setPage(page + 1)}
              className="p-1.5 rounded bg-slate-900 border border-slate-800 disabled:opacity-40 hover:bg-slate-800 text-slate-300"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
