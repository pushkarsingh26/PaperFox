"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { Navbar } from "@/components/dashboard/Navbar";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Button } from "@/components/ui/Button";
import {
  ApplicationStatus,
  JobHistoryItem,
  JobHistoryStats,
  getJobHistoryApi,
  getJobHistoryStatsApi,
  updateJobStatusApi,
  getJobResumePdfUrl,
} from "@/lib/jobs";
import {
  Briefcase,
  Search,
  Filter,
  RefreshCw,
  AlertCircle,
  Clock,
  Calendar,
  Award,
  XCircle,
  CornerUpLeft,
  FileEdit,
  Send,
  FileText,
  Download,
  ExternalLink,
  ChevronRight,
  CheckCircle2,
  Sparkles,
  Layers,
} from "lucide-react";

const STATUS_CONFIG: Record<
  ApplicationStatus,
  {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    badgeClass: string;
    color: string;
  }
> = {
  draft: {
    label: "Draft",
    icon: FileEdit,
    badgeClass: "bg-slate-800 text-slate-300 border-slate-700",
    color: "text-slate-400",
  },
  applied: {
    label: "Applied",
    icon: Send,
    badgeClass: "bg-blue-500/20 text-blue-300 border-blue-500/40",
    color: "text-blue-400",
  },
  interview: {
    label: "Interviewing",
    icon: Calendar,
    badgeClass: "bg-amber-500/20 text-amber-300 border-amber-500/40",
    color: "text-amber-400",
  },
  offer: {
    label: "Offer",
    icon: Award,
    badgeClass: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
    color: "text-emerald-400",
  },
  rejected: {
    label: "Rejected",
    icon: XCircle,
    badgeClass: "bg-red-500/20 text-red-300 border-red-500/40",
    color: "text-red-400",
  },
  withdrawn: {
    label: "Withdrawn",
    icon: CornerUpLeft,
    badgeClass: "bg-zinc-800 text-zinc-400 border-zinc-700",
    color: "text-zinc-400",
  },
};

