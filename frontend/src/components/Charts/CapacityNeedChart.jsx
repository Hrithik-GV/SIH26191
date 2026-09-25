import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

export default function CapacityNeedChart({ data = [] }) {
  const chartData = data.length > 0 ? data : [
    {
      site_name: "Meppadi Safe Plateau",
      available_capacity: 2800,
      matched_demand_population: 2570,
      balance: 230,
    },
    {
      site_name: "Kalpetta South Ridge",
      available_capacity: 2150,
      matched_demand_population: 890,
      balance: 1260,
    },
    {
      site_name: "Muttil North Terrace",
      available_capacity: 1000,
      matched_demand_population: 1530,
      balance: -530,
    },
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const avail = payload.find((p) => p.dataKey === 'available_capacity')?.value || 0;
      const demand = payload.find((p) => p.dataKey === 'matched_demand_population')?.value || 0;
      const diff = avail - demand;
      return (
        <div className="bg-slate-900 border border-slate-700 p-2.5 rounded-lg shadow-xl text-xs text-slate-200">
          <p className="font-bold text-emerald-400 mb-1">{label}</p>
          <p className="text-slate-300">
            Available Capacity: <span className="font-mono font-bold text-emerald-400">{avail.toLocaleString()}</span>
          </p>
          <p className="text-slate-300">
            Displaced Demand: <span className="font-mono font-bold text-amber-400">{demand.toLocaleString()}</span>
          </p>
          <p className="text-slate-300 pt-1 border-t border-slate-800 mt-1">
            Status:{' '}
            <span
              className={`font-mono font-bold ${
                diff >= 0 ? 'text-emerald-400' : 'text-rose-400'
              }`}
            >
              {diff >= 0 ? `+${diff.toLocaleString()} SURPLUS` : `${diff.toLocaleString()} DEFICIT`}
            </span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-full min-h-[220px]">
      <ResponsiveContainer width="100%" height={220}>
        <BarChart
          data={chartData}
          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
          <XAxis
            dataKey="site_name"
            stroke="#94a3b8"
            tick={{ fontSize: 10, fill: '#94a3b8' }}
            interval={0}
          />
          <YAxis stroke="#94a3b8" tick={{ fontSize: 10, fill: '#94a3b8' }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '11px', paddingTop: '4px' }}
            formatter={(value) => <span className="text-slate-300">{value}</span>}
          />
          <Bar
            dataKey="available_capacity"
            name="Available Safe Capacity"
            fill="#10b981"
            radius={[4, 4, 0, 0]}
          />
          <Bar
            dataKey="matched_demand_population"
            name="Displaced Population Demand"
            fill="#f59e0b"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
