"use client";

import { usePathname } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLoginPage = pathname === "/login" || pathname === "/";
  const [mounted, setMounted] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
    const token = localStorage.getItem("token");
    if (!token && !isLoginPage) {
      router.push("/login");
    } else if (token && pathname === "/") {
      router.push("/dashboard");
    }
  }, [pathname, isLoginPage, router]);

  if (!mounted) return <div className="h-screen bg-gray-100" />;

  return (
    <div className="flex h-screen overflow-hidden bg-gray-100 text-gray-900 print:h-auto print:overflow-visible print:bg-white">
      {!isLoginPage && <Sidebar />}
      <main className="flex-1 overflow-y-auto print:overflow-visible print:block">
        {children}
      </main>
    </div>
  );
}
