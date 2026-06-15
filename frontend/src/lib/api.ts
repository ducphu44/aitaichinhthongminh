// API client helper for Dashboard endpoints
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  let token = null;
  if (typeof window !== "undefined") {
    token = localStorage.getItem("token");
  }

  const headers = {
    ...options.headers,
  } as any;

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401 || response.status === 403) {
    if (typeof window !== "undefined" && window.location.pathname !== "/login") {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
  }

  return response;
}

export interface DashboardSummary {
  total_budget: number;
  total_planned: number;
  total_actual: number;
  total_payment_requests: number;
  remaining_budget: number;
  usage_rate: number;
  overspending_count: number;
}

export interface MonthlyTrendItem {
  month: number;
  month_label: string;
  planned: number;
  actual: number;
}

export interface DepartmentItem {
  department_id: number;
  department_name: string;
  planned: number;
  actual: number;
}

export interface ProgramItem {
  program_id: number;
  program_name: string;
  budget: number;
  actual: number;
}

export interface OverspendingItem {
  id: number;
  department_name: string;
  plan_month: number;
  fiscal_year: number;
  quarter: number;
  planned_amount: number;
  actual_amount: number;
  variance_amount: number;
  usage_rate: number;
  warning_status: string | null;
}

export interface DepartmentOption {
  id: number;
  name: string;
  code: string;
}

export type FilterParams = {
  year?: number;
  quarter?: number;
  department_id?: number;
};

function buildQuery(params: FilterParams): string {
  const p = new URLSearchParams();
  if (params.year) p.append("year", String(params.year));
  if (params.quarter) p.append("quarter", String(params.quarter));
  if (params.department_id) p.append("department_id", String(params.department_id));
  const qs = p.toString();
  return qs ? `?${qs}` : "";
}

export async function fetchSummary(filters: FilterParams): Promise<DashboardSummary> {
  const res = await apiFetch(`/dashboard/summary${buildQuery(filters)}`);
  if (!res.ok) throw new Error("Failed to fetch summary");
  return res.json();
}

export async function fetchMonthlyTrend(filters: FilterParams): Promise<MonthlyTrendItem[]> {
  const res = await apiFetch(`/dashboard/monthly-trend${buildQuery(filters)}`);
  if (!res.ok) throw new Error("Failed to fetch monthly trend");
  return res.json();
}

export async function fetchByDepartment(filters: FilterParams): Promise<DepartmentItem[]> {
  const res = await apiFetch(`/dashboard/by-department${buildQuery(filters)}`);
  if (!res.ok) throw new Error("Failed to fetch department data");
  return res.json();
}

export async function fetchByProgram(filters: FilterParams): Promise<ProgramItem[]> {
  const res = await apiFetch(`/dashboard/by-program${buildQuery(filters)}`);
  if (!res.ok) throw new Error("Failed to fetch program data");
  return res.json();
}

export async function fetchOverspending(filters: FilterParams): Promise<OverspendingItem[]> {
  const res = await apiFetch(`/dashboard/overspending${buildQuery(filters)}`);
  if (!res.ok) throw new Error("Failed to fetch overspending data");
  return res.json();
}

export async function fetchDepartments(): Promise<DepartmentOption[]> {
  const res = await apiFetch(`/departments`);
  if (!res.ok) throw new Error("Failed to fetch departments");
  return res.json();
}

export function formatVND(amount: number): string {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatVNDCompact(amount: number): string {
  if (amount >= 1_000_000_000) {
    return `${(amount / 1_000_000_000).toFixed(1)} tỷ`;
  }
  if (amount >= 1_000_000) {
    return `${(amount / 1_000_000).toFixed(1)} triệu`;
  }
  return formatVND(amount);
}

export interface AlertItem {
  alert_type: string;
  severity: string;
  department_name: string;
  program_name: string;
  amount: number;
  message: string;
  recommendation: string;
}

export async function fetchAlerts(params: { department_id?: number | null; severity?: string | null }): Promise<AlertItem[]> {
  const p = new URLSearchParams();
  if (params.department_id) p.append("department_id", String(params.department_id));
  if (params.severity) p.append("severity", String(params.severity));
  const qs = p.toString() ? `?${p.toString()}` : "";
  const res = await apiFetch(`/alerts${qs}`);
  if (!res.ok) throw new Error("Failed to fetch alerts");
  return res.json();
}

export interface AIAskResponse {
  answer_markdown: string;
  used_tools: string[];
}

export async function askAI(question: string, fiscal_year?: number): Promise<AIAskResponse> {
  const response = await apiFetch(`/ai/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question, fiscal_year }),
  });

  if (!response.ok) {
    throw new Error("Failed to communicate with AI Agent");
  }

  return response.json();
}

// Reports API
export interface ReportGenerateRequest {
  fiscal_year: number;
  report_type: string;
  department_id?: number;
  quarter?: number;
  month?: number;
}

export interface ReportResponse {
  id: number;
  title: string;
  report_type: string;
  fiscal_year: number;
  quarter?: number;
  month?: number;
  department_id?: number;
  content_markdown: string;
  raw_data_json?: string;
  created_at: string;
}

export async function generateReport(data: ReportGenerateRequest): Promise<ReportResponse> {
  const response = await apiFetch(`/reports/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Failed to generate report");
  }

  return response.json();
}

export async function getReports(): Promise<ReportResponse[]> {
  const response = await apiFetch(`/reports`);
  if (!response.ok) {
    throw new Error("Failed to fetch reports");
  }
  return response.json();
}

export async function getReport(id: number): Promise<ReportResponse> {
  const response = await apiFetch(`/reports/${id}`);
  if (!response.ok) {
    throw new Error("Failed to fetch report");
  }
  return response.json();
}

// Auth API
export async function login(email: string, password: string) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Đăng nhập thất bại");
  }
  return res.json(); // { access_token, token_type }
}

export async function getMe() {
  const res = await apiFetch(`/auth/me`);
  if (!res.ok) {
    throw new Error("Không thể lấy thông tin người dùng");
  }
  return res.json();
}

export interface UserResponse {
  id: number;
  email: string;
  role: string;
  is_active: number;
}

export async function getUsers(): Promise<UserResponse[]> {
  const res = await apiFetch(`/auth/users`);
  if (!res.ok) {
    throw new Error("Không thể lấy danh sách người dùng");
  }
  return res.json();
}
