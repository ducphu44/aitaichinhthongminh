"use client";

import { useState, useEffect } from "react";

interface Department {
  id: number;
  name: string;
  code: string;
}

interface ImportError {
  id: number;
  row_index: number;
  error_message: string;
  raw_data: string | null;
}

interface UploadStats {
  total_rows: number;
  valid_rows: number;
  error_rows: number;
}

interface UploadRecord {
  id: number;
  file_name: string;
  file_type: string;
  department_name: string;
  import_status: string;
  total_rows: number;
  valid_rows: number;
  error_rows: number;
  uploaded_at: string | null;
}

export default function UploadPage() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [selectedDept, setSelectedDept] = useState<number>(1);
  const [file, setFile] = useState<File | null>(null);
  
  // Status states
  const [uploading, setUploading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [importing, setImporting] = useState(false);
  const [uploadId, setUploadId] = useState<number | null>(null);
  const [validationStatus, setValidationStatus] = useState<string>("pending");
  
  // Results
  const [stats, setStats] = useState<UploadStats | null>(null);
  const [errors, setErrors] = useState<ImportError[]>([]);
  const [importedRows, setImportedRows] = useState<number | null>(null);
  const [notification, setNotification] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // History
  const [history, setHistory] = useState<UploadRecord[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Department mismatch detection
  const [deptMismatch, setDeptMismatch] = useState<{ suggestedId: number; suggestedName: string } | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

  const fetchHistory = async () => {
    await Promise.resolve(); // Avoid synchronous setState in effect
    setLoadingHistory(true);
    try {
      const res = await fetch(`${API_URL}/uploads`);
      if (res.ok) setHistory(await res.json());
    } catch { /* silent */ }
    finally { setLoadingHistory(false); }
  };

  // Fetch departments + history on load
  useEffect(() => {
    fetch(`${API_URL}/departments`)
      .then((res) => {
        if (!res.ok) throw new Error("Could not fetch departments");
        return res.json();
      })
      .then((data) => {
        setDepartments(data);
        if (data.length > 0) setSelectedDept(data[0].id);
      })
      .catch((err) => {
        console.error(err);
        // Fallback departments in case backend is offline during initialization
        setDepartments([
          { id: 1, name: "Phòng CNTT", code: "CNTT" },
          { id: 2, name: "Phòng Marketing Truyền thông", code: "MKT" },
          { id: 3, name: "Phòng Tuyển sinh", code: "TS" },
          { id: 4, name: "Phòng Công tác Sinh viên", code: "CTSV" },
          { id: 5, name: "Phòng Hợp tác Doanh nghiệp & Phát triển", code: "HTDN" },
          { id: 6, name: "Phòng Hợp tác Học thuật", code: "HTHT" },
        ]);
      });

    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchHistory();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [API_URL]);



  /**
   * Try to detect the department from the filename.
   * Returns the matching department or null.
   */
  const detectDeptFromFilename = (filename: string): Department | null => {
    const lower = filename.toLowerCase().replace(/[_\-\s]/g, " ");
    // Keyword map: order matters (longer/more-specific first)
    const keywords: [string[], string][] = [
      [["marketing", "truyen thong", "mkt"], "MKT"],
      [["tuyen sinh", "ts"], "TS"],
      [["cong tac sinh vien", "ctsv"], "CTSV"],
      [["hop tac doanh nghiep", "htdn"], "HTDN"],
      [["hop tac hoc thuat", "htht"], "HTHT"],
      [["cntt", "cong nghe thong tin", "it"], "CNTT"],
    ];
    for (const [keys, code] of keywords) {
      if (keys.some((k) => lower.includes(k))) {
        return departments.find((d) => d.code === code) ?? null;
      }
    }
    return null;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const chosen = e.target.files[0];
      setFile(chosen);
      // Reset flow
      setUploadId(null);
      setStats(null);
      setErrors([]);
      setValidationStatus("pending");
      setNotification(null);
      setDeptMismatch(null);

      // Auto-detect department from filename
      const detected = detectDeptFromFilename(chosen.name);
      if (detected && detected.id !== selectedDept) {
        setDeptMismatch({ suggestedId: detected.id, suggestedName: detected.name });
      }
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setNotification({ type: "error", message: "Vui lòng chọn một file Excel để tải lên." });
      return;
    }

    setUploading(true);
    setNotification(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("department_id", selectedDept.toString());

    try {
      const res = await fetch(`${API_URL}/uploads`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Upload failed");
      }

      const data = await res.json();
      setUploadId(data.id);
      setValidationStatus(data.import_status);
      setNotification({ type: "success", message: "Tải lên file thành công! Vui lòng nhấn nút kiểm tra để tiếp tục." });
    } catch (err: unknown) {
      setNotification({ type: "error", message: `Lỗi tải lên: ${(err as Error).message}` });
    } finally {
      setUploading(false);
    }
  };

  const handleValidate = async () => {
    if (!uploadId) return;

    setValidating(true);
    setNotification(null);
    setErrors([]);

    try {
      const res = await fetch(`${API_URL}/uploads/${uploadId}/validate`, {
        method: "POST",
      });

      if (!res.ok) {
        throw new Error("Validation failed on server");
      }

      const data = await res.json();
      setValidationStatus(data.import_status);
      setStats({
        total_rows: data.total_rows,
        valid_rows: data.valid_rows,
        error_rows: data.error_rows,
      });

      if (data.import_status === "Failed") {
        // Fetch error list
        const errRes = await fetch(`${API_URL}/uploads/${uploadId}/errors`);
        if (errRes.ok) {
          const errData = await errRes.json();
          setErrors(errData);
        }
        setNotification({ type: "error", message: "Phát hiện lỗi cấu trúc hoặc dữ liệu trong file Excel!" });
      } else {
        setNotification({ type: "success", message: "File hợp lệ hoàn toàn! Cấu trúc đúng tiêu chuẩn." });
      }
    } catch (err: unknown) {
      setNotification({ type: "error", message: `Lỗi kiểm tra file: ${(err as Error).message}` });
    } finally {
      setValidating(false);
    }
  };

  const handleImport = async () => {
    if (!uploadId) return;

    setImporting(true);
    setNotification(null);
    setErrors([]);

    try {
      const res = await fetch(`${API_URL}/uploads/${uploadId}/import`, {
        method: "POST",
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Import failed");
      }

      const data = await res.json();
      setValidationStatus(data.import_status);
      setImportedRows(data.imported_rows);
      setNotification({
        type: "success",
        message: `Đã nạp thành công ${data.imported_rows} dòng dữ liệu vào cơ sở dữ liệu!`,
      });
      fetchHistory(); // refresh history card
    } catch (err: unknown) {
      // Re-fetch errors in case some duplicate code errors were logged during import
      const errRes = await fetch(`${API_URL}/uploads/${uploadId}/errors`);
      if (errRes.ok) {
        const errData = await errRes.json();
        setErrors(errData);
      }
      setNotification({ type: "error", message: `Lỗi nạp dữ liệu: ${(err as Error).message}` });
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
          Tải Lên Dữ Liệu Tài Chính
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          Chọn phòng ban và tải lên tệp Excel chứa dữ liệu Dự toán ngân sách, Kế hoạch chi tiêu, và Đề nghị thanh toán.
        </p>
      </div>

      {/* Notification Banner */}
      {notification && (
        <div
          className={`p-4 rounded-xl border flex items-center gap-3 transition-all duration-300 ${
            notification.type === "success"
              ? "bg-emerald-50 border-emerald-200 text-emerald-800 dark:bg-emerald-950/20 dark:border-emerald-800/30 dark:text-emerald-400"
              : "bg-rose-50 border-rose-200 text-rose-800 dark:bg-rose-950/20 dark:border-rose-800/30 dark:text-rose-400"
          }`}
        >
          <span className="text-xl">
            {notification.type === "success" ? "✓" : "⚠"}
          </span>
          <p className="text-sm font-medium">{notification.message}</p>
        </div>
      )}

      {/* ── Department Mismatch Warning ── */}
      {deptMismatch && uploadId === null && (
        <div className="flex items-start gap-4 p-4 rounded-xl border-2 border-amber-300 dark:border-amber-600 bg-amber-50 dark:bg-amber-950/20 shadow-sm animate-pulse-once">
          {/* Icon */}
          <div className="shrink-0 w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-900/40 flex items-center justify-center text-amber-600 text-xl">
            ⚠️
          </div>
          {/* Message */}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-amber-800 dark:text-amber-300">
              Phát hiện không khớp phòng ban!
            </p>
            <p className="text-xs text-amber-700 dark:text-amber-400 mt-0.5">
              File bạn chọn có vẻ thuộc{" "}
              <span className="font-bold underline">{deptMismatch.suggestedName}</span>,
              nhưng bạn đang chọn phòng ban khác. Dữ liệu có thể bị gán sai phòng ban.
            </p>
          </div>
          {/* Actions */}
          <div className="shrink-0 flex items-center gap-2">
            <button
              id="btn-switch-dept"
              onClick={() => {
                setSelectedDept(deptMismatch.suggestedId);
                setDeptMismatch(null);
              }}
              className="px-3 py-1.5 bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold rounded-lg transition-colors duration-150 whitespace-nowrap"
            >
              Đổi sang {deptMismatch.suggestedName.replace("Phòng ", "")}
            </button>
            <button
              id="btn-dismiss-mismatch"
              onClick={() => setDeptMismatch(null)}
              className="px-3 py-1.5 border border-amber-400 dark:border-amber-600 hover:bg-amber-100 dark:hover:bg-amber-900/40 text-amber-700 dark:text-amber-300 text-xs font-semibold rounded-lg transition-colors duration-150 whitespace-nowrap"
            >
              Bỏ qua
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Form (Left Column) */}
        <div className="lg:col-span-1 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6 space-y-6">
          <h2 className="text-lg font-bold text-slate-800 dark:text-slate-200 border-b border-slate-100 dark:border-slate-800 pb-3">
            Cấu hình Tải lên
          </h2>

          <form onSubmit={handleUpload} className="space-y-6">
            {/* Department Select */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
                Phòng ban nhập liệu
              </label>
              <select
                value={selectedDept}
                onChange={(e) => setSelectedDept(Number(e.target.value))}
                disabled={uploading || validating || uploadId !== null}
                className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-150 disabled:opacity-60"
              >
                {departments.map((dept) => (
                  <option key={dept.id} value={dept.id}>
                    {dept.name} ({dept.code})
                  </option>
                ))}
              </select>
            </div>

            {/* File Dropzone */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
                File dữ liệu Excel
              </label>
              <div className="relative border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl hover:border-blue-500 dark:hover:border-blue-500 transition-colors duration-150 flex flex-col items-center justify-center p-6 bg-slate-50/50 dark:bg-slate-950/20 text-center cursor-pointer">
                <input
                  type="file"
                  accept=".xlsx, .xls"
                  onChange={handleFileChange}
                  disabled={uploading || validating}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
                />
                <div className="w-12 h-12 rounded-full bg-blue-50 dark:bg-blue-950/40 flex items-center justify-center text-blue-600 mb-3">
                  🗎
                </div>
                {file ? (
                  <div>
                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200 truncate max-w-[220px] mx-auto">
                      {file.name}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                      Kéo thả hoặc Click để chọn file
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      Hỗ trợ tệp định dạng .xlsx, .xls
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            {uploadId === null ? (
              <button
                type="submit"
                disabled={!file || uploading}
                className="w-full bg-blue-600 text-white rounded-xl py-3 font-semibold text-sm hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
              >
                {uploading ? (
                  <>
                    <span className="animate-spin text-sm">⌛</span> Tải lên...
                  </>
                ) : (
                  "Tải lên máy chủ"
                )}
              </button>
            ) : (
              <div className="space-y-3">
                {validationStatus === "Validated" && (
                  <button
                    type="button"
                    onClick={handleImport}
                    disabled={importing}
                    className="w-full bg-emerald-600 text-white rounded-xl py-3 font-semibold text-sm hover:bg-emerald-700 disabled:bg-slate-200 disabled:text-slate-400 transition-all duration-200 flex items-center justify-center gap-2"
                  >
                    {importing ? (
                      <>
                        <span className="animate-spin text-sm">⌛</span> Đang nạp dữ liệu...
                      </>
                    ) : (
                      "Nạp vào Database (Import)"
                    )}
                  </button>
                )}
                
                {validationStatus !== "Imported" && validationStatus !== "Validated" && (
                  <button
                    type="button"
                    onClick={handleValidate}
                    disabled={validating}
                    className="w-full bg-indigo-600 text-white rounded-xl py-3 font-semibold text-sm hover:bg-indigo-700 disabled:bg-slate-200 disabled:text-slate-400 transition-all duration-200 flex items-center justify-center gap-2"
                  >
                    {validating ? (
                      <>
                        <span className="animate-spin text-sm">⌛</span> Đang kiểm tra...
                      </>
                    ) : (
                      "Kiểm tra file (Validate)"
                    )}
                  </button>
                )}

                {validationStatus === "Imported" && (
                  <div className="bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800/30 text-emerald-800 dark:text-emerald-400 rounded-xl p-3 text-center text-xs font-bold">
                    ✓ Đã nhập thành công {importedRows !== null ? importedRows : stats?.total_rows} dòng dữ liệu!
                  </div>
                )}

                <button
                  type="button"
                  onClick={() => {
                    setFile(null);
                    setUploadId(null);
                    setStats(null);
                    setErrors([]);
                    setValidationStatus("pending");
                    setImportedRows(null);
                    setNotification(null);
                  }}
                  className="w-full border border-slate-200 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/30 text-slate-600 dark:text-slate-300 rounded-xl py-3 font-semibold text-sm transition-all duration-200"
                >
                  Tải file khác
                </button>
              </div>
            )}
          </form>
        </div>

        {/* Validation Details & Errors (Right 2 Columns) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Status Display Card */}
          {uploadId !== null && (
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm space-y-4">
              <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200">
                Thông tin file hiện tại
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-100 dark:border-slate-800/40">
                  <p className="text-xs text-slate-400 font-medium">Trạng thái</p>
                  <p className={`text-sm font-bold mt-1 uppercase ${
                    validationStatus === "Validated" || validationStatus === "Imported"
                      ? "text-emerald-500"
                      : validationStatus === "Failed"
                      ? "text-rose-500"
                      : "text-amber-500"
                  }`}>
                    {validationStatus === "Validated" ? "Hợp lệ" : validationStatus === "Imported" ? "Đã nhập DB" : validationStatus === "Failed" ? "Lỗi" : "Chờ kiểm tra"}
                  </p>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-100 dark:border-slate-800/40">
                  <p className="text-xs text-slate-400 font-medium">Tổng số dòng</p>
                  <p className="text-base font-extrabold mt-1 text-slate-700 dark:text-slate-300">
                    {stats ? stats.total_rows : "-"}
                  </p>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-100 dark:border-slate-800/40">
                  <p className="text-xs text-slate-400 font-medium">Dòng hợp lệ</p>
                  <p className="text-base font-extrabold mt-1 text-emerald-500">
                    {stats ? stats.valid_rows : "-"}
                  </p>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-100 dark:border-slate-800/40">
                  <p className="text-xs text-slate-400 font-medium">Dòng lỗi</p>
                  <p className="text-base font-extrabold mt-1 text-rose-500">
                    {stats ? stats.error_rows : "-"}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Errors List */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-6 min-h-[300px] flex flex-col">
            <div className="border-b border-slate-100 dark:border-slate-800 pb-3 flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-800 dark:text-slate-200">
                Nhật ký kiểm tra (Validation Log)
              </h2>
              {errors.length > 0 && (
                <span className="bg-rose-100 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 px-3 py-1 rounded-full text-xs font-bold">
                  {errors.length} lỗi
                </span>
              )}
            </div>

            {errors.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center text-slate-400 py-12">
                <span className="text-4xl mb-2">📊</span>
                <p className="text-sm font-medium">Chưa có nhật ký lỗi hoặc tệp kiểm tra hợp lệ.</p>
              </div>
            ) : (
              <div className="flex-1 overflow-x-auto mt-4">
                <table className="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr className="border-b border-slate-100 dark:border-slate-800 text-slate-400 text-xs uppercase font-bold">
                      <th className="py-2 px-3">Dòng</th>
                      <th className="py-2 px-3">Nội dung lỗi</th>
                      <th className="py-2 px-3">Dữ liệu nguồn</th>
                    </tr>
                  </thead>
                  <tbody>
                    {errors.map((error) => (
                      <tr
                        key={error.id}
                        className="border-b border-slate-50 dark:border-slate-800/30 hover:bg-slate-50/50 dark:hover:bg-slate-800/10 transition-colors"
                      >
                        <td className="py-3 px-3 align-top">
                          <span className="px-2 py-0.5 rounded-md font-bold text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                            {error.row_index === 0 ? "File" : `Dòng ${error.row_index}`}
                          </span>
                        </td>
                        <td className="py-3 px-3 align-top font-medium text-rose-600 dark:text-rose-400 max-w-xs break-words">
                          {error.error_message}
                        </td>
                        <td className="py-3 px-3 align-top font-mono text-xs text-slate-400 max-w-sm truncate hover:text-clip hover:whitespace-normal">
                          {error.raw_data ? error.raw_data : "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Upload History Card ── */}
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-950/40 flex items-center justify-center text-indigo-600 text-sm">
              🕒
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-800 dark:text-slate-200">Lịch sử Upload</h2>
              <p className="text-xs text-slate-400">{history.length} lần tải lên gần nhất</p>
            </div>
          </div>
          <button
            id="btn-refresh-history"
            onClick={fetchHistory}
            disabled={loadingHistory}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-all duration-150 border border-slate-200 dark:border-slate-700 disabled:opacity-50"
          >
            <svg
              className={`w-3.5 h-3.5 ${loadingHistory ? "animate-spin" : ""}`}
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Làm mới
          </button>
        </div>

        {/* Table */}
        {loadingHistory ? (
          <div className="flex items-center justify-center py-16">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-500 border-t-transparent" />
          </div>
        ) : history.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400">
            <span className="text-4xl mb-3">📂</span>
            <p className="text-sm font-medium">Chưa có file nào được tải lên</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-800/40 text-xs text-slate-500 uppercase tracking-wider font-semibold">
                  <th className="text-left py-3 px-5">#</th>
                  <th className="text-left py-3 px-4">Tên file</th>
                  <th className="text-left py-3 px-4">Phòng ban</th>
                  <th className="text-center py-3 px-4">Trạng thái</th>
                  <th className="text-center py-3 px-4">Tổng dòng</th>
                  <th className="text-center py-3 px-4">Hợp lệ</th>
                  <th className="text-center py-3 px-4">Lỗi</th>
                  <th className="text-right py-3 px-5">Thời gian</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/50">
                {history.map((rec) => {
                  const statusMap: Record<string, { label: string; cls: string }> = {
                    pending:   { label: "Chờ xử lý", cls: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400" },
                    Validated: { label: "✓ Hợp lệ",  cls: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400" },
                    Failed:    { label: "✗ Lỗi",     cls: "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400" },
                    Imported:  { label: "⬆ Đã nhập DB", cls: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400" },
                  };
                  const s = statusMap[rec.import_status] ?? { label: rec.import_status, cls: "bg-slate-100 text-slate-600" };

                  const uploadedAt = rec.uploaded_at ? new Date(rec.uploaded_at) : null;
                  const timeLabel = uploadedAt
                    ? (() => {
                        const diffMs = Date.now() - uploadedAt.getTime();
                        const diffMin = Math.floor(diffMs / 60000);
                        if (diffMin < 1) return "Vừa xong";
                        if (diffMin < 60) return `${diffMin} phút trước`;
                        const diffH = Math.floor(diffMin / 60);
                        if (diffH < 24) return `${diffH} giờ trước`;
                        return uploadedAt.toLocaleDateString("vi-VN");
                      })()
                    : "—";

                  return (
                    <tr key={rec.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/20 transition-colors duration-100 group">
                      <td className="py-3 px-5 text-slate-400 font-mono text-xs">{rec.id}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="text-base">📄</span>
                          <span className="font-medium text-slate-700 dark:text-slate-300 max-w-[220px] truncate" title={rec.file_name}>
                            {rec.file_name}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-slate-500 dark:text-slate-400 text-xs">
                        {rec.department_name || "—"}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-bold ${s.cls}`}>
                          {s.label}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center font-semibold text-slate-600 dark:text-slate-300">
                        {rec.total_rows > 0 ? rec.total_rows.toLocaleString("vi-VN") : "—"}
                      </td>
                      <td className="py-3 px-4 text-center font-semibold text-emerald-600 dark:text-emerald-400">
                        {rec.valid_rows > 0 ? rec.valid_rows.toLocaleString("vi-VN") : "—"}
                      </td>
                      <td className="py-3 px-4 text-center font-semibold text-rose-500">
                        {rec.error_rows > 0 ? rec.error_rows.toLocaleString("vi-VN") : <span className="text-slate-300">0</span>}
                      </td>
                      <td className="py-3 px-5 text-right text-xs text-slate-400" title={uploadedAt?.toLocaleString("vi-VN") ?? ""}>
                        {timeLabel}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
