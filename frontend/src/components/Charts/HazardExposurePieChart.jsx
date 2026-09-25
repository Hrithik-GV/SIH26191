import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

export default function HazardExposurePieChart({ data = [] }) {
  const chartData = data.length > 0 ? data : [
    { hazard_type: "Landslide", affected_population: 9800 },
    { hazard_type: "Flash Flood", affected_population: 7400 },
    { hazard_type: "Cloudburst", affected_population: 5200 },
    { hazard_type: "Debris Flow", affected_population: 3900 },
  ];

  const colors = ['#dc2626', '#0284c7', '#7c3aed', '#ea580c'];

  return (
    <div className="w-full h-full min-h-[220px]">
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={45}
            outerRadius={75}
            paddingAngle={4}
            dataKey="affected_population"
            nameKey="hazard_type"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} stroke="#0f172a" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '11px' }}
            formatter={(value) => [`${value?.toLocaleString()} lives`, 'Exposed Population']}
          />
          <Legend
            wrapperStyle={{ fontSize: '10px' }}
            formatter={(value) => <span className="text-slate-300 capitalize">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
