"use client";

import React, { useState } from "react";
import {
  ApplicationStatus,
  updateJobStatusApi,
  updateJobNotesApi,
  JobApplication,
} from "@/lib/jobs";
import { Button } from "@/components/ui/Button";
import {
  Clock,
  Send,
  Calendar,
  Award,
  XCircle,
  CornerUpLeft,
  FileEdit,
  Save,
  CheckCircle2,
  Loader2,
  AlertCircle,
  StickyNote,
} from "lucide-react";

interface ApplicationStatusPanelProps {
  job: JobApplication;
  onJobUpdated: (updatedJob: JobApplication) => void;
}

const STATUS_CONFIG: Record<
  ApplicationStatus,
  {
    label: string;
    description: string;
    icon: React.ComponentType<{ className?: string }>;
    badgeClass: string;
    activeBorder: string;
    activeBg: string;
    activeText: string;
  }
> = {
  draft: {
    label: "Draft",
    description: "Preparing resume and application materials",
    icon: FileEdit,
    badgeClass: "bg-slate-800 text-slate-300 border-slate-700",
    activeBorder: "border-slate-500",
    activeBg: "bg-slate-800/80",
    activeText: "text-slate-200",
  },
  applied: {
    label: "Applied",
    description: "Application submitted to employer",
    icon: Send,
    badgeClass: "bg-blue-500/20 text-blue-300 border-blue-500/40",
    activeBorder: "border-blue-500",
    activeBg: "bg-blue-500/10",
    activeText: "text-blue-300",
  },
  interview: {
    label: "Interviewing",
    description: "Phone screen, technical rounds, or onsite",
    icon: Calendar,
    badgeClass: "bg-amber-500/20 text-amber-300 border-amber-500/40",
    activeBorder: "border-amber-500",
    activeBg: "bg-amber-500/10",
    activeText: "text-amber-300",
  },
  offer: {
    label: "Offer Received",
    description: "Received formal job offer",
    icon: Award,
    badgeClass: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
    activeBorder: "border-emerald-500",
    activeBg: "bg-emerald-500/10",
    activeText: "text-emerald-300",
  },
  rejected: {
    label: "Rejected",
    description: "Application was not selected",
    icon: XCircle,
    badgeClass: "bg-red-500/20 text-red-300 border-red-500/40",
    activeBorder: "border-red-500",
    activeBg: "bg-red-500/10",
    activeText: "text-red-300",
  },
  withdrawn: {
    label: "Withdrawn",
    description: "Withdrawn by candidate",
    icon: CornerUpLeft,
    badgeClass: "bg-zinc-800 text-zinc-400 border-zinc-700",
    activeBorder: "border-zinc-500",
    activeBg: "bg-zinc-800/80",
    activeText: "text-zinc-300",
  },
};

export const ApplicationStatusPanel: React.FC<ApplicationStatusPanelProps> = ({
  job,
  onJobUpdated,
}) => {
  const currentStatus = (job.application_status as ApplicationStatus) || "draft";
  const [notes, setNotes] = useState(job.notes || "");
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [isSavingNotes, setIsSavingNotes] = useState(false);
  const [notesSavedSuccess, setNotesSavedSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleStatusChange = async (newStatus: ApplicationStatus) => {
    if (newStatus === currentStatus || isUpdatingStatus) return;
    setIsUpdatingStatus(true);
    setErrorMessage(null);

    try {
      const updated = await updateJobStatusApi(job.id, newStatus);
      onJobUpdated(updated);
    } catch (err: any) {
      console.error("Failed to update status:", err);
      setErrorMessage(
        err?.response?.data?.detail || err?.message || "Failed to update status."
      );
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleSaveNotes = async () => {
    setIsSavingNotes(true);
    setErrorMessage(null);
    try {
      const updated = await updateJobNotesApi(job.id, notes);
      onJobUpdated(updated);
      setNotesSavedSuccess(true);
      setTimeout(() => setNotesSavedSuccess(false), 2500);
    } catch (err: any) {
      console.error("Failed to save notes:", err);
      setErrorMessage(
        err?.response?.data?.detail || err?.message || "Failed to save notes."
      );
    } finally {
      setIsSavingNotes(false);
    }
  };

  const currentConfig = STATUS_CONFIG[currentStatus] || STATUS_CONFIG.draft;
  const CurrentIcon = currentConfig.icon;

  const formattedStatusDate = job.status_updated_at
    ? new Date(job.status_updated_at).toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : null;

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-6">
      {/* Header with current status */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <CurrentIcon className="w-5 h-5 text-amber-500" /> Application Lifecycle & Tracking
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Track stage progress, interview notes, and application status for {job.company_name}.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${currentConfig.badgeClass}`}
          >
            <CurrentIcon className="w-3.5 h-3.5" /> {currentConfig.label}
          </span>
          {formattedStatusDate && (
            <span className="text-slate-400 text-xs flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" /> {formattedStatusDate}
            </span>
          )}
        </div>
      </div>

      {errorMessage && (
        <div className="p-3 rounded-lg bg-red-950/40 border border-red-500/40 text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Stage Selector */}
      <div className="space-y-3">
        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
          Transition Application Stage
        </label>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
          {(Object.keys(STATUS_CONFIG) as ApplicationStatus[]).map((st) => {
            const cfg = STATUS_CONFIG[st];
            const Icon = cfg.icon;
            const isSelected = currentStatus === st;

            return (
              <button
                key={st}
                type="button"
                disabled={isUpdatingStatus}
                onClick={() => handleStatusChange(st)}
                className={`flex flex-col items-center justify-center p-3 rounded-xl border text-xs font-medium transition-all text-center gap-1.5 ${
                  isSelected
                    ? `${cfg.activeBorder} ${cfg.activeBg} ${cfg.activeText} shadow-md ring-1 ring-white/10`
                    : "border-slate-800 bg-slate-950/40 text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                }`}
              >
                <Icon className={`w-4 h-4 ${isSelected ? cfg.activeText : "text-slate-400"}`} />
                <span>{cfg.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Notes Section */}
      <div className="space-y-3 pt-2 border-t border-slate-800">
        <div className="flex items-center justify-between">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <StickyNote className="w-3.5 h-3.5 text-amber-400" /> Private Application Notes
          </label>
          <span className="text-[11px] text-slate-400">
            Contacts, referral details, salary expectations, interview feedback
          </span>
        </div>

        <textarea
          rows={4}
          placeholder="e.g. Applied via John Doe (referral). Technical round scheduled for Thursday 2 PM. Focus on distributed systems and FastAPI concurrency..."
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-600 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 leading-relaxed"
        />

        <div className="flex items-center justify-between">
          <div>
            {notesSavedSuccess && (
              <span className="text-xs text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Notes saved successfully!
              </span>
            )}
          </div>

          <Button
            type="button"
            size="sm"
            variant="secondary"
            disabled={isSavingNotes || notes === (job.notes || "")}
            onClick={handleSaveNotes}
            className="text-xs font-semibold bg-slate-800 text-slate-200 hover:bg-slate-700"
          >
            {isSavingNotes ? (
              <>
                <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> Saving Notes...
              </>
            ) : (
              <>
                <Save className="w-3.5 h-3.5 mr-1.5" /> Save Notes
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};
