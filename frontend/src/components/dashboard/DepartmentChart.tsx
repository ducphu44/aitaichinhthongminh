"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { DepartmentItem } from "@/lib/api";

interface Props {
  data: DepartmentItem[];
  loading?: boolean;
}

const COLORS = [
  "#6366f1",
  "#8b5cf6",
  "#a855f7",
  "#ec4899",
  "#f43f5e",
  "#f97316",
  "#eab308",
  "#22c55e",
];

function formatYAxis(value: number): string {
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(0)}tỷ`;
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(0)}tr`;
  return value.toString();
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ name: string; value: number; fill?: string; color?: string }>;
  label?: string;
}

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    const fmt = (v: number) =>
      new Intl.NumberFormat("vi-VN", {
        style: "currency",
        currency: "VND",
        maximumFractionDigits: 0,
      }).format(v);
    return (
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-3 shadow-2xl text-sm max-w-xs">
        <p className="text-slate-200 font-semibold mb-2 truncate">{label}</p>
        {payload.map((entry) => (
          <p key={entry.name} style={{ color: entry.fill || entry.color }} className="font-medium">
            {entry.name === "actual" ? "Thực chi" : "Kế hoạch"}: {fmt(entry.value)}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function DepartmentChart({ data, loading }: Props) {
  if (loading) {
    return (
      <div className="h-80 flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-2 border-violet-500 border-t-transparent" />
      </div>
    );
  }

  const filtered = data.filter((d) => d.actual > 0 || d.planned > 0);

  if (filtered.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center text-slate-400 text-sm">
        Chưa có dữ liệu theo phòng ban
      </div>
    );
  }

  // Truncate long department names
  const chartData = filtered.map((d) => ({
    ...d,
    name: d.department_name.length > 20 ? d.department_name.substring(0, 18) + "…" : d.department_name,
  }));

  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart
        layout="vertical"
        data={chartData}
        margin={{ top: 5, right: 30, left: 10, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
        <XAxis
          type="number"
          tickFormatter={formatYAxis}
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="name"
          tick={{ fill: "#cbd5e1", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          width={120}
        />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
        <Bar dataKey="actual" name="actual" radius={[0, 6, 6, 0]} maxBarSize={24}>
          {chartData.map((_, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
