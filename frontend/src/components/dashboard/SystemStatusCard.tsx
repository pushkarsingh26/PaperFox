"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { CheckCircle2, ShieldCheck, Database, Cpu, User, ArrowRight } from "lucide-react";
import { User as AuthUser } from "@/types/auth";
import { CandidateProfile } from "@/types/profile";
import { JobHistoryItem, JobHistoryStats, getJobHistoryApi, getJobHistoryStatsApi } from "@/lib/jobs";
import { api } from "@/lib/api";
import {
  Briefcase,
  Layers,
  Sparkles,
  Plus,
  Clock,
  Send,
  Calendar,
  Award,
  ChevronRight,
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
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Dashboard Overview
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Welcome back, <span className="text-amber-400 font-medium">{user.email}</span>. Your resume intelligence command center.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="success" className="px-3 py-1 text-xs">
            <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> System Operational
          </Badge>
        </div>
      </div>

      {/* Main Feature Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Candidate Profile Card */}
        <Card className="bg-slate-900/80 border-slate-800 p-6 flex flex-col justify-between space-y-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start space-x-3.5">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
                <User className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white">Master Profile</h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  {profile
                    ? `Single source of truth (${profile.completion_percentage}% complete)`
                    : "Create your master profile to prepare for resume generation"}
                </p>
              </div>
            </div>

            <Badge
              variant={profile?.profile_status === "complete" ? "success" : "warning"}
              className="text-[11px]"
            >
              {profile?.profile_status === "complete" ? "Complete" : "In Progress"}
            </Badge>
          </div>

          <div className="grid grid-cols-3 gap-2 py-3 px-4 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Score</span>
              <span className="text-sm font-bold font-mono text-amber-400">{profile?.completion_percentage || 0}%</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Projects</span>
              <span className="text-sm font-bold font-mono text-slate-200">{totalProjects}</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Evidence</span>
              <span className="text-sm font-bold font-mono text-emerald-400">{evidenceProjects} Active</span>
            </div>
          </div>

          <Link href="/dashboard/profile">
            <Button variant="outline" size="sm" className="w-full text-xs border-slate-700 text-slate-200 hover:bg-slate-800">
              {profile ? "Manage Profile & Evidence" : "Complete Profile"}
              <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
            </Button>
          </Link>
        </Card>

        {/* Application Pipeline Card */}
        <Card className="bg-slate-900/80 border-slate-800 p-6 flex flex-col justify-between space-y-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start space-x-3.5">
              <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center shrink-0">
                <Briefcase className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white">Application Pipeline</h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Track stages from draft to applied, interview, and offer
                </p>
              </div>
            </div>

            <span className="text-xs font-mono font-bold text-blue-400 px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20">
              {stats?.total || 0} Total
            </span>
          </div>

          <div className="grid grid-cols-4 gap-2 py-3 px-4 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Draft</span>
              <span className="text-sm font-bold font-mono text-slate-300">{stats?.by_status?.draft || 0}</span>
            </div>
            <div>
              <span className="text-[10px] text-blue-400 uppercase font-semibold block">Applied</span>
              <span className="text-sm font-bold font-mono text-blue-300">{stats?.by_status?.applied || 0}</span>
            </div>
            <div>
              <span className="text-[10px] text-amber-400 uppercase font-semibold block">Interview</span>
              <span className="text-sm font-bold font-mono text-amber-300">{stats?.by_status?.interview || 0}</span>
            </div>
            <div>
              <span className="text-[10px] text-emerald-400 uppercase font-semibold block">Offer</span>
              <span className="text-sm font-bold font-mono text-emerald-300">{stats?.by_status?.offer || 0}</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link href="/dashboard/jobs" className="flex-1">
              <Button variant="primary" size="sm" className="w-full text-xs bg-amber-500 text-slate-950 font-semibold hover:bg-amber-400">
                <Plus className="w-3.5 h-3.5 mr-1" /> New Job JD
              </Button>
            </Link>
            <Link href="/dashboard/applications" className="flex-1">
              <Button variant="outline" size="sm" className="w-full text-xs border-slate-700 text-slate-200 hover:bg-slate-800">
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
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-400" /> Recent Applications
            </h3>
            <Link href="/dashboard/applications" className="text-xs text-amber-400 hover:underline">
              View all ({stats?.total || 0}) →
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {recentJobs.map((job) => (
              <div
                key={job.id}
                className="p-4 rounded-xl border border-slate-800/80 bg-slate-900/50 hover:bg-slate-900/80 transition-all flex items-center justify-between gap-3"
              >
                <div className="space-y-0.5">
                  <h4 className="text-sm font-semibold text-white line-clamp-1">{job.role_title}</h4>
                  <p className="text-xs text-amber-400 font-medium">{job.company_name}</p>
                </div>

                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold border uppercase bg-slate-800 text-slate-300 border-slate-700">
                    {job.application_status}
                  </span>
                  <Link href="/dashboard/jobs">
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-slate-400 hover:text-white">
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Architecture & Reliability Status Badges */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
        <div className="p-3.5 rounded-xl bg-slate-900/40 border border-slate-800/80 flex items-center space-x-3">
          <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
          <div className="text-xs">
            <p className="font-semibold text-slate-200">JWT Session Security</p>
            <p className="text-slate-400 text-[11px]">Rotation & Revocation Active</p>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-900/40 border border-slate-800/80 flex items-center space-x-3">
          <Database className="w-5 h-5 text-amber-400 shrink-0" />
          <div className="text-xs">
            <p className="font-semibold text-slate-200">MongoDB Atlas</p>
            <p className="text-slate-400 text-[11px]">Production Indexes Ensured</p>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-900/40 border border-slate-800/80 flex items-center space-x-3">
          <Cpu className="w-5 h-5 text-sky-400 shrink-0" />
          <div className="text-xs">
            <p className="font-semibold text-slate-200">Free AI Router & LaTeX</p>
            <p className="text-slate-400 text-[11px]">Gemini, Groq, OpenRouter Active</p>
          </div>
        </div>
      </div>
    </div>
  );
};
