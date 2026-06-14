"use client";

import { formatVNDCompact } from "@/lib/api";

interface SummaryCardProps {
  title: string;
  value: number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: "up" | "down" | "neutral";
  color: "blue" | "green" | "red" | "purple" | "orange";
  isPercentage?: boolean;
  isCount?: boolean;
}

const colorMap = {
  blue: {
    bg: "from-blue-600 to-blue-700",
    icon: "bg-blue-500/30",
    badge: "bg-blue-500/20 text-blue-200",
    glow: "shadow-blue-500/25",
  },
  green: {
    bg: "from-emerald-600 to-emerald-700",
    icon: "bg-emerald-500/30",
    badge: "bg-emerald-500/20 text-emerald-200",
    glow: "shadow-emerald-500/25",
  },
  red: {
    bg: "from-rose-600 to-rose-700",
    icon: "bg-rose-500/30",
    badge: "bg-rose-500/20 text-rose-200",
    glow: "shadow-rose-500/25",
  },
  purple: {
    bg: "from-violet-600 to-violet-700",
    icon: "bg-violet-500/30",
    badge: "bg-violet-500/20 text-violet-200",
    glow: "shadow-violet-500/25",
  },
  orange: {
    bg: "from-amber-500 to-orange-600",
    icon: "bg-amber-500/30",
    badge: "bg-amber-500/20 text-amber-200",
    glow: "shadow-amber-500/25",
  },
};

export default function SummaryCard({
  title,
  value,
  subtitle,
  icon,
  color,
  isPercentage = false,
  isCount = false,
}: SummaryCardProps) {
  const colors = colorMap[color];

  const displayValue = isPercentage
    ? `${value.toFixed(1)}%`
    : isCount
    ? value.toLocaleString("vi-VN")
    : formatVNDCompact(value);

  const fullValue = isPercentage
    ? `${value.toFixed(2)}%`
    : isCount
    ? value.toString()
    : new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND", maximumFractionDigits: 0 }).format(value);

  return (
    <div
      className={`relative rounded-2xl bg-gradient-to-br ${colors.bg} p-6 text-white shadow-xl ${colors.glow} overflow-hidden group hover:scale-[1.02] transition-transform duration-300`}
    >
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-32 h-32 rounded-full bg-white/5 -translate-y-8 translate-x-8" />
      <div className="absolute bottom-0 left-0 w-24 h-24 rounded-full bg-white/5 translate-y-8 -translate-x-8" />

      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 rounded-xl ${colors.icon}`}>{icon}</div>
        </div>

        <div className="space-y-1">
          <p className="text-white/70 text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold tracking-tight" title={fullValue}>
            {displayValue}
          </p>
          {subtitle && (
            <p className="text-white/60 text-xs mt-2">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  );
}
