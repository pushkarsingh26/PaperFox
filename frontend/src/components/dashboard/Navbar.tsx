"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/Button";
import { FoxLogo } from "@/components/ui/FoxLogo";
import {
  LogOut,
  User as UserIcon,
  Menu,
  X,
  LayoutDashboard,
  Briefcase,
  Layers,
  FileCheck,
  Mail,
} from "lucide-react";
import { clsx } from "clsx";

const navItems = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Candidate Profile", href: "/dashboard/profile", icon: UserIcon },
  { name: "Job Workspace", href: "/dashboard/jobs", icon: Briefcase },
  { name: "Applications Pipeline", href: "/dashboard/applications", icon: Layers },
  { name: "Mailing System", href: "/dashboard/mailing", icon: Mail },
  { name: "LaTeX Documents", href: "/dashboard/resume", icon: FileCheck },
];

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <>
      <header className="h-16 bg-slate-950/80 border-b border-slate-800/80 backdrop-blur-xl sticky top-0 z-40 px-4 sm:px-6 flex items-center justify-between">
      {/* Brand & Mobile Toggle */}
      <div className="flex items-center space-x-3">
        <button
          type="button"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors"
          aria-label="Toggle navigation menu"
        >
          {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>

        <Link href="/dashboard" className="flex items-center space-x-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-600/20 to-amber-400/20 border border-amber-500/30 flex items-center justify-center shadow-lg shadow-amber-500/10 group-hover:scale-105 transition-transform duration-200 p-1.5">
            <FoxLogo className="w-6 h-6" size={24} priority />
          </div>
          <span className="font-bold text-lg text-white tracking-tight">
            Paper<span className="text-amber-500">Fox</span>
          </span>
        </Link>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-3">
        {user && (
          <div className="flex items-center space-x-3 border-l border-slate-800/80 pl-3 sm:pl-4">
            <div className="hidden sm:flex items-center space-x-2 bg-slate-900/80 px-3 py-1.5 rounded-xl border border-slate-800/80 text-xs">
              <div className="w-6 h-6 rounded-lg bg-amber-500/15 text-amber-400 flex items-center justify-center font-bold">
                <UserIcon className="w-3.5 h-3.5" />
              </div>
              <span className="font-medium text-slate-300 max-w-[160px] truncate">
                {user.email}
              </span>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => logout()}
              className="text-xs text-slate-300 hover:text-white px-3"
            >
              <LogOut className="w-3.5 h-3.5 mr-1 sm:mr-1.5" />
              <span className="hidden sm:inline">Logout</span>
            </Button>
          </div>
        )}
      </div>
    </header>

    {/* Mobile Navigation Drawer Overlay */}
    {mobileMenuOpen && (
      <div className="fixed inset-x-0 top-16 bottom-0 z-50 bg-[#090d16] border-b border-slate-800 md:hidden p-5 space-y-4 overflow-y-auto shadow-2xl">
        {user && (
          <div className="flex items-center space-x-2.5 p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs mb-2">
            <div className="w-7 h-7 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold">
              <UserIcon className="w-4 h-4" />
            </div>
            <div className="truncate">
              <p className="text-slate-200 font-semibold truncate">{user.email}</p>
              <p className="text-[10px] text-slate-400">Signed In</p>
            </div>
          </div>
        )}

        <nav className="space-y-1.5">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={clsx(
                  "flex items-center space-x-3 px-3.5 py-3 rounded-xl text-sm font-medium transition-colors duration-150",
                  isActive
                    ? "bg-amber-500/15 text-amber-300 border border-amber-500/30 font-semibold"
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
    )}
  </>
  );
};
