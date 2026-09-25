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
  Cell,
} from 'recharts';

export default function RiskHistogramChart({ data = [] }) {
  const chartData = data.length > 0 ? data : [
    { bracket: "0-30 (LOW)", count: 4, population: 7500, vulnerable_population: 1100 },
    { bracket: "31-60 (MODERATE)", count: 7, population: 11200, vulnerable_population: 2510 },
    { bracket: "61-80 (HIGH)", count: 4, population: 4200, vulnerable_population: 2150 },
    { bracket: "81-100 (CRITICAL)", count: 3, population: 3900, vulnerable_population: 3690 },
  ];

  const colors = ['#0284c7', '#d97706', '#ea580c', '#dc2626'];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900 border border-slate-700 p-2.5 rounded-lg shadow-xl text-xs text-slate-200">
          <p className="font-bold text-amber-300 mb-1">{label}</p>
          <p className="text-slate-300">
            Habitations: <span className="font-mono font-bold text-white">{payload[0]?.value}</span>
          </p>
          <p className="text-slate-300">
            Vulnerable Population: <span className="font-mono font-bold text-rose-400">{payload[1]?.value?.toLocaleString()}</span>
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
            dataKey="bracket"
            stroke="#94a3b8"
            tick={{ fontSize: 11, fill: '#94a3b8' }}
          />
          <YAxis
            yAxisId="left"
            stroke="#94a3b8"
            tick={{ fontSize: 10, fill: '#94a3b8' }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="#f43f5e"
            tick={{ fontSize: 10, fill: '#f43f5e' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '11px', paddingTop: '4px' }}
            formatter={(value) => <span className="text-slate-300">{value}</span>}
          />
          <Bar yAxisId="left" dataKey="count" name="Settlements Count" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Bar>
          <Bar
            yAxisId="right"
            dataKey="vulnerable_population"
            name="Vulnerable Population"
            fill="#f43f5e"
            opacity={0.65}
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
