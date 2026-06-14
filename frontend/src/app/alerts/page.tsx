"use client";

import { useState, useEffect, useCallback } from "react";
import { fetchAlerts, fetchDepartments, AlertItem, DepartmentOption, formatVND } from "@/lib/api";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [departments, setDepartments] = useState<DepartmentOption[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [selectedDept, setSelectedDept] = useState<number | null>(null);
  const [selectedSeverity, setSelectedSeverity] = useState<string | null>(null);

  // Fetch data
  const loadAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchAlerts({
        department_id: selectedDept,
        severity: selectedSeverity,
      });
      setAlerts(data);
    } catch (err) {
      console.error("Lỗi khi tải cảnh báo tài chính:", err);
    } finally {
      setLoading(false);
    }
  }, [selectedDept, selectedSeverity]);

  // Load departments
  useEffect(() => {
    fetchDepartments().then(setDepartments).catch(console.error);
  }, []);

  // Reload alerts when filters change
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadAlerts();
  }, [loadAlerts]);

  const severityBadgeClass = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "high":
        return "bg-rose-500/10 text-rose-400 border border-rose-500/20";
      case "medium":
        return "bg-amber-500/10 text-amber-400 border border-amber-500/20";
      case "low":
        return "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
      default:
        return "bg-slate-500/10 text-slate-400 border border-slate-500/20";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            ⚠️ Cảnh Báo Tài Chính
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Hệ thống phát hiện các bất thường, vượt hạn mức, sử dụng ngân sách thấp hoặc vi phạm quy trình thanh toán từ cơ sở dữ liệu.
          </p>
        </div>
        <button
          onClick={loadAlerts}
          className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-semibold transition-all duration-200 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30 self-start sm:self-auto"
        >
          🔄 Làm mới
        </button>
      </div>

      {/* Filters */}
      <div className="bg-slate-900/60 backdrop-blur-sm border border-slate-800 rounded-2xl p-5 flex flex-wrap items-center gap-4">
        {/* Department Filter */}
        <div className="flex items-center gap-2.5">
          <label className="text-slate-400 text-sm font-bold">Phòng ban:</label>
          <select
            id="alert-filter-dept"
            value={selectedDept ?? ""}
            onChange={(e) => setSelectedDept(e.target.value ? Number(e.target.value) : null)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all min-w-[200px]"
          >
            <option value="">Tất cả phòng ban</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>

        {/* Severity Filter */}
        <div className="flex items-center gap-2.5">
          <label className="text-slate-400 text-sm font-bold">Độ nghiêm trọng:</label>
          <select
            id="alert-filter-severity"
            value={selectedSeverity ?? ""}
            onChange={(e) => setSelectedSeverity(e.target.value ? e.target.value : null)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all min-w-[160px]"
          >
            <option value="">Tất cả mức độ</option>
            <option value="High">Cao (High)</option>
            <option value="Medium">Trung bình (Medium)</option>
            <option value="Low">Thấp (Low)</option>
          </select>
        </div>

        {/* Reset Filters */}
        {(selectedDept !== null || selectedSeverity !== null) && (
          <button
            onClick={() => {
              setSelectedDept(null);
              setSelectedSeverity(null);
            }}
            className="flex items-center gap-1.5 px-4 py-2.5 border border-slate-700 hover:bg-slate-800 text-slate-300 text-sm font-medium rounded-xl transition-all duration-150 ml-auto"
          >
            ❌ Xóa bộ lọc
          </button>
        )}
      </div>

      {/* Alerts Table */}
      <div className="bg-slate-900/60 backdrop-blur-sm border border-slate-800 rounded-2xl shadow-xl overflow-hidden min-h-[400px] flex flex-col">
        {loading ? (
          <div className="flex-1 flex flex-col items-center justify-center py-24">
            <div className="animate-spin rounded-full h-10 w-10 border-2 border-blue-500 border-t-transparent mb-4" />
            <p className="text-slate-400 text-sm font-medium">Đang tính toán phân tích cảnh báo...</p>
          </div>
        ) : alerts.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-500 py-24 text-center">
            <span className="text-5xl mb-4">🛡️</span>
            <h3 className="text-lg font-bold text-slate-300">Không tìm thấy cảnh báo tài chính nào</h3>
            <p className="text-sm text-slate-400 mt-1 max-w-md">Dữ liệu tài chính ở trạng thái an toàn, không có bất kỳ dấu hiệu bất thường hay vượt hạn mức nào theo bộ lọc.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="bg-slate-800/40 text-xs text-slate-400 uppercase tracking-wider font-bold border-b border-slate-800">
                  <th className="py-4 px-6">Phòng ban / Chương trình</th>
                  <th className="py-4 px-6">Loại cảnh báo</th>
                  <th className="py-4 px-6 text-center">Mức độ</th>
                  <th className="py-4 px-6 text-right">Giá trị ảnh hưởng</th>
                  <th className="py-4 px-6">Nội dung chi tiết</th>
                  <th className="py-4 px-6">Khuyến nghị xử lý</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {alerts.map((alert, idx) => (
                  <tr
                    key={idx}
                    className="hover:bg-slate-800/20 transition-colors duration-150"
                  >
                    {/* Dept / Program */}
                    <td className="py-4 px-6 align-top">
                      <p className="font-bold text-slate-200">{alert.department_name}</p>
                      <p className="text-xs text-slate-400 mt-0.5">{alert.program_name}</p>
                    </td>

                    {/* Alert Type */}
                    <td className="py-4 px-6 align-top font-semibold text-slate-300">
                      {alert.alert_type}
                    </td>

                    {/* Severity */}
                    <td className="py-4 px-6 align-top text-center">
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${severityBadgeClass(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </td>

                    {/* Amount */}
                    <td className="py-4 px-6 align-top text-right font-mono font-bold text-slate-300">
                      {alert.amount > 0 ? formatVND(alert.amount) : "—"}
                    </td>

                    {/* Message */}
                    <td className="py-4 px-6 align-top text-slate-300 max-w-sm font-medium">
                      {alert.message}
                    </td>

                    {/* Recommendation */}
                    <td className="py-4 px-6 align-top text-slate-400 max-w-xs italic text-xs leading-relaxed">
                      💡 {alert.recommendation}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
