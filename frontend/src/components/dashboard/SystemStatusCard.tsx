"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { User as AuthUser } from "@/types/auth";
import { CandidateProfile } from "@/types/profile";
import { JobHistoryItem, JobHistoryStats, getJobHistoryApi, getJobHistoryStatsApi } from "@/lib/jobs";
import { api } from "@/lib/api";
import {
  Briefcase,
  User,
  Plus,
  Clock,
  ChevronRight,
  ArrowRight,
  Sparkles,
  FileCheck,
  Brain,
  Mail,
  ShieldCheck,
} from "lucide-react";

interface SystemStatusCardProps {
  user: AuthUser;
}

export const SystemStatusCard: React.FC<SystemStatusCardProps> = ({ user }) => {
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [stats, setStats] = useState<JobHistoryStats | null>(null);
  const [recentJobs, setRecentJobs] = useState<JobHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileRes, statsRes, historyRes] = await Promise.allSettled([
          api.get<CandidateProfile>("/profile"),
          getJobHistoryStatsApi(),
          getJobHistoryApi(),
        ]);

        if (profileRes.status === "fulfilled") {
          setProfile(profileRes.value.data);
        }
        if (statsRes.status === "fulfilled") {
          setStats(statsRes.value);
        }
        if (historyRes.status === "fulfilled") {
          setRecentJobs(historyRes.value.items.slice(0, 4));
        }
      } catch (err) {
        // Safe fallback
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const totalProjects = profile?.projects?.length || 0;
  const evidenceProjects =
    profile?.projects?.filter(
      (p) => p.evidence_status === "current" || (p.evidence && Object.keys(p.evidence).length > 0)
    ).length || 0;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Dashboard Overview
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Welcome back, <span className="text-amber-400 font-medium">{user.email}</span>. Your resume intelligence command center.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="success" dot className="px-3.5 py-1 text-xs">
            System Operational
          </Badge>
        </div>
      </div>

      {/* Main Feature Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Candidate Profile Card */}
        <Card hover className="p-6 flex flex-col justify-between space-y-5 border-slate-800/80 bg-slate-900/60">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start space-x-3.5">
              <div className="w-11 h-11 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
                <User className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white tracking-tight">Master Candidate Profile</h2>
                <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">
                  {profile
                    ? `Single source of truth (${profile.completion_percentage}% completed)`
                    : "Create your master profile to prepare for resume generation"}
                </p>
              </div>
            </div>

            <Badge
              variant={profile?.profile_status === "complete" ? "success" : "warning"}
              dot
              className="text-[11px]"
            >
              {profile?.profile_status === "complete" ? "Complete" : "In Progress"}
            </Badge>
          </div>

          <div className="grid grid-cols-3 gap-2 py-3 px-4 rounded-xl bg-slate-950/70 border border-slate-800/80 text-center">
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block tracking-wider">Score</span>
              <span className="text-sm font-bold font-mono text-amber-400">{profile?.completion_percentage || 0}%</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block tracking-wider">Projects</span>
              <span className="text-sm font-bold font-mono text-slate-200">{totalProjects}</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block tracking-wider">Evidence</span>
              <span className="text-sm font-bold font-mono text-emerald-400">{evidenceProjects} Active</span>
            </div>
          </div>

          <Link href="/dashboard/profile">
            <Button variant="outline" size="sm" className="w-full text-xs border-slate-700/80 text-slate-200 hover:bg-slate-800">
              {profile ? "Manage Profile & Evidence" : "Complete Profile"}
              <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
            </Button>
          </Link>
        </Card>

        {/* Application Pipeline Card */}
        <Card hover className="p-6 flex flex-col justify-between space-y-5 border-slate-800/80 bg-slate-900/60">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start space-x-3.5">
              <div className="w-11 h-11 rounded-2xl bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center shrink-0">
                <Briefcase className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white tracking-tight">Applications Pipeline</h2>
                <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">
                  Track stages from draft to applied, interview, and offer
                </p>
              </div>
            </div>

            <Badge variant="info" className="text-[11px] font-mono">
              {stats?.total || 0} Total
            </Badge>
          </div>

          <div className="grid grid-cols-4 gap-2 py-3 px-4 rounded-xl bg-slate-950/70 border border-slate-800/80 text-center">
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block tracking-wider">Draft</span>
              <span className="text-sm font-bold font-mono text-slate-300">{stats?.by_status?.draft || 0}</span>
            </div>
            <div>
              <span className="text-[10px] text-sky-400 uppercase font-semibold block tracking-wider">Applied</span>
              <span className="text-sm font-bold font-mono text-sky-300">{stats?.by_status?.applied || 0}</span>
            </div>
            <div>
              <span className="text-[10px] text-amber-400 uppercase font-semibold block tracking-wider">Interview</span>
              <span className="text-sm font-bold font-mono text-amber-300">{stats?.by_status?.interview || 0}</span>
            </div>
            <div>
              <span className="text-[10px] text-emerald-400 uppercase font-semibold block tracking-wider">Offer</span>
              <span className="text-sm font-bold font-mono text-emerald-300">{stats?.by_status?.offer || 0}</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link href="/dashboard/jobs" className="flex-1">
              <Button variant="primary" size="sm" className="w-full text-xs">
                <Plus className="w-3.5 h-3.5 mr-1" /> New Job JD
              </Button>
            </Link>
            <Link href="/dashboard/applications" className="flex-1">
              <Button variant="outline" size="sm" className="w-full text-xs border-slate-700/80 text-slate-200 hover:bg-slate-800">
                View Pipeline <ChevronRight className="w-3.5 h-3.5 ml-1" />
              </Button>
            </Link>
          </div>
        </Card>
      </div>

      {/* Recent Applications Section */}
      {recentJobs.length > 0 && (
        <div className="space-y-3 pt-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-3.5 h-3.5 text-amber-400" /> Recent Target Jobs
            </h3>
            <Link href="/dashboard/applications" className="text-xs text-amber-400 hover:text-amber-300 font-medium">
              View all ({stats?.total || 0}) →
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {recentJobs.map((job) => (
              <div
                key={job.id}
                className="p-4 rounded-xl border border-slate-800/80 bg-slate-900/50 hover:bg-slate-900/80 transition-all flex items-center justify-between gap-3 group"
              >
                <div className="space-y-0.5 min-w-0">
                  <h4 className="text-sm font-semibold text-white truncate">{job.role_title}</h4>
                  <p className="text-xs text-amber-400 font-medium truncate">{job.company_name}</p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <Badge variant="neutral" className="text-[11px] uppercase">
                    {job.application_status}
                  </Badge>
                  <Link href="/dashboard/jobs">
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-slate-400 group-hover:text-white">
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Product Value Intelligence Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
        <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80 flex items-center space-x-3.5">
          <div className="w-9 h-9 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center shrink-0">
            <FileCheck className="w-4 h-4" />
          </div>
          <div className="text-xs">
            <p className="font-bold text-slate-200">Deterministic LaTeX</p>
            <p className="text-slate-400 text-[11px]">100% Single-page mathematical formatting</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80 flex items-center space-x-3.5">
          <div className="w-9 h-9 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center shrink-0">
            <Brain className="w-4 h-4" />
          </div>
          <div className="text-xs">
            <p className="font-bold text-slate-200">JD Intelligence Engine</p>
            <p className="text-slate-400 text-[11px]">Key competency & skill gap extraction</p>
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800/80 flex items-center space-x-3.5">
          <div className="w-9 h-9 rounded-xl bg-sky-500/10 text-sky-400 border border-sky-500/20 flex items-center justify-center shrink-0">
            <Mail className="w-4 h-4" />
          </div>
          <div className="text-xs">
            <p className="font-bold text-slate-200">Cold Outreach Module</p>
            <p className="text-slate-400 text-[11px]">Targeted hiring manager & recruiter messages</p>
          </div>
        </div>
      </div>
    </div>
  );
};
