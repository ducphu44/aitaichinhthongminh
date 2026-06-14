"use client";

import { DepartmentOption } from "@/lib/api";

interface FilterState {
  year: number;
  quarter: number | null;
  department_id: number | null;
}

interface Props {
  filters: FilterState;
  departments: DepartmentOption[];
  onFiltersChange: (filters: FilterState) => void;
}

const QUARTERS = [
  { value: 1, label: "Quý I" },
  { value: 2, label: "Quý II" },
  { value: 3, label: "Quý III" },
  { value: 4, label: "Quý IV" },
];

const currentYear = new Date().getFullYear();
const YEARS = Array.from({ length: 5 }, (_, i) => currentYear - i);

export default function DashboardFilters({ filters, departments, onFiltersChange }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Year filter */}
      <div className="flex items-center gap-2">
        <label className="text-slate-400 text-sm font-medium whitespace-nowrap">Năm:</label>
        <select
          id="filter-year"
          value={filters.year}
          onChange={(e) => onFiltersChange({ ...filters, year: Number(e.target.value) })}
          className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
        >
          {YEARS.map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
      </div>

      {/* Quarter filter */}
      <div className="flex items-center gap-2">
        <label className="text-slate-400 text-sm font-medium whitespace-nowrap">Quý:</label>
        <select
          id="filter-quarter"
          value={filters.quarter ?? ""}
          onChange={(e) =>
            onFiltersChange({
              ...filters,
              quarter: e.target.value ? Number(e.target.value) : null,
            })
          }
          className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
        >
          <option value="">Tất cả quý</option>
          {QUARTERS.map((q) => (
            <option key={q.value} value={q.value}>
              {q.label}
            </option>
          ))}
        </select>
      </div>

      {/* Department filter */}
      <div className="flex items-center gap-2">
        <label className="text-slate-400 text-sm font-medium whitespace-nowrap">Phòng ban:</label>
        <select
          id="filter-department"
          value={filters.department_id ?? ""}
          onChange={(e) =>
            onFiltersChange({
              ...filters,
              department_id: e.target.value ? Number(e.target.value) : null,
            })
          }
          className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all min-w-[180px]"
        >
          <option value="">Tất cả phòng ban</option>
          {departments.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>
      </div>

      {/* Reset button */}
      {(filters.quarter !== null || filters.department_id !== null) && (
        <button
          id="btn-reset-filters"
          onClick={() =>
            onFiltersChange({
              year: currentYear,
              quarter: null,
              department_id: null,
            })
          }
          className="flex items-center gap-1.5 px-3 py-2 text-sm text-slate-400 hover:text-white hover:bg-slate-700/50 rounded-lg transition-all duration-200 border border-slate-700/50"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
          Xoá bộ lọc
        </button>
      )}
    </div>
  );
}
