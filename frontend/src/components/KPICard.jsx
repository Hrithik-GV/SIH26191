import React from 'react';
import { ArrowUpRight, ArrowDownRight, ShieldAlert, Users, Truck, Building2 } from 'lucide-react';

export default function KPICard({
  title,
  value,
  subvalue,
  icon: Icon,
  colorScheme = 'amber', // 'rose', 'amber', 'emerald', 'sky'
  trend,
  trendDirection = 'neutral',
  onClick,
  badge,
}) {
  const schemeStyles = {
    rose: {
      border: 'border-rose-500/30 hover:border-rose-500/60',
      bg: 'bg-linear-to-b from-rose-950/20 to-slate-900',
      iconBg: 'bg-rose-500/20 text-rose-400 border border-rose-500/30',
      valueColor: 'text-rose-400',
      badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
      accentGlow: 'shadow-rose-950/20',
    },
    amber: {
      border: 'border-amber-500/30 hover:border-amber-500/60',
      bg: 'bg-linear-to-b from-amber-950/20 to-slate-900',
      iconBg: 'bg-amber-500/20 text-amber-400 border border-amber-500/30',
      valueColor: 'text-amber-400',
      badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
      accentGlow: 'shadow-amber-950/20',
    },
    emerald: {
      border: 'border-emerald-500/30 hover:border-emerald-500/60',
      bg: 'bg-linear-to-b from-emerald-950/20 to-slate-900',
      iconBg: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
      valueColor: 'text-emerald-400',
      badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
      accentGlow: 'shadow-emerald-950/20',
    },
    sky: {
      border: 'border-sky-500/30 hover:border-sky-500/60',
      bg: 'bg-linear-to-b from-sky-950/20 to-slate-900',
      iconBg: 'bg-sky-500/20 text-sky-400 border border-sky-500/30',
      valueColor: 'text-sky-400',
      badgeColor: 'bg-sky-500/20 text-sky-300 border-sky-500/30',
      accentGlow: 'shadow-sky-950/20',
    },
  };

  const currentScheme = schemeStyles[colorScheme] || schemeStyles.amber;

  return (
    <div
      onClick={onClick}
      className={`relative p-4 rounded-xl border ${currentScheme.border} ${currentScheme.bg} shadow-lg ${currentScheme.accentGlow} transition-all duration-200 cursor-pointer select-none group`}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              {title}
            </span>
            {badge && (
              <span
                className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${currentScheme.badgeColor}`}
              >
                {badge}
              </span>
            )}
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className={`text-3xl font-black font-mono tracking-tight ${currentScheme.valueColor}`}>
              {typeof value === 'number' ? value.toLocaleString() : value}
            </span>
            {subvalue && (
              <span className="text-xs text-slate-400 font-medium">
                {subvalue}
              </span>
            )}
          </div>
        </div>

        {Icon && (
          <div
            className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${currentScheme.iconBg} transition-transform group-hover:scale-105`}
          >
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      {trend && (
        <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-1 font-mono">
            {trendDirection === 'up' && <ArrowUpRight className="w-3.5 h-3.5 text-rose-400" />}
            {trendDirection === 'down' && <ArrowDownRight className="w-3.5 h-3.5 text-emerald-400" />}
            <span className="text-[11px]">{trend}</span>
          </div>
          <span className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">
            Real-time
          </span>
        </div>
      )}
    </div>
  );
}
