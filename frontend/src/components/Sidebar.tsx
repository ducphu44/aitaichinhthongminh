"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { useEffect, useState } from "react";

const icons = {
  dashboard: (
    <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
    </svg>
  ),
  upload: (
    <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
    </svg>
  ),
  ai: (
    <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  ),
  reports: (
    <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  users: (
    <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  ),
  logout: (
    <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
    </svg>
  ),
};

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [role, setRole] = useState("finance_staff");
  const [email, setEmail] = useState("");

  useEffect(() => {
    const userStr = localStorage.getItem("user");
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        setRole(user.role);
        setEmail(user.email);
      } catch (e) {}
    }
  }, []);

  const handleLogout = (e: React.MouseEvent) => {
    e.preventDefault();
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/login");
  };

  const menuItems = [
    { name: "Dashboard", href: "/dashboard", icon: icons.dashboard, roles: ["admin", "finance_staff", "finance_manager", "leader"] },
    { name: "Upload Excel", href: "/upload", icon: icons.upload, roles: ["admin", "finance_staff"] },
    { name: "Alerts", href: "/alerts", icon: icons.ai, roles: ["admin", "finance_staff", "finance_manager", "leader"] },
    { name: "AI Chat", href: "/ai-assistant", icon: icons.ai, roles: ["admin", "finance_staff", "finance_manager"] },
    { name: "Reports", href: "/reports", icon: icons.reports, roles: ["admin", "finance_staff", "finance_manager", "leader"] },
    { name: "Users", href: "/users", icon: icons.users, roles: ["admin"] },
  ];

  const visibleMenuItems = menuItems.filter((item) => item.roles.includes(role));

  return (
    <div className="w-72 h-screen bg-slate-900 text-white flex flex-col shadow-xl print:hidden">
      <div className="px-6 py-6 border-b border-slate-800 flex flex-col items-start justify-center">
        <div className="text-lg font-bold tracking-wide flex items-center gap-2">
          <span className="text-blue-400">AI</span> 
          <span>Trợ Lý Tài Chính</span>
        </div>
        <div className="mt-1 text-xs font-semibold text-purple-400 bg-purple-900/30 px-2 py-0.5 rounded border border-purple-500/20">
          Mã đề tài: AI20K-046
        </div>
      </div>
      
      <div className="px-6 py-4 flex items-center gap-3 border-b border-slate-800 bg-slate-800/50">
        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center font-bold text-lg shadow-inner">
          {email ? email.charAt(0).toUpperCase() : role.charAt(0).toUpperCase()}
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-medium text-slate-300 truncate w-32" title={email}>{email || "Current Role"}</span>
          <span className="text-xs font-bold text-green-400 bg-green-400/10 px-2 py-0.5 rounded-full w-max mt-0.5">
            {role}
          </span>
        </div>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        <p className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
          Menu
        </p>
        {visibleMenuItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center px-4 py-3 rounded-xl transition-all duration-200 group relative ${
                isActive 
                  ? "bg-blue-600 text-white shadow-md shadow-blue-900/20" 
                  : "text-slate-400 hover:bg-slate-800 hover:text-white"
              }`}
            >
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-8 bg-blue-400 rounded-r-md"></div>
              )}
              <span className={`transition-transform duration-200 ${isActive ? 'scale-110' : 'group-hover:scale-110 group-hover:text-blue-400'}`}>
                {item.icon}
              </span>
              <span className="font-medium text-sm">{item.name}</span>
            </Link>
          );
        })}
      </nav>
      
      <div className="p-4 border-t border-slate-800">
        <a
          href="#"
          onClick={handleLogout}
          className="flex items-center px-4 py-3 text-red-400 hover:bg-red-500/10 hover:text-red-300 rounded-xl transition-all duration-200 group cursor-pointer"
        >
          <span className="group-hover:-translate-x-1 transition-transform duration-200">
            {icons.logout}
          </span>
          <span className="font-medium text-sm">Logout</span>
        </a>
      </div>
    </div>
  );
}
