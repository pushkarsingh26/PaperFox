"use client";

import React from "react";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Navbar } from "@/components/dashboard/Navbar";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { ProfileFormShell } from "@/components/profile/ProfileFormShell";

export default function CandidateProfilePage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950 flex flex-col selection:bg-amber-500/30 selection:text-amber-200">
        <Navbar />

        <div className="flex-1 flex">
          <Sidebar />

          <main className="flex-1 p-6 md:p-10 max-w-6xl">
            <ProfileFormShell />
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