export default function ApplicationsHistoryPage() {
  const [items, setItems] = useState<JobHistoryItem[]>([]);
  const [stats, setStats] = useState<JobHistoryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [historyRes, statsRes] = await Promise.all([
        getJobHistoryApi(statusFilter || undefined),
        getJobHistoryStatsApi(),
      ]);
      setItems(historyRes.items);
      setStats(statsRes);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to load application history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [statusFilter]);

  const handleQuickStatusChange = async (jobId: string, newStatus: ApplicationStatus) => {
    setUpdatingId(jobId);
    try {
      await updateJobStatusApi(jobId, newStatus);
      setItems((prev) =>
        prev.map((item) =>
          item.id === jobId
            ? {
                ...item,
                application_status: newStatus,
                status_updated_at: new Date().toISOString(),
              }
            : item
        )
      );
      // Refresh stats
      const updatedStats = await getJobHistoryStatsApi();
      setStats(updatedStats);
    } catch (err: any) {
      alert(err?.response?.data?.detail || "Failed to update status.");
    } finally {
      setUpdatingId(null);
    }
  };

  const filteredItems = items.filter((item) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      item.company_name.toLowerCase().includes(q) ||
      item.role_title.toLowerCase().includes(q) ||
      (item.location && item.location.toLowerCase().includes(q))
    );
  });

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950 flex flex-col text-slate-100 selection:bg-amber-500/30 selection:text-amber-200">
        <Navbar />

        <div className="flex-1 flex">
          <Sidebar />

          <main className="flex-1 p-6 md:p-8 max-w-7xl">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
                  <Briefcase className="w-6 h-6 text-amber-400" />
                  Application History & Pipeline
                </h1>
                <p className="text-sm text-slate-400 mt-1">
                  Track and manage job applications across every stage of the hiring process.
                </p>
              </div>

              <Link href="/dashboard/jobs">
                <Button
                  variant="primary"
                  className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold flex items-center gap-2"
                >
                  <Briefcase className="w-4 h-4" /> Go to Job Workspace
                </Button>
              </Link>
            </div>

            {/* Error Banner */}
            {error && (
              <div className="mb-6 p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-red-300 flex items-center gap-3">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{error}</span>
                <Button variant="outline" size="sm" onClick={fetchData} className="ml-auto">
                  Retry
                </Button>
              </div>
            )}

            {/* Stats Overview Metric Cards */}
            {stats && (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
                {/* Total */}
                <div
                  onClick={() => setStatusFilter(null)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    statusFilter === null
                      ? "bg-slate-800/90 border-amber-500/40 ring-1 ring-amber-500/20"
                      : "bg-slate-900/50 border-slate-800/80 hover:bg-slate-900/80"
                  }`}
                >
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Total
                  </span>
                  <p className="text-2xl font-bold text-white mt-1">{stats.total}</p>
                </div>

                {/* Draft */}
                <div
                  onClick={() => setStatusFilter("draft")}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    statusFilter === "draft"
                      ? "bg-slate-800/90 border-slate-500 ring-1 ring-slate-500/20"
                      : "bg-slate-900/50 border-slate-800/80 hover:bg-slate-900/80"
                  }`}
                >
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                    <FileEdit className="w-3 h-3" /> Draft
                  </span>
                  <p className="text-2xl font-bold text-slate-300 mt-1">
                    {stats.by_status.draft || 0}
                  </p>
                </div>

                {/* Applied */}
                <div
                  onClick={() => setStatusFilter("applied")}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    statusFilter === "applied"
                      ? "bg-blue-950/40 border-blue-500 ring-1 ring-blue-500/20"
                      : "bg-slate-900/50 border-slate-800/80 hover:bg-slate-900/80"
                  }`}
                >
                  <span className="text-[11px] font-semibold text-blue-400 uppercase tracking-wider flex items-center gap-1">
                    <Send className="w-3 h-3" /> Applied
                  </span>
                  <p className="text-2xl font-bold text-blue-300 mt-1">
                    {stats.by_status.applied || 0}
                  </p>
                </div>

                {/* Interviewing */}
                <div
                  onClick={() => setStatusFilter("interview")}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    statusFilter === "interview"
                      ? "bg-amber-950/40 border-amber-500 ring-1 ring-amber-500/20"
                      : "bg-slate-900/50 border-slate-800/80 hover:bg-slate-900/80"
                  }`}
                >
                  <span className="text-[11px] font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1">
                    <Calendar className="w-3 h-3" /> Interviewing
                  </span>
                  <p className="text-2xl font-bold text-amber-300 mt-1">
                    {stats.by_status.interview || 0}
                  </p>
                </div>

                {/* Offer */}
                <div
                  onClick={() => setStatusFilter("offer")}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    statusFilter === "offer"
                      ? "bg-emerald-950/40 border-emerald-500 ring-1 ring-emerald-500/20"
                      : "bg-slate-900/50 border-slate-800/80 hover:bg-slate-900/80"
                  }`}
                >
                  <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                    <Award className="w-3 h-3" /> Offer
                  </span>
                  <p className="text-2xl font-bold text-emerald-300 mt-1">
                    {stats.by_status.offer || 0}
                  </p>
                </div>

                {/* Rejected / Withdrawn */}
                <div
                  onClick={() => setStatusFilter("rejected")}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    statusFilter === "rejected"
                      ? "bg-red-950/40 border-red-500 ring-1 ring-red-500/20"
                      : "bg-slate-900/50 border-slate-800/80 hover:bg-slate-900/80"
                  }`}
                >
                  <span className="text-[11px] font-semibold text-red-400 uppercase tracking-wider flex items-center gap-1">
                    <XCircle className="w-3 h-3" /> Rejected
                  </span>
                  <p className="text-2xl font-bold text-red-300 mt-1">
                    {(stats.by_status.rejected || 0) + (stats.by_status.withdrawn || 0)}
                  </p>
                </div>
              </div>
            )}

            {/* Filter and Search Bar */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mb-6">
              {/* Search */}
              <div className="relative w-full sm:w-72">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  placeholder="Search role, company..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3.5 py-2 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500/50"
                />
              </div>

              {/* Status Filter Buttons */}
              <div className="flex flex-wrap items-center gap-1.5 w-full sm:w-auto">
                <button
                  type="button"
                  onClick={() => setStatusFilter(null)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    statusFilter === null
                      ? "bg-amber-500 text-slate-950 shadow-sm"
                      : "bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800"
                  }`}
                >
                  All ({stats?.total || 0})
                </button>
                {(Object.keys(STATUS_CONFIG) as ApplicationStatus[]).map((st) => {
                  const cfg = STATUS_CONFIG[st];
                  const isSelected = statusFilter === st;
                  const count = stats?.by_status[st] || 0;

                  return (
                    <button
                      key={st}
                      type="button"
                      onClick={() => setStatusFilter(st)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        isSelected
                          ? "bg-slate-800 text-amber-300 border border-amber-500/40"
                          : "bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800"
                      }`}
                    >
                      {cfg.label} ({count})
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Applications List */}
            {loading ? (
              <div className="p-16 rounded-2xl bg-slate-900/40 border border-slate-800 text-center space-y-3">
                <RefreshCw className="w-8 h-8 text-amber-400 animate-spin mx-auto" />
                <p className="text-sm text-slate-400">Loading application history...</p>
              </div>
            ) : filteredItems.length === 0 ? (
              <div className="p-16 rounded-2xl bg-slate-900/40 border border-dashed border-slate-800 text-center space-y-4">
                <Briefcase className="w-12 h-12 text-slate-600 mx-auto" />
                <div>
                  <h3 className="text-base font-semibold text-slate-200">
                    No Applications Found
                  </h3>
                  <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                    {searchQuery || statusFilter
                      ? "No applications matched your filter criteria."
                      : "Create your first job application in the Job Workspace to start tracking."}
                  </p>
                </div>
                <Link href="/dashboard/jobs">
                  <Button variant="primary" size="sm" className="bg-amber-500 text-slate-950 font-semibold">
                    Open Job Workspace
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredItems.map((item) => {
                  const st = (item.application_status as ApplicationStatus) || "draft";
                  const cfg = STATUS_CONFIG[st] || STATUS_CONFIG.draft;
                  const Icon = cfg.icon;

                  const createdDate = new Date(item.created_at).toLocaleDateString(undefined, {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                  });

                  return (
                    <div
                      key={item.id}
                      className="p-5 rounded-2xl border border-slate-800/80 bg-slate-900/60 hover:bg-slate-900/80 transition-all space-y-4"
                    >
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2.5">
                            <h3 className="text-base font-bold text-white">{item.role_title}</h3>
                            {item.job_url && (
                              <a
                                href={item.job_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-slate-400 hover:text-amber-400 transition-colors"
                              >
                                <ExternalLink className="w-3.5 h-3.5" />
                              </a>
                            )}
                          </div>
                          <p className="text-xs font-semibold text-amber-400">
                            {item.company_name}
                            {item.location && (
                              <span className="text-slate-400 font-normal ml-2">
                                • {item.location}
                              </span>
                            )}
                            <span className="text-slate-500 font-normal ml-2">
                              • Added {createdDate}
                            </span>
                          </p>
                        </div>

                        {/* Status selector & Action buttons */}
                        <div className="flex flex-wrap items-center gap-3">
                          {/* Quick Status Select */}
                          <div className="flex items-center gap-1.5">
                            <select
                              value={st}
                              disabled={updatingId === item.id}
                              onChange={(e) =>
                                handleQuickStatusChange(
                                  item.id,
                                  e.target.value as ApplicationStatus
                                )
                              }
                              className={`px-3 py-1.5 rounded-lg text-xs font-semibold border bg-slate-950 focus:outline-none focus:ring-1 focus:ring-amber-500/50 cursor-pointer ${cfg.badgeClass}`}
                            >
                              {(Object.keys(STATUS_CONFIG) as ApplicationStatus[]).map((s) => (
                                <option key={s} value={s} className="bg-slate-900 text-slate-200">
                                  {STATUS_CONFIG[s].label}
                                </option>
                              ))}
                            </select>
                            {updatingId === item.id && (
                              <RefreshCw className="w-3.5 h-3.5 text-amber-400 animate-spin" />
                            )}
                          </div>

                          {/* PDF Download link if generated */}
                          {item.is_resume_generated && (
                            <a
                              href={getJobResumePdfUrl(item.id)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/20 transition-all"
                            >
                              <Download className="w-3.5 h-3.5" /> Download PDF
                            </a>
                          )}

                          <Link href="/dashboard/jobs">
                            <Button
                              variant="outline"
                              size="sm"
                              className="text-xs border-slate-700 text-slate-300 hover:bg-slate-800"
                            >
                              Workspace <ChevronRight className="w-3.5 h-3.5 ml-1" />
                            </Button>
                          </Link>
                        </div>
                      </div>

                      {/* Feature Pills */}
                      <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/60 text-xs">
                        {item.is_analyzed ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            <CheckCircle2 className="w-3 h-3" /> JD Analyzed
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-400 border border-slate-700">
                            <Clock className="w-3 h-3" /> JD Unanalyzed
                          </span>
                        )}

                        {item.is_optimized ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                            <Sparkles className="w-3 h-3" /> Resume Optimized
                          </span>
                        ) : null}

                        {item.is_resume_generated ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                            <FileText className="w-3 h-3" /> PDF Generated
                          </span>
                        ) : null}
                      </div>

                      {/* Notes snippet */}
                      {item.notes && item.notes.trim() && (
                        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs text-slate-300 leading-relaxed">
                          <span className="font-semibold text-amber-400/90 mr-1.5">Note:</span>
                          {item.notes}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
