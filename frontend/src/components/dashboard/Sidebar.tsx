"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  User,
  Briefcase,
  Layers,
  FileCheck,
  Mail,
  Zap,
} from "lucide-react";
import { clsx } from "clsx";
import { Badge } from "@/components/ui/Badge";
import { FoxLogo } from "@/components/ui/FoxLogo";

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Candidate Profile", href: "/dashboard/profile", icon: User },
  { name: "Job Workspace", href: "/dashboard/jobs", icon: Briefcase },
  { name: "Applications Pipeline", href: "/dashboard/applications", icon: Layers },
  { name: "Mailing System", href: "/dashboard/mailing", icon: Mail },
  { name: "LaTeX Documents", href: "/dashboard/resume", icon: FileCheck },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-950/60 border-r border-slate-800/80 p-4 flex flex-col justify-between hidden md:flex min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        <div>
          <p className="px-3 text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">
            Workspace
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={clsx(
                    "flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 relative group",
                    isActive
                      ? "bg-amber-500/10 text-amber-300 border border-amber-500/30 shadow-sm shadow-amber-500/5 font-semibold"
                      : "text-slate-400 hover:bg-slate-900/80 hover:text-slate-100"
                  )}
                >
                  <Icon
                    className={clsx(
                      "w-4 h-4 transition-colors",
                      isActive ? "text-amber-400" : "text-slate-500 group-hover:text-slate-300"
                    )}
                  />
                  <span>{item.name}</span>
                  {isActive && (
                    <span className="absolute right-3 w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                  )}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FoxLogo className="w-4 h-4" size={16} />
            <span className="text-xs font-bold text-slate-200 tracking-tight">PaperFox Engine</span>
          </div>
          <Badge variant="success" dot>Active</Badge>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          AI Intelligence, LaTeX Compiler & Cold Outreach Online.
        </p>
      </div>
    </aside>
  );
};
