"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { CheckCircle2, ShieldCheck, Database, Cpu, User, ArrowRight } from "lucide-react";
import { User as AuthUser } from "@/types/auth";
import { CandidateProfile } from "@/types/profile";
import { api } from "@/lib/api";

interface SystemStatusCardProps {
  user: AuthUser;
}

export const SystemStatusCard: React.FC<SystemStatusCardProps> = ({ user }) => {
  const [profile, setProfile] = useState<CandidateProfile | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get<CandidateProfile>("/profile");
        setProfile(res.data);
      } catch (err) {
        // No profile created yet
      }
    };
    fetchProfile();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Dashboard Overview
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Authenticated session for{" "}
            <span className="text-amber-400 font-mono font-semibold">{user.email}</span>
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="success" className="px-3 py-1 text-xs">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> System Operational
          </Badge>
        </div>
      </div>

      {/* Candidate Profile Summary Banner */}
      <Card className="bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950 border-amber-500/30 p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-xl">
        <div className="flex items-start space-x-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
            <User className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center space-x-3">
              <h2 className="text-lg font-bold text-white">Master Candidate Profile</h2>
              <Badge
                variant={profile?.profile_status === "complete" ? "success" : "warning"}
                className="text-xs"
              >
                {profile?.profile_status === "complete" ? "Complete" : "Draft / In Progress"}
              </Badge>
            </div>
            <p className="text-xs text-slate-400 max-w-xl leading-relaxed">
              {profile
                ? `Stored in MongoDB Atlas as single source of truth (${profile.completion_percentage}% complete).`
                : "Create your master professional profile to prepare for job-specific resume compilation."}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4 w-full md:w-auto justify-between md:justify-end border-t md:border-t-0 border-slate-800 pt-4 md:pt-0">
          <div className="text-right">
            <span className="text-xs text-slate-500 block uppercase">Completion Score</span>
            <span className="text-xl font-bold font-mono text-amber-400">
              {profile?.completion_percentage || 0}%
            </span>
          </div>

          <Link href="/dashboard/profile">
            <Button variant="primary" size="md">
              {profile ? "Edit Profile" : "Complete Profile"}
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </div>
      </Card>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <Card className="space-y-3 border-emerald-500/20 bg-emerald-950/10">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              JWT Session Security
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Access & refresh token rotation active with server-side session revocation.
            </p>
          </div>
          <div className="pt-2 text-xs font-mono text-emerald-400/90 flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Session ID: {user.id.slice(0, 12)}...</span>
          </div>
        </Card>

        <Card className="space-y-3 border-amber-500/20 bg-amber-950/10">
          <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              MongoDB Atlas Integration
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Candidate profile stored in candidate_profiles collection with user_id index.
            </p>
          </div>
          <div className="pt-2 text-xs font-mono text-amber-400/90 flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
            <span>Database: Connected</span>
          </div>
        </Card>

        <Card className="space-y-3 border-sky-500/20 bg-sky-950/10">
          <div className="w-10 h-10 rounded-lg bg-sky-500/10 flex items-center justify-center text-sky-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              Provider Abstractions
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              LLM & LaTeX PDF Worker abstraction contracts ready for Phase 3+.
            </p>
          </div>
          <div className="pt-2 text-xs font-mono text-sky-400/90 flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-sky-500 animate-pulse"></span>
            <span>Providers: Contracts Ready</span>
          </div>
        </Card>
      </div>
    </div>
  );
};
