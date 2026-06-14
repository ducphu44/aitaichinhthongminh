"use client";

import { useState, useEffect, useCallback } from "react";
import SummaryCard from "@/components/dashboard/SummaryCard";
import BudgetVsActualChart from "@/components/dashboard/BudgetVsActualChart";
import DepartmentChart from "@/components/dashboard/DepartmentChart";
import OverspendingTable from "@/components/dashboard/OverspendingTable";
import DashboardFilters from "@/components/dashboard/DashboardFilters";
import {
  fetchSummary,
  fetchMonthlyTrend,
  fetchByDepartment,
  fetchOverspending,
  fetchDepartments,
  DashboardSummary,
  MonthlyTrendItem,
  DepartmentItem,
  OverspendingItem,
  DepartmentOption,
} from "@/lib/api";

// ─── Icons ───────────────────────────────────────────────────────────────────
const WalletIcon = () => (
  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
  </svg>
);
const TrendIcon = () => (
  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
  </svg>
);
const PiggyIcon = () => (
  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);
const GaugeIcon = () => (
  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
);

// ─── Skeleton ─────────────────────────────────────────────────────────────────
function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-slate-700/50 rounded-xl ${className}`} />;
}

// ─── Chart card wrapper ───────────────────────────────────────────────────────
function ChartCard({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <div className="bg-slate-800/60 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 shadow-xl">
      <div className="mb-6">
        <h3 className="text-slate-100 font-semibold text-base">{title}</h3>
        {subtitle && <p className="text-slate-400 text-xs mt-1">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────
interface FilterState {
  year: number;
  quarter: number | null;
  department_id: number | null;
}

export default function DashboardPage() {
  const currentYear = new Date().getFullYear();

  const [filters, setFilters] = useState<FilterState>({
    year: currentYear,
    quarter: null,
    department_id: null,
  });

  const [departments, setDepartments] = useState<DepartmentOption[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trend, setTrend] = useState<MonthlyTrendItem[]>([]);
  const [deptData, setDeptData] = useState<DepartmentItem[]>([]);
  const [overspending, setOverspending] = useState<OverspendingItem[]>([]);

  const [loadingSummary, setLoadingSummary] = useState(true);
  const [loadingTrend, setLoadingTrend] = useState(true);
  const [loadingDept, setLoadingDept] = useState(true);
  const [loadingOver, setLoadingOver] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const filterParams = {
    year: filters.year,
    ...(filters.quarter ? { quarter: filters.quarter } : {}),
    ...(filters.department_id ? { department_id: filters.department_id } : {}),
  };

  const loadAll = useCallback(async () => {
    setLoadingSummary(true);
    setLoadingTrend(true);
    setLoadingDept(true);
    setLoadingOver(true);

    try {
      const [s, t, d, o] = await Promise.all([
        fetchSummary(filterParams),
        fetchMonthlyTrend(filterParams),
        fetchByDepartment(filterParams),
        fetchOverspending(filterParams),
      ]);
      setSummary(s);
      setTrend(t);
      setDeptData(d);
      setOverspending(o);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setLoadingSummary(false);
      setLoadingTrend(false);
      setLoadingDept(false);
      setLoadingOver(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  // Load departments once
  useEffect(() => {
    fetchDepartments().then(setDepartments).catch(console.error);
  }, []);

  // Reload when filters change
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadAll();
  }, [loadAll]);

  const usageColor =
    (summary?.usage_rate ?? 0) >= 100
      ? "red"
      : (summary?.usage_rate ?? 0) >= 80
      ? "orange"
      : "green";

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6 space-y-6">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            📊 Dashboard Tài Chính
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Tổng quan ngân sách và chi tiêu tài chính
            {lastUpdated && (
              <span className="ml-2 text-slate-500">
                · Cập nhật lúc {lastUpdated.toLocaleTimeString("vi-VN")}
              </span>
            )}
          </p>
        </div>
        <button
          id="btn-refresh"
          onClick={loadAll}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-medium transition-all duration-200 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30 self-start sm:self-auto"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Làm mới
        </button>
      </div>

      {/* ── Filters ── */}
      <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/40 rounded-2xl px-5 py-4">
        <DashboardFilters
          filters={filters}
          departments={departments}
          onFiltersChange={setFilters}
        />
      </div>

      {/* ── KPI Cards ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {loadingSummary ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-36" />
          ))
        ) : (
          <>
            <SummaryCard
              title="Tổng dự toán ngân sách"
              value={summary?.total_budget ?? 0}
              subtitle="Dự toán năm tài chính"
              icon={<WalletIcon />}
              color="blue"
            />
            <SummaryCard
              title="Tổng thực chi"
              value={summary?.total_actual ?? 0}
              subtitle={`${summary?.overspending_count ?? 0} khoản vượt kế hoạch`}
              icon={<TrendIcon />}
              color="purple"
            />
            <SummaryCard
              title="Ngân sách còn lại"
              value={summary?.remaining_budget ?? 0}
              subtitle="Chưa sử dụng"
              icon={<PiggyIcon />}
              color={(summary?.remaining_budget ?? 0) >= 0 ? "green" : "red"}
            />
            <SummaryCard
              title="Tỷ lệ sử dụng ngân sách"
              value={summary?.usage_rate ?? 0}
              subtitle={`Kế hoạch: ${new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND", maximumFractionDigits: 0 }).format(summary?.total_planned ?? 0)}`}
              icon={<GaugeIcon />}
              color={usageColor}
              isPercentage
            />
          </>
        )}
      </div>

      {/* ── Charts row ── */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <ChartCard
          title="Ngân sách vs Thực chi theo tháng"
          subtitle={`Năm ${filters.year}${filters.quarter ? ` · Quý ${filters.quarter}` : ""}`}
        >
          <BudgetVsActualChart data={trend} loading={loadingTrend} />
        </ChartCard>

        <ChartCard
          title="Thực chi theo Phòng ban"
          subtitle="Sắp xếp theo thực chi giảm dần"
        >
          <DepartmentChart data={deptData} loading={loadingDept} />
        </ChartCard>
      </div>

      {/* ── Overspending warning table ── */}
      <div className="bg-slate-800/60 backdrop-blur-sm border border-rose-500/20 rounded-2xl shadow-xl overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-700/50 flex items-center justify-between">
          <div>
            <h3 className="text-slate-100 font-semibold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
              Cảnh báo vượt kế hoạch
            </h3>
            <p className="text-slate-400 text-xs mt-1">Top 5 khoản thực chi vượt kế hoạch cao nhất</p>
          </div>
          {overspending.length > 0 && (
            <span className="px-3 py-1 bg-rose-500/15 text-rose-400 text-xs font-bold rounded-full border border-rose-500/30">
              {overspending.length} khoản
            </span>
          )}
        </div>
        <div className="p-2">
          <OverspendingTable data={overspending} loading={loadingOver} />
        </div>
      </div>

      {/* ── Summary stats footer ── */}
      {!loadingSummary && summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: "Tổng kế hoạch chi tiêu", value: summary.total_planned },
            { label: "Tổng đề nghị TT", value: summary.total_payment_requests },
            { label: "Số khoản vượt KH", value: summary.overspending_count, isCount: true },
            { label: "Tỷ lệ SD ngân sách", value: summary.usage_rate, isPerc: true },
          ].map((item) => (
            <div
              key={item.label}
              className="bg-slate-800/40 border border-slate-700/40 rounded-xl p-4 text-center"
            >
              <p className="text-slate-400 text-xs mb-1">{item.label}</p>
              <p className="text-slate-100 font-bold text-sm">
                {item.isPerc
                  ? `${item.value.toFixed(1)}%`
                  : item.isCount
                  ? item.value.toLocaleString("vi-VN")
                  : (() => {
                      const v = item.value as number;
                      if (v >= 1_000_000_000) return `${(v / 1_000_000_000).toFixed(1)} tỷ ₫`;
                      if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(0)} triệu ₫`;
                      return new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND", maximumFractionDigits: 0 }).format(v);
                    })()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
