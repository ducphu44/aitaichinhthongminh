"use client";

import { useState, useEffect, useRef } from "react";
import { generateReport, getReports, ReportGenerateRequest, ReportResponse } from "@/lib/api";
import { useReactToPrint } from "react-to-print";
import { FiRefreshCw, FiCopy, FiFileText, FiPieChart } from "react-icons/fi";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

const COLORS = ['#8B5CF6', '#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#EC4899', '#6366F1'];

export default function ReportsPage() {
  const [reports, setReports] = useState<ReportResponse[]>([]);
  const [selectedReport, setSelectedReport] = useState<ReportResponse | null>(null);
  const [editableMarkdown, setEditableMarkdown] = useState("");
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  const contentRef = useRef<HTMLDivElement>(null);
  const handlePrint = useReactToPrint({
    contentRef,
    documentTitle: selectedReport?.title || "Bao_cao_tai_chinh",
  });

  // Form State
  const [fiscalYear, setFiscalYear] = useState(2026);
  const [reportType, setReportType] = useState("yearly");
  const [quarter, setQuarter] = useState("");

  async function fetchReports() {
    try {
      const data = await getReports();
      setReports(data);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchReports();
  }, []);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const req: ReportGenerateRequest = {
        fiscal_year: fiscalYear,
        report_type: reportType,
      };
      if (reportType === "quarterly" && quarter) {
        req.quarter = parseInt(quarter);
      }
      const newReport = await generateReport(req);
      setReports([newReport, ...reports]);
      selectReport(newReport);
    } catch (err) {
      console.error(err);
      alert("Lỗi sinh báo cáo!");
    } finally {
      setLoading(false);
    }
  };

  const selectReport = (report: ReportResponse) => {
    setSelectedReport(report);
    setEditableMarkdown(report.content_markdown);
    setIsEditing(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(editableMarkdown);
    alert("Đã copy nội dung báo cáo!");
  };

  // Prepare chart data
  let chartData: Array<{ name: string; "Dự toán": number; "Thực chi": number }> = [];
  let pieData: Array<{ name: string; value: number }> = [];
  if (selectedReport?.raw_data_json) {
    try {
      const raw = JSON.parse(selectedReport.raw_data_json);
      if (raw.summary) {
        chartData = [
          {
            name: "Tổng Ngân sách",
            "Dự toán": raw.summary.total_planned,
            "Thực chi": raw.summary.total_actual,
          }
        ];
      }
      if (raw.department_budgets) {
        pieData = raw.department_budgets.map((dept: { name: string; actual: number }) => ({
          name: dept.name,
          value: dept.actual
        })).filter((d: { name: string; value: number }) => d.value > 0);
      }
    } catch (e) {
      console.error("Invalid JSON raw data", e);
    }
  }

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100 font-sans print:h-auto print:bg-white print:text-black">
      <style dangerouslySetInnerHTML={{__html: `
        @media print {
          body, html { background: white !important; color: black !important; }
          .prose-invert * { color: black !important; border-color: #ccc !important; }
          .prose-invert h1, .prose-invert h2, .prose-invert h3 { background: none !important; color: black !important; -webkit-text-fill-color: black !important; }
          .bg-gray-900, .bg-gray-950 { background: white !important; }
          .border-gray-800 { border-color: #eee !important; }
        }
      `}} />
      {/* Sidebar - History */}
      <div className="w-80 bg-gray-900 border-r border-gray-800 flex flex-col print:hidden">
        <div className="p-4 border-b border-gray-800 bg-gray-950/50">
          <h2 className="text-lg font-semibold flex items-center text-purple-400">
            <FiFileText className="mr-2" /> Báo cáo đã tạo
          </h2>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {reports.map((r) => (
            <div
              key={r.id}
              onClick={() => selectReport(r)}
              className={`p-3 mb-2 rounded cursor-pointer transition-colors ${
                selectedReport?.id === r.id ? "bg-purple-900/40 border border-purple-500/30" : "hover:bg-gray-800 border border-transparent"
              }`}
            >
              <div className="font-medium text-sm">{r.title}</div>
              <div className="text-xs text-gray-500 mt-1">{new Date(r.created_at).toLocaleString()}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-full overflow-hidden print:overflow-visible print:h-auto print:block">
        {/* Toolbar */}
        <div className="bg-gray-900 border-b border-gray-800 p-4 flex justify-between items-center z-10 shadow-md print:hidden">
          <div className="flex space-x-3 items-center">
            <select 
              value={fiscalYear} 
              onChange={e => setFiscalYear(Number(e.target.value))}
              className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm outline-none focus:border-purple-500 transition-colors"
            >
              <option value={2025}>Năm 2025</option>
              <option value={2026}>Năm 2026</option>
              <option value={2027}>Năm 2027</option>
            </select>

            <select 
              value={reportType} 
              onChange={e => setReportType(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm outline-none focus:border-purple-500 transition-colors"
            >
              <option value="yearly">Báo cáo Năm</option>
              <option value="quarterly">Báo cáo Quý</option>
              <option value="monthly">Báo cáo Tháng</option>
            </select>

            {reportType === "quarterly" && (
              <select 
                value={quarter} 
                onChange={e => setQuarter(e.target.value)}
                className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm outline-none focus:border-purple-500 transition-colors"
              >
                <option value="">Chọn Quý</option>
                <option value="1">Quý 1</option>
                <option value="2">Quý 2</option>
                <option value="3">Quý 3</option>
                <option value="4">Quý 4</option>
              </select>
            )}

            <button
              onClick={handleGenerate}
              disabled={loading}
              className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-1.5 rounded text-sm font-medium transition-colors flex items-center disabled:opacity-50 shadow-lg shadow-purple-500/20"
            >
              {loading ? <FiRefreshCw className="animate-spin mr-2" /> : <FiPieChart className="mr-2" />}
              Generate Report
            </button>
          </div>

          {selectedReport && (
            <div className="flex space-x-2">
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="bg-gray-800 hover:bg-gray-700 border border-gray-600 px-3 py-1.5 rounded text-sm transition-colors"
              >
                {isEditing ? "View Mode" : "Edit Mode"}
              </button>
              <button
                onClick={handleCopy}
                className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded text-sm flex items-center transition-colors shadow-lg shadow-blue-500/20"
              >
                <FiCopy className="mr-2" /> Copy
              </button>
              <button
                onClick={() => handlePrint()}
                className="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1.5 rounded text-sm flex items-center transition-colors shadow-lg shadow-emerald-500/20"
              >
                <FiFileText className="mr-2" /> Xuất PDF
              </button>
            </div>
          )}
        </div>

        {/* Report Content */}
        {selectedReport ? (
          <div ref={contentRef} className="flex-1 overflow-auto bg-gray-950 p-6 flex flex-col items-center print:p-8 print:overflow-visible print:block print:bg-white print:text-black">
            
            {/* Report Header (Visible mainly for Context & Print) */}
            <div className="w-full max-w-4xl mb-8 border-b border-gray-800 pb-6 print:border-gray-300">
              <h1 className="text-3xl font-bold text-white print:text-black mb-2">
                {selectedReport.title}
              </h1>
              <p className="text-gray-400 print:text-gray-600 text-sm">
                Ngày tạo báo cáo: {new Date(selectedReport.created_at).toLocaleDateString("vi-VN", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </div>

            {/* Chart Section */}
            {!isEditing && chartData.length > 0 && (
              <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 print:flex print:flex-col print:gap-12 print:mb-12">
                
                {/* Bar Chart */}
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-xl flex flex-col print:break-inside-avoid print:shadow-none print:border-none print:p-0">
                  <h3 className="text-lg font-semibold text-gray-300 mb-4 flex items-center print:text-black">
                    <FiPieChart className="mr-2 text-purple-400" /> Biểu đồ Tổng quan Ngân sách
                  </h3>
                  <div className="flex-1 min-h-[300px] print:h-[300px] print:min-h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={true} vertical={false} />
                        <XAxis type="number" stroke="#9CA3AF" tickFormatter={(value) => `${value / 1000000}M`} />
                        <YAxis dataKey="name" type="category" stroke="#9CA3AF" width={100} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F3F4F6' }}
                          // eslint-disable-next-line @typescript-eslint/no-explicit-any
                          formatter={(value: any) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(Number(value))}
                        />
                        <Legend />
                        <Bar dataKey="Dự toán" fill="#8B5CF6" radius={[0, 4, 4, 0]} barSize={30} />
                        <Bar dataKey="Thực chi" fill="#10B981" radius={[0, 4, 4, 0]} barSize={30} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Pie Chart */}
                {pieData.length > 0 && (
                  <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-xl flex flex-col print:break-inside-avoid print:shadow-none print:border-none print:p-0 print:mt-8">
                    <h3 className="text-lg font-semibold text-gray-300 mb-4 flex items-center print:text-black">
                      <FiPieChart className="mr-2 text-blue-400" /> Cơ cấu Thực chi theo Phòng ban
                    </h3>
                    <div className="flex-1 min-h-[350px] print:h-[350px] print:min-h-[350px] w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={pieData}
                            cx="50%"
                            cy="40%"
                            innerRadius={60}
                            outerRadius={90}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            {pieData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip 
                            contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F3F4F6' }}
                            // eslint-disable-next-line @typescript-eslint/no-explicit-any
                            formatter={(value: any) => new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(Number(value))}
                          />
                          <Legend 
                            layout="horizontal" 
                            verticalAlign="bottom" 
                            align="center" 
                            wrapperStyle={{ fontSize: '12px', paddingTop: '20px' }} 
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Document Section */}
            <div className={`w-full max-w-4xl flex gap-6 ${isEditing ? 'h-full' : ''}`}>
              {/* Editor */}
              {isEditing && (
                <textarea
                  className="flex-1 bg-gray-900 border border-gray-700 text-gray-200 rounded p-4 font-mono text-sm resize-none focus:outline-none focus:border-purple-500"
                  value={editableMarkdown}
                  onChange={(e) => setEditableMarkdown(e.target.value)}
                />
              )}

              {/* Preview */}
              <div className={`${isEditing ? 'flex-1' : 'w-full'} bg-gray-900 border border-gray-800 rounded-xl p-8 shadow-2xl prose prose-invert prose-purple max-w-none print:border-none print:shadow-none print:p-0`}>
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // eslint-disable-next-line @typescript-eslint/no-unused-vars
                    table: ({node: _n, ...props}) => <div className="overflow-x-auto my-6 rounded-lg border border-gray-700"><table className="min-w-full text-sm text-left" {...props} /></div>,
                    // eslint-disable-next-line @typescript-eslint/no-unused-vars
                    thead: ({node: _n, ...props}) => <thead className="bg-gray-800 text-gray-300" {...props} />,
                    // eslint-disable-next-line @typescript-eslint/no-unused-vars
                    th: ({node: _n, ...props}) => <th className="px-4 py-3 font-semibold border-b border-gray-700" {...props} />,
                    // eslint-disable-next-line @typescript-eslint/no-unused-vars
                    td: ({node: _n, ...props}) => <td className="px-4 py-3 border-b border-gray-800/50" {...props} />,
                    // eslint-disable-next-line @typescript-eslint/no-unused-vars
                    h1: ({node: _n, ...props}) => <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400 pb-2 border-b border-gray-800" {...props} />,
                    // eslint-disable-next-line @typescript-eslint/no-unused-vars
                    h2: ({node: _n, ...props}) => <h2 className="text-xl font-semibold text-gray-200 mt-8 mb-4 flex items-center before:content-[''] before:block before:w-1.5 before:h-6 before:bg-purple-500 before:mr-2 before:rounded-sm" {...props} />,
                  }}
                >
                  {editableMarkdown}
                </ReactMarkdown>
              </div>
            </div>
            
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500 flex-col">
            <FiFileText className="text-6xl mb-4 opacity-20" />
            <p>Chọn báo cáo bên trái hoặc tạo báo cáo mới</p>
          </div>
        )}
      </div>
    </div>
  );
}
