"use client";

import { OverspendingItem } from "@/lib/api";

interface Props {
  data: OverspendingItem[];
  loading?: boolean;
}

const fmt = (v: number) =>
  new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(v);

function getStatusBadge(usage: number) {
  if (usage >= 150)
    return (
      <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/30">
        ⚠ Nguy hiểm
      </span>
    );
  if (usage >= 120)
    return (
      <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">
        ⚡ Cao
      </span>
    );
  return (
    <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">
      ↑ Vượt
    </span>
  );
}

export default function OverspendingTable({ data, loading }: Props) {
  if (loading) {
    return (
      <div className="h-48 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-rose-500 border-t-transparent" />
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="h-48 flex flex-col items-center justify-center gap-3 text-slate-400">
        <svg className="w-12 h-12 text-emerald-500/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-sm">Không có khoản vượt kế hoạch</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700/50">
            <th className="text-left py-3 px-4 text-slate-400 font-semibold text-xs uppercase tracking-wider">
              Phòng ban
            </th>
            <th className="text-center py-3 px-3 text-slate-400 font-semibold text-xs uppercase tracking-wider">
              Tháng
            </th>
            <th className="text-center py-3 px-3 text-slate-400 font-semibold text-xs uppercase tracking-wider">
              Quý
            </th>
            <th className="text-right py-3 px-4 text-slate-400 font-semibold text-xs uppercase tracking-wider">
              Kế hoạch
            </th>
            <th className="text-right py-3 px-4 text-slate-400 font-semibold text-xs uppercase tracking-wider">
              Thực chi
            </th>
            <th className="text-right py-3 px-4 text-slate-400 font-semibold text-xs uppercase tracking-wider">
              Vượt
            </th>
            <th className="text-center py-3 px-4 text-slate-400 font-semibold text-xs uppercase tracking-wider">
              Trạng thái
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/50">
          {data.map((item) => {
            const overAmt = Math.abs(item.variance_amount);
            const usageRate = item.usage_rate || (item.planned_amount > 0 ? (item.actual_amount / item.planned_amount) * 100 : 0);
            return (
              <tr
                key={item.id}
                className="hover:bg-slate-800/30 transition-colors duration-150 group"
              >
                <td className="py-3 px-4 font-medium text-slate-200 max-w-[180px] truncate">
                  {item.department_name}
                </td>
                <td className="py-3 px-3 text-center text-slate-400">T{item.plan_month}</td>
                <td className="py-3 px-3 text-center text-slate-400">Q{item.quarter}</td>
                <td className="py-3 px-4 text-right text-slate-300 font-mono text-xs">
                  {fmt(item.planned_amount)}
                </td>
                <td className="py-3 px-4 text-right text-rose-400 font-mono text-xs font-semibold">
                  {fmt(item.actual_amount)}
                </td>
                <td className="py-3 px-4 text-right font-mono text-xs">
                  <span className="text-rose-500 font-bold">+{fmt(overAmt)}</span>
                </td>
                <td className="py-3 px-4 text-center">{getStatusBadge(usageRate)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
