"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  User,
  Sparkles,
  FileCheck,
  Settings,
  Lock,
} from "lucide-react";
import { clsx } from "clsx";
import { Badge } from "@/components/ui/Badge";

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  phase2?: boolean;
}

const navItems: NavItem[] = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Candidate Profile", href: "/dashboard/profile", icon: User },
  { name: "Resume Optimizer", href: "#", icon: Sparkles, phase2: true },
  { name: "LaTeX Documents", href: "/dashboard/resume", icon: FileCheck },
  { name: "System Settings", href: "#", icon: Settings, phase2: true },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-900/60 border-r border-slate-800/80 p-4 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div>
          <p className="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
            Navigation
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              if (item.phase2) {
                return (
                  <div
                    key={item.name}
                    className="flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium text-slate-500 cursor-not-allowed hover:bg-slate-900/40 opacity-70"
                    title="Phase 2 Feature"
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className="w-4 h-4 text-slate-600" />
                      <span>{item.name}</span>
                    </div>
                    <Lock className="w-3 h-3 text-slate-600" />
                  </div>
                );
              }

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={clsx(
                    "flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150",
                    isActive
                      ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
                  )}
                >
                  <Icon
                    className={clsx(
                      "w-4 h-4",
                      isActive ? "text-amber-400" : "text-slate-400"
                    )}
                  />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-3.5 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-300">Phase 1 Target</span>
          <Badge variant="success">Active</Badge>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          Foundation & Auth active. Service layers & API readiness complete.
        </p>
      </div>
    </aside>
  );
};
